# PharmaLens AI V0.1 Integration Map

## Source repository

- Repository: `https://github.com/alifathallaali/PharmaLens_AI_V0.1`
- Inspected commit: `236a0fb36012511e148b06385842789ee97b013d`
- Important source areas: `src/`, `notebooks/`, `templates/`, and synthetic data.

## Existing backend bridge

The current FastAPI backend already contains a governed adapter-style engine registry under `app/engines/`. It consumes canonical `DatasetVersion` rows and returns structured outputs with evidence and warnings. It should remain the production execution path.

| V0.1 source capability | Current backend bridge | Status |
|---|---|---|
| `src/market_intelligence.py` and market notebooks | `product-01`, `product-05` in `analytics_engines.py` | Available; canonical rows required |
| `src/company.py` and company notebook | `product-02` in `analytics_engines.py` | Available |
| `src/molecule.py` and molecule notebook | `product-03` in `analytics_engines.py` | Available when molecule/active ingredient exists |
| `src/forecasting.py` and forecasting notebook | `product-06` in `strategy_engines.py` | Available as transparent historical diagnostics/run-rate; not a notebook-grade forecast claim |
| `src/launch.py` and launch notebook | `product-07` in `strategy_engines.py` | Available when launch date and reporting period exist |
| `src/scenario.py` and scenario notebook | `product-08` in `strategy_engines.py` | Available with explicit verified assumptions |
| GTM, recommendation, similarity, medical affairs, market access, financial intelligence | Product catalog foundation/in-progress states | Must be added as explicit adapters after data contracts and authorization are confirmed |
| `src/agent.py` and `src/tools.py` | Existing FastAPI Copilot plus DatasetVersion/Product Engine architecture | Do not run the legacy agent against local filesystem data in production |
| `src/report_orchestrator.py` | Existing backend report routers/generators | Reconcile output contracts before connecting additional renderers |

## Recommended production boundary

```text
Supabase upload
  -> DatasetVersion / canonical service
  -> existing Product Engine Registry
  -> structured metrics + evidence + provenance
  -> centralized Copilot AI service
  -> Dashboard / Reports / Excel
```

The V0.1 notebooks are valuable as research and validation references. They should not be executed directly inside a FastAPI request because many of them assume local filesystem paths, notebook state, or a fixed processed Parquet file. If a capability is needed, create one small adapter that accepts canonical rows and returns the existing structured output contract.

## Sensitive-data boundary

The repository contains patient, diagnosis, treatment, prescription, and medical-affairs datasets. These must not be automatically copied into the commercial Copilot context or exposed through generic dataset/file endpoints. Any future medical-affairs integration requires explicit dataset classification, authorization, provenance, and a separate permitted output contract.

## Current decision

No duplicate notebook runner or second data loader was added. The current backend remains the single runtime, the AI Data Layer remains the source of truth, and the existing engine registry remains the single calculation path. The inspected source commit is recorded here for traceability.

## Next implementation slices

1. Add a canonical dataframe adapter for the remaining non-sensitive capabilities: GTM, recommendations, similarity, and commercial finance.
2. Add contract tests comparing adapter outputs with approved V0.1 notebook fixtures.
3. Add classification-aware policy before any patient, medical-affairs, licensed, or external-data module is exposed.
4. Connect dashboard/Excel outputs to the same structured aggregation rather than directly to notebook files.
5. Only then expose selected outputs to the centralized Copilot through structured `data_context`.
