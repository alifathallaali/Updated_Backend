"""Thin Consumer Health adapter composing canonical PharmaLens analytics."""
from __future__ import annotations
from typing import Any
from ..analytics_engines import run_market_intelligence, run_company_intelligence, run_product_performance
from ..strategy_engines import run_forecasting, run_launch_success, run_scenario_planning, run_portfolio_strategy
from ..commercial_adapters import run_recommendation_adapter, run_commercial_finance_adapter
from .category_management import calculate_category_management
from .grounding import grounding_map
from .._helpers import build_output


def run_consumer_health_adapter(rows:list[dict], input_:dict[str,Any])->dict:
    if not rows:
        return build_output("product-20","Consumer Health Intelligence requires governed canonical data.",{},[],["No governed rows were supplied."])
    columns=list(rows[0].keys()); grounding=grounding_map(columns)
    category=calculate_category_management(rows)
    market=run_market_intelligence(rows,input_)
    company=run_company_intelligence(rows,input_)
    product=run_product_performance(rows,input_)
    # Reuse engines only when their declared required evidence exists; keep outputs as nested reusable intelligence.
    reused={"market":market,"company":company,"product":product}
    if any(c in columns for c in ("period","month","year","date")) and any(c in columns for c in ("sales_units","units","quantity","qty")):
        reused["forecast"]=run_forecasting(rows,input_)
    if any(c in columns for c in ("product_launch","launch_date")):
        reused["launch"]=run_launch_success(rows,input_)
    if any(c in columns for c in ("period","month","year","date")):
        reused["scenario"]=run_scenario_planning(rows,input_)
        reused["portfolio"]=run_portfolio_strategy(rows,input_)
        reused["recommendation"]=run_recommendation_adapter(rows,input_)
        reused["commercial_finance"]=run_commercial_finance_adapter(rows,input_)
    warnings=list(category["warnings"])
    if not grounding.get("category"):warnings.append("Consumer Health category is not explicitly mapped; category-specific interpretation is limited.")
    metrics={**category["metrics"],"grounded_semantics":sorted(grounding),"reused_capabilities":sorted(reused)}
    evidence=[*category["evidence"],{"field":"canonical_reuse","value":sorted(reused),"source":"canonical_pharmalens_engines"}]
    out=build_output("product-20","Consumer Health intelligence composed from canonical PharmaLens engines plus evidence-gated Category Management primitives.",metrics,evidence,warnings)
    out["categoryManagement"]=category["details"]
    out["reusedIntelligence"]={k:{"status":v.get("status"),"metrics":v.get("metrics",{}),"warnings":v.get("warnings",[])} for k,v in reused.items()}
    out["grounding"]={"mapped":grounding,"availableColumns":columns}
    out["governance"]={"marketShare":"Only from governed sales denominators in the attached dataset.","distribution":"Only when distribution evidence exists.","ecommerce":"Only when e-commerce/channel evidence exists.","promotion":"No effectiveness claim without promotion evidence.","consumerInsights":"No consumer inference without governed consumer evidence.","rationalization":"Review candidates only; never automatic deletion.","forecastLabeling":"Nested forecast/scenario outputs remain distinct from historical observations."}
    return out
