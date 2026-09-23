"""Deterministic chart prioritization for exercise presentation.

Prioritization changes display order only. It never changes chart data or analytics.
"""
from __future__ import annotations

FAMILY_PRIORITIES = {
 "forecast": ("forecast-output","forecast","actual","trend","growth"),
 "scenario": ("scenario-value","scenario","comparison","incremental"),
 "finance": ("variance","waterfall","finance","budget","achievement","trend"),
 "sales": ("achievement","ranking","coverage","sales","review"),
 "inventory": ("risk","cover","stock","inventory"),
 "supply": ("coverage","supply","demand","units","trend"),
 "launch": ("launch-success","risk","score","launch","trend"),
 "market": ("market-trend","share","ranking","market"),
 "company": ("company-kpis","company","ranking","trend"),
 "molecule": ("molecule-kpis","molecule","ranking","trend"),
 "product": ("product-kpis","trend","ranking","product"),
 "market_access": ("opportunity","access","priority","barrier"),
 "medical": ("trend","evidence","engagement"),
 "quality": ("risk","trend","quality","capa"),
 "generic": ("trend","ranking","comparison"),
}

def _haystack(chart:dict)->str:
 meta=chart.get("meta") or {}
 series=" ".join(str(x.get("label",""))+" "+str(x.get("role","")) for x in chart.get("series") or [])
 return " ".join([str(chart.get("chartId","")),str(chart.get("chartType","")),str(meta.get("title","")),str(meta.get("description","")),series]).lower()

def chart_priority_score(chart:dict,family:str,patterns:list[str]|None=None)->float:
 text=_haystack(chart)
 family_prefs=list(FAMILY_PRIORITIES.get(family,FAMILY_PRIORITIES["generic"]))
 score=0.0
 # Family-specific semantics are authoritative for the primary visual.
 for i,term in enumerate(family_prefs):
  words=str(term).lower().replace("_"," ").split()
  if all(w in text for w in words):
   score=max(score,120-(i*6))
 # Manifest patterns refine/tie-break; they must not override family semantics.
 for i,term in enumerate(patterns or []):
  words=str(term).lower().replace("_"," ").split()
  if all(w in text for w in words):
   score=max(score,80-(i*4))
 score += {"line":3,"area":3,"bar":2,"waterfall":4,"scatter":1}.get(str(chart.get("chartType","")).lower(),0)
 return score

def prioritize_charts(charts:list[dict],family:str,patterns:list[str]|None=None)->list[dict]:
 scored=[]
 for index,chart in enumerate(charts):
  item=dict(chart)
  score=chart_priority_score(item,family,patterns)
  item["presentationPriority"]={"score":round(score,1),"originalIndex":index}
  scored.append((score,-index,item))
 scored.sort(key=lambda x:(x[0],x[1]),reverse=True)
 ordered=[x[2] for x in scored]
 for i,item in enumerate(ordered):
  item["presentationPriority"]["rank"]=i+1
  item["presentationPriority"]["role"]="primary" if i==0 else "diagnostic"
 return ordered
