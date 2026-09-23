"""Summarize visualization presentation health for a result."""
from .chart_quality import assess_chart_quality

def visualization_quality_summary(charts:list[dict])->dict:
    assessed=[{"chartId":c.get("chartId"),**assess_chart_quality(c)} for c in charts]
    return {
        "chartCount":len(charts),
        "usableCount":sum(1 for x in assessed if x["usable"]),
        "warningCount":sum(len(x["warnings"]) for x in assessed),
        "status":"good" if assessed and all(x["usable"] and not x["warnings"] for x in assessed)
                 else "review" if any(x["usable"] for x in assessed) else "insufficient",
        "assessments":assessed,
    }
