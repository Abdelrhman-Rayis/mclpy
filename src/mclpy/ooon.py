"""OOON: the Object Oriented Ontology Notation policy layer of MCL 2.0.

Implements the specification in docs/OOON-SPEC.md: the mark model and
its composition rules, the JSON-LD compiler with graceful degradation,
and the run-time enforcement the SVC applies to payloads.

Marks are epistemic policies attached to properties:

    expose    (^)        available to queries and views
    bound     (~ #r)     withheld under a boundary policy; reason required
    firewall  (x)        access refused and logged; composes with nothing
    drifting  (8)        value is an interval, never a point
    join_key  (+(k))     participates in contact rules on key k
    perspective (@id)    whose representation an object is (per document)
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

OOON_CONTEXT = "https://www.geoiot.org/ooon#"

MARK_FIELDS = ("expose", "bound", "firewall", "drifting", "join_key")

# Canonical display symbols (OOON-SPEC section 1). ASCII aliases exist for
# authoring; these are what users SEE in envelopes, dashboards and docs.
SYMBOLS = {
    "expose": "↑",      # ↑
    "bound": "~",
    "join_key": "⊕",    # ⊕
    "firewall": "✕",    # ✕
    "drifting": "∞",    # ∞
    "perspective": "@",
    "reason": "#",
}


class OOONError(Exception):
    """A mark set violates OOON well-formedness (spec section 1)."""


def check_marks(marks: dict[str, Any], where: str = "") -> list[str]:
    """Return violations of the composition rules for one mark set."""
    violations = []
    prefix = f"{where}: " if where else ""
    unknown = set(marks) - set(MARK_FIELDS)
    if unknown:
        violations.append(f"{prefix}unknown mark(s) {sorted(unknown)}")
    if marks.get("firewall"):
        others = [f for f in MARK_FIELDS
                  if f != "firewall" and marks.get(f)]
        if others:
            violations.append(
                f"{prefix}firewall composes with nothing, found {others}")
    bound = marks.get("bound")
    if bound is not None and (not isinstance(bound, str)
                              or not bound.startswith("#") or len(bound) < 2):
        violations.append(
            f"{prefix}bound requires a #reason, got {bound!r}")
    return violations


def compile_jsonld(doc: dict[str, Any]) -> dict[str, Any]:
    """Compile an MCL 2.0 document's policy layer to JSON-LD.

    Standard consumers ignore ooon:* terms and still see the plain
    composition; OOON-aware consumers recover every mark. Bound
    properties ship their reason but not their value; firewalled
    properties ship only inside the ooon:firewall record.
    """
    out: dict[str, Any] = {
        "@context": {"ooon": OOON_CONTEXT},
        "ooon:perspective": doc.get("perspective"),
        "title": doc.get("title"),
        "components": [],
    }
    for comp in doc.get("components", []):
        binding = comp.get("binding", {})
        entry: dict[str, Any] = {
            "id": comp["id"],
            "kind": comp["kind"],
            "concept": binding.get("concept"),
        }
        marks = binding.get("marks", {})
        if marks.get("expose"):
            entry["ooon:expose"] = True
        if marks.get("drifting"):
            entry["ooon:drifting"] = True
        if marks.get("bound"):
            entry["ooon:bound"] = f"ooon:reason/{marks['bound'][1:]}"
        if marks.get("join_key"):
            entry["ooon:trigger"] = {"ooon:key": marks["join_key"]}
        firewalled = [p for p, m in binding.get("property_marks", {}).items()
                      if m.get("firewall")]
        if firewalled:
            entry["ooon:firewall"] = [{"ooon:property": p} for p in firewalled]
        bound_props = {p: m["bound"]
                       for p, m in binding.get("property_marks", {}).items()
                       if m.get("bound")}
        if bound_props:
            entry["ooon:boundProperties"] = {
                p: f"ooon:reason/{r[1:]}" for p, r in bound_props.items()}
        out["components"].append(entry)
    return out


def enforce(payload: dict[str, Any],
            binding: dict[str, Any]) -> tuple[dict[str, Any], list[dict], list[dict]]:
    """Apply a binding's OOON marks to a payload before it reaches a view.

    Returns (payload, policy_verdicts, audit_events):
    - firewalled properties are stripped and the attempt logged;
    - bound properties are stripped, withheld-with-reason;
    - drifting marks the payload interval-valued (rendering hint);
    - exposed properties pass through (default).
    Value validation (unit, range, completeness) is a separate engine;
    OOON governs disclosure, not quality.
    """
    verdicts: list[dict] = []
    audit: list[dict] = []
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    property_marks: dict[str, dict] = binding.get("property_marks", {}) or {}
    marks: dict[str, Any] = binding.get("marks", {}) or {}
    out = dict(payload)

    for prop, pmarks in property_marks.items():
        present = prop in out
        if pmarks.get("firewall"):
            if present:
                del out[prop]
            audit.append({"event": "firewall", "property": prop,
                          "present": present, "at": now})
            verdicts.append({"mark": "firewall", "symbol": SYMBOLS["firewall"], "property": prop,
                             "action": "blocked",
                             "detail": "access refused and logged"})
        elif pmarks.get("bound"):
            reason = pmarks["bound"]
            if present:
                del out[prop]
            verdicts.append({"mark": "bound", "symbol": SYMBOLS["bound"], "property": prop,
                             "action": "withheld", "reason": reason,
                             "detail": f"withheld under {reason}"})
        elif pmarks.get("drifting") and present:
            verdicts.append({"mark": "drifting", "symbol": SYMBOLS["drifting"], "property": prop,
                             "action": "interval",
                             "detail": "value is an interval, not a point"})

    if marks.get("drifting"):
        out["intervalValued"] = True
        verdicts.append({"mark": "drifting", "symbol": SYMBOLS["drifting"], "property": "(series)",
                         "action": "interval",
                         "detail": "series declared interval-valued; render "
                                   "uncertainty, not a line"})
    if marks.get("bound"):
        verdicts.append({"mark": "bound", "symbol": SYMBOLS["bound"], "property": "(component)",
                         "action": "withheld", "reason": marks["bound"],
                         "detail": f"component withheld under {marks['bound']}"})
        out = {}
    return out, verdicts, audit
