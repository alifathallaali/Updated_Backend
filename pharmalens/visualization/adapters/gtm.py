"""Reference adapter: GTM -> Visualization Pack."""
from __future__ import annotations
from ..chart_builder import build_chart
from ..chart_spec import ExerciseResult


def build_gtm_pack(*, positioning: list[dict], source: str | None = None) -> ExerciseResult:
    result = ExerciseResult("gtm", "Go-to-Market Analysis")
    result.add_chart(build_chart(
        chart_id="gtm_positioning", chart_type="scatter", title="GTM positioning",
        x_key="attractiveness", data=positioning,
        series=[{"data_key": "capability", "label": "Capability"}],
        source=source,
    ))
    return result
