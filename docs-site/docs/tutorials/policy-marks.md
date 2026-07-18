# Tutorial 5: Policy marks (MCL 2.0 preview)

!!! warning "This is a preview"
    Everything here is implemented and runnable in `mclpy` today, but MCL 2.0 (the OOON policy layer) is a **preview**: not yet evaluated to the standard of the validation layer, and its research positioning against policy languages such as ODRL and DPV is still in progress. Use it to explore; do not depend on it in production yet.

**What you will build.** A dashboard whose components carry *governance* policy, not just quality rules: a label withheld for privacy, an identifier firewalled and logged, and an uncertain series marked as interval-valued.

**You need.** `mclpy[server]`, and the ideas from [The semantic envelope](../foundations/semantic-envelope.md).

---

## The idea in one line

MCL v1 enforces data **quality** (unit, range, completeness). MCL 2.0 adds a second dimension at the same enforcement point: data **disclosure**. You mark *how each property may be treated*, and the runtime enforces it exactly as it enforces validation.

## The marks

Policy travels as a small set of marks, each with a symbol:

| Symbol | Mark | What it does |
|:---:|---|---|
| ↑ | **expose** | property is available to views (the default) |
| ~ | **bound** | property is withheld, under a required machine-readable reason (`#privacy`) |
| ✕ | **firewall** | property is stripped and every access attempt is logged |
| ∞ | **drifting** | value is an interval, never a point; render uncertainty, not a line |
| @ | **perspective** | whose representation this whole composition is |

## Write a policy-bearing composition

The builder gains policy methods. Every mark upgrades the document to MCL 2.0, and a 2.0 document must declare a perspective:

```python title="policy_app.py"
from mclpy import Composition, GEOIOT
from mclpy.server import serve

comp = (
    Composition("Campus monitor with policy")
    .perspective("estates-team")                       # (1) who this view belongs to
    .service("obs", "http://127.0.0.1:7302")
    .timeseries("energy", concept=GEOIOT.Series,
                parameter="electricity", unit="kW", title="Building electricity")
    .mark_expose()                                     # the series itself is public
    .mark_property("siteLabel", bound="#privacy")      # (2) withhold the building name
    .mark_property("feed", firewall=True)              # (3) never expose the raw feed id
    .expect_unit("kW")
    .expect_range(0, 10000)
    .flow("energy", service="obs", endpoint="/feeds/{feed}/series")
)
comp.check()      # runs the v1 checks plus five OOON policy checks
```

1. `perspective` records the stance of the composition. A 2.0 document is invalid without it.
2. `bound="#privacy"` withholds the building label and records *why*. A bound mark without a reason is a load-time error.
3. `firewall=True` strips the property entirely and logs any attempt to read it.

## What the runtime does

Run this against a live data service and open the dashboard. In the envelope panel a new **Policy verdicts (OOON)** card appears, alongside the familiar validation card, showing the symbols in action:

- `~ WITHHELD siteLabel #privacy` — the building name is gone from the payload; the reason is recorded.
- `✕ BLOCKED feed` — the feed identifier is stripped, and an entry is written to an audit log.

Meanwhile the quality rules (`unit`, `range`) still run and still pass on the same payload. Quality and disclosure are enforced by one mechanism, at one point.

Visit the audit endpoint to see the firewall log:

```bash
curl http://127.0.0.1:7300/audit
```

## Graceful degradation

An MCL 2.0 document compiles to JSON-LD in which the policy terms live under an `ooon:` namespace. A consumer that does not understand OOON simply ignores those terms and still reads a valid document. Policy is intrinsic to the data, but it does not break tools that do not know about it.

## Why this exists

The same argument that put *quality* enforcement at the interface applies to *governance*. Once you have a declared document and a mediating runtime, "this property is private" or "this value is uncertain" can be declared and enforced exactly like "this must be in kW". The full rationale, and the honest account of what is not yet proven, is in [The research behind it](../explanation/research.md).

## Next

- [The research behind it](../explanation/research.md): where the preview sits and what it still needs.
- The full specification lives in the repository at `docs/OOON-SPEC.md`.
