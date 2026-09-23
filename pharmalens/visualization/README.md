# PharmaLens AI — Visualization Foundation Pack V0.2

This is a **patch pack**, not a replacement project structure. Merge the files into the existing `PharmaLens AI V0.2/` repository at the matching relative paths.

## Architecture

`Existing Exercise → Existing/Canonical Result → Visualization Adapter → ChartSpec → Renderer → Web / Report / Export`

## Principles

- No duplicate analytics engine.
- No duplicate data ingestion/database/auth/Copilot/report engine.
- Exercise adapters only translate existing results into canonical `ChartSpec` objects.
- One PharmaLens theme contract for UI and future exports.
- Registry describes reusable visualization patterns.
- Export formats are part of the contract from day one.

## Frontend dependency

The React components assume `echarts-for-react` is available. If the existing frontend already uses another ECharts wrapper, adapt only `PharmaChart.tsx`; do not introduce a second charting stack.

## Next integration step

1. Inspect the existing exercise result contracts.
2. Map each exercise to `Visualization Adapter` entries.
3. Connect `VisualizationPack` to the existing exercise UI.
4. Connect `ExportMenu` to the existing report/export APIs.
5. Extend the registry only when a real business visualization is required.
