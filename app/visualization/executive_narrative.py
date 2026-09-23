"""Grounded executive narrative cards for exercise results.

Narrative is derived only from existing result summary, metrics, evidence, warnings,
confidence and next-exercise metadata. It does not invent causal explanations.
"""
from __future__ import annotations

def _text(value)->str:
    return str(value).strip() if value is not None else ""

def _metric_highlights(metrics:dict,limit:int=3)->list[str]:
    out=[]
    for key,value in (metrics or {}).items():
        if key in {"readiness_state","notebook_logic_scope"}: continue
        if isinstance(value,(int,float,str)) and _text(value):
            out.append(f"{key.replace('_',' ').title()}: {value}")
        if len(out)>=limit: break
    return out

def build_executive_narrative(result:dict,next_exercises:list[dict]|None=None)->dict:
    summary=_text(result.get("summary"))
    metrics=result.get("metrics") or {}
    evidence=result.get("evidence") or []
    warnings=[_text(x) for x in (result.get("warnings") or []) if _text(x)]
    confidence=result.get("confidence") or {}
    metric_lines=_metric_highlights(metrics)
    evidence_lines=[]
    for e in evidence[:3]:
        if isinstance(e,dict):
            label=_text(e.get("label") or e.get("metric") or e.get("name") or e.get("type"))
            value=_text(e.get("value") or e.get("detail") or e.get("description"))
            line=": ".join(x for x in [label,value] if x)
            if line:evidence_lines.append(line)
        elif _text(e): evidence_lines.append(_text(e))
    confidence_text=_text(confidence.get("rationale") or confidence.get("level") or confidence.get("score"))
    next_items=next_exercises or []
    return {
        "whatHappened": summary or ("; ".join(metric_lines) if metric_lines else "No concise result summary is available."),
        "whyItMatters": "Review the quantified result in the context of the stated exercise objective and available evidence. No causal claim is inferred beyond the engine output.",
        "evidence": evidence_lines or metric_lines or ["No additional evidence items were produced for this run."],
        "watchouts": warnings[:3] or ([confidence_text] if confidence_text else ["No additional presentation watchout was reported."]),
        "nextAnalysis": [{"exerciseId":x.get("exerciseId"),"name":x.get("name"),"reason":"Related next analysis in the declared exercise journey."} for x in next_items[:3]],
        "grounding":{"causalInferenceAdded":False,"sourceFields":["summary","metrics","evidence","warnings","confidence","next_exercises"]},
    }
