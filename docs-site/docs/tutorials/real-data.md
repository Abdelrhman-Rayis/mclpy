# Tutorial 2: Real open data

**What you will build.** A dashboard fed by a live, real UK sensor network: the Environment Agency's river-level API. No API key, no signup.

**You need.** Tutorial 1 done, and `pip install requests`.

---

## Step 1 — meet the data

The [Environment Agency flood-monitoring API](https://environment.data.gov.uk/flood-monitoring/doc/reference) publishes real-time readings from thousands of river gauges across England, under the Open Government Licence. Every gauge has a reference, coordinates, and a stream of level readings in metres. That maps cleanly onto GeoIoT: each gauge is a `Site`, its level readings are a `Series`.

Try it in your browser: [a station's recent readings](https://environment.data.gov.uk/flood-monitoring/id/stations/2069/readings?_sorted&_limit=10&parameter=level). You will get JSON with `dateTime` and `value` fields.

## Step 2 — write a resolver that calls it

A resolver is just a function that returns `{"unit": ..., "points": [...]}`. Here it calls the live API:

```python title="river_app.py"
import requests
from mclpy import Composition, GEOIOT
from mclpy.server import serve

STATION = "2069"   # a gauge reference; try others from the API

comp = (
    Composition("Live river level")
    .service("ea", "https://environment.data.gov.uk/flood-monitoring")
    .timeseries("level", concept=GEOIOT.Series,
                parameter="waterLevel", unit="m", title=f"River level, station {STATION}")
    .expect_unit("m")
    .expect_range(-1, 12)
    .expect_completeness(0.5, expected_points=96)
    .flow("level", service="ea", endpoint="/level/series")
)

def ea(endpoint, params):
    r = requests.get(
        f"https://environment.data.gov.uk/flood-monitoring/id/stations/{STATION}/readings",
        params={"_sorted": "", "_limit": 96, "parameter": "level"}, timeout=30)
    r.raise_for_status()
    points = [{"t": it["dateTime"], "v": it["value"]}
              for it in r.json()["items"] if isinstance(it.get("value"), (int, float))]
    points.reverse()   # API returns newest-first; charts want oldest-first
    return {"unit": "m", "points": points}

if __name__ == "__main__":
    comp.check()
    serve(comp, resolvers={"ea": ea}, port=7300)
```

Run `python river_app.py` and open [http://127.0.0.1:7300](http://127.0.0.1:7300). That is a real river, updating from real gauges, validated against a plausible range for water level.

## Step 3 — the rules now earn their keep

With synthetic data you controlled every value. With real data you do not, and that is when validation matters. The Environment Agency's gauges occasionally report bad values or drop offline. Your `range` rule (-1 to 12 metres) will catch a glitched reading; your `completeness` rule (at least half of 96 expected readings) will withhold a series from a gauge that has gone quiet, rather than drawing a misleading sparse line.

You did not write code for those cases. You declared the expectation, and the runtime handles the exception.

## Step 4 — pick a broken station (optional)

Browse the [stations list](https://environment.data.gov.uk/flood-monitoring/id/stations?parameter=level&_limit=50) and try a few references in `STATION`. Some will render cleanly; some will be withheld because their recent data is too sparse. Watch the envelope explain each decision.

## What just happened

You connected MCL to a real national sensor network with about 20 lines, and the validation rules you declared in Tutorial 1 now protect you against real-world faults you cannot see coming. The resolver pattern means *any* data source (an API, a database, a message queue, a DataFrame) plugs in the same way.

## Next

- [Tutorial 3](own-ontology.md): use your own vocabulary instead of GeoIoT.
- [How-to: serve a component from a database](../reference/mcl-document.md) (resolver patterns).
