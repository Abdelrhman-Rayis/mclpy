"""mclpy: the Microservice Composition Language for Python.

Declare ontology-bound, validated data interfaces in Python and run
them. The ontology layer is modular: any RDF ontology can back a
composition; the GeoIoT ontology is the bundled default.

    from mclpy import Composition, GEOIOT

    comp = (Composition("My dashboard")
            .service("obs", "http://127.0.0.1:7302")
            .timeseries("temp", concept=GEOIOT.Series,
                        parameter="airTemperature", unit="degC")
            .expect_unit("degC").expect_range(-20, 45)
            .flow("temp", service="obs", endpoint="/feeds/temp/series"))
    comp.check()                       # schema + ontology static checks

    from mclpy.server import serve
    serve(comp, port=7300)             # validated dashboard on localhost
"""
from .builder import Composition
from .checks import (MCLStaticError, check_document, load_schema,
                     schema_violations, static_violations)
from .ontology import (GEOIOT, CompositeOntology, Namespace, Ontology,
                       RDFOntology, geoiot)
from .render import dashboard_html, render_html
from .runtime import validate_payload

__version__ = "0.1.0"

__all__ = [
    "Composition",
    "MCLStaticError", "check_document", "load_schema",
    "schema_violations", "static_violations",
    "GEOIOT", "CompositeOntology", "Namespace", "Ontology",
    "RDFOntology", "geoiot",
    "dashboard_html", "render_html",
    "validate_payload",
    "__version__",
]
