"""MVP visualization coverage audit for executable PharmaLens exercises."""
from __future__ import annotations
from ..engines.exercise_manifest import EXERCISE_MANIFESTS
from ..engines.engine_registry import ENGINE_REGISTRY
from .exercise_catalog import get_exercise_presentation
from .layout_templates import get_family_layout

REQUIRED_PRESENTATION_FIELDS=("family","kpis","table","report_section","chart_patterns","semantic_role","layout")

def audit_exercise_coverage()->dict:
    rows=[]
    for m in EXERCISE_MANIFESTS:
        p=get_exercise_presentation(m.id,name=m.name,domain=m.domain)
        checks={
            "engine": m.id in ENGINE_REGISTRY,
            "manifest": True,
            "kpis": bool(m.kpis) or m.id in {"product-15","product-16","product-17"},
            "chartPatterns": bool(p.get("chart_patterns")),
            "layout": bool(p.get("layout")) and bool(get_family_layout(m.family)),
            "table": bool(p.get("table")),
            "reportSection": bool(p.get("report_section")),
        }
        rows.append({"exerciseId":m.id,"name":m.name,"family":m.family,"readiness":m.readiness,
                     "checks":checks,"covered":all(checks.values()),
                     "gaps":[k for k,v in checks.items() if not v]})
    covered=sum(1 for x in rows if x["covered"])
    return {"exerciseCount":len(rows),"coveredCount":covered,"gapCount":len(rows)-covered,
            "coveragePct":round((covered/max(1,len(rows)))*100,1),"exercises":rows}
