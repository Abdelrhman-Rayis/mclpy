import pytest
from fastapi.testclient import TestClient

from mclpy import GEOIOT, Composition, validate_payload
from mclpy.render import dashboard_html
from mclpy.server import create_svc_app

RULES = [
    {"type": "unit", "expected": "degC"},
    {"type": "range", "min": -20, "max": 45},
    {"type": "completeness", "min_ratio": 0.5, "expected_points": 10},
]

CLEAN = {"unit": "degC",
         "points": [{"t": f"2026-07-17T{h:02d}:00:00", "v": 15 + h}
                    for h in range(10)]}


def test_validate_payload_rules():
    assert validate_payload(CLEAN, RULES)["passed"]
    bad_unit = dict(CLEAN, unit="F")
    r = validate_payload(bad_unit, RULES)
    assert not r["passed"]
    assert [v["passed"] for v in r["verdicts"]] == [False, True, True]
    bad_range = {"unit": "degC",
                 "points": CLEAN["points"][:-1] + [{"t": "x", "v": 999.0}]}
    assert not validate_payload(bad_range, RULES)["passed"]
    sparse = {"unit": "degC", "points": CLEAN["points"][:3]}
    assert not validate_payload(sparse, RULES)["passed"]


def _comp() -> Composition:
    return (Composition("Local resolver demo")
            .service("local", "http://unused.invalid")
            .timeseries("temp", concept=GEOIOT.Series,
                        parameter="airTemperature", unit="degC",
                        title="Temperature")
            .expect_unit("degC").expect_range(-20, 45)
            .flow("temp", service="local", endpoint="/temp/series"))


def _resolver(payload):
    def resolve(endpoint, params):
        assert endpoint == "/temp/series"
        return payload
    return resolve


def test_server_serves_validated_envelope_from_local_resolver():
    app = create_svc_app(_comp(), resolvers={"local": _resolver(CLEAN)})
    client = TestClient(app)

    doc = client.get("/composition").json()["document"]
    assert doc["title"] == "Local resolver demo"

    env = client.get("/component/temp/data").json()
    assert env["status"] == "ok"
    assert env["binding"]["concept"] == str(GEOIOT.Series)
    assert env["provenance"]["url"].startswith("resolver:local")
    assert len(env["data"]["points"]) == 10

    page = client.get("/").text
    assert "Semantic envelope" in page


def test_server_withholds_failing_payload():
    bad = dict(CLEAN, unit="F")
    app = create_svc_app(_comp(), resolvers={"local": _resolver(bad)})
    env = TestClient(app).get("/component/temp/data").json()
    assert env["status"] == "rejected"
    assert env["data"] is None
    assert not env["validation"]["passed"]


def test_server_refuses_ill_formed_composition():
    from mclpy import MCLStaticError
    comp = _comp()
    doc = comp.to_dict()
    doc["components"][0]["binding"]["concept"] = "http://nope.example/X"
    with pytest.raises(MCLStaticError):
        create_svc_app(doc)


def test_concept_endpoint_dereferences_default_ontology():
    app = create_svc_app(_comp(), resolvers={"local": _resolver(CLEAN)})
    info = TestClient(app).get(
        "/concept", params={"uri": str(GEOIOT.Series)}).json()
    assert info["label"] == "Series"
    assert "time-ordered" in info["comment"]


def test_dashboard_html_contains_title():
    page = dashboard_html(_comp())
    assert "<title>Local resolver demo</title>" in page
