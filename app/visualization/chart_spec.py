"""Backend ChartSpec helpers. JSON contract consumed by the Next.js frontend."""
from typing import Any

def chart_spec(*, chart_id: str, chart_type: str, title: str, data: list[dict[str, Any]],
               x_key: str | None = None, series: list[dict[str, Any]] | None = None,
               description: str | None = None, **options: Any) -> dict[str, Any]:
    spec = {
        "chartId": chart_id,
        "chartType": chart_type,
        "meta": {"title": title, "description": description},
        "data": data,
    }
    if x_key is not None:
        spec["xKey"] = x_key
    if series is not None:
        spec["series"] = series
    spec.update(options)
    return spec
