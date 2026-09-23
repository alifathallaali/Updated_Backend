from __future__ import annotations
from typing import Any, Mapping
from .schemas import CanonicalResult


def _as_dict(spec: Any) -> dict[str, Any]:
    """Serialize existing PharmaLens ChartSpec without introducing a second contract."""
    data = dict(spec.__dict__)
    data["series"] = [dict(s.__dict__) for s in data.get("series", [])]
    return data


def resolve_visualizations(
    exercise_id: str,
    result: CanonicalResult,
    *,
    child_runs: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Map canonical exercise semantics to the existing PharmaLens ChartSpec system."""
    from pharmalens.visualization import ChartSpec, ChartSeries

    exercise_id = exercise_id.upper()
    if exercise_id == "SAL-008":
        rows = list(result.metadata.get("rows", []))
        chart = ChartSpec(
            chart_id="SAL-008-trend",
            chart_type="line",
            title="Sales value trend",
            x_key="period",
            series=[ChartSeries(data_key="sales_value", label="Sales value")],
            data=rows,
            source=result.lineage.get("source"),
            methodology="Deterministic first-to-last sales trend from canonical exercise input.",
            metadata={"exercise_id": exercise_id, "pattern": "TIME_SERIES", "viz_id": "VIZ-003"},
        )
        growth = next((m for m in result.metrics if m.get("id") == "sales_growth_pct"), None)
        kpi = {
            "chart_id": "SAL-008-growth-kpi", "chart_type": "gauge", "title": "Sales growth",
            "value": growth.get("value") if growth else None, "unit": "%", "pattern": "KPI", "viz_id": "VIZ-001",
        }
        return [_as_dict(chart), kpi]

    if exercise_id == "STR-004":
        child_runs = child_runs or {}
        rows = []
        for child_id, run in child_runs.items():
            rows.append({
                "exercise_id": child_id,
                "status": run.status.value,
                "quality_status": run.quality_status.value,
                "has_evidence": bool(run.result),
                "evidence_count": len(run.result.key_findings) if run.result else 0,
            })
        coverage = ChartSpec(
            chart_id="STR-004-evidence-coverage",
            chart_type="bar",
            title="Strategic evidence coverage",
            x_key="exercise_id",
            series=[ChartSeries(data_key="evidence_count", label="Evidence items")],
            data=rows,
            methodology="Counts validated child findings; unavailable children remain explicit and are not imputed.",
            metadata={"exercise_id": exercise_id, "pattern": "EVIDENCE", "viz_id": "VIZ-022"},
        )
        quality_table = ChartSpec(
            chart_id="STR-004-child-quality",
            chart_type="table",
            title="Child exercise quality",
            data=rows,
            methodology="Displays child execution and quality states without converting them into a composite score.",
            metadata={"exercise_id": exercise_id, "pattern": "QUALITY", "viz_id": "VIZ-013"},
        )
        return [_as_dict(coverage), _as_dict(quality_table)]

    return []
