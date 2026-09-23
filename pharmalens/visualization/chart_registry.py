"""Business visualization registry.

Registry entries describe reusable patterns, not exercise-specific calculations.
"""
from __future__ import annotations

CHART_REGISTRY = {
    "market_share": {"chart_type": "bar", "pattern": "ranking"},
    "market_trend": {"chart_type": "line", "pattern": "time_series"},
    "company_ranking": {"chart_type": "bar", "pattern": "ranking"},
    "therapeutic_mix": {"chart_type": "treemap", "pattern": "composition"},
    "forecast_vs_actual": {"chart_type": "line", "pattern": "time_series_comparison"},
    "forecast_confidence": {"chart_type": "area", "pattern": "forecast_band"},
    "gtm_positioning": {"chart_type": "scatter", "pattern": "portfolio_positioning"},
    "launch_timeline": {"chart_type": "line", "pattern": "timeline"},
    "price_comparison": {"chart_type": "bar", "pattern": "comparison"},
    "recommendation_matrix": {"chart_type": "scatter", "pattern": "priority_matrix"},
    "sales_trend": {"chart_type": "line", "pattern": "time_series"},
    "sales_achievement": {"chart_type": "bar", "pattern": "actual_vs_target"},
    "event_timeline": {"chart_type": "line", "pattern": "timeline"},
}


def get_chart_definition(chart_key: str) -> dict:
    try:
        return CHART_REGISTRY[chart_key].copy()
    except KeyError as exc:
        raise KeyError(f"Unknown PharmaLens chart key: {chart_key}") from exc
