# Glossary

Plain definitions for every specialised term in this wiki. When a page uses one of these for the first time, this is where it points.

### Binding
The statement, in a component, of which ontology **concept** it represents, and optionally the parameter and unit. A binding is what makes a chart mean something checkable rather than just displaying numbers.

### Component
One element of an interface: a `map`, `timeseries`, `kpi`, or `table`. The building block of an MCL composition.

### Composition
A whole MCL document: the components, their data sources, their bindings, their rules, and their interactions. One file describing one interface.

### Concept
A named category of thing in an ontology, such as `Site` or `Series`. Also called a *class*. Your individual buildings and sensors are *instances* of concepts.

### Dataflow
The connection between one component and one service endpoint. It says where a component's data comes from.

### GeoIoT
The ontology that ships with MCL as the default vocabulary. It models sensor data as a chain: Site, Asset, Device, Feed, Series, Measurement.

### JSON-LD
JSON with a linked-data context, so that plain JSON can carry ontology meaning. MCL 2.0 compiles policy to JSON-LD so ordinary consumers can ignore the policy terms and still read a valid document.

### mclpy
The Python library that implements MCL. What this wiki documents.

### Ontology
A shared, machine-readable dictionary of concepts and their relationships. Where JSON Schema types your data's *shape*, an ontology types its *meaning*.

### OOON
Object Oriented Ontology Notation: the policy layer added in MCL 2.0 (preview). Attaches disclosure marks (expose, bound, firewall, drifting) and a perspective to data.

### Provenance
The record of where a piece of data came from: which service, which URL, when. Carried in every semantic envelope.

### Resolver
A local Python function that serves a component's data in-process, instead of an HTTP microservice. Takes `(endpoint, params)` and returns `{"unit": ..., "points": [...]}`.

### RDF
Resource Description Framework: the data model ontologies are built on, made of subject-predicate-object **triples**. You almost never touch it directly to use MCL.

### Semantic envelope
The structured record the runtime returns for every update: the binding, the provenance, the validation verdicts, and (only if valid) the data. Makes each chart self-explaining.

### Semantic View Controller (SVC)
The runtime that executes an MCL document: checks it, mediates every update, validates, and wraps the result in a semantic envelope.

### Service
A named data source in a composition: an HTTP microservice with a base URL, or a local resolver.

### SHACL
A W3C standard for constraints over RDF graphs. MCL's rules are deliberately not SHACL: they act on payloads in flight at the interface, not on graphs at rest.

### Static checks
The dozen checks the runtime runs on a composition before executing it. A violation stops the runtime from starting. See [the reference](reference/static-checks.md).

### Triple
The atom of an ontology: subject, predicate, object. "Series hasUnit kW."

### URI
A globally unique identifier written as a web address, used to name a concept unambiguously. It identifies; it need not resolve to a live page.

### Validation rule
A declared expectation on a component's data: `unit`, `range`, or `completeness`. Enforced on every update; failure withholds the data.
