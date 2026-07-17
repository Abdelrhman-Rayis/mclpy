"""A complete mclpy app in one file: your own Python data, no microservices.

The composition binds a temperature chart to the GeoIoT ontology; a
local resolver serves the data straight from Python (here synthetic,
in real projects a DataFrame, a database, an API client...). Run:

    python examples/local_resolver_app.py
    open http://127.0.0.1:7300
"""
import math
from datetime import datetime, timedelta

from mclpy import GEOIOT, Composition
from mclpy.server import serve

comp = (Composition("Local Python data, declaratively composed",
                    description="mclpy local-resolver example")
        .service("local", "resolver://in-process",
                 "data served by a Python function in this file")
        .timeseries("temp", concept=GEOIOT.Series,
                    parameter="airTemperature", unit="degC",
                    title="Synthetic campus temperature")
        .expect_unit("degC")
        .expect_range(-20, 45)
        .expect_completeness(0.8, expected_points=72)
        .flow("temp", service="local", endpoint="/temp/series"))


def local(endpoint: str, params: dict) -> dict:
    now = datetime(2026, 7, 17)
    points = [{"t": (now - timedelta(hours=72 - h)).isoformat(),
               "v": round(17 + 6 * math.sin(h / 24 * 2 * math.pi), 2)}
              for h in range(72)]
    return {"unit": "degC", "points": points}


if __name__ == "__main__":
    comp.check()
    serve(comp, resolvers={"local": local}, port=7300)
