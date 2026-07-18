# Coming from Grafana, Plotly or Streamlit

If you have built dashboards before, you already understand most of MCL. This page maps what you know onto MCL's vocabulary, then says clearly what MCL adds and what it deliberately does not do.

## The concepts you already know

| You know | In MCL it is called | Notes |
|---|---|---|
| A panel / chart / widget | a **component** | `map`, `timeseries`, `kpi`, `table` |
| A data source / datasource | a **service** | an HTTP endpoint, or a local Python function |
| A query that fills a panel | a **dataflow** | connects one component to one endpoint |
| A dashboard variable / drill-down | an **interaction** | e.g. click a map marker to filter a chart |
| Dashboard-as-code (JSON/YAML) | the **MCL document** | one declarative file for the whole interface |

So far, nothing new. If MCL stopped here it would be a smaller Grafana.

## What MCL adds

Three things that dashboard tools do not give you:

**1. Components are bound to meaning, not just to a query.** In Grafana a panel shows whatever a query returns; the panel does not know that the number is a CO2 reading in kilograms. In MCL every component declares the ontology *concept* it represents and the *unit* it expects. That declaration is machine-checkable.

**2. The composition is validated before it runs.** MCL runs [static checks](../reference/static-checks.md) when the document loads: unknown concepts, dangling dataflows, and rules that contradict their bindings are all caught before a single service is called. A broken dashboard fails at load, not in front of a user.

**3. Bad data is refused, with a reason.** Every update passes through declared validation rules. A payload in the wrong unit, out of range, or too incomplete is *withheld from the view*, and the reason travels back in a [semantic envelope](../foundations/semantic-envelope.md). Grafana will happily plot a wrong-unit series; MCL will not.

## What MCL does not do

Be clear about the boundary. MCL is not trying to replace your whole stack.

- **Panel styling and theming.** MCL renders a clean default dashboard. It is not a pixel-level design tool.
- **Alerting and notifications.** MCL withholds bad data at render time; it does not page you at 3am. Pair it with your existing alerting.
- **A managed server, users, and permissions.** MCL is a library you run. There is no hosted control plane.
- **A visualisation grammar.** MCL composes services, interactions and validation; it does not describe marks, scales and encodings the way Vega-Lite does. It could embed such a grammar for rendering a single component.

## The honest one-liner

Grafana asks *"what should this panel show?"* MCL asks *"what should this panel show, what does that data mean, and what must be true about it before anyone sees it?"* If the third question matters for your data, MCL is for you.

## Next

- [Install and quickstart](install.md) to feel the difference in 15 minutes.
- [How MCL compares](../explanation/architecture.md#how-mcl-compares) for the detailed positioning.
