import pytest
from fastapi.testclient import TestClient

from mclpy import GEOIOT, Composition, MCLStaticError
from mclpy.ooon import check_marks, compile_jsonld, enforce
from mclpy.server import create_svc_app


def v2_comp() -> Composition:
    return (Composition("Policy demo")
            .perspective("estates-team")
            .service("local", "resolver://in-process")
            .timeseries("energy", concept=GEOIOT.Series,
                        parameter="electricity", unit="kW",
                        title="Building electricity")
            .mark_expose()
            .mark_property("siteLabel", bound="#privacy")
            .mark_property("uri", firewall=True)
            .expect_unit("kW")
            .flow("energy", service="local", endpoint="/e/{feed}/series"))


PAYLOAD = {"unit": "kW", "siteLabel": "Larchwood Residence",
           "uri": "http://www.geoiot.org/id/site/keele-173130",
           "points": [{"t": f"2026-07-{d:02d}T00:00:00", "v": 40 + d}
                      for d in range(1, 11)]}


def test_builder_upgrades_to_v2_and_passes_checks():
    comp = v2_comp()
    doc = comp.to_dict()
    assert doc["mcl_version"] == "2.0"
    assert doc["perspective"] == "@estates-team"
    comp.check()


def test_v2_without_perspective_is_rejected():
    comp = v2_comp()
    doc = comp.to_dict()
    del doc["perspective"]
    from mclpy import check_document
    with pytest.raises(MCLStaticError):
        check_document(doc)


def test_mark_composition_rules():
    assert check_marks({"expose": True, "join_key": "feed"}) == []
    assert check_marks({"firewall": True}) == []
    v = check_marks({"firewall": True, "expose": True})
    assert any("composes with nothing" in x for x in v)
    v = check_marks({"bound": "privacy"})
    assert any("#reason" in x for x in v)


def test_enforce_firewall_strips_and_logs():
    out, verdicts, audit = enforce(PAYLOAD, v2_comp().to_dict()["components"][0]["binding"])
    assert "uri" not in out
    assert "siteLabel" not in out
    assert len(out["points"]) == 10          # data itself untouched
    assert [a["event"] for a in audit] == ["firewall"]
    actions = {v["mark"]: v["action"] for v in verdicts}
    assert actions == {"firewall": "blocked", "bound": "withheld"}
    withheld = next(v for v in verdicts if v["mark"] == "bound")
    assert withheld["reason"] == "#privacy"


def test_compile_jsonld_degrades_gracefully():
    doc = v2_comp().to_dict()
    ld = compile_jsonld(doc)
    assert ld["ooon:perspective"] == "@estates-team"
    comp = ld["components"][0]
    assert comp["ooon:expose"] is True
    assert comp["ooon:firewall"] == [{"ooon:property": "uri"}]
    assert comp["ooon:boundProperties"]["siteLabel"] == "ooon:reason/privacy"
    # a marks-blind consumer still reads plain structure
    plain = {k: v for k, v in comp.items() if not k.startswith("ooon:")}
    assert plain == {"id": "energy", "kind": "timeseries",
                     "concept": str(GEOIOT.Series)}


def test_join_key_without_endpoint_slot_is_rejected():
    comp = (Composition("Bad join")
            .perspective("x")
            .service("s", "http://127.0.0.1:9")
            .map("m", concept=GEOIOT.Site)
            .timeseries("t", concept=GEOIOT.Series, parameter="p", unit="u")
            .flow("m", service="s", endpoint="/entities")
            .flow("t", service="s", endpoint="/series")   # no {feed} slot
            .on_join("m", "t", key="feed"))
    with pytest.raises(MCLStaticError) as e:
        comp.check()
    assert any("check 11" in v for v in e.value.violations)


def test_server_envelope_carries_policy_and_audit():
    def resolver(endpoint, params):
        return dict(PAYLOAD)
    app = create_svc_app(v2_comp(), resolvers={"local": resolver})
    client = TestClient(app)
    env = client.get("/component/energy/data", params={"feed": "f1"}).json()
    assert env["policy"]["perspective"] == "@estates-team"
    acts = {v["mark"]: v["action"] for v in env["policy"]["verdicts"]}
    assert acts == {"firewall": "blocked", "bound": "withheld"}
    assert "uri" not in env["data"] and "siteLabel" not in env["data"]
    assert env["validation"]["passed"]      # quality layer still runs
    audit = client.get("/audit").json()
    assert audit["count"] == 1
    assert audit["events"][0]["property"] == "uri"


def test_v1_documents_unaffected():
    comp = (Composition("Plain v1")
            .service("s", "http://127.0.0.1:9")
            .timeseries("t", concept=GEOIOT.Series, parameter="p", unit="u")
            .flow("t", service="s", endpoint="/series"))
    doc = comp.to_dict()
    assert doc["mcl_version"] == "1.0"
    assert "perspective" not in doc
    comp.check()
