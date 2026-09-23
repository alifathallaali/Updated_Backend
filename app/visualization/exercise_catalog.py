"""Presentation metadata derived from the canonical Exercise Manifest."""
from __future__ import annotations
from copy import deepcopy
from ..engines.exercise_manifest import EXERCISE_MANIFESTS
from .exercise_profiles import resolve_profile
from .layout_templates import get_family_layout

EXERCISE_CATALOG = {
    m.id: {
        "name": m.name, "family": m.family, "kpis": list(m.kpis),
        "table": m.table, "report_section": m.report_section,
        "manifest_chart_patterns": list(m.chart_patterns),
        "personas": list(m.personas),
    }
    for m in EXERCISE_MANIFESTS
}

PLANNED_FAMILY_TEMPLATES = {
    "heor": {"family": "market_access", "table": "heor_decision_matrix", "report_section": "HEOR & value evidence"},
    "market_access": {"family": "market_access", "table": "access_barriers", "report_section": "Market access"},
    "tender_procurement": {"family": "supply", "table": "tender_pipeline", "report_section": "Tender & procurement"},
    "hospital_supply_chain": {"family": "supply", "table": "supply_risk", "report_section": "Hospital supply chain"},
    "quality": {"family": "quality", "table": "quality_events", "report_section": "Quality intelligence"},
    "medical_affairs": {"family": "medical", "table": "medical_evidence", "report_section": "Medical affairs"},
    "med_rep_planner": {"family": "sales", "table": "activity_plan", "report_section": "Field execution"},
    "category_management": {"family": "market", "table": "category_performance", "report_section": "Category management"},
    "commercial_finance": {"family": "finance", "table": "financial_variance", "report_section": "Commercial finance"},
}


def get_exercise_presentation(exercise_id: str, *, name: str = "", domain: str = "") -> dict:
    if exercise_id in EXERCISE_CATALOG:
        item=deepcopy(EXERCISE_CATALOG[exercise_id])
        _, profile=resolve_profile(exercise_id,name=item["name"],domain=domain)
    else:
        family,profile=resolve_profile(exercise_id,name=name,domain=domain)
        item={"name":name or exercise_id,"family":family,"kpis":[],"table":"generic_evidence","report_section":"Analysis","manifest_chart_patterns":[],"personas":[]}
    item["exercise_id"]=exercise_id
    item["chart_patterns"]=item.get("manifest_chart_patterns") or list(profile["patterns"])
    item.pop("manifest_chart_patterns",None)
    item["semantic_role"]=profile["role"]
    item["layout"] = get_family_layout(item["family"])
    return item

def list_exercise_presentations() -> list[dict]:
    return [get_exercise_presentation(key) for key in sorted(EXERCISE_CATALOG)]
