"""Validation for canonical visualization contracts."""
from __future__ import annotations
from .chart_spec import ChartSpec

SUPPORTED_EXPORTS = {"png", "svg", "pdf", "pptx", "xlsx"}


def validate_chart(spec: ChartSpec) -> list[str]:
    errors: list[str] = []
    if not spec.chart_id:
        errors.append("chart_id is required")
    if not spec.title:
        errors.append("title is required")
    if spec.chart_type in {"bar", "line", "area", "scatter"} and not spec.series:
        errors.append("series is required for this chart type")
    if spec.chart_type in {"bar", "line", "area", "scatter"} and not spec.data:
        errors.append("data is required for this chart type")
    unknown = set(spec.export_formats) - SUPPORTED_EXPORTS
    if unknown:
        errors.append(f"unsupported export formats: {sorted(unknown)}")
    return errors


def assert_valid_chart(spec: ChartSpec) -> None:
    errors = validate_chart(spec)
    if errors:
        raise ValueError("Invalid ChartSpec: " + "; ".join(errors))
