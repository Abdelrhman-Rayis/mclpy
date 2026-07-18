# Install and quickstart

This page gets you from nothing to a running, self-validating dashboard on your own machine. It takes about 15 minutes and assumes only that you have Python 3.10 or newer and know `pip`.

## 1. Install

`mclpy` is the Python library that implements MCL. Install it with the `server` extra, which adds the runtime that serves dashboards:

```bash
python -m venv .venv
source .venv/bin/activate          # on Windows: .venv\Scripts\activate
pip install "mclpy[server] @ git+https://github.com/Abdelrhman-Rayis/mclpy"
```

The core library needs only two small packages (`rdflib`, `jsonschema`). The `server` extra adds `fastapi` and `uvicorn` for the dashboard.

## 2. Write the whole app

Create `app.py`. This is the complete program. Read the comments; every line is doing one job.

```python title="app.py"
import math
from datetime import datetime, timedelta

from mclpy import Composition, GEOIOT      # (1)
from mclpy.server import serve

comp = (
    Composition("My first dashboard")
    .service("local", "resolver://in-process")           # (2)
    .timeseries("temp", concept=GEOIOT.Series,           # (3)
                parameter="airTemperature", unit="degC",
                title="Air temperature")
    .expect_unit("degC")                                 # (4)
    .expect_range(-20, 45)
    .expect_completeness(0.8, expected_points=72)
    .flow("temp", service="local", endpoint="/temp/series")  # (5)
)

def local(endpoint, params):                             # (6)
    now = datetime(2026, 7, 18)
    points = [
        {"t": (now - timedelta(hours=72 - h)).isoformat(),
         "v": round(17 + 6 * math.sin(h / 24 * 2 * math.pi), 2)}
        for h in range(72)
    ]
    return {"unit": "degC", "points": points}

if __name__ == "__main__":
    comp.check()                                          # (7)
    serve(comp, resolvers={"local": local}, port=7300)    # (8)
```

1. `GEOIOT` is a helper for writing ontology concept URIs. `GEOIOT.Series` is just the string `http://www.geoiot.org/ontology#Series`. More on this in [Ontologies for JSON developers](../foundations/ontologies-for-json-devs.md).
2. A **service** names a data source. Here it is a local Python function, not an HTTP server, so the URL is a placeholder.
3. A **component** is one thing on the screen. This one is a time-series chart, bound to the `Series` concept, showing an `airTemperature` parameter measured in `degC`.
4. **Validation rules**: the data must be in `degC`, every value must fall between -20 and 45, and at least 80% of the expected 72 points must be present.
5. A **dataflow** connects the component to a service endpoint.
6. The **resolver**: your Python function that returns the data. Any source works: a DataFrame, a database, an API client. Here it returns 72 hours of a synthetic sine wave.
7. `check()` validates the document against the schema and the ontology *before* anything runs. A malformed composition stops here.
8. `serve()` starts the runtime and the dashboard.

## 3. Run it

```bash
python app.py
```

You should see `MCL composition checked` and a server start message. Open **[http://127.0.0.1:7300](http://127.0.0.1:7300)** in your browser.

You have a dashboard: a temperature chart with a green **validated** badge, and below it a *semantic envelope* panel showing the concept the chart is bound to, where the data came from, and the pass/fail verdict of each rule.

## 4. Now break it

This is the whole point. Change one line in your resolver so the data arrives in the wrong unit:

```python hl_lines="2"
def local(endpoint, params):
    return {"unit": "F", "points": [...]}   # was "degC"
```

Restart (`python app.py`) and refresh the browser. The chart is gone. In its place is a rejection:

> **Update rejected by declared rules; data withheld.**
> unit: expected unit 'degC', payload carries 'F'

The runtime caught the mismatch and refused to draw it. It did not guess, convert, or silently render. That refusal, declared once and enforced automatically, is what MCL gives you.

## What just happened

You wrote a dashboard as a *declaration*, not as procedural code. You said what each part is and what its data must satisfy, and the runtime did the orchestration, the fetching, and the checking. When the data broke its contract, the contract won.

## Next

- Understand the idea you just used: [Declare, check, enforce](../foundations/declare-check-enforce.md).
- Do it with real, live open data: [Tutorial 1](../tutorials/first-dashboard.md) and [Tutorial 2](../tutorials/real-data.md).
- See exactly what the runtime returned: [The semantic envelope](../foundations/semantic-envelope.md).
