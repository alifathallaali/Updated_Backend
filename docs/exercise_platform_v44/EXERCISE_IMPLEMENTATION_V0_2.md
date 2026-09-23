# PharmaLens AI V0.2 — Exercise Layer Implementation

## Exact physical paths used

All new implementation files are rooted under:

`PharmaLens AI V0.2/`

### Exercise orchestration

- `PharmaLens AI V0.2/src/exercises/__init__.py`
- `PharmaLens AI V0.2/src/exercises/types.py`
- `PharmaLens AI V0.2/src/exercises/schemas.py`
- `PharmaLens AI V0.2/src/exercises/availability.py`
- `PharmaLens AI V0.2/src/exercises/lineage.py`
- `PharmaLens AI V0.2/src/exercises/results.py`
- `PharmaLens AI V0.2/src/exercises/registry.py`
- `PharmaLens AI V0.2/src/exercises/resolver.py`
- `PharmaLens AI V0.2/src/exercises/validation.py`
- `PharmaLens AI V0.2/src/exercises/runner.py`
- `PharmaLens AI V0.2/src/exercises/visualization.py`

### Tests

- `PharmaLens AI V0.2/tests/exercises/test_sal_008.py`

## Reused existing architecture

The existing visualization foundation under `PharmaLens AI V0.2/pharmalens/visualization/` is reused. No second charting stack was created.

The existing reporting architecture under `PharmaLens AI V0.2/src/reports/` remains unchanged.

No new authentication, database, ingestion pipeline, Copilot, forecasting engine, scenario engine, or reporting engine was created.

## First production vertical slice

`SAL-008` is registered at version `1.0` and currently supports:

- deterministic sales-value trend calculation
- data availability check
- immutable run metadata
- canonical result normalization
- evidence typing
- lineage
- visualization resolution
- golden test dataset

Golden dataset:

- Jan = 100
- Feb = 110
- Mar = 105
- Apr = 90

Expected first-to-last growth: `-10%`.

## Validation result

Exercise-specific tests: **5 passed**.

The complete pre-existing pytest suite currently has unrelated repository import failures caused by existing `__init__.py` imports referencing modules that are not present in the supplied repository snapshot. Those failures were not modified as part of the Exercise Layer slice.

## Next implementation gate

After this vertical slice is reviewed, the next production slice is the composite orchestrator and `STR-004`, followed by catalog-driven migration of the remaining exercises.

## Composite Slice v0.2

Added `src/exercises/orchestrator.py` with generic composite execution, required/optional child handling, conflict detection, quality aggregation, child-run lineage, and evidence-only synthesis. Registered the STR-004 Brand Growth Strategy definition with its 9 required child exercises.

Added `tests/exercises/test_composite.py` covering completion/lineage, conflicting child metrics, and required-child blocking.

Validation: `PYTHONPATH=. pytest -q tests/exercises/test_sal_008.py tests/exercises/test_composite.py` → **8 passed**.

## Composite Slice v0.3 — Engine Binding Hardening

Added:
- `PharmaLens AI V0.2/src/exercises/adapters.py`
- `PharmaLens AI V0.2/tests/exercises/test_adapters.py`

The adapter layer is declarative and fail-closed. It records verified mappings to existing engine modules but does not calculate fallback results. If an existing engine cannot import cleanly or lacks a validated canonical-result adapter, the child Exercise is BLOCKED rather than fabricated.

Current discovered binding:
- `MKT-003` → `src.engines.market_intelligence.market_intelligence.market_share_by_brand`

Current repository state prevents this binding from executing because the existing `market_intelligence` package imports a missing `src.engines.market_intelligence.agent` dependency. This is an existing repository dependency issue, not replaced by a duplicate engine.

Exercise tests: **11 passed**.

## v0.4 — First Real Existing-Engine Binding

- Reused `src/engines/market_intelligence/market_intelligence.py` for `MKT-003`.
- Removed the legacy package initializer dependency that referenced missing modules.
- Kept default data loading lazy so supplied DataFrames are executed directly by the existing engine.
- Added a canonical-result adapter for observed brand market-share output.
- Missing required columns fail closed with `BLOCK`.
- `MKT-003` now executes as a real child run; `STR-004` remains blocked until the other required child capabilities have validated adapters.
- Exercise tests: 12 passed.
- Full repository tests remain blocked by pre-existing missing `src.agents.tools` and `src.core.agent` imports outside this slice.
