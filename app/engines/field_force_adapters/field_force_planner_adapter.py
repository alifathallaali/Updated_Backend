"""Canonical Product-13 Field Force Planner.

Thin deterministic orchestration over governed PharmaLens data. It does not
implement CRM, scheduling, route optimization, or duplicate target/forecast/
recommendation/scenario/finance engines.
"""
from __future__ import annotations
from collections import defaultdict
from typing import Any
import pandas as pd

from .grounding import present_keys, first_value, number
from ..commercial_adapters.contracts import build_adapter_output, build_incomplete_output
from ..commercial_adapters.recommendation_adapter import run_recommendation_adapter
from ..commercial_adapters.commercial_finance_adapter import run_commercial_finance_adapter
from ..strategy_engines import run_forecasting, run_scenario_planning
from src.engines.target_planning.target_engine import (
    company_target, build_region_opportunity, top_down, bottom_up, iterative_reconcile,
)


def _sum(rows, keys):
    vals=[number(first_value(r,keys)) for r in rows]
    return sum(v for v in vals if v is not None)

def _has(rows, logical): return bool(present_keys(rows,logical))

def _readiness(rows):
    available=sorted({k for r in rows for k in r})
    required=["territory","sales_rep"]
    missing=[x for x in required if not _has(rows,x)]
    return {"status":"READY" if not missing else "MISSING_FIELDS","required_fields":required,
            "missing_fields":missing,"available_fields":available,"governed_row_count":len(rows)}

def _activity_by_customer(rows):
    hcp_keys=present_keys(rows,"hcp"); call_keys=present_keys(rows,"calls")
    out=defaultdict(float)
    if not hcp_keys or not call_keys: return out
    for r in rows:
        h=str(first_value(r,hcp_keys) or "").strip()
        c=number(first_value(r,call_keys))
        if h and c is not None: out[h]+=c
    return out

def _priority_queue(rows):
    hcp_keys=present_keys(rows,"hcp"); hco_keys=present_keys(rows,"hco"); pot_keys=present_keys(rows,"potential")
    target_keys=present_keys(rows,"target"); actual_keys=present_keys(rows,"actual"); call_keys=present_keys(rows,"calls")
    if not (hcp_keys or hco_keys): return []
    grouped={}
    for r in rows:
        label=str(first_value(r,hcp_keys) or first_value(r,hco_keys) or "").strip()
        if not label: continue
        g=grouped.setdefault(label,{"customer":label,"potential":None,"target":0.0,"actual":0.0,"calls":0.0})
        p=number(first_value(r,pot_keys)) if pot_keys else None
        if p is not None: g["potential"]=max(g["potential"] if g["potential"] is not None else p,p)
        for name,keys in (("target",target_keys),("actual",actual_keys),("calls",call_keys)):
            if keys:
                v=number(first_value(r,keys)); g[name]+=v or 0.0
    potentials=[g["potential"] for g in grouped.values() if g["potential"] is not None]
    maxp=max(potentials) if potentials else None
    for g in grouped.values():
        score=0.0; reasons=[]
        if maxp and g["potential"] is not None:
            score += 50*(g["potential"]/maxp); reasons.append("observed potential")
        if g["target"]>0:
            gap=max(0.0,g["target"]-g["actual"]); score += 35*min(1.0,gap/g["target"])
            if gap>0: reasons.append("target gap")
        if call_keys and g["calls"]<=0:
            score+=15; reasons.append("no observed calls")
        g["priority_score"]=round(score,2); g["reasons"]=reasons
    return sorted(grouped.values(),key=lambda x:(x["priority_score"],x["target"]-x["actual"]),reverse=True)[:20]

def _target_reuse(rows, params):
    cfg=params.get("target_planning") or {}
    if not cfg: return None, []
    required={"base_year","target_year"}
    if not required.issubset(cfg): return None,["Smart Target Planning requested but base_year and target_year were not both supplied."]
    # Reuse only with the canonical sales fields expected by the existing target engine.
    converted=[]
    for r in rows:
        year=first_value(r,present_keys(rows,"period"))
        try: year=int(str(year)[:4])
        except (TypeError,ValueError): continue
        units=number(r.get("sales_units") if "sales_units" in r else r.get("units"))
        value=number(first_value(r,present_keys(rows,"actual")))
        if units is None or value is None: continue
        converted.append({"Year":year,"Sales Units":units,"Sales Value":value,
                          "Brand Name":str(first_value(r,present_keys(rows,"product")) or "Unknown"),
                          "Therapeutic Class":str(r.get("therapeutic_class") or "Unknown")})
    if not converted: return None,["Smart Target Planning was not run because governed Year, Sales Units and Sales Value evidence was incomplete."]
    sales=pd.DataFrame(converted)
    ct=company_target(sales,int(cfg["base_year"]),int(cfg["target_year"]),growth_rate=float(cfg.get("growth_rate",0.10)))
    region_rows=cfg.get("region_opportunity_rows") or []
    payload={"company_target":ct,"methodology":"reuse: src.engines.target_planning.target_engine"}
    if region_rows:
        opp=build_region_opportunity(pd.DataFrame(region_rows))
        td=top_down(ct,opp,float(cfg.get("damping",0.70)))
        bu=bottom_up(td); rec=iterative_reconcile(ct,td)
        payload.update({"top_down":td.to_dict(orient="records"),"bottom_up":{"target_units":bu["target_units"],"target_value":bu["target_value"]},"iterative":rec.to_dict(orient="records")})
    return payload,[]

def run_field_force_planner_adapter(rows:list[dict], input_:dict)->dict:
    readiness=_readiness(rows)
    if readiness["status"]!="READY":
        out=build_incomplete_output("Product-13 Field Force Planner",readiness,{"engine":"app.engines.field_force_adapters"})
        out["warnings"].append("No rep, territory, HCP, activity, target, potential, or sales values are fabricated when absent.")
        out["confidence"]["rationale"]="Field Force Planner requires governed territory and representative identifiers before rep/FLM conclusions are produced."
        return out

    warnings=[]; evidence=[]; metrics={"territories":len({str(first_value(r,present_keys(rows,"territory"))) for r in rows}),
                                      "sales_reps":len({str(first_value(r,present_keys(rows,"sales_rep"))) for r in rows}),"observed_records":len(rows)}
    target_keys=present_keys(rows,"target"); actual_keys=present_keys(rows,"actual")
    if target_keys and actual_keys:
        target=_sum(rows,target_keys); actual=_sum(rows,actual_keys); metrics.update({"target":target,"actual":actual,"variance":actual-target,"achievement_pct":round(actual/target*100,2) if target else None})
        evidence += [{"field":"field_force.target","value":target,"source":"governed_dataset"},{"field":"field_force.actual","value":actual,"source":"governed_dataset"}]
    else: warnings.append("Target-vs-actual omitted because governed target and actual evidence were not both available.")

    hcp_keys=present_keys(rows,"hcp"); calls=_activity_by_customer(rows)
    if hcp_keys and present_keys(rows,"calls"):
        universe={str(first_value(r,hcp_keys)).strip() for r in rows if first_value(r,hcp_keys)}; reached={h for h,c in calls.items() if c>0}
        metrics.update({"hcp_universe":len(universe),"hcp_reached":len(reached),"reach_pct":round(len(reached)/len(universe)*100,2) if universe else None,"average_frequency":round(sum(calls.values())/len(reached),2) if reached else 0.0})
        evidence.append({"field":"field_force.reach","value":len(reached),"source":"governed HCP + call activity"})
    else: warnings.append("Reach and observed visit frequency require governed HCP/account and call/activity fields.")

    req_keys=present_keys(rows,"required_frequency")
    if hcp_keys and req_keys and present_keys(rows,"calls"):
        required={}
        for r in rows:
            h=str(first_value(r,hcp_keys) or "").strip(); f=number(first_value(r,req_keys))
            if h and f is not None: required[h]=max(required.get(h,0),f)
        eligible=[h for h,f in required.items() if f>0]; compliant=[h for h in eligible if calls.get(h,0)>=required[h]]
        metrics["frequency_compliance_pct"]=round(len(compliant)/len(eligible)*100,2) if eligible else None
    else: warnings.append("Frequency compliance omitted because required/planned frequency evidence was not available.")

    planned_keys=present_keys(rows,"planned_calls"); call_keys=present_keys(rows,"calls")
    if planned_keys and call_keys:
        planned=_sum(rows,planned_keys); actual_calls=_sum(rows,call_keys); metrics.update({"planned_calls":planned,"actual_calls":actual_calls,"plan_adherence_pct":round(actual_calls/planned*100,2) if planned else None})
    else: warnings.append("Plan-vs-actual call adherence requires both planned and actual call fields.")

    capacity_keys=present_keys(rows,"capacity")
    if capacity_keys and planned_keys:
        cap=_sum(rows,capacity_keys); planned=_sum(rows,planned_keys); metrics.update({"call_capacity":cap,"planned_workload":planned,"capacity_utilization_pct":round(planned/cap*100,2) if cap else None})
    else: warnings.append("Workload/capacity metrics omitted because explicit capacity evidence was not supplied.")

    priority=_priority_queue(rows)
    if not priority: warnings.append("Customer priority queue omitted because no governed HCP/HCO/account identifiers were available.")
    elif not present_keys(rows,"potential"): warnings.append("Priority queue has no potential/value component because customer potential evidence was not supplied.")

    params=((input_ or {}).get("filters") or {}).get("field_force") or (input_ or {}).get("field_force") or {}
    target_reuse,target_warnings=_target_reuse(rows,params); warnings.extend(target_warnings)
    reused=[]; reuse={}
    if target_reuse: reuse["smart_target_planning"]=target_reuse; reused.append("src.engines.target_planning.target_engine")
    if _has(rows,"period") and any(k in readiness["available_fields"] for k in ("sales_units","units")):
        reuse["forecast"]=run_forecasting(rows,input_); reused.append("app.engines.strategy_engines.run_forecasting")
    if _has(rows,"product") and _has(rows,"period") and _has(rows,"actual"):
        reuse["recommendation"]=run_recommendation_adapter(rows,input_); reused.append("app.engines.commercial_adapters.run_recommendation_adapter")
    if params.get("include_scenario") and _has(rows,"period") and _has(rows,"actual"):
        reuse["scenario"]=run_scenario_planning(rows,input_); reused.append("app.engines.strategy_engines.run_scenario_planning")
    if params.get("include_finance") and _has(rows,"period") and _has(rows,"actual"):
        reuse["commercial_finance"]=run_commercial_finance_adapter(rows,input_); reused.append("app.engines.commercial_adapters.run_commercial_finance_adapter")

    manager_review={"off_track": metrics.get("achievement_pct") is not None and metrics["achievement_pct"]<100,
                    "coverage_gap_pct": round(100-metrics["reach_pct"],2) if metrics.get("reach_pct") is not None else None,
                    "top_priorities":priority[:5],"warnings":warnings[:8]}
    planning={"monthly_focus":priority[:10],"weekly_priorities":priority[:7],"daily_priority_queue":priority[:5]}
    out=build_adapter_output("partial" if warnings else "success","Product-13 Field Force Planner calculated governed performance, coverage and execution priorities without CRM or scheduling behavior.",metrics,evidence,warnings,readiness,
        provenance={"engine":"app.engines.field_force_adapters.field_force_planner_adapter","reused_engines":reused,"raw_rows_sent_to_llm":False},
        extra_payload={"field_force":{"priorities":priority,"planning":planning,"manager_review":manager_review,"reused_outputs":reuse,"missing_inputs":warnings}})
    out["confidence"]["rationale"]="Deterministic SFE metrics use only governed supplied evidence; unavailable target, activity, potential, frequency and capacity inputs remain explicit warnings."
    return out
