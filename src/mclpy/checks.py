"""MCL document checking: JSON Schema plus ontology-aware static checks.

Load-time checking is the heart of MCL: an ill-formed composition is
rejected before any service is invoked. The checks are the reference
set (duplicate ids, dangling dataflows, exactly one flow per component,
unit rules consistent with bindings, interactions over declared
components) plus the ontology check, which verifies every bound concept
exists in the supplied ontology; by default, the bundled GeoIoT
ontology.
"""
from __future__ import annotations

import json
from importlib import resources
from typing import Any

import jsonschema

from .ontology import Ontology, geoiot


class MCLStaticError(Exception):
    """A composition failed schema validation or static checks."""

    def __init__(self, violations: list[str]):
        self.violations = violations
        super().__init__("MCL static checks failed:\n" +
                         "\n".join(f"  - {v}" for v in violations))


def load_schema() -> dict[str, Any]:
    path = resources.files("mclpy").joinpath("schema/mcl_schema.json")
    return json.loads(path.read_text())


def schema_violations(doc: dict[str, Any]) -> list[str]:
    validator = jsonschema.Draft7Validator(load_schema())
    return [f"schema: {e.message} (at {'/'.join(map(str, e.path))})"
            for e in validator.iter_errors(doc)]


def static_violations(doc: dict[str, Any],
                      ontology: Ontology | None = None) -> list[str]:
    """The static checks; pass any Ontology, default is bundled GeoIoT."""
    ontology = ontology or geoiot()
    violations: list[str] = []

    service_ids = [s["id"] for s in doc.get("services", [])]
    component_ids = [c["id"] for c in doc.get("components", [])]

    for name, ids in (("service", service_ids), ("component", component_ids)):
        for d in sorted({i for i in ids if ids.count(i) > 1}):
            violations.append(f"duplicate {name} id '{d}'")

    for flow in doc.get("dataflows", []):
        if flow["service"] not in service_ids:
            violations.append(
                f"dataflow for '{flow['target']}' references unknown service "
                f"'{flow['service']}'")
        if flow["target"] not in component_ids:
            violations.append(
                f"dataflow targets unknown component '{flow['target']}'")

    flow_targets = [f["target"] for f in doc.get("dataflows", [])]
    for cid in component_ids:
        if flow_targets.count(cid) == 0:
            violations.append(f"component '{cid}' has no dataflow")
        elif flow_targets.count(cid) > 1:
            violations.append(f"component '{cid}' has multiple dataflows")

    for comp in doc.get("components", []):
        concept = comp["binding"]["concept"]
        if not ontology.has_term(concept):
            violations.append(
                f"component '{comp['id']}' binds concept <{concept}> "
                f"not present in the ontology")

    for comp in doc.get("components", []):
        bound_unit = comp["binding"].get("unit")
        for rule in comp.get("validation", []):
            if (rule["type"] == "unit" and bound_unit
                    and rule.get("expected") != bound_unit):
                violations.append(
                    f"component '{comp['id']}': unit rule expects "
                    f"'{rule.get('expected')}' but binding declares "
                    f"'{bound_unit}'")

    for inter in doc.get("interactions", []):
        for side in ("source", "target"):
            if inter[side] not in component_ids:
                violations.append(
                    f"interaction references unknown component "
                    f"'{inter[side]}'")
    return violations


def check_document(doc: dict[str, Any],
                   ontology: Ontology | None = None) -> dict[str, Any]:
    """Full check; returns the document or raises MCLStaticError."""
    violations = schema_violations(doc)
    if violations:
        raise MCLStaticError(violations)
    violations = static_violations(doc, ontology)
    if violations:
        raise MCLStaticError(violations)
    return doc
