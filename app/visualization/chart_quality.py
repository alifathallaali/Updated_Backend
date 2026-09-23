"""Presentation quality checks for ChartSpec.

This layer does not change analytics. It identifies charts that are empty,
misleadingly sparse, or visually overloaded and supplies presentation guidance.
"""
from __future__ import annotations

def assess_chart_quality(chart:dict)->dict:
    data=chart.get("data") or []
    typ=str(chart.get("chartType","")).lower()
    x=chart.get("xKey")
    series=chart.get("series") or []
    issues=[]; warnings=[]; usable=True
    if not data:
        issues.append("no_data"); usable=False
    elif len(data)==1 and typ in {"line","area"}:
        issues.append("single_point_trend"); usable=False
    if len(data)>30 and typ in {"bar","pie","treemap"}:
        warnings.append("too_many_categories")
    if typ=="pie" and len(data)>8:
        warnings.append("pie_category_overload")
    if series and data:
        numeric_points=0
        for row in data:
            for s in series:
                v=row.get(s.get("dataKey"))
                if isinstance(v,(int,float)): numeric_points+=1
        if numeric_points==0:
            issues.append("no_numeric_series"); usable=False
    return {
        "usable":usable,
        "issues":issues,
        "warnings":warnings,
        "dataPoints":len(data),
        "recommendation": (
            "show" if usable and not warnings else
            "show_with_caution" if usable else
            "empty_state"
        ),
    }

def apply_chart_quality(charts:list[dict])->tuple[list[dict],list[dict]]:
    rendered=[]; suppressed=[]
    for chart in charts:
        item=dict(chart)
        quality=assess_chart_quality(item)
        item["presentationQuality"]=quality
        if quality["usable"]: rendered.append(item)
        else: suppressed.append({
            "chartId":item.get("chartId"),
            "title":(item.get("meta") or {}).get("title"),
            **quality,
        })
    return rendered,suppressed
