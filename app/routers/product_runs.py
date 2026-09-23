from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..deps import get_current_user
from ..models import User, DatasetStatus
from ..schemas import ProductRunRefreshRequest
from .. import canonical_service
from ..engines.engine_registry import run_product_engine
from ..engines.data_compatibility import assess_exercise_compatibility

router = APIRouter(prefix="/api/product-runs", tags=["product-runs"])


@router.get("")
def list_runs(workspace_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.list_product_runs(db, user.id, workspace_id)


@router.get("/{run_id}")
def get_run(run_id: int, workspace_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return a saved run with its parsed output for report composition."""
    if not crud.is_workspace_member(db, user.id, workspace_id):
        from fastapi import HTTPException
        raise HTTPException(403, "You do not have access to this workspace")
    run = crud.get_product_run(db, user.id, run_id)
    if not run or run.workspace_id != workspace_id:
        from fastapi import HTTPException
        raise HTTPException(404, "Product run not found in this workspace")
    import json
    try:
        output = json.loads(run.output_definition)
    except (json.JSONDecodeError, TypeError):
        output = {}
    return {
        "id": run.id,
        "product_id": run.product_id,
        "status": run.status,
        "recipe": json.loads(run.input_definition) if run.input_definition else {},
        **output,
    }


@router.post("/{run_id}/refresh")
def refresh_run(run_id: int, body: ProductRunRefreshRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Re-run a saved analysis recipe against the requested/latest governed dataset version."""
    import json
    from fastapi import HTTPException
    run = crud.get_product_run(db, user.id, run_id)
    if not run or run.workspace_id != body.workspace_id:
        raise HTTPException(404, "Product run not found in this workspace")
    try:
        recipe = json.loads(run.input_definition or "{}")
    except json.JSONDecodeError:
        recipe = {}
    version_id = body.dataset_version_id or recipe.get("datasetVersionId")
    if not version_id:
        raise HTTPException(409, "This saved analysis has no dataset version recipe to refresh")
    version = crud.get_dataset_version(db, user.id, int(version_id))
    if not version or getattr(version.status, "value", version.status) != DatasetStatus.ready.value:
        raise HTTPException(409, "Requested dataset version is not ready")
    dataset = crud.get_dataset(db, user.id, version.dataset_id)
    if not dataset or dataset.workspace_id != body.workspace_id:
        raise HTTPException(403, "Dataset version is not in this workspace")
    parsed = canonical_service.load_canonical_dataset_version(version)
    rows = parsed.get("rows", [])[:25000]
    columns = list(rows[0].keys()) if rows else []
    compatibility = assess_exercise_compatibility(run.product_id, columns, dataset_status="ready")
    if not compatibility.get("canRun"):
        return {"status":"requires_data", "compatibility":compatibility, "datasetVersionId":version.id}
    result = run_product_engine(run.product_id, rows, {"workspaceId":body.workspace_id, "filters":recipe.get("filters") or {}, "datasetVersionId":version.id})
    refreshed = crud.create_product_run(db, user.id, body.workspace_id, run.product_id, result["status"],
        json.dumps({**recipe, "datasetVersionId":version.id, "datasetId":version.dataset_id, "refreshedFromRunId":run.id, "rowCount":len(rows)}), json.dumps(result))
    return {**result, "id": refreshed.id if refreshed else None, "refreshedFromRunId":run.id, "datasetVersionId":version.id,
            "source": {**parsed.get("source",{}), "profile":parsed.get("profile"), "governance":parsed.get("governance")}}
