"""Reference adapter: Forecasting -> Visualization Pack."""
from __future__ import annotations
from ..chart_builder import build_chart
from ..chart_spec import ExerciseResult


def build_forecasting_pack(*, forecast: list[dict], period: str | None = None,
                           source: str | None = None) -> ExerciseResult:
    result = ExerciseResult("forecasting", "Forecasting", period=period)
    result.add_chart(build_chart(
        chart_id="forecast_vs_actual", chart_type="line", title="Forecast vs actual",
        x_key="period", data=forecast,
        series=[
            {"data_key": "actual", "label": "Actual"},
            {"data_key": "forecast", "label": "Forecast"},
        ], source=source,
    ))
    return result
