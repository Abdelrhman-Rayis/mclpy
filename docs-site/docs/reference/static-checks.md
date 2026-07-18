# Reference: the static checks

Before any service is invoked, `check()` runs the composition through the JSON Schema and then through the static checks below. Any violation is a refusal: the runtime will not start, and the error names the check and the offending element. This turns a class of integration faults into load-time errors.

## v1 checks (always run)

| # | Check | Example violation |
|---|---|---|
| 1 | service identifiers are unique | `duplicate service id 'obs'` |
| 2 | component identifiers are unique | `duplicate component id 'chart'` |
| 3 | every dataflow references a declared service | `dataflow for 'chart' references unknown service 'ghost'` |
| 4 | every dataflow targets a declared component | `dataflow targets unknown component 'chrt'` |
| 5 | every component is fed by exactly one dataflow | `component 'chart' has no dataflow` |
| 6 | every bound concept exists in the ontology | `component 'chart' binds concept <...#Seriez> not present in the ontology` |
| 7 | every unit rule agrees with its binding's unit; interactions reference declared components | `component 'chart': unit rule expects 'ft' but binding declares 'm'` |

## v2 checks (run when `mcl_version` is `2.0`)

| # | Check | Example violation |
|---|---|---|
| 8 | the composition declares a perspective | `2.0 composition declares no perspective (check 8)` |
| 9 | mark compositions are legal | `firewall composes with nothing, found ['expose']` |
| 10 | no firewalled property appears in a validation rule | `firewalled property 'feed' appears in a validation rule (check 10)` |
| 11 | every join key has a slot in the target dataflow endpoint | `join key 'feed' has no slot in target dataflow endpoint '/series' (check 11)` |
| 12 | every `bound` mark carries a `#reason` | `bound requires a #reason, got 'privacy'` |

## Running the checks

=== "Python"

    ```python
    from mclpy import MCLStaticError
    try:
        comp.check()                      # default ontology (GeoIoT)
        comp.check(ontology=my_ontology)  # or your own
    except MCLStaticError as e:
        for v in e.violations:
            print(v)
    ```

=== "CLI"

    ```bash
    mcl validate dash.mcl.json
    mcl validate dash.mcl.json --ontology farm.ttl
    ```

A clean document prints an OK line; a broken one prints each violation and exits non-zero.

## Design note

The checks are intentionally cheap and total: they run in-process, need no network, and either pass entirely or name every problem. That is what lets `check()` be a hard precondition for `serve()` rather than an optional lint.
