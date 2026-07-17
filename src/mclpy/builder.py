"""Fluent Python builder for MCL compositions.

Author the composition in Python instead of hand-writing JSON; the
result serialises to a standard MCL v1.0 document that any conformant
runtime (including mclpy's own server) can execute.

    from mclpy import Composition, GEOIOT

    comp = (Composition("Campus Monitor",
                        description="River gauges and campus energy")
        .service("obs", "http://127.0.0.1:7302", "observation service")
        .map("sitemap", concept=GEOIOT.Site, title="Monitored sites")
        .timeseries("river", concept=GEOIOT.Series,
                    parameter="waterLevel", unit="m",
                    title="River level")
            .expect_unit("m").expect_range(-1, 12)
            .expect_completeness(0.6, expected_points=96)
        .flow("sitemap", service="obs", endpoint="/entities")
        .flow("river", service="obs", endpoint="/feeds/{feed}/series")
        .on_select("sitemap", filter="river"))

    comp.check()          # schema + ontology-aware static checks
    comp.to_json("dashboard.mcl.json")
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .checks import check_document
from .ontology import Ontology


class Composition:
    def __init__(self, title: str, description: str = "",
                 mcl_version: str = "1.0"):
        self._doc: dict[str, Any] = {
            "mcl_version": mcl_version,
            "title": title,
            "services": [],
            "components": [],
            "dataflows": [],
            "interactions": [],
        }
        if description:
            self._doc["description"] = description
        self._last_component: dict[str, Any] | None = None

    # ---- services -------------------------------------------------------

    def service(self, id: str, base_url: str,
                description: str = "") -> "Composition":
        entry: dict[str, Any] = {"id": id, "base_url": base_url}
        if description:
            entry["description"] = description
        self._doc["services"].append(entry)
        return self

    # ---- components -----------------------------------------------------

    def _component(self, id: str, kind: str, concept: str,
                   title: str = "", parameter: str | None = None,
                   unit: str | None = None) -> "Composition":
        binding: dict[str, Any] = {"concept": str(concept)}
        if parameter:
            binding["parameter"] = parameter
        if unit:
            binding["unit"] = unit
        comp: dict[str, Any] = {"id": id, "kind": kind, "binding": binding}
        if title:
            comp["title"] = title
        self._doc["components"].append(comp)
        self._last_component = comp
        return self

    def map(self, id: str, concept: str, title: str = "") -> "Composition":
        return self._component(id, "map", concept, title)

    def timeseries(self, id: str, concept: str, parameter: str | None = None,
                   unit: str | None = None, title: str = "") -> "Composition":
        return self._component(id, "timeseries", concept, title, parameter, unit)

    def kpi(self, id: str, concept: str, parameter: str | None = None,
            unit: str | None = None, title: str = "") -> "Composition":
        return self._component(id, "kpi", concept, title, parameter, unit)

    def table(self, id: str, concept: str, title: str = "") -> "Composition":
        return self._component(id, "table", concept, title)

    # ---- validation rules (attach to the most recent component) ---------

    def _rule(self, rule: dict[str, Any]) -> "Composition":
        if self._last_component is None:
            raise ValueError("declare a component before attaching rules")
        self._last_component.setdefault("validation", []).append(rule)
        return self

    def expect_unit(self, expected: str) -> "Composition":
        return self._rule({"type": "unit", "expected": expected})

    def expect_range(self, min: float, max: float) -> "Composition":
        return self._rule({"type": "range", "min": min, "max": max})

    def expect_completeness(self, min_ratio: float,
                            expected_points: int | None = None) -> "Composition":
        rule: dict[str, Any] = {"type": "completeness", "min_ratio": min_ratio}
        if expected_points is not None:
            rule["expected_points"] = expected_points
        return self._rule(rule)

    # ---- dataflows and interactions -------------------------------------

    def flow(self, target: str, service: str, endpoint: str,
             description: str = "") -> "Composition":
        entry: dict[str, Any] = {"target": target, "service": service,
                                 "endpoint": endpoint}
        if description:
            entry["description"] = description
        self._doc["dataflows"].append(entry)
        return self

    def on_select(self, source: str, filter: str | None = None,
                  highlight: str | None = None) -> "Composition":
        if (filter is None) == (highlight is None):
            raise ValueError("pass exactly one of filter= or highlight=")
        effect = "filter" if filter else "highlight"
        target = filter or highlight
        self._doc["interactions"].append(
            {"source": source, "event": "select",
             "target": target, "effect": effect})
        return self

    # ---- output ---------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        doc = json.loads(json.dumps(self._doc))   # deep copy
        if not doc["interactions"]:
            del doc["interactions"]
        return doc

    def to_json(self, path: str | Path | None = None, indent: int = 2) -> str:
        text = json.dumps(self.to_dict(), indent=indent)
        if path is not None:
            Path(path).write_text(text + "\n")
        return text

    @classmethod
    def from_dict(cls, doc: dict[str, Any]) -> "Composition":
        comp = cls(doc.get("title", "untitled"))
        comp._doc = json.loads(json.dumps(doc))
        comp._doc.setdefault("interactions", [])
        comp._last_component = None
        return comp

    @classmethod
    def from_json(cls, path: str | Path) -> "Composition":
        return cls.from_dict(json.loads(Path(path).read_text()))

    def check(self, ontology: Ontology | None = None) -> "Composition":
        """Schema-validate and statically check; raises MCLStaticError."""
        check_document(self.to_dict(), ontology=ontology)
        return self

    def __repr__(self) -> str:
        d = self._doc
        return (f"Composition({d['title']!r}, services={len(d['services'])}, "
                f"components={len(d['components'])}, "
                f"dataflows={len(d['dataflows'])})")
