import pytest

from mclpy import (GEOIOT, Composition, MCLStaticError, RDFOntology,
                   check_document, static_violations)


def sample() -> Composition:
    return (Composition("Test dashboard", description="builder round-trip")
            .service("obs", "http://127.0.0.1:9000", "observations")
            .map("sitemap", concept=GEOIOT.Site, title="Sites")
            .timeseries("levels", concept=GEOIOT.Series,
                        parameter="waterLevel", unit="m", title="Levels")
            .expect_unit("m").expect_range(-1, 12)
            .expect_completeness(0.6, expected_points=96)
            .flow("sitemap", service="obs", endpoint="/entities")
            .flow("levels", service="obs", endpoint="/feeds/{feed}/series")
            .on_select("sitemap", filter="levels"))


def test_builder_produces_checkable_document():
    doc = sample().check().to_dict()
    assert doc["mcl_version"] == "1.0"
    assert [c["id"] for c in doc["components"]] == ["sitemap", "levels"]
    rules = doc["components"][1]["validation"]
    assert [r["type"] for r in rules] == ["unit", "range", "completeness"]


def test_json_round_trip(tmp_path):
    p = tmp_path / "comp.mcl.json"
    sample().to_json(p)
    again = Composition.from_json(p)
    assert again.to_dict() == sample().to_dict()
    again.check()


def test_unknown_concept_rejected_by_default_geoiot():
    comp = sample()
    doc = comp.to_dict()
    doc["components"][0]["binding"]["concept"] = str(GEOIOT.NoSuchClass)
    with pytest.raises(MCLStaticError) as e:
        check_document(doc)
    assert any("not present in the ontology" in v for v in e.value.violations)


def test_custom_ontology_is_pluggable(tmp_path):
    ttl = tmp_path / "farm.ttl"
    ttl.write_text("""
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
<http://example.org/farm#Barn> a owl:Class ;
    rdfs:label "Barn" ; rdfs:comment "A farm building." .
""")
    farm = RDFOntology(ttl, name="farm")
    comp = (Composition("Farm")
            .service("s", "http://127.0.0.1:9000")
            .table("barns", concept="http://example.org/farm#Barn")
            .flow("barns", service="s", endpoint="/barns"))
    comp.check(ontology=farm)          # passes with the custom ontology
    with pytest.raises(MCLStaticError):
        comp.check()                   # fails against default GeoIoT
    info = farm.describe("http://example.org/farm#Barn")
    assert info["label"] == "Barn" and "Class" in info["types"]


def test_static_checks_catch_structural_faults():
    doc = sample().to_dict()
    doc["dataflows"][0]["service"] = "ghost"
    v = static_violations(doc)
    assert any("unknown service 'ghost'" in x for x in v)

    doc2 = sample().to_dict()
    doc2["dataflows"] = doc2["dataflows"][:1]
    v2 = static_violations(doc2)
    assert any("'levels' has no dataflow" in x for x in v2)

    doc3 = sample().to_dict()
    doc3["components"][1]["binding"]["unit"] = "ft"
    v3 = static_violations(doc3)
    assert any("unit rule expects" in x for x in v3)


def test_schema_rejects_bad_kind():
    doc = sample().to_dict()
    doc["components"][0]["kind"] = "hologram"
    with pytest.raises(MCLStaticError) as e:
        check_document(doc)
    assert any(v.startswith("schema:") for v in e.value.violations)
