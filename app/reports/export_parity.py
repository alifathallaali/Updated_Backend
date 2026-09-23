"""Normalize saved visualizations for UI/export presentation parity."""
from __future__ import annotations
from ..visualization.chart_priority import prioritize_charts
from ..visualization.chart_quality import apply_chart_quality
from ..visualization.chart_adaptation import adapt_charts

PHARMALENS_THEME={"navy":"16324F","teal":"2FA7A0","slate":"2F6B7C","green":"2E8B70","red":"C94C4C","background":"F7F9FB","muted":"64748B"}

def prepare_export_output(output:dict)->dict:
    prepared=dict(output)
    charts=list(output.get("visualizations") or [])
    # Saved runs normally already contain presentation metadata. Sort by rank when present.
    charts.sort(key=lambda c:(c.get("presentationPriority") or {}).get("rank",999))
    usable,_=apply_chart_quality(charts)
    charts=adapt_charts(usable)
    prepared["visualizations"]=charts
    prepared["exportPresentation"]={
        "theme":"pharmalens","layout":(output.get("presentation") or {}).get("layout","executive_overview"),
        "chartCount":len(charts),"primaryChartId":charts[0].get("chartId") if charts else None,
        "parityVersion":"1.0",
    }
    return prepared
