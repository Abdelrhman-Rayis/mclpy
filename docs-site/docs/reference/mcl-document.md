# Reference: the MCL document

An MCL composition is one JSON (or YAML) document. This page lists every section and field. The authoritative machine version is the JSON Schema shipped in the package (`mcl validate` and `check()` use it); run `mcl schema` to print it.

## Top level

| Field | Required | Meaning |
|---|---|---|
| `mcl_version` | yes | `"1.0"` or `"2.0"` |
| `title` | yes | human-readable name |
| `description` | no | free text |
| `services` | yes | list of data sources |
| `components` | yes | list of interface elements |
| `dataflows` | yes | connections from components to endpoints |
| `interactions` | no | selection-driven re-binding between components |
| `perspective` | 2.0 only | `@ident`; required in 2.0, forbidden in 1.0 |

## services

Each service names a data source.

```json
{ "id": "obs", "base_url": "http://127.0.0.1:7302", "description": "feeds and series" }
```

In the library, a service may instead be backed by a local Python function (a *resolver*), in which case `base_url` is a placeholder and the resolver is passed to `create_svc_app` / `serve`.

## components

Each component is one thing on the screen.

```json
{
  "id": "airchart",
  "kind": "timeseries",
  "title": "NO2",
  "binding": { "concept": "http://www.geoiot.org/ontology#Series",
               "parameter": "no2", "unit": "ug/m3" },
  "validation": [ { "type": "unit", "expected": "ug/m3" } ]
}
```

- `kind`: one of `map`, `timeseries`, `kpi`, `table`.
- `binding.concept`: the ontology concept URI the component represents (required).
- `binding.parameter`, `binding.unit`: optional descriptors.
- `validation`: list of rules; see [Validation rules](validation-rules.md).
- **2.0 only:** `binding.marks` and `binding.property_marks` carry OOON policy; see [Tutorial 5](../tutorials/policy-marks.md).

## dataflows

Each dataflow connects one component to one endpoint. Every component must have exactly one.

```json
{ "target": "airchart", "service": "obs", "endpoint": "/feeds/{feed}/series" }
```

`{feed}` is a slot filled at interaction time.

## interactions

Optional. Selecting a feature in one component re-binds another.

```json
{ "source": "sitemap", "event": "select", "target": "airchart", "effect": "filter" }
```

`effect` is `filter`, `highlight`, or (2.0) `join` with a `trigger.key`.

## The runtime endpoints

An SVC app serves:

| Endpoint | Returns |
|---|---|
| `GET /` | the dashboard |
| `GET /composition` | the checked document |
| `GET /component/{id}/data` | a [semantic envelope](../foundations/semantic-envelope.md) |
| `GET /concept?uri=...` | a concept's label, comment and type from the ontology |
| `GET /audit` | (2.0) the firewall attempt log |

## Building it in Python

You rarely write the JSON by hand; the fluent builder emits it:

```python
from mclpy import Composition, GEOIOT
comp = (Composition("Demo")
        .service("obs", "http://127.0.0.1:7302")
        .timeseries("airchart", concept=GEOIOT.Series, parameter="no2", unit="ug/m3")
        .expect_unit("ug/m3")
        .flow("airchart", service="obs", endpoint="/feeds/{feed}/series"))
doc = comp.to_dict()      # the JSON document
comp.to_json("dash.mcl.json")
```

`Composition.from_json` reads a document back, so hand-written and builder-made compositions are interchangeable.
