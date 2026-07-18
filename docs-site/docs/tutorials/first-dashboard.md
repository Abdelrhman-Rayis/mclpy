# Tutorial 1: Your first validated dashboard

**What you will build.** A single-chart dashboard fed by your own Python data, with three validation rules, and you will read the semantic envelope that explains every update.

**You need.** Python 3.10+, `mclpy[server]` installed ([install guide](../start/install.md)), 15 minutes.

---

## Step 1 — the app

If you did the [quickstart](../start/install.md), you already have `app.py`. If not, create it now:

```python title="app.py"
import math
from datetime import datetime, timedelta
from mclpy import Composition, GEOIOT
from mclpy.server import serve

comp = (
    Composition("My first dashboard")
    .service("local", "resolver://in-process")
    .timeseries("temp", concept=GEOIOT.Series,
                parameter="airTemperature", unit="degC", title="Air temperature")
    .expect_unit("degC")
    .expect_range(-20, 45)
    .expect_completeness(0.8, expected_points=72)
    .flow("temp", service="local", endpoint="/temp/series")
)

def local(endpoint, params):
    now = datetime(2026, 7, 18)
    return {"unit": "degC", "points": [
        {"t": (now - timedelta(hours=72 - h)).isoformat(),
         "v": round(17 + 6 * math.sin(h / 24 * 2 * math.pi), 2)}
        for h in range(72)]}

if __name__ == "__main__":
    comp.check()
    serve(comp, resolvers={"local": local}, port=7300)
```

Run `python app.py` and open [http://127.0.0.1:7300](http://127.0.0.1:7300).

## Step 2 — read the envelope

Below the chart is the **semantic envelope** panel. Look at its three cards:

- **Concept binding** shows `Series · airTemperature [degC]`. Click the `Series` chip: MCL looks up the concept in the ontology and shows its definition. This chart is not showing "some numbers"; it is showing a `Series`, and it knows what that means.
- **Provenance** shows the resolver and the time. Your data's origin travels with it.
- **Validation verdicts** shows three green PASS rows, one per rule.

Everything the dashboard knows about this update is in that panel. Nothing is hidden.

## Step 3 — understand each rule

You declared three rules. Each maps to one way [data goes wrong](../foundations/why-dashboards-lie.md):

| Your line | Guards against | Verdict detail |
|---|---|---|
| `.expect_unit("degC")` | wrong units | "expected unit 'degC', payload carries 'degC'" |
| `.expect_range(-20, 45)` | impossible values | "0 of 72 values outside plausible range [-20, 45]" |
| `.expect_completeness(0.8, expected_points=72)` | missing data | "72/72 points present (100%, minimum 80%)" |

## Step 4 — trip the range rule

Change the resolver so one value is impossible:

```python hl_lines="3"
def local(endpoint, params):
    now = datetime(2026, 7, 18)
    points = [{"t": (now - timedelta(hours=72 - h)).isoformat(), "v": 999.0 if h == 0 else 20.0}
              for h in range(72)]
    return {"unit": "degC", "points": points}
```

Restart and refresh. The chart is withheld and the envelope shows a red **FAIL** on the range rule: "1 of 72 values outside plausible range [-20, 45]". One impossible reading, caught, and the whole series held back rather than drawn with a spike hiding the real data.

## What just happened

You bound a chart to a concept, declared what its data must satisfy, and watched the runtime enforce it, twice, without you writing a validator or an if-statement. You also saw that when data is refused, you are told precisely why.

## Next

- [Tutorial 2](real-data.md): replace synthetic data with a live UK river-level API.
- [The semantic envelope](../foundations/semantic-envelope.md): the full structure you just read.
