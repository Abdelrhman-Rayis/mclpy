# The semantic envelope

Every time a component gets data, the runtime does not just hand the view a bare payload. It wraps the payload in a **semantic envelope**: a structured record of what the data means, where it came from, and whether it passed its rules. This page dissects a real one.

## Why wrap the data at all

A raw payload answers one question: *what are the numbers?* An envelope answers three more that matter just as much: *what do these numbers mean, where did they come from, and can I trust them?* By attaching those answers to every update, MCL makes each chart self-explaining. You can point at any component and know exactly what it is showing and why you should believe it.

## An envelope, field by field

Here is an actual envelope, returned when a validated air-quality chart updates:

```json
{
  "component": "airchart",
  "binding": {
    "concept": "http://www.geoiot.org/ontology#Series",
    "parameter": "no2",
    "unit": "ug/m3"
  },
  "provenance": {
    "service": "observation",
    "url": "http://127.0.0.1:7302/feeds/metraq-28079058-no2/series",
    "retrievedAt": "2026-07-18T21:05:04+00:00"
  },
  "validation": {
    "passed": true,
    "verdicts": [
      { "rule": "unit",  "passed": true, "detail": "expected unit 'ug/m3', payload carries 'ug/m3'" },
      { "rule": "range", "passed": true, "detail": "0 of 168 values outside plausible range [0, 1000]" }
    ]
  },
  "status": "ok",
  "data": { "unit": "ug/m3", "siteLabel": "El Pardo", "points": [ /* ... */ ] }
}
```

Read it top to bottom:

- **`component`** — which part of the dashboard this update is for.
- **`binding`** — the *meaning*. This chart represents the `Series` concept, specifically the `no2` parameter, measured in `ug/m3`. This comes straight from your declaration.
- **`provenance`** — the *origin*. Which service answered, the exact URL called, and when. If a number looks wrong, you can retrace it to its source in one step.
- **`validation`** — the *verdict*. Each declared rule, whether it passed, and a human-readable explanation. Here both rules passed.
- **`status`** — `ok` if every rule passed, `rejected` if any failed.
- **`data`** — the actual payload, present only when `status` is `ok`.

## What a rejection looks like

When a rule fails, the shape stays the same but two fields change: `status` becomes `rejected`, and `data` becomes `null`. The view gets the verdicts, not the numbers:

```json
{
  "component": "airchart",
  "status": "rejected",
  "validation": {
    "passed": false,
    "verdicts": [
      { "rule": "unit", "passed": false, "detail": "expected unit 'ug/m3', payload carries 'ppb'" }
    ]
  },
  "data": null
}
```

The failing data never reaches the view. This is enforcement made visible: the reason is in your hands, the fault is not on the screen.

## Inspecting envelopes live

The dashboard includes an envelope inspector panel that renders this structure as readable cards, and lets you click the concept to look up its definition from the ontology. You do not have to read JSON; the panel is there so that "why is this chart showing this?" always has an answer one glance away.

## For MCL 2.0

The policy preview ([Tutorial 5](../tutorials/policy-marks.md)) adds one more block to the envelope, `policy`, carrying the disclosure verdicts (what was withheld, firewalled, or marked uncertain) beside the validation verdicts. The structure is the same; there is simply a second dimension of enforcement to report.

## Next

- Build something that produces these: [Tutorial 1](../tutorials/first-dashboard.md).
- The full envelope specification: [Reference](../reference/mcl-document.md).
