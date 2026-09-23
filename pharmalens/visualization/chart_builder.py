"""Small deterministic builder used by exercise adapters."""
from __future__ import annotations
from .chart_spec import ChartSeries, ChartSpec
from .validators import assert_valid_chart


def build_chart(
    *, chart_id: str, chart_type: str, title: str, data: list[dict],
    x_key: str | None = None, series: list[dict] | None = None,
    description: str | None = None, insight: str | None = None,
    source: str | None = None, filters: dict | None = None,
    metadata: dict | None = None,
) -> ChartSpec:
    spec = ChartSpec(
        chart_id=chart_id,
        chart_type=chart_type,
        title=title,
        description=description,
        x_key=x_key,
        series=[ChartSeries(**item) for item in (series or [])],
        data=data,
        insight=insight,
        source=source,
        filters=filters or {},
        metadata=metadata or {},
    )
    assert_valid_chart(spec)
    return spec
