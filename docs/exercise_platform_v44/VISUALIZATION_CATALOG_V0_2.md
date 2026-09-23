# PharmaLens Visualization Catalog V0.2

## Purpose
A presentation contract for the existing PharmaLens AI exercises. It does not replace analytics, ingestion, Copilot, or reporting logic.

## Flow
Exercise → ExerciseResult → Visualization Adapter → ChartSpec → Web UI / Report / Export

## Design rules
- Analytics remains the source of truth.
- Each exercise declares KPIs, visuals, insights and supported exports.
- Visual types are reusable patterns; titles and data mappings are exercise-specific.
- The same ChartSpec must be renderable in the web UI and reusable by report/PPTX exporters.
- Visualization must preserve provenance/source metadata when available.
- AI may select a registered visual pattern, but rendering stays deterministic.
- No raw/restricted source tables are exposed merely because a visualization exists.

## Initial exercise packs
Market Intelligence, Forecasting, GTM, Launch, Pricing, Market Access, HEOR, SFE, KOL, Medical Affairs, Supply Chain, Company Intelligence, Recommendations.

## Integration
Merge into the existing `PharmaLens AI V0.2/` tree. This pack is additive; it is not a parallel application.
