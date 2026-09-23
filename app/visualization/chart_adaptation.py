"""Responsive/data-shape presentation adaptation for ChartSpec copies."""
from __future__ import annotations

def adapt_chart(chart:dict)->dict:
    item=dict(chart); data=list(item.get("data") or []); typ=str(item.get("chartType","")).lower()
    meta=dict(item.get("meta") or {}); xkey=item.get("xKey")
    adaptation={"topNApplied":False,"orientation":"vertical","mobile":"scroll","labelStrategy":"default"}
    # Ranking/category visuals: cap visual clutter, preserving full analytics elsewhere.
    if typ in {"bar","pie","treemap"} and len(data)>15:
        data=data[:15]; item["data"]=data; adaptation["topNApplied"]=True; adaptation["topN"]=15
        meta["description"]=(str(meta.get("description") or "")+" Showing top 15 categories for readability.").strip()
    labels=[str(r.get(xkey,"")) for r in data] if xkey else []
    if typ=="bar" and labels and (max(map(len,labels))>18 or len(labels)>10):
        adaptation["orientation"]="horizontal"; adaptation["labelStrategy"]="long_labels"
    if len(data)>8:
        adaptation["mobile"]="horizontal_scroll"
    elif len(data)<=5:
        adaptation["mobile"]="compact"
    item["meta"]=meta; item["presentationAdaptation"]=adaptation
    return item

def adapt_charts(charts:list[dict])->list[dict]:
    return [adapt_chart(c) for c in charts]
