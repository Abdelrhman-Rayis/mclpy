"""mcl command-line interface.

    mcl validate dashboard.mcl.json [--ontology my.ttl ...]
    mcl render   dashboard.mcl.json -o dashboard.html
    mcl serve    dashboard.mcl.json [--port 7300] [--ontology my.ttl ...]
    mcl schema                       # print the MCL v1.0 JSON Schema
"""
from __future__ import annotations

import argparse
import json
import sys

from .builder import Composition
from .checks import MCLStaticError, check_document, load_schema
from .ontology import CompositeOntology, RDFOntology, geoiot


def _ontology(paths: list[str] | None):
    if not paths:
        return geoiot()
    parts = [RDFOntology(p) for p in paths]
    return parts[0] if len(parts) == 1 else CompositeOntology(*parts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mcl",
        description="Microservice Composition Language tools (mclpy)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_val = sub.add_parser("validate", help="check a composition document")
    p_val.add_argument("document")
    p_val.add_argument("--ontology", action="append",
                       help="ontology file(s); default is bundled GeoIoT")

    p_ren = sub.add_parser("render", help="write the dashboard HTML")
    p_ren.add_argument("document")
    p_ren.add_argument("-o", "--output", default="dashboard.html")

    p_srv = sub.add_parser("serve", help="serve the composition (SVC)")
    p_srv.add_argument("document")
    p_srv.add_argument("--port", type=int, default=7300)
    p_srv.add_argument("--host", default="127.0.0.1")
    p_srv.add_argument("--ontology", action="append")

    sub.add_parser("schema", help="print the MCL v1.0 JSON Schema")

    args = parser.parse_args(argv)

    if args.command == "schema":
        print(json.dumps(load_schema(), indent=2))
        return 0

    comp = Composition.from_json(args.document)

    if args.command == "validate":
        try:
            check_document(comp.to_dict(), ontology=_ontology(args.ontology))
        except MCLStaticError as e:
            print(str(e), file=sys.stderr)
            return 1
        doc = comp.to_dict()
        print(f"OK: '{doc['title']}' is a well-formed MCL {doc['mcl_version']} "
              f"composition ({len(doc['components'])} components, "
              f"{len(doc['services'])} services)")
        return 0

    if args.command == "render":
        from .render import render_html
        render_html(comp, args.output)
        print(f"wrote {args.output}")
        return 0

    if args.command == "serve":
        from .server import serve
        serve(comp, ontology=_ontology(args.ontology),
              host=args.host, port=args.port)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
