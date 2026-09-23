"""Minimal Hospital Procurement calculations.

This module deliberately implements only procurement primitives that are not
already supplied by PharmaLens Forecasting, Scenario, Market Access, HEOR or
Commercial Finance engines.
"""
from __future__ import annotations
from math import ceil, sqrt
from statistics import pstdev
from typing import Any


def _num(row: dict, *keys: str) -> float | None:
    for key in keys:
        value=row.get(key)
        if value is None or value=="": continue
        try: return float(value)
        except (TypeError,ValueError): continue
    return None


def _text(row: dict,*keys:str)->str:
    for key in keys:
        value=row.get(key)
        if value is not None and str(value).strip(): return str(value).strip()
    return "Unknown"


def safety_stock(daily_demand_std:float, lead_time_days:float, service_z:float=1.65)->float:
    if min(daily_demand_std,lead_time_days,service_z)<0: raise ValueError("Safety-stock inputs cannot be negative")
    return service_z*daily_demand_std*sqrt(lead_time_days)


def reorder_point(avg_daily_demand:float, lead_time_days:float, safety_stock_qty:float)->float:
    if min(avg_daily_demand,lead_time_days,safety_stock_qty)<0: raise ValueError("Reorder-point inputs cannot be negative")
    return avg_daily_demand*lead_time_days+safety_stock_qty


def net_procurement_requirement(forecast_qty:float,safety_stock_qty:float,stock_on_hand:float,open_po_qty:float=0,contract_covered_qty:float=0)->float:
    if min(forecast_qty,safety_stock_qty,stock_on_hand,open_po_qty,contract_covered_qty)<0: raise ValueError("Procurement quantities cannot be negative")
    return max(0.0,forecast_qty+safety_stock_qty-stock_on_hand-open_po_qty-contract_covered_qty)


def constrained_order_qty(requirement:float,moq:float=0,pack_size:float=1)->float:
    if requirement<0 or moq<0 or pack_size<=0: raise ValueError("Invalid order constraints")
    return ceil(max(requirement,moq)/pack_size)*pack_size if requirement>0 else 0.0


def buyer_tender_comparison(offers:list[dict],weights:dict[str,float])->list[dict]:
    """Transparent hospital buyer comparison; never chooses weights or an award."""
    if not offers: return []
    if not weights or sum(weights.values())<=0 or any(v<0 for v in weights.values()): raise ValueError("Positive hospital-supplied tender weights are required")
    total=sum(weights.values()); out=[]
    for offer in offers:
        components={}; score=0.0
        for criterion,weight in weights.items():
            raw=_num(offer,criterion)
            if raw is None: components[criterion]=None; continue
            normalized=max(0.0,min(100.0,raw))
            contribution=normalized*(weight/total); components[criterion]=round(contribution,4); score+=contribution
        out.append({"supplier":_text(offer,"supplier","supplier_name","vendor"),"weighted_score":round(score,2),"components":components})
    return sorted(out,key=lambda x:x["weighted_score"],reverse=True)


def supplier_kpis(rows:list[dict])->list[dict]:
    groups:dict[str,list[dict]]={}
    for row in rows:
        supplier=_text(row,"supplier","supplier_name","vendor")
        if supplier!="Unknown": groups.setdefault(supplier,[]).append(row)
    result=[]
    for supplier,items in groups.items():
        ordered=sum(_num(r,"ordered_quantity","ordered_qty","po_quantity") or 0 for r in items)
        received=sum(_num(r,"received_quantity","received_qty","delivered_quantity") or 0 for r in items)
        on_time=[]; lead=[]
        for r in items:
            promised=_num(r,"promised_lead_time_days")
            actual=_num(r,"actual_lead_time_days","lead_time_days")
            if actual is not None: lead.append(actual)
            if promised is not None and actual is not None: on_time.append(actual<=promised)
        result.append({"supplier":supplier,"orders":len(items),"fill_rate_pct":round(received/ordered*100,2) if ordered>0 else None,
                       "otif_pct":round(sum(on_time)/len(on_time)*100,2) if on_time else None,
                       "avg_lead_time_days":round(sum(lead)/len(lead),2) if lead else None})
    return result


def analyze_hospital_procurement(rows:list[dict],params:dict|None=None)->dict[str,Any]:
    params=params or {}; warnings=[]; evidence=[]; items=[]
    service_z=float(params.get("service_z",1.65)); default_pack=float(params.get("pack_size",1) or 1); default_moq=float(params.get("moq",0) or 0)
    for row in rows:
        product=_text(row,"product","product_name","brand_name","sku","item_code")
        demand=_num(row,"consumption_quantity","consumption_qty","quantity_consumed","demand","sales_units","units")
        stock=_num(row,"inventory_on_hand","stock_on_hand","available_stock","inventory")
        lead=_num(row,"lead_time_days")
        open_po=_num(row,"open_po_quantity","open_po_qty") or 0.0
        contract=_num(row,"contract_covered_quantity","contract_covered_qty") or 0.0
        forecast=_num(row,"forecast_quantity","forecast_qty")
        forecast=forecast if forecast is not None else demand
        unit_cost=_num(row,"expected_unit_cost","unit_cost","price","retail_price")
        budget=_num(row,"budget","procurement_budget")
        if demand is None: continue
        avg_daily=max(0.0,demand)/30.44
        std=_num(row,"daily_demand_std")
        ss=safety_stock(std,lead,service_z) if std is not None and lead is not None else 0.0
        rop=reorder_point(avg_daily,lead,ss) if lead is not None else None
        cover=(stock/avg_daily) if stock is not None and avg_daily>0 else None
        requirement=net_procurement_requirement(max(0.0,forecast or 0),ss,max(0.0,stock or 0),max(0.0,open_po),max(0.0,contract)) if stock is not None else None
        order=constrained_order_qty(requirement,float(_num(row,"moq") or default_moq),float(_num(row,"pack_size") or default_pack)) if requirement is not None else None
        spend=order*unit_cost if order is not None and unit_cost is not None else None
        gap=spend-budget if spend is not None and budget is not None else None
        shortage=bool(cover is not None and lead is not None and cover<lead) or bool(rop is not None and stock is not None and stock<rop)
        items.append({"product":product,"consumption_quantity":demand,"forecast_quantity":forecast,"stock_on_hand":stock,"stock_cover_days":cover,
                      "lead_time_days":lead,"safety_stock":ss if std is not None and lead is not None else None,"reorder_point":rop,
                      "open_po_quantity":open_po,"contract_covered_quantity":contract,"net_procurement_requirement":requirement,
                      "recommended_order_quantity":order,"projected_procurement_spend":spend,"budget_gap":gap,"shortage_risk":shortage})
    if not items: warnings.append("No governed consumption/demand quantity was available; procurement calculations were not fabricated.")
    if items and all(x["stock_on_hand"] is None for x in items): warnings.append("Inventory/stock-on-hand is missing; net procurement requirement and stock-out exposure are incomplete.")
    if items and all(x["lead_time_days"] is None for x in items): warnings.append("Lead time is missing; reorder-point and lead-time shortage evidence are incomplete.")
    if items and all(x["projected_procurement_spend"] is None for x in items): warnings.append("Unit cost is missing; procurement budget impact is not calculated.")
    for x in items[:25]:
        evidence.append({"field":"hospital_procurement.item","value":x,"source":"governed_dataset + deterministic procurement primitives"})
    return {"items":items,"supplier_kpis":supplier_kpis(rows),"warnings":warnings,"evidence":evidence}
