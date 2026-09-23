"""Canonical, renderer-agnostic visualization contracts for PharmaLens AI."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

ChartType = Literal[
    "bar", "line", "area", "scatter", "pie", "donut", "heatmap",
    "treemap", "funnel", "waterfall", "radar", "sankey", "gauge", "table"
]


@dataclass(frozen=True)
class ChartSeries:
    data_key: str
    label: str
    unit: str | None = None
    value_format: str = "auto"
    axis_label: str | None = None


@dataclass
class ChartSpec:
    chart_id: str
    chart_type: ChartType
    title: str
    description: str | None = None
    x_key: str | None = None
    x_axis_label: str | None = None
    y_axis_label: str | None = None
    series: list[ChartSeries] = field(default_factory=list)
    data: list[dict[str, Any]] = field(default_factory=list)
    filters: dict[str, Any] = field(default_factory=dict)
    annotations: list[dict[str, Any]] = field(default_factory=list)
    insight: str | None = None
    source: str | None = None
    methodology: str | None = None
    theme: str = "pharmalens"
    export_formats: list[str] = field(default_factory=lambda: ["png", "svg", "pdf", "pptx", "xlsx"])
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExerciseResult:
    exercise_id: str
    exercise_name: str
    status: str = "completed"
    filters: dict[str, Any] = field(default_factory=dict)
    period: str | None = None
    kpis: list[dict[str, Any]] = field(default_factory=list)
    tables: list[dict[str, Any]] = field(default_factory=list)
    charts: list[ChartSpec] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    data_quality: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)

    def add_chart(self, chart: ChartSpec) -> "ExerciseResult":
        self.charts.append(chart)
        return self
