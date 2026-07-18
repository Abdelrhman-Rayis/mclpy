# Tutorial 3: Bring your own ontology

**What you will build.** A composition validated against a *custom* ontology, not GeoIoT, and you will prove the swap is real by watching the same document pass against your ontology and correctly fail against the default.

**You need.** Tutorial 1 done.

---

## Step 1 — a tiny ontology

Create `farm.ttl`. This is a complete two-concept ontology (see [Ontologies for JSON developers](../foundations/ontologies-for-json-devs.md) if the syntax is new):

```turtle title="farm.ttl"
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix farm: <http://example.org/farm#> .

farm:Barn a owl:Class ;
    rdfs:label "Barn" ;
    rdfs:comment "A farm building holding livestock or equipment." .

farm:SensorSeries a owl:Class ;
    rdfs:label "Sensor series" ;
    rdfs:comment "A time-ordered series of readings from a barn sensor." .
```

## Step 2 — load it and bind to it

`Namespace` builds concept URIs the way `GEOIOT` does. `RDFOntology` loads any ontology file:

```python title="farm_app.py"
from mclpy import Composition, Namespace, RDFOntology

FARM = Namespace("http://example.org/farm#")           # FARM.SensorSeries -> ...#SensorSeries
farm = RDFOntology("farm.ttl", name="farm")

comp = (
    Composition("Barn monitor")
    .service("s", "http://127.0.0.1:9000")
    .timeseries("humidity", concept=FARM.SensorSeries,
                parameter="humidity", unit="percent", title="Barn humidity")
    .expect_unit("percent")
    .expect_range(0, 100)
    .flow("humidity", service="s", endpoint="/humidity/series")
)

comp.check(ontology=farm)          # (1)
print("valid against the farm ontology")
print(farm.describe(str(FARM.SensorSeries)))
```

1. `check(ontology=farm)` validates the composition against *your* ontology. The concept `farm:SensorSeries` exists there, so the check passes.

Run it: the composition is accepted, and `describe` prints the concept's label and comment, pulled from your Turtle file.

## Step 3 — prove the swap is real

Add these lines and run again:

```python
from mclpy import MCLStaticError
try:
    comp.check()                   # no ontology argument -> the default, GeoIoT
except MCLStaticError as e:
    print("correctly rejected against the default GeoIoT ontology:")
    print("  ", e.violations[0])
```

The same document now *fails*, with a precise message: the concept `http://example.org/farm#SensorSeries` is not present in GeoIoT. This is the point. The ontology is a genuine, swappable module: bind to farm concepts and check against farm; the machinery does not care which vocabulary, only that the concepts you bind to actually exist in the one you check against.

## Step 4 — stack ontologies (optional)

To use several vocabularies at once, wrap them in a `CompositeOntology`:

```python
from mclpy import CompositeOntology, geoiot
combined = CompositeOntology(farm, geoiot())
comp.check(ontology=combined)      # concepts from either ontology are accepted
```

## What just happened

You replaced MCL's built-in vocabulary with your own in one line, bound components to your own concepts, and confirmed the binding is checked for real. Any RDF ontology works: SOSA, SAREF, a schema your organisation maintains, or a two-line file you wrote this morning.

## Next

- [Tutorial 4](break-it.md): the systematic tour of what the rules catch, and what they cannot.
- [Reference: static checks](../reference/static-checks.md): including the concept-existence check you just triggered.
