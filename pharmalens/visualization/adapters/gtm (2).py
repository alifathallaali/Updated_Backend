from .base import VisualizationAdapter
from ..chart_spec import ChartSpec

class GTMAdapter(VisualizationAdapter):
    exercise_key = "gtm"

    def build(self, result):
        source = self.source(result)
        charts = []
        segments = self.rows(result, "segment_attractiveness")
        if segments:
            charts.append(ChartSpec("segment_attractiveness", "horizontal_bar", "Segment attractiveness", segments, "segment", [{"dataKey":"score","label":"Attractiveness score"}], source=source))
        matrix = self.rows(result, "gtm_priority_matrix")
        if matrix:
            charts.append(ChartSpec("gtm_priority_matrix", "scatter", "GTM priority matrix", matrix, "market_attractiveness", [{"dataKey":"competitive_intensity","label":"Competitive intensity"}], source=source, metadata={"x_axis_label":"Market attractiveness"}))
        return charts
