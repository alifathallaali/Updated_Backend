"""Goal-to-exercise routing for governed datasets.

The resolver never calculates business metrics. It ranks already-governed
exercise capabilities against a user's stated goal and dataset compatibility.
"""
from __future__ import annotations
import re
from .dataset_intelligence import inspect_unknown_dataset
from .exercise_manifest import EXERCISE_MANIFESTS

INTENT_TERMS = {
    "understand": {"understand","analyze","analyse","performance","why","decline","growth","compare","achievement","consumer health","category","subcategory","sku","assortment","price band","retailer","otc","supplement","vitamin","cosmetic","beauty","personal care","wellness"},
    "predict": {"forecast","predict","demand","future","projection","trend"},
    "plan": {"target","plan","budget","brand","reorder","production","procurement","purchase order","stock","inventory","supplier","tender","shortage","field force","med rep","call plan","coverage","frequency","territory","hcp"},
    "decide": {"recommend","opportunity","prioritize","choose","scenario","risk","heor","icer","qaly","cost effectiveness","cost-effectiveness","budget impact","mcda","hta","market access"},
    "execute": {"report","ppt","pptx","pdf","presentation","export"},
}

def _intent(goal: str) -> tuple[str,float]:
    text=re.sub(r"\s+"," ",(goal or "").lower()).strip()
    if not text: return "discover",0.0
    scores={k:sum(1 for term in terms if term in text) for k,terms in INTENT_TERMS.items()}
    best=max(scores,key=scores.get)
    return (best,min(1.0,0.55+0.15*scores[best])) if scores[best] else ("custom",0.25)

def resolve_dataset_goal(columns:list[str], goal:str, *, profile:dict|None=None, persona:str|None=None, top_n:int=5)->dict:
    intelligence=inspect_unknown_dataset(columns,profile=profile,top_n=max(top_n,len(EXERCISE_MANIFESTS)))
    intent,confidence=_intent(goal)
    # Compatibility remains the hard gate. Goal matching only re-orders compatible suggestions.
    goal_tokens=set(re.findall(r"[a-z0-9]+",(goal or "").lower()))
    ranked=[]
    for item in intelligence["suggestedExercises"]:
        manifest=next((m for m in EXERCISE_MANIFESTS if m.id==item["exerciseId"]),None)
        tag_text=" ".join(manifest.tags) if manifest else ""
        hay=set(re.findall(r"[a-z0-9]+",f'{item["name"]} {item["domain"]} {item["family"]} {tag_text}'.lower()))
        lexical=len(goal_tokens & hay)
        persona_match=bool(persona and manifest and persona in manifest.personas)
        readiness={"ready":30,"partial":15,"missing_data":0}.get(item["state"],-20)
        heor_terms={"heor","icer","qaly","qalys","mcda","hta"}
        heor_phrase=any(term in (goal or "").lower() for term in ("cost effectiveness","cost-effectiveness","budget impact","health economics"))
        heor_boost=100 if item["exerciseId"]=="product-18" and (goal_tokens & heor_terms or heor_phrase) else 0
        procurement_terms={"procurement","supplier","vendor","stock","inventory","reorder","tender","shortage","hospital"}
        procurement_boost=100 if item["exerciseId"]=="product-19" and (goal_tokens & procurement_terms or "purchase order" in (goal or "").lower()) else 0
        field_force_terms={"rep","representative","territory","hcp","hco","coverage","frequency","calls","visits","achievement","field","force"}
        field_force_phrase=any(term in (goal or "").lower() for term in ("med rep","field force","call plan","frequency compliance","sales force"))
        field_force_boost=100 if item["exerciseId"]=="product-13" and (goal_tokens & field_force_terms or field_force_phrase) else 0
        consumer_terms={"consumer","health","category","subcategory","sku","assortment","retailer","otc","supplement","supplements","vitamin","vitamins","cosmetic","cosmetics","beauty","wellness"}
        consumer_phrase=any(term in (goal or "").lower() for term in ("consumer health","personal care","price band","category management"))
        consumer_boost=100 if item["exerciseId"]=="product-20" and (goal_tokens & consumer_terms or consumer_phrase) else 0
        item={**item,"personaMatch":persona_match,"goalScore":round(item["score"]+readiness+min(20,lexical*5)+(8 if persona_match else 0)+heor_boost+procurement_boost+field_force_boost+consumer_boost,1)}
        ranked.append(item)
    ranked.sort(key=lambda x:x["goalScore"],reverse=True)
    best=next((x for x in ranked if x["state"] in {"ready","partial"}),None)
    return {
        "goal":goal,"persona":persona,"intent":intent,"intentConfidence":round(confidence,2),
        "recommendedExercise":best,"alternatives":ranked[:top_n],
        "requiresUserClarification":best is None or intent in {"discover","custom"},
        "clarificationPrompt":"What decision or analysis do you want to make with this dataset?" if not goal.strip() else None,
        "trust":{
            "routingStatus":"calculated",
            "source":"governed_dataset_schema",
            "method":"exercise_manifest_compatibility_plus_goal_and_persona_match",
            "rawRowsSentToLLM":False,
            "limitations":["Routing selects an analysis capability; it does not itself calculate business results."]
        },
        "datasetIntelligence":intelligence,
    }
