"""UI/Copilot-ready projection of canonical exercise results."""
from __future__ import annotations
from typing import Any
from .schemas import CanonicalResult, ExerciseRun
from .orchestrator import CompositeRun

_SECTION_ORDER=("summary","kpis","visualizations","findings","drivers","risks","opportunities","recommendations","actions","quality","lineage")

def _section(section_id,title,items,visible=None):
    if visible is None: visible=bool(items) or section_id in {"summary","quality","lineage"}
    return {"id":section_id,"title":title,"visible":visible,"items":items}

def _result_sections(result: CanonicalResult):
    s={
      "summary":_section("summary","Executive Summary",[{"text":result.executive_summary}]),
      "kpis":_section("kpis","Key Metrics",result.metrics),
      "visualizations":_section("visualizations","Visualizations",result.visualization_specs),
      "findings":_section("findings","Key Findings",result.key_findings),
      "drivers":_section("drivers","Drivers",result.drivers),
      "risks":_section("risks","Risks",result.risks),
      "opportunities":_section("opportunities","Opportunities",result.opportunities),
      "recommendations":_section("recommendations","Recommendations",result.recommendations),
      "actions":_section("actions","Actions",result.actions),
      "quality":_section("quality","Quality",[result.data_quality]),
      "lineage":_section("lineage","Lineage",[result.lineage]),
    }
    return [s[k] for k in _SECTION_ORDER]

def _copilot_context(exercise_id,run_id,status,quality_status,result,**extra):
    p={"exercise_id":exercise_id,"run_id":run_id,"status":status,"quality_status":quality_status,
       "executive_summary":result.executive_summary if result else None,"metrics":result.metrics if result else [],
       "findings":result.key_findings if result else [],"risks":result.risks if result else [],
       "opportunities":result.opportunities if result else [],"recommendations":result.recommendations if result else [],
       "assumptions":result.assumptions if result else [],"data_quality":result.data_quality if result else {},
       "lineage":result.lineage if result else {},"evidence_only":True}
    p.update(extra); return p

def exercise_workspace_payload(run: ExerciseRun):
    r=run.result
    return {"contract":"pharmalens.exercise_workspace.v1","kind":"exercise","id":run.exercise_id,"version":run.exercise_version,
      "run_id":run.run_id,"status":run.status.value,"quality_status":run.quality_status.value,
      "context":{"market":run.market,"parameters":run.parameters,"data_snapshot":run.data_snapshot},
      "sections":_result_sections(r) if r else [],"limitations":list((r.data_quality or {}).get("warnings",[])) if r else [],
      "copilot_context":_copilot_context(run.exercise_id,run.run_id,run.status.value,run.quality_status.value,r)}

def composite_workspace_payload(run: CompositeRun):
    r=run.result
    refs=[{"exercise_id":eid,"run_id":c.run_id,"status":c.status.value,"quality_status":c.quality_status.value,"exercise_version":c.exercise_version} for eid,c in run.child_runs.items()]
    limitations=list(r.data_quality.get("optional_unavailable",[])) if r else []
    if run.conflicts: limitations.append("Conflicting evidence requires review.")
    return {"contract":"pharmalens.exercise_workspace.v1","kind":"composite","id":run.composite_id,"version":run.composite_version,
      "run_id":run.run_id,"status":run.status.value,"quality_status":run.quality_status.value,"child_runs":refs,"conflicts":run.conflicts,
      "sections":_result_sections(r) if r else [],"limitations":limitations,
      "copilot_context":_copilot_context(run.composite_id,run.run_id,run.status.value,run.quality_status.value,r,child_runs=refs,conflicts=run.conflicts)}
