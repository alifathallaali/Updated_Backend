# Exercise Manifest

`app/engines/exercise_manifest.py` is the canonical declarative metadata contract for exercises.

It defines: identity, domain, family, personas, required/optional inputs, dependencies, KPI keys,
chart patterns, table pattern, report section, readiness, source and tags.

Analytics remain in engine modules. The manifest does not pretend planned/foundation exercises are complete.

Current invariant:
Exercise Manifest IDs = Product Catalog IDs = Engine Registry IDs = Presentation Catalog IDs.

Future exercise expansion should add a manifest plus an execution handler only when the analytics actually exist.
