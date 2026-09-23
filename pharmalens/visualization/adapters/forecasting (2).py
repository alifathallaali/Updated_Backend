from .base import VisualizationAdapter
from ..chart_spec import ChartSpec

class ForecastingAdapter(VisualizationAdapter):
    exercise_key = "forecasting"

    def build(self, result):
        source = self.source(result)
        charts = []
        actual = self.rows(result, "actual_vs_forecast")
        if actual:
            charts.append(ChartSpec("actual_vs_forecast", "line", "Actual vs forecast", actual, "period", [{"dataKey":"actual","label":"Actual"},{"dataKey":"forecast","label":"Forecast"}], source=source))
        error = self.rows(result, "forecast_error")
        if error:
            charts.append(ChartSpec("forecast_error", "bar", "Forecast error by period", error, "period", [{"dataKey":"error_pct","label":"Forecast error","valueSuffix":"%"}], source=source))
        scenarios = self.rows(result, "scenario_comparison")
        if scenarios:
            charts.append(ChartSpec("scenario_comparison", "line", "Scenario comparison", scenarios, "period", [{"dataKey":"base","label":"Base"},{"dataKey":"upside","label":"Upside"},{"dataKey":"downside","label":"Downside"}], source=source))
        return charts
