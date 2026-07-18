# The research behind it

MCL is not a weekend project; it comes from peer-reviewed PhD research at Keele University on making heterogeneous geospatial and IoT data trustworthy from source to screen. This page summarises that work in plain terms and tells you how to cite it.

## The one-paragraph summary

Developers who build dashboards over IoT data hand-write the code that connects data services to charts, and that code silently renders faulty sensor data because validation, where it exists at all, is scattered and implicit. The research argues that this connective layer can instead be declared in a document, checked against a domain ontology before it runs, and enforced at run time. It contributes the language (MCL) and runtime (SVC) that do so, and evaluates them on real data: declarative composition removed about half the developer-written code against an equivalent hand-built dashboard, and the declared rules caught every injected fault of the classes they cover while raising no false alarms on clean data.

## The evaluation, honestly

The claims are backed by a self-contained, re-runnable evaluation artefact, not by assertion:

- **Effort:** the MCL version of a dashboard needed 49.1% fewer developer-authored lines than a behaviourally-equivalent procedural baseline (checked for equivalence automatically before measuring).
- **Extensibility:** adding a new view cost 2.1 times less in the declarative version, and touched one document instead of four separate concerns.
- **Enforcement:** across 30 fault-injection trials, the rules caught all 1,440 injected faults of the three covered classes, with zero false positives on 3,600 clean records, at 0.31 ms median overhead.
- **The boundary:** the rules caught 0% of "in-range corruption" (plausible-but-wrong values), reported openly, because single-record rules cannot detect a plausible falsehood.

The work is candid about what it has not shown: no user study has been run yet, and every human-factors claim is either scoped away or attributed to the external DSL-comprehension literature.

## The lineage

- **MicroMaps** (ICCBDC 2025) contributed the GeoIoT ontology and the microservice architecture for fusing geospatial and IoT data.
- **GeoIoT Core** (ICCBDC 2026) is the standards-aligned bridging ontology that evolved from it.
- The **MCL/SVC paper** (under submission) contributes the declarative interface layer that both earlier papers left procedural. This wiki documents its `mclpy` implementation.

## The MCL 2.0 preview

The [policy-marks tutorial](../tutorials/policy-marks.md) previews an extension (OOON) that carries the same enforcement idea from data *quality* to data *disclosure*. It is implemented and runnable, but the research treats it as a preview: it has not been evaluated to the standard above, and its novelty relative to policy languages such as ODRL and DPV requires a positioning survey still in progress. The specification lives in the repository at `docs/OOON-SPEC.md`.

## How to cite

Until the MCL/SVC paper has a published venue, cite the implementation and the foundational papers:

```bibtex
@software{mclpy,
  author = {Rayis, Abdelrhman},
  title  = {mclpy: the Microservice Composition Language for Python},
  url    = {https://github.com/Abdelrhman-Rayis/mclpy},
  year   = {2026}
}

@inproceedings{rayis2025micromaps,
  author    = {Rayis, Abdelrhman and Ortolani, Marco and David, Ruusa-Magano and M{\i}s{\i}rl{\i}, G{\"o}ksel},
  title     = {{MicroMaps}: Ontology-Driven Semantic Geospatial Data Fusion for {IoT} Integration and Decision Making in Smart Cities},
  booktitle = {Proc. 9th Int. Conf. on Cloud and Big Data Computing (ICCBDC)},
  year      = {2025}
}
```

Check the [repository](https://github.com/Abdelrhman-Rayis/mclpy) for the current citation once the paper appears.
