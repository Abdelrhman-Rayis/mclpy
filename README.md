# mclpy

**The Microservice Composition Language (MCL) for Python: declare
ontology-bound, validated data interfaces and run them.**

MCL is a small declarative language in which you state the components of a
data interface (maps, time-series charts, KPIs, tables), the services or
Python functions that feed them, the ontology concepts they are bound to,
and the validation rules every payload must satisfy before it is rendered.
A Semantic View Controller (SVC) runtime executes the composition: an
ill-formed composition is rejected at load time, before any service is
invoked, and at run time every update is validated, provenance-stamped and
wrapped in a semantic envelope. Data that fails its declared rules is
withheld from the view, never silently rendered.

The language and pattern come from the PhD thesis *An Ontology-Driven
Framework for Composable and Semantically Interoperable Geospatial Systems*
(Keele University) and its reference implementation,
[micromaps-framework](https://github.com/Abdelrhman-Rayis/micromaps-framework).

## Install

```bash
pip install "mclpy[server] @ git+https://github.com/Abdelrhman-Rayis/mclpy"
# or from a clone:
pip install -e ".[server]"
```

The core (builder, checks, ontology layer) needs only `rdflib` and
`jsonschema`; the `[server]` extra adds the FastAPI runtime.

## Quickstart: an interface from your own Python data

```python
from mclpy import Composition, GEOIOT
from mclpy.server import serve

comp = (Composition("My dashboard")
        .service("local", "resolver://in-process")
        .timeseries("temp", concept=GEOIOT.Series,
                    parameter="airTemperature", unit="degC",
                    title="Air temperature")
        .expect_unit("degC")
        .expect_range(-20, 45)
        .expect_completeness(0.8, expected_points=72)
        .flow("temp", service="local", endpoint="/temp/series"))

def local(endpoint, params):                    # any Python data source
    return {"unit": "degC", "points": [{"t": "...", "v": 21.5}, ...]}

comp.check()                                    # schema + ontology checks
serve(comp, resolvers={"local": local})         # dashboard on :7300
```

Components can equally be fed by HTTP microservices (give the service a
real `base_url` and skip the resolver), or a mix of both. The generated
dashboard renders every component by kind, wires the declared
interactions (clicking a map feature re-binds target charts), and shows
the semantic envelope of each update: concept binding (click the chip to
dereference the term from the ontology), provenance, and per-rule
PASS/FAIL verdicts.

## The ontology layer is modular

Bindings are checked against an ontology, and the ontology is a plug-in.
The default is the bundled **GeoIoT** ontology; any RDF ontology works:

```python
from mclpy import RDFOntology, CompositeOntology, Namespace

SOSA = Namespace("http://www.w3.org/ns/sosa/")
sosa = RDFOntology("https://www.w3.org/ns/sosa/", format="turtle")

comp = (Composition("Observations")
        .service("s", "http://127.0.0.1:9000")
        .timeseries("obs", concept=SOSA.Observation, parameter="value")
        .flow("obs", service="s", endpoint="/obs"))

comp.check(ontology=sosa)                        # not GeoIoT: your choice
comp.check(ontology=CompositeOntology(sosa, RDFOntology("mine.ttl")))
```

`examples/custom_ontology.py` shows a composition validated against a
custom ontology and correctly rejected against the default.

## What gets checked

Load time (`comp.check()` / `mcl validate` / server start):

- MCL v1.0 JSON Schema conformance;
- unique service and component ids;
- every dataflow references a declared service and component;
- every component fed by exactly one dataflow;
- every bound concept exists in the ontology;
- unit rules agree with the binding's declared unit;
- interactions reference declared components.

Run time (every component update): declared `unit`, `range` and
`completeness` rules; failing payloads are withheld and the verdicts
returned in the envelope.

## CLI

```bash
mcl validate dashboard.mcl.json                 # against bundled GeoIoT
mcl validate dashboard.mcl.json --ontology my.ttl --ontology other.ttl
mcl serve    dashboard.mcl.json --port 7300
mcl render   dashboard.mcl.json -o dashboard.html
mcl schema                                      # print the JSON Schema
```

Plain MCL JSON documents and builder-made compositions are fully
interchangeable (`Composition.from_json` / `.to_json`).

## Layout

```
src/mclpy/builder.py      fluent Composition builder
src/mclpy/ontology.py     Ontology protocol, RDFOntology, CompositeOntology,
                          Namespace, bundled GeoIoT default
src/mclpy/checks.py       JSON Schema + ontology-aware static checks
src/mclpy/runtime.py      declarative validation engine
src/mclpy/server.py       embeddable FastAPI SVC (HTTP services or local
                          Python resolvers)
src/mclpy/render.py       generic dashboard (Leaflet + Chart.js)
src/mclpy/cli.py          mcl validate | render | serve | schema
src/mclpy/schema/         MCL v1.0 JSON Schema
src/mclpy/ontologies/     bundled GeoIoT ontology (Turtle)
examples/                 local-resolver app, custom-ontology demo
```

## Tests

```bash
pip install -e ".[dev]"
pytest -q
```

## License

MIT. The bundled GeoIoT ontology is part of the GeoIoT project
(geoiot.org).
