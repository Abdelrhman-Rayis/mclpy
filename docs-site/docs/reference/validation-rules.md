# Reference: validation rules

Validation rules attach to a component and run on every update. A payload that fails any rule is withheld; the verdicts are returned in the [semantic envelope](../foundations/semantic-envelope.md). There are three rule types.

## unit

Checks that the payload carries the expected unit string.

```python
.expect_unit("kW")
```
```json
{ "type": "unit", "expected": "kW" }
```

**Passes** when `payload["unit"] == expected`. **Detail:** `expected unit 'kW', payload carries 'W'`.

The commonest and cheapest guard. A unit rule must agree with the component's binding unit, or [static check 7](static-checks.md) rejects the composition.

## range

Checks that every value falls within a plausible interval.

```python
.expect_range(0, 10000)
```
```json
{ "type": "range", "min": 0, "max": 10000 }
```

**Passes** when every point's value is present and `min <= v <= max`. **Detail:** `2 of 168 values outside plausible range [0, 10000]`. A single out-of-range point fails the whole update, so a glitch spike cannot slip through.

## completeness

Checks that enough of the expected points are present.

```python
.expect_completeness(0.5, expected_points=168)
```
```json
{ "type": "completeness", "min_ratio": 0.5, "expected_points": 168 }
```

**Passes** when `present / expected_points >= min_ratio`. **Detail:** `45/168 points present (27%, minimum 50%)`. If `expected_points` is not declared and the payload does not carry one, the rule is skipped with a note.

## What the rules deliberately do not do

These are single-record rules: each checks one payload against a fixed expectation. They cannot detect a value that is well-formed, correctly-typed, in-range, and complete but simply *wrong*. That limit is demonstrated in [Tutorial 4](../tutorials/break-it.md) and is honest by design: catching plausible-but-wrong values needs cross-signal evidence, which lives in a separate anomaly-detection layer, not in a per-component rule.

## Choosing good rules

- Set `range` from the physics of the sensor, not the data you happen to have seen. Water level, air temperature and power each have known plausible bounds.
- Set `completeness` from the reporting cadence: if a gauge reports every 15 minutes, 96 points is a day; require the fraction below which the chart would mislead.
- Always set `unit`. It is one line and it catches the fault that hides best.
