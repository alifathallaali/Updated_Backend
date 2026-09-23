"""Canonical HEOR & Market Access orchestrator.

Reuses existing PharmaLens scenario/patient-flow, market-access and commercial-
finance capabilities instead of duplicating them. Advanced PSA and payer/country
submission frameworks are intentionally outside MVP scope.
"""
from __future__ import annotations
from typing import Any, Mapping, Optional, Sequence
import pandas as pd

from .heor import economic_evaluation
from .budget_impact import multi_year_budget_impact
from .mcda import run_mcda, weight_sensitivity
from src.engines.scenario_planning.scenario import calculate_patient_flow, run_patient_flow_scenarios
from src.engines.market_access.market_access import price_access_tradeoff, classify_access_barrier
from src.engines.commercial_finance.commercial_finance import gtn_net_price, price_volume_analysis


def _records(df: pd.DataFrame) -> list[dict]:
    return df.where(pd.notna(df), None).to_dict(orient="records")


def _pricing_scenarios(scenarios: Sequence[Mapping[str, Any]]) -> list[dict]:
    rows=[]
    for item in scenarios:
        price=float(item["price"])
        volume=float(item["expected_volume"])
        access_pct=float(item["access_probability_pct"])
        units=float(item.get("units", volume))
        gross_sales=price*volume
        gtn=float(item.get("gtn_rate",0.0))
        finance=gtn_net_price(gross_sales,units,gtn)
        access_value=price_access_tradeoff(price,volume,access_pct)
        row={
            "scenario":str(item.get("name","Scenario")),
            "price":price,"expected_volume":volume,"access_probability_pct":access_pct,
            "access_adjusted_value":access_value,"gtn_rate":gtn,
            "net_sales":finance["net_sales"],"net_price":finance["net_price"],
        }
        if item.get("base_price") is not None and item.get("base_volume") is not None:
            row["price_volume_analysis"]=price_volume_analysis(
                float(item["base_price"]),float(item["base_volume"]),price,volume
            )
        rows.append(row)
    return rows


def run_heor_market_access_decision(
    *, product: Mapping[str, Any], comparator: Mapping[str, Any],
    economic_method: str="CUA", willingness_to_pay: Optional[float]=None,
    perspective: Optional[str]=None, time_horizon_years: Optional[float]=None,
    currency: Optional[str]=None, assumptions: Optional[Mapping[str, Any]]=None,
    patient_population: Optional[Mapping[str, Any]]=None,
    patient_scenarios: Optional[Mapping[str, Mapping[str,float]]]=None,
    budget_impact: Optional[Mapping[str, Any]]=None,
    pricing_scenarios: Optional[Sequence[Mapping[str, Any]]]=None,
    market_access: Optional[Mapping[str, Any]]=None,
    mcda: Optional[Mapping[str, Any]]=None,
) -> dict:
    warnings=[]; gaps=[]
    econ=economic_evaluation(
        {"cost":product["cost"],"effect":product["effect"]},
        {"cost":comparator["cost"],"effect":comparator["effect"]},
        method=economic_method,willingness_to_pay=willingness_to_pay,
        intervention_name=str(product.get("name","Product")),
        comparator_name=str(comparator.get("name","Comparator")),
        perspective=perspective,time_horizon_years=time_horizon_years,
        currency=currency,assumptions=assumptions,
    )
    warnings.extend(econ.get("warnings",[]))

    patient_out=None; patient_scenario_out=None
    if patient_population:
        required={"population","prevalence_rate","diagnosis_rate","treatment_rate"}
        missing=required-set(patient_population)
        if missing:gaps.append(f"Patient flow not run; missing: {sorted(missing)}")
        else:
            patient_out=calculate_patient_flow(**{k:patient_population[k] for k in required})
            if patient_scenarios:
                baseline={k:patient_population[k] for k in required}
                patient_scenario_out=_records(run_patient_flow_scenarios(baseline,scenarios=patient_scenarios))

    bia_out=None
    if budget_impact:
        payload=dict(budget_impact)
        if payload.get("eligible_patients") is None and patient_out is not None:
            payload["eligible_patients"]=patient_out["Treated_Patients"]
        required={"eligible_patients","uptake_rates","intervention_cost_per_patient","comparator_cost_per_patient"}
        missing=required-set(payload)
        if missing:gaps.append(f"Budget impact not run; missing: {sorted(missing)}")
        else:bia_out=multi_year_budget_impact(**payload)

    pricing_out=_pricing_scenarios(pricing_scenarios) if pricing_scenarios else None

    access_out=None
    if market_access:
        access_out={"barrier":classify_access_barrier(
            market_access.get("formulary_status","unknown"),
            market_access.get("procurement_status"),
            bool(market_access.get("competitor_contract",False)),
            bool(market_access.get("price_barrier",False)),
        )}
        if all(k in market_access for k in ("price","expected_volume","access_probability_pct")):
            access_out["access_adjusted_value"]=price_access_tradeoff(
                market_access["price"],market_access["expected_volume"],market_access["access_probability_pct"]
            )

    mcda_out=None
    if mcda:
        alternatives=mcda.get("alternatives"); criteria=mcda.get("criteria")
        if alternatives is None or not criteria:gaps.append("MCDA not run; alternatives and criteria are required.")
        else:
            frame=alternatives.copy() if isinstance(alternatives,pd.DataFrame) else pd.DataFrame(alternatives)
            run=run_mcda(frame,criteria,mcda.get("weights"),mcda.get("directions"),method=mcda.get("method","TOPSIS"),id_column=mcda.get("id_column"),missing_policy=mcda.get("missing_policy","median"))
            mcda_out={"method":run["method"],"criteria":run["criteria"],"weights":run["weights"],"directions":run["directions"],"results":_records(run["results"])}
            if mcda.get("sensitivity",False):
                sensitivity=weight_sensitivity(frame,criteria,run["weights"],run["directions"],method=run["method"],id_column=mcda.get("id_column"),variation_pct=float(mcda.get("variation_pct",.20)),steps=int(mcda.get("steps",5)),missing_policy=mcda.get("missing_policy","median"))
                mcda_out["sensitivity"]=_records(sensitivity)

    return {
        "status":"success" if not gaps else "partial","product":dict(product),"comparator":dict(comparator),
        "economic_evaluation":econ,"patient_flow":patient_out,"patient_scenarios":patient_scenario_out,
        "budget_impact":bia_out,"pricing_access":pricing_out,"market_access":access_out,"mcda":mcda_out,
        "decision_context":{"warnings":warnings,"evidence_gaps":gaps,"reused_capabilities":[
            "scenario_planning.calculate_patient_flow","scenario_planning.run_patient_flow_scenarios",
            "market_access.price_access_tradeoff","market_access.classify_access_barrier",
            "commercial_finance.gtn_net_price","commercial_finance.price_volume_analysis"],
            "interpretation_rule":"Quantified trade-offs support, but do not replace, decision-maker judgment."}
    }
