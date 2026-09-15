import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import canonical_service, crud
from ..database import get_db
from ..deps import get_current_user
from ..engines.engine_registry import run_product_engine
from ..engines.product_catalog import PRODUCT_CATALOG
from ..models import User
from ..schemas import ProductRunFromDatasetVersionRequest, ProductRunFromFileRequest, ProductRunRequest

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/catalog")
def catalog():
    return PRODUCT_CATALOG


@router.post("/run")
def run(body: ProductRunRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not crud.is_workspace_member(db, user.id, body.workspace_id):
        raise HTTPException(403, "You do not have access to this workspace")
    result = run_product_engine(body.product_id, body.rows, {"workspaceId": body.workspace_id, "filters": body.filters})
    crud.create_product_run(
        db, user.id, body.workspace_id, body.product_id, result["status"],
        json.dumps({"filters": body.filters or {}, "rowCount": len(body.rows)}),
        json.dumps(result),
    )
    return result


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
    crud.create_product_run(
        db, user.id, body.workspace_id, body.product_id, result["status"],
        json.dumps({
            "fileId": body.file_id, "fileName": file.file_name, "rawRowCount": parsed["rawRowCount"],
            "governedRowCount": len(rows), "governance": parsed["governance"], "filters": body.filters or {},
        }),
        json.dumps(result),
    )
    return {
        **result,
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
    result = run_product_engine(body.product_id, rows, {"workspaceId": body.workspace_id, "filters": body.filters, "datasetVersionId": version.id})
    crud.create_product_run(
        db, user.id, body.workspace_id, body.product_id, result["status"],
        json.dumps({"datasetVersionId": version.id, "datasetId": version.dataset_id, "filters": body.filters or {}, "rowCount": len(rows)}),
        json.dumps(result),
    )
    return {
        **result,
        "source": {**parsed["source"], "rawRowCount": parsed["rawRowCount"], "governedRowCount": len(rows), "profile": parsed["profile"], "governance": parsed["governance"]},
    }
