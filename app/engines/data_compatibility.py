"""Pre-flight dataset compatibility checks for PharmaLens exercises."""
from __future__ import annotations
from typing import Iterable
from .exercise_manifest import get_exercise_manifest

ALIASES = {
    "category": {"category","market_category","consumer_health_category","category_name","therapeutic_class"},
    "subcategory": {"subcategory","sub_category","segment","subsegment"},
    "sku": {"sku","sku_code","item_code","product_code","ean","barcode","product","product_name"},
    "pack": {"pack","pack_size","packsize","size","package_size","presentation"},
    "channel": {"channel","distribution_channel","sales_channel","trade_channel"},
    "retailer": {"retailer","retail_chain","chain","customer_name","account_name","outlet"},
    "price": {"price","selling_price","retail_price","unit_price","net_price","list_price"},
    "period": {"period","period_month","month","year","date"},
    "sales_value": {"sales_value","value","lc_value","selling_value"},
    "sales_units": {"sales_units","units","quantity","qty"},
    "manufacturer": {"manufacturer","manufacturer_name","corporation","company"},
    "active_ingredient": {"active_ingredient","molecule","generic_name"},
    "product": {"product","brand","brand_name","product_name"},
    "brand": {"brand","brand_name","product","product_name"},
    "territory": {"territory","region","area","brick"},
    "sales_rep": {"sales_rep","representative","rep","employee"},
    "hcp": {"hcp","hcp_name","doctor","customer","account"},
    "hco": {"hco","hco_name","hospital","clinic","account_name"},
    "calls": {"calls","call_count","visits","visit_count","actual_calls"},
    "target": {"target","target_value","sales_target","quota"},
    "actual": {"actual","actual_value","sales_value","achievement_value"},
    "potential": {"potential","potential_score","customer_potential","hcp_potential","account_potential"},
    "planned_calls": {"planned_calls","planned_visits","call_plan"},
    "required_frequency": {"required_frequency","target_frequency","planned_frequency"},
    "capacity": {"capacity","call_capacity","visit_capacity"},
    "consumption_quantity": {"consumption_quantity","consumption_qty","quantity_consumed","qty_used","issued_quantity","usage_quantity","demand"},
    "inventory_on_hand": {"inventory_on_hand","stock_on_hand","available_stock","on_hand_quantity"},
    "lead_time_days": {"lead_time_days","supplier_lead_time_days","lead_time"},
    "open_po_quantity": {"open_po_quantity","open_po_qty","outstanding_po_quantity"},
    "contract_covered_quantity": {"contract_covered_quantity","contract_covered_qty","contract_quantity_remaining"},
    "expected_unit_cost": {"expected_unit_cost","unit_cost","purchase_price"},
    "budget": {"budget","procurement_budget"},
    "supplier": {"supplier","supplier_name","vendor","vendor_name"},
}
def _norm(value:str)->str:
    return str(value).strip().lower().replace(" ","_").replace("-","_")

def compatible_columns(required: Iterable[str], available: Iterable[str]) -> dict:
    available_norm={_norm(c):str(c) for c in available}
    matched={}; missing=[]
    for req in required:
        candidates={_norm(req), *{_norm(x) for x in ALIASES.get(_norm(req),set())}}
        hit=next((available_norm[c] for c in candidates if c in available_norm),None)
        if hit: matched[req]=hit
        else: missing.append(req)
    return {"matched":matched,"missing":missing}

def assess_exercise_compatibility(exercise_id:str, available_columns:list[str], *, dataset_status:str="ready")->dict:
    manifest=get_exercise_manifest(exercise_id)
    if not manifest:
        return {"exerciseId":exercise_id,"state":"blocked","ready":False,"reason":"Unknown exercise.","matched":{},"missingRequired":[],"missingOptional":[],"availableColumns":available_columns}
    required=compatible_columns(manifest.required_inputs,available_columns)
    optional=compatible_columns(manifest.optional_inputs,available_columns)
    if dataset_status!="ready":
        state="blocked"; reason="Dataset must complete mapping and quality validation first."
    elif required["missing"]:
        state="missing_data"; reason="Required fields are missing."
    elif optional["missing"] and manifest.readiness=="additional_inputs":
        state="partial"; reason="Core fields are present, but this exercise needs additional evidence for full analysis."
    else:
        state="ready"; reason="Dataset satisfies the declared exercise inputs."
    return {
        "exerciseId":exercise_id,"exerciseName":manifest.name,"state":state,"ready":state=="ready",
        "canRun":state in {"ready","partial"},"reason":reason,
        "matched":required["matched"],"missingRequired":required["missing"],
        "matchedOptional":optional["matched"],"missingOptional":optional["missing"],
        "availableColumns":available_columns,"readiness":manifest.readiness,
    }
