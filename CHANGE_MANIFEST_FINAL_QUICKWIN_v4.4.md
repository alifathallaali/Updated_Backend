# Scientific Office Final High-Confidence Quick-Win Wave — v4.4

Scope was restricted to the 14 manager-approved Wave 2C high-confidence candidates.

## Changes
- Registered 14 exact bindings to existing PharmaLens callables.
- Reused the canonical exact-binding runner and output normalization.
- Extended the existing launch preparation adapter to LCH-005, because `calculate_launch_growth` consumes the launch feature frame already produced by the existing launch preparation pipeline.
- Repaired the legacy `src.engines.company` package imports so the existing `company_performance` callable can be imported without removed legacy agent/tools or a nonexistent local data_loader.
- Added end-to-end execution and output-contract tests for the approved 14.

## Guardrails
- No new analytical engine or methodology.
- No Synthetic Data changes.
- No frontend/UI, Newsletter, Visualization, Universal Data Intake, Intent Resolver, Trust Layer, Unknown Sheet, Copilot, or unrelated changes.
- Bulk Scientific Office closure stops after this wave.

## Validation
- Approved candidates: 14
- Successfully executed: 14
- Failures: 0
- VERIFIED_EXECUTABLE: 60 -> 74 of 229
- Full repository regression: 196/196 passed
