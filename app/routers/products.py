import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import canonical_service, crud
from ..database import get_db
from ..deps import get_current_user
from ..engines.engine_registry import run_product_engine
from ..engines.product_catalog import PRODUCT_CATALOG
from ..engines.exercise_manifest import list_exercise_manifests
from ..engines.exercise_taxonomy import list_exercise_packs
from ..engines.data_compatibility import assess_exercise_compatibility
from ..engines.dataset_intelligence import inspect_unknown_dataset
from ..engines.intent_resolver import resolve_dataset_goal
from ..visualization.exercise_catalog import list_exercise_presentations
from ..visualization.coverage_audit import audit_exercise_coverage
from ..models import User
from ..schemas import ProductRunFromDatasetVersionRequest, ProductRunFromFileRequest, ProductRunRequest, DatasetGoalResolveRequest

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/catalog")
def catalog():
    return PRODUCT_CATALOG


@router.get("/exercise-packs")
def exercise_packs():
    """Current and planned exercise taxonomy. Planned items are not executable."""
    return list_exercise_packs()


@router.get("/exercise-manifests")
def exercise_manifests():
    """Declarative exercise contracts for dynamic UI/orchestration."""
    return list_exercise_manifests()


@router.get("/visualization-coverage")
def visualization_coverage():
    """MVP presentation coverage audit for executable exercises."""
    return audit_exercise_coverage()


@router.get("/visualization-catalog")
def visualization_catalog():
    """Presentation mappings for currently registered exercise engines."""
    return list_exercise_presentations()



@router.get("/dataset-intelligence")
def dataset_intelligence(workspace_id: int, dataset_version_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Inspect a governed dataset schema and suggest compatible exercises."""
    if not crud.is_workspace_member(db,user.id,workspace_id):
        raise HTTPException(403,"You do not have access to this workspace")
    version=crud.get_dataset_version(db,user.id,dataset_version_id)
    if not version:
        raise HTTPException(404,"Dataset version not found")
    dataset=crud.get_dataset(db,user.id,version.dataset_id)
    if not dataset or dataset.workspace_id!=workspace_id:
        raise HTTPException(403,"Dataset version is not in this workspace")
    try:
        parsed=canonical_service.load_canonical_dataset_version(version)
    except ValueError as error:
        raise HTTPException(400,str(error))
    columns=list(parsed["rows"][0].keys()) if parsed.get("rows") else []
    return inspect_unknown_dataset(columns,profile=parsed.get("profile") or {})


@router.post("/resolve-goal")
def resolve_goal(body: DatasetGoalResolveRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Resolve a business goal to compatible governed exercises without exposing raw rows to an LLM."""
    if not crud.is_workspace_member(db,user.id,body.workspace_id):
        raise HTTPException(403,"You do not have access to this workspace")
    version=crud.get_dataset_version(db,user.id,body.dataset_version_id)
    if not version:
        raise HTTPException(404,"Dataset version not found")
    dataset=crud.get_dataset(db,user.id,version.dataset_id)
    if not dataset or dataset.workspace_id!=body.workspace_id:
        raise HTTPException(403,"Dataset version is not in this workspace")
    try:
        parsed=canonical_service.load_canonical_dataset_version(version)
    except ValueError as error:
        raise HTTPException(400,str(error))
    columns=list(parsed.get("schema",{}).get("mapping",{}).values())
    if not columns and parsed.get("rows"):
        columns=list(parsed["rows"][0].keys())
    return resolve_dataset_goal(columns,body.goal,profile=parsed.get("profile") or {},persona=body.persona)


@router.get("/compatibility")
def compatibility(exercise_id: str, workspace_id: int, dataset_version_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Pre-flight check: exercise manifest requirements vs governed dataset columns."""
    if not crud.is_workspace_member(db, user.id, workspace_id):
        raise HTTPException(403, "You do not have access to this workspace")
    version=crud.get_dataset_version(db,user.id,dataset_version_id)
    if not version:
        raise HTTPException(404,"Dataset version not found")
    dataset=crud.get_dataset(db,user.id,version.dataset_id)
    if not dataset or dataset.workspace_id!=workspace_id:
        raise HTTPException(403,"Dataset version is not in this workspace")
    status=getattr(version.status,"value",version.status)
    try:
        parsed=canonical_service.load_canonical_dataset_version(version)
        columns=list(parsed.get("schema",{}).get("mapping",{}).values())
        if not columns and parsed.get("rows"):
            columns=list(parsed["rows"][0].keys())
    except ValueError as error:
        return {"exerciseId":exercise_id,"state":"blocked","ready":False,"canRun":False,"reason":str(error),"missingRequired":[],"missingOptional":[],"availableColumns":[]}
    return assess_exercise_compatibility(exercise_id,columns,dataset_status=status)


@router.post("/run")
def run(body: ProductRunRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not crud.is_workspace_member(db, user.id, body.workspace_id):
        raise HTTPException(403, "You do not have access to this workspace")
    result = run_product_engine(body.product_id, body.rows, {"workspaceId": body.workspace_id, "filters": body.filters})
    saved_run = crud.create_product_run(
        db, user.id, body.workspace_id, body.product_id, result["status"],
        json.dumps({"filters": body.filters or {}, "rowCount": len(body.rows)}),
        json.dumps(result),
    )
    return {**result, "id": saved_run.id if saved_run else None, "product_id": body.product_id}


@router.post("/run-from-file")
def run_from_file(body: ProductRunFromFileRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not crud.is_workspace_member(db, user.id, body.workspace_id):
        raise HTTPException(403, "You do not have access to this workspace")
    file = crud.get_workspace_file(db, user.id, body.file_id)
    if not file or file.workspace_id != body.workspace_id:
        raise HTTPException(404, "File not found in this workspace")
    try:
        parsed = canonical_service.load_canonical_file(file)
    except ValueError as error:
        raise HTTPException(400, str(error))
    if not parsed["validation"]["valid"]:
        raise HTTPException(400, f"Data validation failed: {' '.join(parsed['validation']['issues'])}")

    rows = parsed["rows"][:25000]
    result = run_product_engine(body.product_id, rows, {"workspaceId": body.workspace_id, "filters": body.filters})
    saved_run = crud.create_product_run(
        db, user.id, body.workspace_id, body.product_id, result["status"],
        json.dumps({
            "fileId": body.file_id, "fileName": file.file_name, "rawRowCount": parsed["rawRowCount"],
            "governedRowCount": len(rows), "governance": parsed["governance"], "filters": body.filters or {},
        }),
        json.dumps(result),
    )
    return {
        **result, "id": saved_run.id if saved_run else None, "product_id": body.product_id,
        "source": {
            "fileId": file.id, "fileName": file.file_name, "rawRowCount": parsed["rawRowCount"],
            "governedRowCount": len(rows), "profile": parsed["profile"], "governance": parsed["governance"],
        },
    }


@router.post("/run-from-dataset-version")
def run_from_dataset_version(body: ProductRunFromDatasetVersionRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Run an engine from the governed Dataset Registry version.

    This is the canonical path for new clients. It uses DatasetVersion access
    control and provenance directly; UploadedFile is not required.
    """
    if not crud.is_workspace_member(db, user.id, body.workspace_id):
        raise HTTPException(403, "You do not have access to this workspace")
    version = crud.get_dataset_version(db, user.id, body.dataset_version_id)
    if not version:
        raise HTTPException(404, "Dataset version not found")
    dataset = crud.get_dataset(db, user.id, version.dataset_id)
    if not dataset or dataset.workspace_id != body.workspace_id:
        raise HTTPException(403, "Dataset version is not in this workspace")
    if getattr(version.status, "value", version.status) != "ready":
        return {"status": "requires_data", "reason": "Dataset version must pass mapping and data quality before analysis.", "datasetVersionId": version.id, "processingStatus": getattr(version.status, "value", version.status)}
    try:
        parsed = canonical_service.load_canonical_dataset_version(version)
    except ValueError as error:
        raise HTTPException(400, str(error))
    if not parsed["validation"]["valid"]:
        raise HTTPException(400, f"Data validation failed: {' '.join(parsed['validation']['issues'])}")
    rows = parsed["rows"][:25000]
    available_columns = list(rows[0].keys()) if rows else []
    compatibility = assess_exercise_compatibility(body.product_id, available_columns, dataset_status="ready")
    if not compatibility.get("canRun"):
        return {"status":"requires_data","reason":compatibility["reason"],"compatibility":compatibility,"datasetVersionId":version.id}
    result = run_product_engine(body.product_id, rows, {"workspaceId": body.workspace_id, "filters": body.filters, "datasetVersionId": version.id})
    saved_run = crud.create_product_run(
        db, user.id, body.workspace_id, body.product_id, result["status"],
        json.dumps({"datasetVersionId": version.id, "datasetId": version.dataset_id, "filters": body.filters or {}, "rowCount": len(rows)}),
        json.dumps(result),
    )
    return {
        **result, "id": saved_run.id if saved_run else None, "product_id": body.product_id,
        "source": {**parsed["source"], "rawRowCount": parsed["rawRowCount"], "governedRowCount": len(rows), "profile": parsed["profile"], "governance": parsed["governance"]},
    }
