# Why dashboards lie

Before the tools, the problem. This page explains, without jargon, why a normal dashboard will confidently show you wrong numbers, and where the fix has to live.

## A dashboard is a very trusting program

When a chart receives a list of numbers, it draws them. It does not ask where they came from, whether they are in the unit it expects, or whether half of them are missing. It just plots. That trust is fine when the data is clean. It is dangerous when the data comes from sensors in the real world, because real-world sensor data is routinely broken.

## The three ways sensor data goes wrong

Studies that survey Internet-of-Things data find the same failure modes again and again. It helps to name them, because MCL's rules map directly onto them.

**Wrong units.** A meter is reconfigured, or a new data source is added, and suddenly a feed reports watt-hours where the chart expects kilowatt-hours. Every value is off by a factor of 1000, but each individual number looks plausible, so nothing flags it.

**Impossible values.** A sensor glitches and reports a river level of 9,999,999 metres, or a negative humidity. A single spike can rescale an entire chart, hiding the real signal behind one absurd point.

**Missing data.** A station drops offline for three days. The chart plots the few points it has as a smooth line across the gap, implying continuity that never happened.

None of these is exotic. They are the normal weather of operational data.

## Where people try to fix it, and why it is not enough

The standard response is to clean the data in the *pipeline*: a stage between the sensor and the dashboard that detects outliers, imputes missing values, and corrects drift. This is good and necessary work, and there is a large research literature on it.

But the pipeline is not the last line of defence. Data can bypass it, arrive from a source that was never wired through it, or carry a fault the cleaning stage was not built to catch. And crucially, the pipeline does not know what any particular *chart* expects. It cleans data in general; it cannot know that *this* component is supposed to show water level in metres between -1 and 12.

## The interface is the last checkpoint

The dashboard is the final place a wrong value can be stopped before a human reads it and acts. It is also, in almost every system, the one layer with no declared expectations at all. The chart will draw whatever it is handed.

MCL's core idea is to give that last checkpoint a memory of what it expects. You declare, next to each component, the unit it should receive and the range its values should fall in. The runtime enforces those declarations on every update and refuses anything that violates them.

## This is not hypothetical

While building the reference deployment, the authors added a public air-quality dataset from Madrid. One monitoring station, Sanchinarro, had only 45 of an expected 168 hourly readings for the week: 27% coverage. A normal dashboard would have drawn those 45 points as a continuous line and called it air quality.

MCL had a completeness rule declared on that chart: at least 50% of expected points must be present. The rule fired. The station's series was withheld, the dashboard showed the reason, and the neighbouring stations, which passed, rendered normally. Nobody wrote special-case code for Sanchinarro. The rule that protected against it was one line, written once, and it caught a real fault in real public data that the authors had never seen.

## The takeaway

Dashboards lie because they trust their input and have no way to say what they expect. MCL lets you *say what you expect*, in a way a machine can enforce, at the one point where it still matters. The rest of this wiki is about how.

## Next

- [Declare, check, enforce](declare-check-enforce.md): the shape of the solution.
- [Ontologies for JSON developers](ontologies-for-json-devs.md): the one unfamiliar idea, made simple.
