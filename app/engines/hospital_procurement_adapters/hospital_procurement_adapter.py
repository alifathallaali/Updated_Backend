"""Canonical Product Run adapter for Hospital Procurement Intelligence (product-19)."""
from __future__ import annotations
import pandas as pd
from ..commercial_adapters.contracts import build_adapter_output, build_incomplete_output
from src.engines.hospital_procurement.procurement import analyze_hospital_procurement, buyer_tender_comparison
from src.engines.commercial_finance.commercial_finance import price_volume_analysis
from src.engines.market_access.market_access import tender_opportunity_score


def run_hospital_procurement_adapter(rows:list[dict],input_:dict)->dict:
    available=sorted({k for row in rows for k in row})
    demand_keys={"consumption_quantity","consumption_qty","quantity_consumed","demand","sales_units","units"}
    missing=[] if demand_keys & set(available) else ["consumption_quantity"]
    readiness={"status":"READY" if not missing else "MISSING_FIELDS","required_fields":["consumption_quantity"],"missing_fields":missing,"available_fields":available,"governed_row_count":len(rows)}
    if missing:
        out=build_incomplete_output("Hospital Procurement Intelligence",readiness,{"engine":"src.engines.hospital_procurement.procurement"})
        out["warnings"].append("Purchase-order quantity is never substituted for hospital consumption.")
        out["confidence"]["rationale"]="Hospital procurement execution requires governed consumption/demand evidence; PO quantity is not a substitute."
        return out
    filters=(input_ or {}).get("filters") or {}; params=filters.get("hospital_procurement") or (input_ or {}).get("hospital_procurement") or {}
    result=analyze_hospital_procurement(rows,params)
    items=result["items"]
    req=[x["net_procurement_requirement"] for x in items if x["net_procurement_requirement"] is not None]
    spend=[x["projected_procurement_spend"] for x in items if x["projected_procurement_spend"] is not None]
    gaps=[x["budget_gap"] for x in items if x["budget_gap"] is not None]
    metrics={"items_analyzed":len(items),"total_consumption_quantity":sum(float(x["consumption_quantity"] or 0) for x in items),
             "shortage_risk_items":sum(1 for x in items if x["shortage_risk"]),"supplier_count":len(result["supplier_kpis"])}
    if req: metrics["net_procurement_requirement"]=sum(req)
    if spend: metrics["projected_procurement_spend"]=sum(spend)
    if gaps: metrics["budget_gap"]=sum(gaps)
    # Reuse Commercial Finance price-volume methodology when explicit scenario inputs are supplied.
    finance_reuse=None
    pv=params.get("price_volume_scenario")
    if pv:
        finance_reuse=price_volume_analysis(float(pv["base_price"]),float(pv["base_volume"]),float(pv["new_price"]),float(pv["new_volume"]))
        metrics["scenario_total_variance"]=finance_reuse["total_variance"]
    # Reuse Market Access tender opportunity only when its governed score inputs are explicitly supplied.
    tender_opportunity=None
    tender_rows=params.get("tender_opportunity_rows") or []
    if tender_rows:
        tender_opportunity=tender_opportunity_score(pd.DataFrame(tender_rows)).to_dict(orient="records")
    buyer_tender=None
    if params.get("tender_offers") and params.get("tender_weights"):
        buyer_tender=buyer_tender_comparison(params["tender_offers"],params["tender_weights"])
    evidence=list(result["evidence"])
    if finance_reuse: evidence.append({"field":"hospital_procurement.price_volume_scenario","value":finance_reuse,"source":"reuse: src.engines.commercial_finance.price_volume_analysis"})
    if tender_opportunity: evidence.append({"field":"hospital_procurement.tender_opportunity","value":tender_opportunity,"source":"reuse: src.engines.market_access.tender_opportunity_score"})
    warnings=list(result["warnings"])
    out=build_adapter_output("partial" if warnings else "success","Hospital procurement analysis calculated from governed demand, stock, PO, contract and cost evidence.",metrics,evidence,warnings,readiness,
        provenance={"engine":"src.engines.hospital_procurement.procurement","reused_engines":["commercial_finance.price_volume_analysis","market_access.tender_opportunity_score"],"raw_rows_sent_to_llm":False},
        extra_payload={"hospital_procurement":{"items":items,"supplier_kpis":result["supplier_kpis"],"buyer_tender_comparison":buyer_tender,"tender_opportunity":tender_opportunity,"finance_scenario":finance_reuse}})
    out["confidence"]["rationale"]="Deterministic procurement calculations use only governed fields; missing operational inputs remain explicit warnings."
    return out
