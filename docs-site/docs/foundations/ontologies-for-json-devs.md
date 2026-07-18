# Ontologies for JSON developers

This is the one idea in MCL that might be new to you. It is much simpler than its reputation. If you understand JSON Schema, you are 90% of the way there.

!!! tip "The short version"
    You can use MCL forever with the built-in vocabulary and **never write an ontology**. Read the first two sections, then skip to [GeoIoT in one picture](geoiot-in-one-picture.md). Come back here the day you want your own vocabulary.

## Schema types the shape; an ontology types the meaning

You already know **JSON Schema**. It says what a document's *shape* must be: this field is a string, that one is a number between 0 and 100, this array has at least one item. Shape, not meaning.

An **ontology** says what a value *means*. It is a shared dictionary of concepts and the relationships between them. Where JSON Schema says "this is a number", an ontology says "this is a `Measurement`, which belongs to a `Series`, which is produced by a `Device`, which is attached to a `Building`."

That is the whole difference. Schema types the shape of your data. An ontology types the meaning of your data. MCL uses both: JSON Schema to check the composition document is well-formed, and an ontology to check that each component is bound to a concept that actually exists.

## Three words, defined once

You will meet three terms. Here they are, plainly.

**Concept** (also called a *class*). A kind of thing, like `Building`, `Sensor`, or `Series`. In your data, individual buildings and sensors are *instances* of these concepts. A concept is just a named category.

**URI**. A globally unique name for a concept, written as a web address. `http://www.geoiot.org/ontology#Series` is the URI for the `Series` concept. The web-address form guarantees no two projects accidentally use the same name for different things. It does not have to resolve to a live page; it is an identifier, like a package name.

**Triple**. The atom of an ontology: *subject, predicate, object*. "Series (subject) hasUnit (predicate) kW (object)." Ontologies are built from triples, but you rarely write them by hand for MCL. This is background, not homework.

## What an ontology looks like

Ontologies are usually written in **Turtle**, a compact text format. Here is a complete, tiny one. You do not need to memorise it, just see that it is readable:

```turtle
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix farm: <http://example.org/farm#> .

farm:Barn a owl:Class ;                       # (1)
    rdfs:label "Barn" ;                        # (2)
    rdfs:comment "A farm building holding livestock or equipment." .

farm:SensorSeries a owl:Class ;
    rdfs:label "Sensor series" ;
    rdfs:comment "A time-ordered series of readings from a barn sensor." .
```

1. `farm:Barn a owl:Class` declares that `Barn` is a concept. `a` means "is a".
2. `rdfs:label` and `rdfs:comment` give a human-readable name and description. MCL can show these when you click a concept in the dashboard.

That is a usable ontology. Two concepts, each with a name and a description. Real ontologies add relationships between concepts (`hasSensor`, `locatedIn`), but the idea does not get harder.

## How MCL uses it

When you bind a component to a concept:

```python
.timeseries("temp", concept=GEOIOT.Series, parameter="airTemperature", unit="degC")
```

MCL does two things with that binding. At load time, its [static checks](../reference/static-checks.md) confirm the concept actually exists in the ontology, so a typo like `Seriez` is caught before anything runs. At run time, the concept travels in the [semantic envelope](semantic-envelope.md), so anyone inspecting the chart can see what it claims to represent and read the concept's definition.

## Why bother, honestly

You could skip all this and bind charts to bare strings. The payoff of using real concepts is threefold: typos become load-time errors instead of silent bugs; every chart carries a checkable statement of what it means; and the same interface can be pointed at a different domain by swapping the ontology, which [Tutorial 3](../tutorials/own-ontology.md) demonstrates. The cost is close to zero, because MCL ships a ready-made ontology you can use immediately.

## Next

- [GeoIoT in one picture](geoiot-in-one-picture.md): the built-in vocabulary, so you can start today without writing any of this.
- [Bring your own ontology](../tutorials/own-ontology.md): when you are ready, in about ten minutes.
