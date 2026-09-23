from .base import VisualizationAdapter
from ..chart_spec import ChartSpec

class MarketIntelligenceAdapter(VisualizationAdapter):
    exercise_key = "market_intelligence"

    def build(self, result):
        source = self.source(result)
        charts = []
        trend = self.rows(result, "market_trend")
        if trend:
            charts.append(ChartSpec("market_trend", "line", "Market value trend", trend, "period", [{"dataKey":"value","label":"Market value"}], source=source))
        share = self.rows(result, "company_share")
        if share:
            charts.append(ChartSpec("company_share", "horizontal_bar", "Company market share", share, "company", [{"dataKey":"share_pct","label":"Market share","valueSuffix":"%"}], source=source))
        brands = self.rows(result, "brand_ranking")
        if brands:
            charts.append(ChartSpec("brand_ranking", "horizontal_bar", "Top brands by value", brands, "brand", [{"dataKey":"value","label":"Sales value"}], source=source))
        return charts
