"""Deterministic next-exercise suggestions for the result experience."""
from .exercise_manifest import MANIFEST_BY_ID
from .data_compatibility import assess_exercise_compatibility

NEXT_EXERCISES = {
 "product-01":["product-05","product-02","product-03"],
 "product-02":["product-09","product-15","product-16"],
 "product-03":["product-05","product-07","product-09"],
 "product-04":["product-05","product-06","product-15"],
 "product-05":["product-06","product-08","product-15"],
 "product-06":["product-08","product-10","product-17"],
 "product-07":["product-16","product-08","product-15"],
 "product-08":["product-17","product-15","product-14"],
 "product-09":["product-15","product-16","product-17"],
 "product-10":["product-11","product-12","product-14"],
 "product-11":["product-12","product-14","product-17"],
 "product-12":["product-11","product-14","product-17"],
 "product-13":["product-14","product-15","product-17"],
 "product-14":["product-15","product-17","product-08"],
 "product-15":["product-08","product-16","product-17"],
 "product-16":["product-07","product-15","product-17"],
 "product-17":["product-08","product-14","product-15"],
}

def next_exercises(exercise_id: str, available_columns: list[str] | None = None) -> list[dict]:
 """Return next analyses, filtering out routes the current dataset cannot run."""
 out=[]
 for target in NEXT_EXERCISES.get(exercise_id,[]):
  m=MANIFEST_BY_ID.get(target)
  if not m:
   continue
  compatibility = assess_exercise_compatibility(target, available_columns, dataset_status="ready") if available_columns is not None else None
  if compatibility and not compatibility.get("canRun"):
   continue
  out.append({
   "exerciseId":m.id,"name":m.name,"domain":m.domain,"family":m.family,"readiness":m.readiness,
   "compatibilityState": compatibility.get("state") if compatibility else "not_checked",
   "missingOptional": compatibility.get("missingOptional",[]) if compatibility else [],
  })
  if len(out) >= 3:
   break
 return out
