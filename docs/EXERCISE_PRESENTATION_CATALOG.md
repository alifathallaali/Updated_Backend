# Exercise Presentation Catalog

The visualization layer now separates three concerns:

1. **Engine readiness** — owned by analytics/engine code.
2. **Presentation mapping** — KPI keys, reusable chart family, table pattern, report section.
3. **Rendering** — website and report renderers consume the same ChartSpec contract.

`app/visualization/exercise_catalog.py` explicitly maps the currently registered product-01 through product-14 engines. Planned PharmaLens domains are templates only and do not imply that their analytics engines are complete.

To add a future exercise, add one presentation entry or allow the family resolver to infer a safe profile. Do not create a dedicated renderer unless the exercise genuinely requires a unique visual grammar.
