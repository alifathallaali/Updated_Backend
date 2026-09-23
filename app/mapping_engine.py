"""Smart, reviewable mapping from uploaded columns to PharmaLens canonical fields."""
import re
from difflib import SequenceMatcher

UNIFIED_FIELDS: dict[str,list[str]]={
 "product_name":["product","product name","product_name","drug name","sku name"],
 "brand_name":["brand","brand name","brand_name","trade name"],
 "molecule":["molecule","active ingredient","generic name","inn"],
 "corporation":["corporation","manufacturer","manufacturer name","company","company name"],
 "therapeutic_class":["therapeutic class","therapy class","atc4","class"],
 "pack":["pack","pack size","package","pack_size"],
 "strength":["strength","drug strength","dose strength"],
 "sales_value":["sales value","sales","lc value","selling value","value","revenue","net sales"],
 "sales_units":["units","sales units","quantity","qty","volume"],
 "retail_price":["retail price","selling price","unit price","price"],
 "currency":["currency","currency code","iso currency"],
 "period":["period","month","calendar month","period month","mat month","yyyymm"],
 "calendar_year":["year","calendar year","fiscal year"],
 "country":["country","country name","market"],
 "region":["region","province","governorate"],
 "territory_name":["territory","area","district","brick"],
 "hcp_name":["doctor","physician","hcp","hcp name","prescriber"],
 "hco_name":["hospital","clinic","hco","facility","hco name","account"],
 "disease":["disease","indication","condition"],
 "population":["population","total population","patients"],
 "date":["date","transaction date","visit date","sales date"],
 "consumption_quantity":["consumption quantity","consumption qty","quantity consumed","qty used","issued quantity","usage quantity","demand"],
 "inventory_on_hand":["inventory on hand","stock on hand","available stock","on hand quantity"],
 "lead_time_days":["lead time days","supplier lead time days","lead time"],
 "open_po_quantity":["open po quantity","open po qty","outstanding po quantity"],
 "contract_covered_quantity":["contract covered quantity","contract covered qty","contract quantity remaining"],
 "expected_unit_cost":["expected unit cost","unit cost","purchase price"],
 "budget":["procurement budget","budget"],
 "supplier":["supplier","supplier name","vendor","vendor name"],
 "ordered_quantity":["ordered quantity","ordered qty","po quantity"],
 "received_quantity":["received quantity","received qty","delivered quantity"],
}
def _normalize(v:str)->str:
 return re.sub(r"[^a-z0-9]+"," ",str(v).strip().lower()).strip()
def _similarity(a:str,b:str)->float:
 if a==b:return 1.0
 at=set(a.split());bt=set(b.split())
 token=(len(at&bt)/len(at|bt)) if at and bt else 0
 seq=SequenceMatcher(None,a,b).ratio()
 containment=0.92 if (a in b or b in a) and min(len(a),len(b))>=4 else 0
 return max(seq,token,containment)
def _band(score:float)->str:
 return "high" if score>=0.9 else "medium" if score>=0.75 else "low"
def suggest_mapping(columns:list[str])->dict:
 """One source column can map to only one canonical field automatically."""
 candidates=[]
 for field,aliases in UNIFIED_FIELDS.items():
  for col in columns:
   n=_normalize(col)
   scores=[(_similarity(_normalize(a),n),a) for a in [field.replace("_"," "),*aliases]]
   score,alias=max(scores,key=lambda x:x[0])
   if score>=0.6:candidates.append((score,field,col,alias))
 candidates.sort(reverse=True)
 used_fields=set();used_cols=set();suggestions={}
 for score,field,col,alias in candidates:
  if field in used_fields or col in used_cols:continue
  competing=[x for x in candidates if x[2]==col and x[1]!=field]
  second=max([x[0] for x in competing],default=0)
  ambiguous=score<0.8 or (score-second)<0.08
  suggestions[field]={"column":col,"confidence":round(score,2),"confidenceBand":_band(score),
                      "matchedAlias":alias,"requiresConfirmation":ambiguous}
  used_fields.add(field);used_cols.add(col)
 unmatched=[c for c in columns if c not in used_cols]
 review=[f for f,s in suggestions.items() if s["requiresConfirmation"]]
 warnings=[]
 if not any(f in suggestions for f in ("sales_value","sales_units")):
  warnings.append("No sales value or units field was detected; quantitative analysis may be limited.")
 if review:warnings.append("Review suggested mappings before confirmation: "+", ".join(review)+".")
 return {"suggestions":suggestions,"unmatchedColumns":unmatched,
         "coverage":round(len(suggestions)/max(1,len(UNIFIED_FIELDS)),3),
         "reviewRequired":review,"warnings":warnings,
         "policy":{"autoAcceptConfidence":0.9,"oneSourceColumnPerCanonicalField":True}}
def apply_confirmed_mapping(rows:list[dict],mapping:dict[str,str])->list[dict]:
 result=[]
 for row in rows:
  mapped={field:row.get(source) for field,source in mapping.items()}
  if row.get("source_sheet") is not None:mapped["source_sheet"]=row["source_sheet"]
  result.append(mapped)
 return result
