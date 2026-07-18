# Tutorial 4: Break it on purpose

**What you will build.** Nothing new. You will systematically feed bad data to a validated component and watch each rule catch it, then find the one fault class the rules *cannot* catch, and understand why that boundary is honest rather than a weakness.

**You need.** The `app.py` from [Tutorial 1](first-dashboard.md).

---

## The three faults the rules catch

Your Tutorial 1 chart declares three rules. Each defends against one fault class. Trigger them one at a time by editing the resolver's return value.

=== "Wrong unit"

    ```python
    return {"unit": "F", "points": good_points}   # rule expects degC
    ```

    **Verdict:** `unit FAIL — expected unit 'degC', payload carries 'F'`. The classic silent killer, caught before a single point is drawn.

=== "Out of range"

    ```python
    return {"unit": "degC", "points": [{"t": "...", "v": 999.0}, ...]}
    ```

    **Verdict:** `range FAIL — 1 of N values outside plausible range [-20, 45]`. One impossible reading withholds the series, rather than rescaling the whole chart around a spike.

=== "Missing data"

    ```python
    return {"unit": "degC", "points": good_points[:10]}   # 10 of 72 expected
    ```

    **Verdict:** `completeness FAIL — 10/72 points present (14%, minimum 80%)`. A gauge that dropped offline is withheld, not drawn as a smooth line across the gap.

In each case the data is refused, the reason is reported, and nothing wrong reaches the screen.

## The fault the rules cannot catch

Now try this. Keep the unit correct, keep every value inside the range, keep the series complete, but make one value simply *wrong*:

```python
return {"unit": "degC", "points": [{"t": "...", "v": 21.0}, ...]}  # true value was 4.0
```

**Verdict: all rules PASS. The chart renders.** A temperature of 21°C is a perfectly plausible value; it is just not the *correct* one. The rules check that data is well-formed, in the right unit, and in a sensible range. They cannot check that a plausible number is the true number.

## Why this boundary is the honest part

This is not a bug in MCL; it is the edge of what any single-record rule can do. To know that 21°C is wrong, you would need *other evidence*: a neighbouring sensor reading 4°C, or a physical model saying the value cannot have jumped that far in an hour. That is cross-signal reasoning, and it belongs to a different layer (an anomaly detector over the whole data history), not to a rule attached to one chart.

The authors measured exactly this. Under fault injection, MCL's rules caught 100% of the wrong-unit, out-of-range and missing-data faults, and 0% of "in-range corruption" (plausible-but-wrong values). They report the 0% openly, because a tool that pretends to catch everything is less trustworthy than one that tells you precisely where it stops.

## The takeaway

MCL guarantees that what you see is well-formed, correctly-typed, in-range and complete enough. It does not, and cannot, guarantee that a plausible value is true. Knowing that boundary is what lets you rely on the guarantee it does make.

## Next

- [Tutorial 5](policy-marks.md): the MCL 2.0 preview, extending enforcement from quality to disclosure.
- [Explanation: the research behind it](../explanation/research.md), including how the cross-signal layer fits.
