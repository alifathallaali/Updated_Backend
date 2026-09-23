# Exercise Platform v4.4 consolidation

Baseline: MVP USER JOURNEY CLOSURE (which already includes VISUALIZATION MVP FINAL and the later intake/intent/trust/copilot/user-journey work).

The Scientific Office / Exercise Platform v4.4 runtime is preserved additively under `src/` and its visualization catalog under `pharmalens/visualization/`. Existing `app/` routes, engines, Universal Data Intake, Intent Resolver, Trust Layer, Unknown Dataset workflow, grounded Copilot, visualization and user journey were not overwritten.

The legacy `updated-frontend/` snapshot from the v4.4 archive was intentionally not copied because it predates the current MVP frontend and would regress the UI/user journey.

v4.4 release facts retained from its source manifest: 229 canonical definitions, 231 runtime definitions, 49 Tier-1 executable, 162 Tier-2 candidate, 10 Tier-3 unmapped, 10 strategic composites, 48/48 exact semantic bindings verified, release gate `READY_WITH_DOCUMENTED_GAPS`.

No new product feature is introduced by this consolidation. The v4.4 runtime is retained as a namespaced canonical source for subsequent bridge work; current production API behavior remains owned by `app/`.
