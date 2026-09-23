"""Evidence-gated Category Management primitives for Consumer Health MVP."""
from __future__ import annotations
from collections import defaultdict
from statistics import median
from typing import Any
from .grounding import resolve_column


def _num(row:dict,key:str|None)->float:
    if not key:return 0.0
    try:return float(row.get(key) or 0)
    except (TypeError,ValueError):return 0.0

def _text(row:dict,key:str|None)->str:
    if not key:return "Unknown"
    value=row.get(key)
    return str(value).strip() if value is not None and str(value).strip() else "Unknown"

def _group(rows,label_key,sales_key,units_key=None):
    out=defaultdict(lambda:{"sales_value":0.0,"sales_units":0.0,"records":0})
    for r in rows:
        label=_text(r,label_key); d=out[label]; d["sales_value"]+=_num(r,sales_key); d["sales_units"]+=_num(r,units_key); d["records"]+=1
    return out

def calculate_category_management(rows:list[dict[str,Any]])->dict[str,Any]:
    columns=list(rows[0].keys()) if rows else []
    sales=resolve_column(columns,"sales_value") or next((c for c in columns if c.lower() in {"sales_value","value","lc_value"}),None)
    units=resolve_column(columns,"sales_units") or next((c for c in columns if c.lower() in {"sales_units","units","quantity","qty"}),None)
    category=resolve_column(columns,"category"); subcategory=resolve_column(columns,"subcategory")
    sku=resolve_column(columns,"sku"); pack=resolve_column(columns,"pack"); channel=resolve_column(columns,"channel")
    retailer=resolve_column(columns,"retailer"); price=resolve_column(columns,"price"); distribution=resolve_column(columns,"distribution")
    promotion=resolve_column(columns,"promotion"); consumer=resolve_column(columns,"consumer_segment"); ecommerce=resolve_column(columns,"ecommerce")
    period=next((c for c in columns if c.lower() in {"period","period_month","month","year","date"}),None)
    warnings=[]; evidence=[]; metrics={}; details={}
    total=sum(_num(r,sales) for r in rows) if sales else 0.0
    if not sales: warnings.append("Contribution and market-share outputs omitted: governed sales-value evidence is missing.")
    if category and sales:
        groups=_group(rows,category,sales,units); ranked=sorted(groups.items(),key=lambda x:x[1]["sales_value"],reverse=True)
        details["category_contribution"]=[{"category":k,**v,"contribution_pct":(v["sales_value"]/total*100 if total else 0)} for k,v in ranked]
        metrics["categories_analyzed"]=len(groups)
        evidence.append({"field":"category_contribution","value":len(groups),"source":"governed_dataset","method":"grouped sales contribution"})
    else: warnings.append("Category contribution unavailable: category and sales-value evidence are required.")
    if subcategory and sales:
        groups=_group(rows,subcategory,sales,units); details["subcategory_contribution"]=[{"subcategory":k,**v,"contribution_pct":(v["sales_value"]/total*100 if total else 0)} for k,v in sorted(groups.items(),key=lambda x:x[1]["sales_value"],reverse=True)]
    if sku and sales:
        groups=_group(rows,sku,sales,units); ranked=sorted(groups.items(),key=lambda x:x[1]["sales_value"],reverse=True)
        details["sku_contribution"]=[{"sku":k,**v,"contribution_pct":(v["sales_value"]/total*100 if total else 0)} for k,v in ranked]
        metrics["skus_analyzed"]=len(groups)
    else: warnings.append("SKU contribution unavailable: SKU and sales-value evidence are required.")
    if sku and sales and distribution:
        productivity=[]
        for name,data in _group(rows,sku,sales,units).items():
            denom=sum(_num(r,distribution) for r in rows if _text(r,sku)==name)
            productivity.append({"sku":name,"sales_value":data["sales_value"],"distribution_denominator":denom,"sku_productivity":data["sales_value"]/denom if denom>0 else None})
        details["sku_productivity"]=productivity
    else: warnings.append("SKU productivity omitted: a governed distribution/outlet denominator is required.")
    if sku and retailer:
        assortment=defaultdict(set)
        for r in rows: assortment[_text(r,retailer)].add(_text(r,sku))
        details["assortment"]=[{"retailer":k,"sku_count":len(v)} for k,v in sorted(assortment.items())]
    elif sku and channel:
        assortment=defaultdict(set)
        for r in rows: assortment[_text(r,channel)].add(_text(r,sku))
        details["assortment"]=[{"channel":k,"sku_count":len(v)} for k,v in sorted(assortment.items())]
    else: warnings.append("Assortment analysis omitted: SKU plus retailer or channel evidence is required.")
    if price:
        values=sorted(_num(r,price) for r in rows if _num(r,price)>0)
        if values:
            med=median(values); low=med*0.8; high=med*1.2
            counts={"value":0,"mainstream":0,"premium":0}
            for v in values: counts["value" if v<low else "premium" if v>high else "mainstream"]+=1
            metrics.update({"median_price":med,"price_observations":len(values)})
            details["price_architecture"]={"method":"dataset-relative median bands","value_below":low,"mainstream_range":[low,high],"premium_above":high,"counts":counts}
            evidence.append({"field":"price_architecture","value":med,"source":"governed_dataset","method":"median price with ±20% descriptive bands"})
        else:warnings.append("Price architecture omitted: no positive governed price observations were available.")
    else:warnings.append("Price architecture omitted: governed price evidence is missing.")
    if channel and sales:
        groups=_group(rows,channel,sales,units); details["channel_mix"]=[{"channel":k,**v,"share_pct":(v["sales_value"]/total*100 if total else 0)} for k,v in sorted(groups.items(),key=lambda x:x[1]["sales_value"],reverse=True)]
    else:warnings.append("Channel mix omitted: channel and sales-value evidence are required.")
    if distribution and sku:
        gaps=[]
        for name,data in _group(rows,sku,sales,units).items():
            vals=[_num(r,distribution) for r in rows if _text(r,sku)==name and _num(r,distribution)>0]
            if vals:gaps.append({"sku":name,"observed_distribution":sum(vals)/len(vals)})
        if gaps:
            benchmark=max(x["observed_distribution"] for x in gaps)
            for x in gaps:x["gap_to_observed_leader"]=benchmark-x["observed_distribution"]
            details["distribution_gaps"]=gaps
        else:warnings.append("Distribution-gap analysis omitted: no positive governed distribution observations were available.")
    else:warnings.append("Distribution-gap analysis omitted: distribution evidence is required.")
    if promotion is None:warnings.append("Promotion effectiveness omitted: promotion evidence is missing.")
    else: details["promotion_evidence_available"]=True
    if ecommerce is None and not (channel and any("online" in _text(r,channel).lower() or "ecommerce" in _text(r,channel).lower() for r in rows)):
        warnings.append("E-commerce performance omitted: e-commerce evidence is missing.")
    if consumer is None:warnings.append("Consumer insights omitted: governed consumer/segment evidence is missing.")
    if sku and sales:
        sku_rows=details.get("sku_contribution",[]); contribs=[x["contribution_pct"] for x in sku_rows]
        threshold=median(contribs) if contribs else 0
        candidates=[]
        for x in sku_rows:
            if x["contribution_pct"]<threshold:
                candidates.append({"sku":x["sku"],"status":"review_candidate","reason":"Below-median observed sales contribution; requires commercial review and additional evidence before any action."})
        details["rationalization_candidates"]=candidates
        metrics["rationalization_review_candidates"]=len(candidates)
    if period and sku and sales:
        by_sku_period=defaultdict(lambda:defaultdict(float))
        for r in rows: by_sku_period[_text(r,sku)][_text(r,period)]+=_num(r,sales)
        matrix=[]
        for name,vals in by_sku_period.items():
            ordered=sorted(vals.items()); first=ordered[0][1] if ordered else 0; last=ordered[-1][1] if ordered else 0
            growth=((last/first)-1)*100 if first>0 and len(ordered)>1 else None
            sales_total=sum(vals.values()); matrix.append({"sku":name,"share_pct":sales_total/total*100 if total else None,"growth_pct":growth})
        details["share_growth_matrix"]=matrix
    else:warnings.append("Share-growth matrix omitted: period, SKU and governed sales evidence are required.")
    metrics["historical_observations_only"]=True
    return {"metrics":metrics,"details":details,"evidence":evidence,"warnings":list(dict.fromkeys(warnings))}
