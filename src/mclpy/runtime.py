"""Runtime validation engine: enforce declared MCL rules on payloads.

Three rule classes, mirroring MCL v1.0: unit (payload must carry the
expected unit string), range (every value inside the declared plausible
range), completeness (enough of the expected points present). A payload
failing any rule must be withheld from the view; the verdicts explain
why.
"""
from __future__ import annotations

from typing import Any


def validate_payload(payload: dict[str, Any],
                     rules: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply rules to a series payload.

    payload: {"unit": str, "points": [{"t": iso, "v": float}, ...],
              "expected_points": int (optional)}
    Returns {"passed": bool, "verdicts": [{rule, passed, detail}, ...]}
    """
    verdicts = []
    for rule in rules:
        rtype = rule.get("type")
        if rtype == "unit":
            expected = rule["expected"]
            actual = payload.get("unit")
            passed = actual == expected
            detail = f"expected unit '{expected}', payload carries '{actual}'"
        elif rtype == "range":
            lo, hi = rule["min"], rule["max"]
            pts = payload.get("points", [])
            bad = [p for p in pts
                   if p.get("v") is None or not (lo <= p["v"] <= hi)]
            passed = len(bad) == 0
            detail = (f"{len(bad)} of {len(pts)} values outside plausible "
                      f"range [{lo}, {hi}]")
        elif rtype == "completeness":
            min_ratio = rule.get("min_ratio", 0.8)
            expected_n = payload.get("expected_points") or rule.get("expected_points")
            actual_n = len([p for p in payload.get("points", [])
                            if p.get("v") is not None])
            if not expected_n:
                passed, detail = True, "no expected point count declared; rule skipped"
            else:
                ratio = actual_n / expected_n
                passed = ratio >= min_ratio
                detail = (f"{actual_n}/{expected_n} points present "
                          f"({ratio:.0%}, minimum {min_ratio:.0%})")
        else:
            passed, detail = False, f"unknown rule type '{rtype}'"
        verdicts.append({"rule": rtype, "passed": passed, "detail": detail})
    return {"passed": all(v["passed"] for v in verdicts), "verdicts": verdicts}
