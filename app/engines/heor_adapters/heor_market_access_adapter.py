"""Canonical backend adapter for HEOR & Market Access (product-18)."""
from __future__ import annotations
from typing import Any
from ..commercial_adapters.contracts import build_adapter_output, build_incomplete_output
from src.engines.heor_market_access.heor_decision_engine import run_heor_market_access_decision


def _evidence(field:str,value:Any,source:str)->dict:
    return {"field":field,"value":value,"source":source}


def run_heor_market_access_adapter(rows:list[dict], input_:dict)->dict:
    # HEOR economic inputs are decision parameters, not inferred from sales rows.
    # Product Run carries them in filters.heor to preserve the existing API schema.
    filters=(input_ or {}).get("filters") or {}
    payload=(input_ or {}).get("heor") or filters.get("heor") or {}
    required=("product","comparator")
    missing=[key for key in required if not payload.get(key)]
    readiness={
        "status":"READY" if not missing else "MISSING_FIELDS",
        "required_fields":list(required),"missing_fields":missing,
        "available_fields":sorted(payload.keys()),
        "governed_row_count":len(rows),
    }
    if missing:
        out=build_incomplete_output("HEOR & Market Access Decision Engine",readiness,
            provenance={"engine":"src.engines.heor_market_access.heor_decision_engine","input_source":"product_run.filters.heor"})
        out["warnings"].append("Clinical/economic parameters are never inferred from commercial sales rows.")
        out["confidence"]["rationale"]="HEOR execution requires explicit governed clinical/economic assumptions."
        return out
    try:
        result=run_heor_market_access_decision(**payload)
    except (ValueError,KeyError,TypeError) as exc:
        out=build_adapter_output("error",f"HEOR calculation could not be completed: {exc}",{},[],[str(exc)],readiness,
            provenance={"engine":"src.engines.heor_market_access.heor_decision_engine"})
        out["confidence"]["rationale"]="HEOR execution failed input or calculation validation."
        return out

    econ=result.get("economic_evaluation") or {}
    bia=result.get("budget_impact") or {}
    patient=result.get("patient_flow") or {}
    access=result.get("market_access") or {}
    metrics={
        "incremental_cost":econ.get("incremental_cost"),"incremental_effect":econ.get("incremental_effect"),
        "icer":econ.get("icer"),"incremental_nmb":econ.get("incremental_nmb"),
        "dominance":econ.get("dominance"),
    }
    if bia:metrics.update({"cumulative_budget_impact":bia.get("cumulative_budget_impact"),"discounted_cumulative_budget_impact":bia.get("discounted_cumulative_budget_impact")})
    if patient:metrics.update({"disease_population":patient.get("Disease_Population"),"diagnosed_patients":patient.get("Diagnosed_Patients"),"treated_patients":patient.get("Treated_Patients")})
    if access:metrics.update({"access_barrier":access.get("barrier"),"access_adjusted_value":access.get("access_adjusted_value")})
    evidence=[
        _evidence("heor.incremental_cost",econ.get("incremental_cost"),"deterministic: intervention cost - comparator cost"),
        _evidence("heor.incremental_effect",econ.get("incremental_effect"),"deterministic: intervention effect - comparator effect"),
        _evidence("heor.icer",econ.get("icer"),"deterministic: incremental cost / incremental effect"),
    ]
    if econ.get("willingness_to_pay") is not None:evidence.append(_evidence("heor.incremental_nmb",econ.get("incremental_nmb"),"deterministic NMB at supplied willingness-to-pay"))
    if bia:evidence.append(_evidence("heor.cumulative_budget_impact",bia.get("cumulative_budget_impact"),"deterministic multi-year budget impact"))
    warnings=list(dict.fromkeys([*(result.get("decision_context") or {}).get("warnings",[]),*(result.get("decision_context") or {}).get("evidence_gaps",[])]))
    status="success" if result.get("status")=="success" else "partial"
    out=build_adapter_output(status,
        f"HEOR assessment completed for {result['product'].get('name','Product')} versus {result['comparator'].get('name','Comparator')}.",
        metrics,evidence,warnings,readiness,
        provenance={"engine":"src.engines.heor_market_access.heor_decision_engine","input_source":"governed_product_run_parameters","raw_rows_used_for_economic_assumptions":False},
        extra_payload={"heor":result})
    out["confidence"]["rationale"]="Deterministic HEOR calculations use explicit supplied assumptions and governed PharmaLens engine dependencies."
    return out
