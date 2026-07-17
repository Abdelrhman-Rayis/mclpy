"""Using mclpy with a NON-default ontology.

The ontology layer is modular: any RDF ontology can back a composition.
Here a tiny farm ontology (examples/farm.ttl) replaces GeoIoT, and the
same builder, checks and runtime work unchanged. Run:

    python examples/custom_ontology.py
"""
from pathlib import Path

from mclpy import Composition, MCLStaticError, Namespace, RDFOntology

FARM = Namespace("http://example.org/farm#")
farm_ontology = RDFOntology(Path(__file__).parent / "farm.ttl", name="farm")

comp = (Composition("Barn monitor")
        .service("s", "http://127.0.0.1:9000")
        .timeseries("humidity", concept=FARM.SensorSeries,
                    parameter="humidity", unit="percent",
                    title="Barn humidity")
        .expect_unit("percent").expect_range(0, 100)
        .flow("humidity", service="s", endpoint="/humidity/series"))

comp.check(ontology=farm_ontology)
print("valid against the farm ontology:",
      farm_ontology.describe(str(FARM.SensorSeries)))

try:
    comp.check()   # default GeoIoT ontology does not know farm terms
except MCLStaticError as e:
    print("and correctly rejected against the default GeoIoT ontology:")
    print("  ", e.violations[0])
