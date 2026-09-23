# Visualization Integration

`run_product_engine()` now appends `visualizations: ChartSpec[]` to each product result.
The visualization service is presentation-only and does not replace engine metrics.

Frontend consumes the same JSON contract through `ProductRun.visualizations`.
No exporters were added in this patch.

## Current visualization coverage
Presentation packs are now explicitly mapped for product-01 through product-14.
Foundation-only engines remain labeled by the engine readiness system; visualization does not upgrade their analytical readiness.
