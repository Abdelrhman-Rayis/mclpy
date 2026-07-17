# OOON Specification (draft 0.9)

**Object Oriented Ontology Notation: an intrinsic policy layer for MCL.**

Status: Phase-0 draft for supervisor review. Formalises the notation
introduced in the 31 March 2026 progress presentation. Normative words
(MUST, MUST NOT, SHOULD, MAY) follow RFC 2119 usage.

OOON attaches per-property *epistemic policy* to data objects: not what
a value is, but how it may be treated. Marks travel with the data. A
document without its marks is not a valid OOON document, which is the
design's central claim: policy is intrinsic to the data, not a
strippable middleware layer.

The marks are epistemic policies, not metaphysical claims. `bound` does
not assert that reality is hidden; it records an auditable decision to
withhold, and the mandatory reason makes that decision falsifiable.

**Structural inspiration (Tajweed, علوم التجويد).** The mark system is
modelled on Tajweed, the rule system of Quranic recitation, where marks
are embedded in the text itself and carry their rules with them: no
external rulebook is consulted at the point of use. Three properties
carry over: self-containment (marks live in the object, not an external
schema), local contact rules (relations emerge from adjacency and
mark-matching, as idgham fires between adjacent letters), and
completeness (the system is interpretable without consulting anything
outside the text). Each mark has a Tajweed root:

| Mark | Root | | Mark | Root |
|---|---|---|---|---|
| `↑` expose | izhar (إظهار) | | `✕` firewall | waqf (وقف) |
| `~` bound | ikhfa (إخفاء) | | `∞` drifting | madd (مد) |
| `⊕` join | idgham (إدغام) | | `°` self-assertion | tanwin (تنوين) |

The analogy's limits are stated honestly: Tajweed's rules are grounded
in centuries of phonological practice with determinate outputs; OOON's
contact rules are grounded in epistemic policy theory and are a
research prototype. The structural form is borrowed; the semantics are
original.

---

## 1. Marks

| Mark | Name | Meaning at the interface |
|---|---|---|
| `^` (`↑`) | expose | Property is available to queries and views. |
| `~ #reason` | bound | Property is withheld under a boundary policy; the reason MUST be given. |
| `+(key)` (`⊕`) | join trigger | Property participates in contact rules, joining on `key`. |
| `x` (`✕`) | firewall | Relation blocked; any access attempt MUST be refused and logged. |
| `8` (`∞`) | drifting | Value is an interval or distribution, never a point. |
| `@ident` | perspective | Whose representation this object is. MANDATORY per object. |
| `#ident` | reason | Machine-readable justification; MANDATORY wherever `~` appears. |
| `°` | self-assertion | Automatic on every object header: the object exists on its own terms, prior to any property list. Not user-written; emitted by serialisers. |

The Unicode symbols (`↑ ~ ⊕ ✕ ∞ @ #`) are the canonical *display* form.
The ASCII aliases in parentheses are accepted by parsers. JSON and
JSON-LD carriers use named terms only (Section 4); symbols never appear
in machine-exchanged keys.

### 1.1 Composition

Marks compose left to right on one property. `~∞ #privacy` means bound
and drifting: withheld under a policy, and interval-valued if ever
disclosed. Legal compositions:

- `^` MAY combine with `+(key)` and `∞`.
- `~` MAY combine with `∞`; the composite still requires `#reason`.
- `x` composes with nothing: a firewalled property has no other policy.
- `@` and `#` are not property marks; `@` scopes an object, `#`
  completes a `~`.

### 1.2 Operational rules (well-formedness)

1. Every object MUST carry exactly one perspective (`@ident`).
2. Every `~` MUST carry a `#reason`. A document violating this is
   invalid, not merely incomplete.
3. Marks MAY combine as in 1.1; illegal combinations are rejected
   statically.
4. Objects are self-contained: a property's policy is interpretable
   without consulting any other object.

## 2. Grammar (EBNF)

```
document    = object , { object } ;
object      = "(" , ident , "°" , perspective , ")" ,
              { property } ,
              "(/)" ;
perspective = "@" , ident ;                 (* who made this representation *)
property    = key , ":" , value , { mark } , [ reason ] ;
key         = ident ;
value       = literal | "?" | ident ;       (* "?" = declared-unknown *)
mark        = "^"                            (* expose *)
            | "~"                            (* bound; reason REQUIRED *)
            | "+(" , key , ")"               (* join trigger *)
            | "x"                            (* firewall *)
            | "8" ;                          (* drifting *)
reason      = "#" , ident ;
```

Contact between adjacent objects and the resulting relation:

```
contact     = object , "|" , object ;        (* pipe triggers evaluation *)
result      = relation | contact-event | "0" ;   (* 0 = no relation *)
relation    = "(" , '"rel"' , "°" , perspective , ")" ,
              "from:"    , ident , "^" ,
              "to:"      , ident , "^" ,
              "key:"     , key   , "^" ,
              "type:"    , ( "full" | "partial" | "asymmetric" ) , "^" ,
              [ "residue:" , value , "~" , "#partial" ] ,
              "(/)" ;
```

A relation is itself an OOON object: it has a perspective, exposed
properties, and (for partial matches) a bound residue recording what
did not match, with the mandatory `#partial` reason.

## 3. Contact rules

When two objects are piped, their join-triggered properties (`+(key)`)
are evaluated pairwise on the shared key:

| Outcome | Condition | Result |
|---|---|---|
| Matching | values agree on the join key | `relation` with `type: full` |
| Partial | values overlap | `relation` with `type: partial` and a `residue` |
| Bound | either side's property is `~` | contact-event recording the refusal and its `#reason` |
| Firewall | either side is `x` | no relation; the attempt is logged |

**OPEN-QUESTION (supervisors):** the `asymmetric` relation type and the
precise semantics of `residue` (is it the unmatched value set, a
similarity score, or free-form?) are underspecified in the source
material and MUST be fixed before implementation.

## 4. JSON-LD carrier (`ooon:` vocabulary)

OOON compiles to JSON-LD so that standard consumers degrade gracefully:
a schema.org processor ignores `ooon:*` terms and still sees a valid
document. Namespace: `https://www.geoiot.org/ooon#` (prefix `ooon:`).

| Term | Value | Carries |
|---|---|---|
| `ooon:perspective` | string/IRI | `@ident` (object level, REQUIRED) |
| `ooon:expose` | `true` | `^` |
| `ooon:bound` | IRI of reason, e.g. `ooon:reason/privacy` | `~ #reason` |
| `ooon:trigger` | `{ "ooon:key": k, "ooon:value": v }` | `+(key)` |
| `ooon:firewall` | `{ "ooon:property": p }` | `x` |
| `ooon:drifting` | `true` (value becomes `{min,max}` or `{value,uncertainty}`) | `8` |

A bound property's *value* is omitted from the compiled document; only
the `ooon:bound` reason ships. A firewalled property ships neither
value nor key outside the `ooon:firewall` record.

**OPEN-QUESTION (supervisors):** is the reason vocabulary closed
(`#privacy`, `#unresolvable`, `#out-of-scope`, `#partial`, ...) or an
open set of identifiers? The compiler needs to know whether to validate
reasons against a list.

## 5. OOON in MCL 2.0

MCL 2.0 embeds OOON as the policy layer beside (not replacing) the
validation layer:

- The document gains a REQUIRED top-level `perspective`.
- A component binding MAY carry `marks` for the bound concept and
  `property_marks` for individual payload properties.
- Interactions MAY be declared as join triggers (`trigger: {key}`),
  grounding v1's ad-hoc select/filter in contact rules.
- Validation rules (unit, range, completeness) are unchanged: MCL v1
  governs *quality*; OOON governs *disclosure*. Same enforcement point,
  two dimensions.

### 5.1 New static checks (Phase 1 implements)

8. The document declares a perspective (2.0 only).
9. Every `bound` mark carries a reason.
10. No firewalled property appears in any dataflow, interaction or
    validation rule.
11. Every join trigger's key exists in both source and target bindings.
12. Mark compositions are legal per Section 1.1.

### 5.2 SVC enforcement semantics (Phase 1 implements)

- **expose**: default render path (unchanged from v1).
- **bound**: the property is withheld; the envelope's policy verdicts
  record `withheld` with the reason. The view MAY show the reason.
- **firewall**: the property is stripped before the envelope is built;
  the access attempt is logged. **OPEN-QUESTION (supervisors):** do
  firewall logs belong in the envelope history or a separate audit log?
- **drifting**: the payload carries intervals; the envelope marks the
  series as interval-valued and views SHOULD render uncertainty (bands,
  not lines).
- **perspective**: recorded in every envelope beside provenance.

## 6. Versioning and compatibility

- MCL `mcl_version: "1.0"` documents remain valid: no perspective, no
  marks, v1 checks only.
- `mcl_version: "2.0"` activates checks 8-12 and the enforcement
  semantics of 5.2.
- The machine schema for both lives in
  `src/mclpy/schema/mcl_schema_v2.json`.

## 7. Design lineage: the five critiques and the v2 answers

OOON v2 (this specification) is shaped by five recorded criticisms of
v1 (philosopher and supervisor review, documented in the OOON research
report):

| Critique | v1 | v2 answer (this spec) |
|---|---|---|
| Notation paradox (ontological) | `history:?~` claimed metaphysical withdrawal | `~` is an epistemic policy plus mandatory audit tag |
| Untestable withdrawal (epistemological) | `~` with no justification | `~` is syntactically invalid without `#reason` |
| Tajweed ungrounded (practical) | "a relation emerges" | typed contact output: relations are OOON objects with `type: full/partial` and residue |
| Situated flatness (epistemological) | `(city°)` claimed neutrality | `(city° @cartographer)`: flatness is a declared stance |
| No engineering path (pragmatic) | visual notation only | grammar + contact types + this implementation (mclpy 0.2) |

## 8. Candidate v3 marks (recorded, NOT implemented)

Four further epistemic states are proposed and tested against real
data in the research report; they are recorded here for roadmap
purposes and are deliberately absent from MCL 2.0:

- `≈` inferred: derived, not directly observed (for example computed centroids);
- contested: no authoritative value exists, without splitting into two perspectives;
- `→` delegated: ask another object (for example `speed-limit:30→@highways`);
- `∂` approximate: shared at deliberately reduced precision.

Equally recorded is what NOT to add: negation (firewall and absence
already serve), confidence scores (false precision; `~`, `≈`, `∂`
handle uncertainty without quantifying it), and mandatory markers
(schema validation is OWL/SHACL's job).

## 9. Positioning: the six clusters and three closest precursors

A prior literature review across six clusters (vagueness and
uncertainty; provenance and perspective; policy and access control;
critical GIS; geospatial linked data; self-describing data) found the
mechanisms existing separately but never composed: no system lets a
spatial data object declare which of its properties are exposed,
bounded, unknown or drifting, inside its own serialisation. The three
closest precursors, and where each stops:

- **Galton and Hood (2005), anchoring relations**: epistemically
  motivated ("state only what we know for certain") but operates at
  the representation level, not object serialisation.
- **Sacco and Passant (2011), Privacy Preference Ontology**:
  per-triple access policy, but maintained in a separate document, not
  embedded in the object.
- **Kirrane and Akaichi (2023), GUCON**: RDF-star-attached policy
  metadata, mechanistically closest, but addresses usage-control
  compliance, not epistemic visibility classification.

The Phase-4 positioning survey (ODRL, DPV, GeoXACML, PPO, GUCON) MUST
formalise this comparison before any published novelty claim.

## 10. What OOON is not

- Not access control: an optional ACL layer may still sit above
  (deployment concern). OOON makes policy travel with data so that
  stripping the middleware cannot strip the policy.
- Not SHACL: SHACL constrains graph shapes at rest; OOON policies act
  on data in flight at the interface boundary. Compilation between the
  two is future work.
- Not ODRL/DPV replacement until proven: a positioning survey against
  ODRL, DPV, XACML and policy-aware Linked Data is REQUIRED before any
  novelty claim is published (Phase 4 of the v2 plan).
```
