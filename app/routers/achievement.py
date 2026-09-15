from collections import defaultdict
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import canonical_service, crud
from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas import AchievementAnalyze

router = APIRouter(prefix="/api/achievement", tags=["achievement"])

def _number(value: Any) -> float | None:
    try:
        if value is None or value == "": return None
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError): return None

def _pick(row: dict, requested: str | None, aliases: list[str]):
    if requested and requested in row: return row.get(requested)
    lowered = {str(k).lower().replace(" ", "_"): k for k in row}
    for alias in aliases:
        if alias in lowered: return row.get(lowered[alias])
    return None

def _group(rows: list[dict], key_aliases: list[str], target_field: str | None, actual_field: str | None):
    groups = defaultdict(lambda: {"target": 0.0, "actual": 0.0, "rows": 0})
    for row in rows:
        key = _pick(row, None, key_aliases) or "Unknown"
        target = _number(_pick(row, target_field, ["target", "target_value", "target_units", "planned_sales"]))
        actual = _number(_pick(row, actual_field, ["actual", "actual_value", "sales_value", "sales_units", "achievement"]))
        if target is None and actual is None: continue
        groups[str(key)]["target"] += target or 0
        groups[str(key)]["actual"] += actual or 0
        groups[str(key)]["rows"] += 1
    return [{"label": key, "target": round(v["target"], 4), "actual": round(v["actual"], 4), "variance": round(v["actual"] - v["target"], 4), "achievementPct": round((v["actual"] / v["target"]) * 100, 2) if v["target"] else None, "rows": v["rows"]} for key, v in sorted(groups.items(), key=lambda item: item[1]["actual"], reverse=True)]

@router.post("/analyze")
def analyze(body: AchievementAnalyze, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not crud.is_workspace_member(db, user.id, body.workspace_id): raise HTTPException(403, "You do not have access to this workspace")
    version = crud.get_dataset_version(db, user.id, body.dataset_version_id)
    if not version: raise HTTPException(404, "Dataset version not found")
    dataset = crud.get_dataset(db, user.id, version.dataset_id)
    if not dataset or dataset.workspace_id != body.workspace_id: raise HTTPException(403, "Dataset version is not in this workspace")
    if getattr(version.status, "value", version.status) != "ready":
        return {"status": "requires_data", "reason": "Dataset version must pass mapping and data quality before Achievement analysis.", "missing": ["ready_dataset_version"], "datasetVersionId": version.id, "processingStatus": getattr(version.status, "value", version.status)}
    try: parsed = canonical_service.load_canonical_dataset_version(version)
    except ValueError as error: raise HTTPException(400, str(error))
    rows = parsed.get("rows") or []
    if not rows: return {"status": "requires_data", "reason": "No usable performance rows were found in the selected file.", "missing": ["actual", "target"]}
    target_aliases = ["target", "target_value", "target_units", "planned_sales"]
    actual_aliases = ["actual", "actual_value", "sales_value", "sales_units", "achievement"]
    target_count = sum(_number(_pick(r, body.target_field, target_aliases)) is not None for r in rows)
    actual_count = sum(_number(_pick(r, body.actual_field, actual_aliases)) is not None for r in rows)
    missing = ([] if target_count else ["target"]) + ([] if actual_count else ["actual"])
    if missing: return {"status": "requires_data", "reason": "Achievement needs real target and actual performance fields.", "missing": missing, "availableColumns": list(rows[0].keys())}
    total = _group(rows, ["total"], body.target_field, body.actual_field)[0]
    result = {"status": "ready", "workspaceId": body.workspace_id, "datasetVersionId": version.id, "datasetId": version.dataset_id, "fileName": version.file_name, "summary": {"target": total["target"], "actual": total["actual"], "variance": total["variance"], "achievementPct": total["achievementPct"], "rowCount": len(rows)}, "byProduct": _group(rows, ["product", "product_name", "brand", "brand_name"], body.target_field, body.actual_field), "byTerritory": _group(rows, ["territory", "territory_name", "region"], body.target_field, body.actual_field), "byRepresentative": _group(rows, ["sales_rep", "representative", "rep", "salesperson"], body.target_field, body.actual_field), "provenance": {**parsed.get("source", {}), "rawRowCount": parsed.get("rawRowCount"), "governance": parsed.get("governance"), "dataType": "dataset_version"}}
    return result

@router.get("/status")
def status():
    return {"status": "available", "requires": ["target", "actual"], "note": "General territory percentages are not applied to product targets."}
