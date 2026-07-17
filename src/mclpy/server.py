"""Embeddable Semantic View Controller (SVC) runtime.

create_svc_app() turns a checked composition into a FastAPI application
that serves the generic dashboard, mediates every component update,
enforces the declared validation rules, and wraps each response in a
semantic envelope (concept binding, provenance, verdicts).

Components get their data in either of two ways:

- HTTP services: the dataflow's service base_url + endpoint is fetched
  over HTTP (the microservice deployment style); or
- local resolvers: your own Python functions serve the data directly,
  no HTTP hop, which is how mclpy builds interfaces INSIDE a Python
  project:

      def obs(endpoint: str, params: dict) -> dict:
          return {"unit": "degC", "points": my_dataframe_to_points()}

      app = create_svc_app(comp, resolvers={"obs": obs})
      # uvicorn module:app  ->  validated dashboard on /

A resolver takes (endpoint, params) where endpoint is the dataflow's
endpoint string with {feed} already substituted, and returns the
payload dict. Resolvers win over HTTP when both are possible.

Requires the [server] extra (fastapi, uvicorn, requests).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from .builder import Composition
from .checks import check_document
from .ontology import Ontology, geoiot
from .render import dashboard_html
from .runtime import validate_payload

Resolver = Callable[[str, dict[str, Any]], dict[str, Any]]


def create_svc_app(composition: Composition | dict[str, Any],
                   resolvers: dict[str, Resolver] | None = None,
                   ontology: Ontology | None = None,
                   check: bool = True):
    """Build the FastAPI app for a composition.

    composition: a Composition or a plain MCL document dict.
    resolvers: optional {service_id: resolver} for in-process data.
    ontology: the ontology for static checks and /concept dereference
              (default: bundled GeoIoT).
    check: refuse to build if the composition fails its checks.
    """
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse

    doc = (composition.to_dict() if isinstance(composition, Composition)
           else composition)
    ontology = ontology or geoiot()
    if check:
        check_document(doc, ontology=ontology)   # raises MCLStaticError
    resolvers = resolvers or {}

    components = {c["id"]: c for c in doc["components"]}
    services = {s["id"]: s for s in doc["services"]}
    flows = {f["target"]: f for f in doc["dataflows"]}
    page = dashboard_html(doc)

    app = FastAPI(title=f"mclpy SVC: {doc['title']}", version="1.0")

    @app.get("/", response_class=HTMLResponse)
    def index():
        return page

    @app.get("/composition")
    def composition_endpoint():
        return {"document": doc, "static_checks": "all static checks passed"}

    @app.get("/concept")
    def concept(uri: str):
        return ontology.describe(uri)

    @app.get("/component/{cid}/data")
    def component_data(cid: str, feed: str | None = None):
        comp = components.get(cid)
        if comp is None:
            raise HTTPException(status_code=404,
                                detail=f"unknown component '{cid}'")
        flow = flows[cid]
        service = services[flow["service"]]
        endpoint = flow["endpoint"]
        if "{feed}" in endpoint:
            if not feed:
                raise HTTPException(status_code=400,
                                    detail="this component needs ?feed=<id>")
            endpoint = endpoint.replace("{feed}", feed)

        resolver = resolvers.get(flow["service"])
        try:
            if resolver is not None:
                payload = resolver(endpoint, {"feed": feed})
                origin = f"resolver:{flow['service']}{endpoint}"
            else:
                import requests
                url = service["base_url"] + endpoint
                resp = requests.get(url, timeout=20)
                resp.raise_for_status()
                payload = resp.json()
                origin = url
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=502,
                                detail=f"data source failed: {exc}")

        envelope: dict[str, Any] = {
            "component": cid,
            "binding": comp["binding"],
            "provenance": {
                "service": service["id"],
                "url": origin,
                "retrievedAt": datetime.now(timezone.utc)
                               .isoformat(timespec="seconds"),
            },
            "validation": None,
            "status": "ok",
            "data": payload,
        }
        rules = comp.get("validation", [])
        if rules:
            result = validate_payload(payload, rules)
            envelope["validation"] = result
            if not result["passed"]:
                envelope["status"] = "rejected"
                envelope["data"] = None   # never render failing data
        return envelope

    return app


def serve(composition: Composition | dict[str, Any],
          resolvers: dict[str, Resolver] | None = None,
          ontology: Ontology | None = None,
          host: str = "127.0.0.1", port: int = 7300) -> None:
    """Blocking convenience runner: build the app and serve it."""
    import uvicorn
    app = create_svc_app(composition, resolvers=resolvers, ontology=ontology)
    uvicorn.run(app, host=host, port=port)
