"""Dashboard rendering.

The generic dashboard is a single self-contained HTML page driven
entirely by the composition document: it lays out one card per
component (maps left, everything else right), fetches each component
through the SVC's /component endpoints, renders by kind (map,
timeseries, kpi, table), wires the declared interactions (map select
re-binds target components via their binding.parameter), and shows the
semantic envelope of every update, with concept dereference against
the loaded ontology.
"""
from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Any

from .builder import Composition


def dashboard_html(composition: Composition | dict[str, Any]) -> str:
    """The dashboard page for a composition (served by create_svc_app)."""
    doc = (composition.to_dict() if isinstance(composition, Composition)
           else composition)
    template = resources.files("mclpy").joinpath(
        "templates/dashboard.html").read_text()
    return template.replace("__TITLE__", json.dumps(doc["title"])[1:-1])


def render_html(composition: Composition | dict[str, Any],
                path: str | Path | None = None) -> str:
    """Write the dashboard page to a file (it still needs an SVC server
    at the same origin for /composition and /component data)."""
    page = dashboard_html(composition)
    if path is not None:
        Path(path).write_text(page)
    return page
