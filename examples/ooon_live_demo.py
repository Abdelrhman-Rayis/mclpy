"""MCL 2.0 + OOON over real data: a running policy-enforcing dashboard.

Composes the LIVE MicroMaps observation and entity services (real Keele
SEND energy readings and real Madrid METRAQ air quality) and applies
OOON policy on top of MCL validation:

- site canonical URIs are FIREWALLED on the public map (stripped and
  every access attempt logged at /audit);
- building labels on the energy chart are BOUND under #privacy
  (withheld, with the machine-readable reason in the envelope);
- the interpolation-bearing NO2 series is DRIFTING (declared
  interval-valued; views should render uncertainty);
- the composition carries the @estates-team perspective.

Requires the micromaps-framework services on :7301/:7302. Run:

    python examples/ooon_live_demo.py
    open http://127.0.0.1:7320       (dashboard)
    open http://127.0.0.1:7320/audit (firewall attempt log)
"""
from mclpy import GEOIOT, Composition
from mclpy.server import serve

comp = (Composition("Campus monitor with OOON policy",
                    description="MCL 2.0: quality validation plus OOON "
                                "disclosure policy, enforced by the SVC")
        .perspective("estates-team")
        .service("entity", "http://127.0.0.1:7301", "entities and geometry")
        .service("observation", "http://127.0.0.1:7302", "feeds and series")

        .map("sitemap", concept=GEOIOT.Site, title="Monitored sites")

        .timeseries("energychart", concept=GEOIOT.Series,
                    parameter="electricity", unit="kW",
                    title="Building electricity (SEND)")
        .mark_expose()
        .mark_property("siteLabel", bound="#privacy")
        .mark_property("feed", firewall=True)
        .expect_unit("kW")
        .expect_range(0, 10000)

        .timeseries("airchart", concept=GEOIOT.Series,
                    parameter="no2", unit="ug/m3",
                    title="NO2 (METRAQ, interpolation-aware)")
        .mark_expose()
        .mark_drifting()
        .expect_unit("ug/m3")
        .expect_range(0, 1000)

        .flow("sitemap", service="entity", endpoint="/entities")
        .flow("energychart", service="observation",
              endpoint="/feeds/{feed}/series")
        .flow("airchart", service="observation",
              endpoint="/feeds/{feed}/series")

        .on_join("sitemap", "energychart", key="feed")
        .on_join("sitemap", "airchart", key="feed"))


if __name__ == "__main__":
    comp.check()          # schema v2 + static checks 1-12
    print("MCL 2.0 composition checked: 12 static checks passed")
    serve(comp, port=7320)
