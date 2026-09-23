# Exercise Visualization Framework

The visualization layer scales by **exercise family + reusable visual patterns**, not one renderer per exercise.

Flow:

`exercise -> analytical result -> family resolver -> visual patterns -> ChartSpec[] -> web/report renderers`

Existing product-01..14 packs remain hand-tuned. Future exercises can resolve to market, company, molecule, product, forecast, scenario, launch, sales, finance, supply, inventory, market access, medical, quality, or generic families. This does not claim an exercise is analytically implemented; it only controls presentation of governed outputs.

This separation is intentional: analytics readiness remains owned by the engine registry, while visualization can scale independently toward the larger exercise catalog.
