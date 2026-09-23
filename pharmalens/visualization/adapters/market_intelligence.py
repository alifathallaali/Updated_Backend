"""Reference adapter: Market Intelligence -> Visualization Pack."""
from __future__ import annotations
from ..chart_builder import build_chart
from ..chart_spec import ExerciseResult


def build_market_intelligence_pack(*, market_trend: list[dict], company_share: list[dict],
                                   period: str | None = None, source: str | None = None) -> ExerciseResult:
    result = ExerciseResult("market_intelligence", "Market Intelligence", period=period)
    result.add_chart(build_chart(
        chart_id="market_trend", chart_type="line", title="Market evolution",
        x_key="period", data=market_trend,
        series=[{"data_key": "value", "label": "Market value", "value_format": "currency"}],
        source=source,
    ))
    result.add_chart(build_chart(
        chart_id="company_share", chart_type="bar", title="Company market share",
        x_key="company", data=company_share,
        series=[{"data_key": "share", "label": "Market share", "value_format": "percent"}],
        source=source,
    ))
    return result
