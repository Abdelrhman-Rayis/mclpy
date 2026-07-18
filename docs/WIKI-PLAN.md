# MCL Developer Wiki: full build plan

Goal: a public wiki that takes a developer with **no semantic-web,
ontology or GIS background** from zero to (a) understanding the whole
framework of the MCL/SVC paper and (b) building their own validated,
ontology-bound dashboard on their own data.

Working title: **"MCL: declare dashboards you can trust"** (site name
`mcl.dev` style; actual host below).

---

## 1. Audience and the one promise

**Persona (design everything for this person):** a working Python or
web developer. Knows JSON, REST, pip, maybe Grafana. Has NEVER heard
of RDF, OWL, SPARQL, triples, or ontologies. Suspicious of academic
vocabulary. Wants running code in minutes, understanding second,
theory last.

**The wiki's one promise (on the landing page):** *"In 15 minutes you
will run a dashboard that refuses to render bad data, and you will
know why that matters."*

**Anti-goals:** not a semantic-web textbook; not the thesis; not API
docs only. Never require reading a paper to proceed.

## 2. Structure: Diátaxis

Organise by the four Diátaxis quadrants, visible as top navigation:

1. **Tutorials** (learning by doing, guaranteed success)
2. **How-to guides** (task recipes for people already oriented)
3. **Reference** (exact, exhaustive, generated where possible)
4. **Explanation** (understanding, background, the paper's ideas)

Plus two cross-cutting front doors: **Start here** and **Glossary**.

## 3. Full page inventory (36 pages)

### 3.0 Start here (3 pages)
- **Home / the pitch**: the kWh-vs-Wh story in 5 sentences; animated
  GIF of a rejection; the promise; 3 buttons (Quickstart, What is this,
  I know Grafana).
- **Install and quickstart**: pip install, the 15-line local-resolver
  app, browser screenshot, "you just did X" recap.
- **Coming from Grafana/Plotly/Streamlit**: mapping table of familiar
  concepts to MCL ones; what MCL adds (bindings, checks, envelopes) and
  what it does not do (panel styling, alerting).

### 3.1 Foundations without the jargon (5 pages, Explanation)
Written so each takes under 7 minutes; no page may use a term before
its primer or a glossary link.
- **Why dashboards lie**: unit switches, impossible values, sparse
  series rendered as truth; the real Sanchinarro rejection as the
  hook; pipeline cleaning vs point-of-use enforcement.
- **Ontologies for JSON developers**: "JSON Schema types your data's
  *shape*; an ontology types its *meaning*". Concepts, URIs as global
  IDs, labels/comments; a 10-line Turtle file dissected. Explicitly:
  you can use MCL forever with the bundled GeoIoT ontology and never
  write Turtle.
- **The GeoIoT ontology in one picture**: Site - Asset - Device -
  Feed - Series - Measurement chain diagram; when this vocabulary fits
  (anything with sensors somewhere) and when to bring your own.
- **Declare, check, enforce**: the paper's thesis as a developer story;
  what "declarative" buys (static checks, one artefact, machine
  generation later).
- **The semantic envelope**: annotated real envelope JSON, field by
  field; why provenance and verdicts travel with every update.

### 3.2 Tutorials (7 pages, strictly progressive)
Each: "What you'll build / You need / Steps / What just happened /
Next". Every snippet copy-paste runnable and CI-tested.
1. **Your first validated dashboard** (local resolver, synthetic
   temperature, one chart; inject a wrong unit by editing one line and
   watch the rejection).
2. **Real open data** (Environment Agency river API; no key; map +
   chart + click-to-filter; the reader's first real interaction
   declaration).
3. **Two services, one composition** (split the resolver into two
   FastAPI microservices; same document, base_url swap; the
   microservice story).
4. **Bring your own ontology** (farm.ttl from the repo; RDFOntology,
   check() failing against GeoIoT and passing against farm;
   CompositeOntology stacking).
5. **Extend a running dashboard** (the paper's T2 water-view task as a
   tutorial; count your own added lines; re-check on load).
6. **Break it on purpose** (fault-injection tour: unit, range,
   completeness; read verdicts in the envelope inspector; where the
   boundary is: in-range corruption passes and why).
7. **Policy marks preview (MCL 2.0/OOON)** (clearly labelled preview:
   perspective, bound #privacy, firewall + /audit, drifting; the
   symbols ↑ ~ ⊕ ✕ ∞ @ #).

### 3.3 How-to guides (8 pages)
- Write validation rules that match your sensor's physics.
- Serve a component from a DataFrame / database / message queue
  (local-resolver patterns).
- Load an ontology from a URL (SOSA example) and pin it locally.
- Run and read the `mcl` CLI (validate / render / serve / schema).
- Debug a composition that will not start (violation message
  catalogue walk-through).
- Put the SVC behind uvicorn/nginx (deployment notes, ports, CORS).
- Regenerate the paper's evaluation numbers (run_all.sh of the
  evaluation artefact).
- Migrate a v1 document to 2.0 (add perspective; add marks; what
  changes in envelopes).

### 3.4 Reference (8 pages, generated where possible)
- MCL v1.0 document: every field, types, defaults (generated from
  JSON Schema).
- MCL v2.0 additions: perspective, marks, property_marks, join
  trigger (generated from schema v2).
- The 12 static checks: number, meaning, example violation text.
- Validation rules: unit/range/completeness semantics, edge cases.
- OOON marks: symbol, name, enforcement action, envelope shape.
- `mclpy` Python API (mkdocstrings from docstrings: Composition,
  RDFOntology, CompositeOntology, Namespace, create_svc_app, serve,
  validate_payload, ooon module).
- HTTP endpoints of an SVC app (/composition, /component/{id}/data,
  /concept, /audit) with example responses.
- Envelope format spec (validation + policy variants).

### 3.5 Explanation, deeper (3 pages)
- **Architecture** (mermaid: document -> checks -> SVC -> services/
  resolvers -> envelope -> view; where MicroMaps fits as the big
  sibling deployment).
- **How MCL compares** (the paper's positioning table rewritten for
  developers: vs Grafana-as-code, Vega-Lite, WebDSL, plain FastAPI).
- **The research behind it** (plain-language summary of the paper +
  links/citations to MicroMaps ICCBDC 2025, GeoIoT Core ICCBDC 2026,
  the MCL/SVC paper; how to cite).

### 3.6 Community (2 pages)
- Contributing (dev setup, tests, doc style rules, PR checklist).
- Roadmap and status (v1 stable, 2.0 preview, candidate v3 marks;
  honest known-limits list from the paper).

## 4. Pedagogy rules (enforced in review)

1. **No term before its primer**: jargon linter list (ontology, RDF,
   URI, SPARQL, triple, OWL, provenance, envelope...) — first use on
   any page must be a glossary link.
2. **Runnable or absent**: every code block executes in CI against the
   released package; snippets are extracted and pytest-run.
3. **Under 7 minutes a page** (~1,200 words); split otherwise.
4. **Show the failure first** where possible: rejections teach the
   value faster than successes.
5. **Real data over toy data** after tutorial 1.
6. **British spelling; no em-dashes** (house style).
7. Screenshots dpi-consistent, dark-friendly; every diagram has alt
   text.

## 5. Infrastructure

- **Tooling**: MkDocs + Material theme; `mkdocstrings[python]` for API
  reference; `mike` for versioned docs (v0.2, latest); mermaid via
  pymdownx.superfences; glossary via abbreviations file.
- **Location**: `mclpy/docs-site/` (own mkdocs.yml), deployed by
  GitHub Actions to GitHub Pages on push to main.
- **Gate**: GitHub Pages needs the repo public (or Pro plan).
  DECISION FOR ABDELRHMAN: make mclpy public at wiki launch, or deploy
  to Read the Docs (works with private repos on paid tier), or keep
  private and ship the wiki as static HTML in releases. Recommended:
  go public at launch; the paper says artefacts public on acceptance
  anyway.
- **CI jobs**: build docs, run snippet tests, link checker (lychee),
  spell check (codespell with UK dictionary), deploy.
- **Search**: Material built-in. Analytics: none by default (privacy).

## 6. Build phases

- **Phase A (scaffold + golden path)**: mkdocs skeleton, theme, CI
  deploy; Home, Quickstart, Tutorial 1, Glossary seed (20 terms).
  Exit: a stranger can install and see a rejection in 15 minutes.
- **Phase B (foundations + core tutorials)**: the 5 primer pages;
  Tutorials 2-4; envelope page. Exit: own-data + own-ontology paths
  complete.
- **Phase C (how-to + reference)**: all how-tos; generated reference;
  violation catalogue. Exit: every public API and check documented.
- **Phase D (depth + 2.0)**: Tutorials 5-7, architecture, comparison,
  research page, roadmap, contributing.
- **Phase E (hardening)**: jargon-lint pass, snippet CI, link/spell
  CI, mobile pass, hallway test with 2 outside developers (one
  no-background by design); fix what they trip on.
- **Phase F (launch)**: repo public, README points to wiki, DOI/cite
  page, announce (group, supervisors, X/LinkedIn optional).

Rough effort if Claude builds with Abdelrhman reviewing: A+B one day,
C+D one day, E half a day. Human-only estimate: 2-3 weeks part-time.

## 7. Success criteria (measurable)

- Time-to-first-rejection < 15 min from a clean machine (tested).
- A no-background tester explains bindings and verdicts back
  correctly after Tutorials 1-2.
- 100% code blocks CI-tested; 0 broken links; every glossary term
  linked on first use per page.
- Both example ontologies (GeoIoT default, farm custom) exercised in
  tutorials.
- Wiki version pinned to package release (mike).

## 8. Open decisions for Abdelrhman

1. Public repo at launch vs Read the Docs vs static-only (Section 5).
2. Site name/branding ("MCL", "mclpy", or umbrella "GeoIoT MCL").
3. Whether Tutorial 7 (OOON) ships at launch or after the 2.0
   evaluation (recommend: ship, clearly badged "preview").
4. Custom domain (for example docs.geoiot.org) or default
   github.io URL.
