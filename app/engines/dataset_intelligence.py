"""Unknown Dataset Intelligence.

Uses schema/column metadata and governed profile only. It does not send raw rows
to an LLM. Suggestions are compatibility hints, not fabricated analytics.
"""
from __future__ import annotations
from .data_compatibility import ALIASES, _norm, assess_exercise_compatibility
from .exercise_manifest import EXERCISE_MANIFESTS

SEMANTIC_ROLES = {
    "time": {"period","period_month","month","year","date","week","quarter"},
    "value": {"sales_value","value","revenue","lc_value","amount"},
    "volume": {"sales_units","units","quantity","qty","volume"},
    "product": {"product","product_name","brand","brand_name","sku"},
    "company": {"manufacturer","manufacturer_name","company","corporation"},
    "molecule": {"active_ingredient","molecule","generic_name"},
    "geography": {"territory","region","area","brick","city","country"},
    "person": {"sales_rep","representative","rep","hcp","doctor","employee"},
    "price": {"price","selling_price","unit_price"},
    "inventory": {"inventory","inventory_on_hand","stock","stock_on_hand","available_stock"},
    "procurement": {"consumption_quantity","consumption_qty","quantity_consumed","open_po_quantity","ordered_quantity","received_quantity","supplier","vendor","lead_time_days","contract_covered_quantity"},
    "target": {"target","budget","plan"},
}

def infer_column_roles(columns:list[str]) -> list[dict]:
    result=[]
    for original in columns:
        n=_norm(original)
        roles=[role for role,names in SEMANTIC_ROLES.items() if n in {_norm(x) for x in names}]
        canonical=[]
        for key, aliases in ALIASES.items():
            if n in {_norm(key), *{_norm(x) for x in aliases}}:
                canonical.append(key)
        result.append({"column":original,"normalized":n,"roles":roles or ["unknown"],"canonicalCandidates":sorted(set(canonical))})
    return result

def _score_suggestion(exercise_id:str, columns:list[str]) -> dict:
    assessment=assess_exercise_compatibility(exercise_id,columns,dataset_status="ready")
    manifest=next(m for m in EXERCISE_MANIFESTS if m.id==exercise_id)
    req=max(1,len(manifest.required_inputs))
    matched=len(assessment.get("matched",{}))
    optional_total=len(manifest.optional_inputs)
    optional_matched=len(assessment.get("matchedOptional",{}))
    score=(matched/req)*80 + ((optional_matched/optional_total)*20 if optional_total else 20)
    if assessment["state"]=="missing_data": score=min(score,79)
    if assessment["state"]=="partial": score=min(score,89)
    return {
        "exerciseId":exercise_id,"name":manifest.name,"domain":manifest.domain,"family":manifest.family,
        "score":round(score,1),"state":assessment["state"],"matched":assessment["matched"],
        "missingRequired":assessment["missingRequired"],"missingOptional":assessment["missingOptional"],
        "reason":assessment["reason"],
    }

def inspect_unknown_dataset(columns:list[str], *, profile:dict|None=None, top_n:int=6) -> dict:
    roles=infer_column_roles(columns)
    suggestions=sorted((_score_suggestion(m.id,columns) for m in EXERCISE_MANIFESTS),
                       key=lambda x:(x["score"],x["state"]=="ready"),reverse=True)[:top_n]
    role_counts={}
    for col in roles:
        for role in col["roles"]:
            role_counts[role]=role_counts.get(role,0)+1
    known=sum(1 for c in roles if c["roles"]!=["unknown"])
    confidence=round(known/max(1,len(columns)),2)
    likely=[]
    if role_counts.get("time") and (role_counts.get("value") or role_counts.get("volume")): likely.append("time_series_commercial")
    if role_counts.get("product"): likely.append("product_or_brand_level")
    if role_counts.get("company"): likely.append("manufacturer_or_company_level")
    if role_counts.get("geography"): likely.append("territory_or_geographic")
    if role_counts.get("inventory"): likely.append("inventory_or_supply")
    if role_counts.get("procurement"): likely.append("hospital_procurement")
    if role_counts.get("person"): likely.append("field_force_or_hcp")
    return {
        "columnCount":len(columns),"columns":roles,"roleCounts":role_counts,
        "likelyDatasetTypes":likely or ["unclassified"],"schemaConfidence":confidence,
        "suggestedExercises":suggestions,
        "needsUserClarification":confidence < 0.45 or not any(x["state"] in {"ready","partial"} for x in suggestions),
        "clarificationPrompt":"What decision or analysis do you want to make with this dataset?",
        "privacy":{"rawRowsSentToLLM":False,"basis":"column names, canonical aliases and governed profile metadata only"},
        "profileSummary":{k:v for k,v in (profile or {}).items() if k in {"rowCount","columnCount","missingness","dateRange"}},
    }
