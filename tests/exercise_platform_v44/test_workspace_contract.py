from src.exercises.workspace import exercise_workspace_payload, composite_workspace_payload
from src.exercises.schemas import CanonicalResult, ExerciseRun
from src.exercises.orchestrator import CompositeRun
from src.exercises.types import ExerciseStatus, QualityStatus

def _child(eid="MKT-003"):
 r=CanonicalResult(executive_summary="Validated market evidence.",metrics=[{"id":"share","value":12.0,"unit":"%"}],key_findings=[{"id":"f1","statement":"Share observed."}],data_quality={"status":"PASS"},lineage={"source":"canonical_data"},metadata={"raw_rows":[{"secret":"must-not-leak"}]})
 return ExerciseRun("run-1",eid,"1.0",ExerciseStatus.COMPLETED,QualityStatus.PASS,"2026-09-22T00:00:00Z","u1","o1","Egypt","snap-1",{"mi":"1"},{},result=r)

def test_exercise_workspace_is_metadata_driven_and_copilot_safe():
 p=exercise_workspace_payload(_child()); assert p["contract"]=="pharmalens.exercise_workspace.v1"; assert p["kind"]=="exercise"
 assert [s["id"] for s in p["sections"]][:4]==["summary","kpis","visualizations","findings"]
 assert p["copilot_context"]["evidence_only"] is True; assert "metadata" not in p["copilot_context"]; assert "raw_rows" not in str(p["copilot_context"])

def test_composite_workspace_exposes_child_refs_not_raw_child_results():
 c=_child(); r=CanonicalResult(executive_summary="Composite evidence summary.",data_quality={"status":"WARNING","optional_unavailable":["SAL-012"]},lineage={"composite_id":"STR-004"})
 comp=CompositeRun("cr-1","STR-004","1.0",ExerciseStatus.PARTIAL,QualityStatus.WARNING,child_runs={"MKT-003":c},result=r,conflicts=[{"type":"METRIC_CONFLICT","resolution":"REVIEW_REQUIRED"}])
 p=composite_workspace_payload(comp); assert p["kind"]=="composite"; assert p["child_runs"][0]["run_id"]=="run-1"; assert "result" not in p["child_runs"][0]
 assert "SAL-012" in p["limitations"]; assert p["copilot_context"]["conflicts"][0]["resolution"]=="REVIEW_REQUIRED"

def test_str004_visualizations_are_existing_contract_and_evidence_safe():
 from src.exercises.visualization import resolve_visualizations
 c=_child(); r=CanonicalResult(executive_summary="Composite evidence summary.",data_quality={"status":"WARNING"},lineage={"composite_id":"STR-004"})
 specs=resolve_visualizations("STR-004",r,child_runs={"MKT-003":c})
 assert [x["chart_id"] for x in specs]==["STR-004-evidence-coverage","STR-004-child-quality"]
 assert specs[0]["metadata"]["viz_id"]=="VIZ-022"
 assert specs[1]["chart_type"]=="table"
 assert "result" not in str(specs)
