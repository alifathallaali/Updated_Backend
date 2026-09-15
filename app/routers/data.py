import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud
from ..database import get_db
from ..deps import get_current_user
from ..models import User

router = APIRouter(prefix="/api/data", tags=["ai-data-layer"])

def _dataset_payload(dataset, version=None, quality=None):
    return {
        "id": dataset.id,
        "name": dataset.name,
        "workspaceId": dataset.workspace_id,
        "sourceType": dataset.source_type,
        "datasetType": dataset.dataset_type,
        "status": dataset.status.value if hasattr(dataset.status, "value") else dataset.status,
        "latestVersionId": dataset.latest_version_id,
        "updatedAt": dataset.updated_at,
        "version": None if version is None else {
            "id": version.id, "versionNumber": version.version_number, "fileName": version.file_name,
            "rowCount": version.row_count, "status": version.status.value if hasattr(version.status, "value") else version.status,
            "createdAt": version.created_at, "rawStorageKeyPresent": bool(version.raw_storage_key),
            "curatedStorageKeyPresent": bool(version.curated_storage_key),
        },
        "quality": None if quality is None else {
            "qualityScore": quality.quality_score,
            "criticalErrors": json.loads(quality.critical_errors_json),
            "warnings": json.loads(quality.warnings_json),
            "recommendations": json.loads(quality.recommendations_json),
            "createdAt": quality.created_at,
        },
    }

@router.get("/datasets")
def list_data_datasets(workspace_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = []
    for dataset in crud.list_datasets(db, user.id, workspace_id):
        version = crud.get_dataset_version(db, user.id, dataset.latest_version_id) if dataset.latest_version_id else None
        quality = crud.get_latest_quality_report(db, version.id) if version else None
        result.append(_dataset_payload(dataset, version, quality))
    return result

@router.get("/datasets/{dataset_id}")
def get_data_dataset(dataset_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = crud.get_dataset(db, user.id, dataset_id)
    if not dataset: raise HTTPException(404, "Dataset not found")
    version = crud.get_dataset_version(db, user.id, dataset.latest_version_id) if dataset.latest_version_id else None
    quality = crud.get_latest_quality_report(db, version.id) if version else None
    return _dataset_payload(dataset, version, quality)

@router.get("/datasets/{dataset_id}/metadata")
def dataset_metadata(dataset_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = crud.get_dataset(db, user.id, dataset_id)
    if not dataset: raise HTTPException(404, "Dataset not found")
    versions = crud.list_dataset_versions(db, user.id, dataset_id)
    return {"dataset": _dataset_payload(dataset), "versions": [_dataset_payload(dataset, v).get("version") for v in versions]}

@router.get("/datasets/{dataset_id}/quality")
def dataset_quality(dataset_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = crud.get_dataset(db, user.id, dataset_id)
    if not dataset: raise HTTPException(404, "Dataset not found")
    if not dataset.latest_version_id: return {"status": "requires_data", "reason": "Dataset has no processed version."}
    report = crud.get_latest_quality_report(db, dataset.latest_version_id)
    if not report: return {"status": "requires_data", "reason": "Dataset has no quality report."}
    return _dataset_payload(dataset, quality=report).get("quality")

@router.get("/datasets/{dataset_id}/provenance")
def dataset_provenance(dataset_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dataset = crud.get_dataset(db, user.id, dataset_id)
    if not dataset: raise HTTPException(404, "Dataset not found")
    versions = crud.list_dataset_versions(db, user.id, dataset_id)
    return {"datasetId": dataset.id, "dataset": dataset.name, "source": dataset.source_type, "workspaceId": dataset.workspace_id, "versions": [{"versionId": v.id, "versionNumber": v.version_number, "fileName": v.file_name, "status": v.status.value if hasattr(v.status, "value") else v.status, "createdAt": v.created_at, "rawData": "uploaded file", "normalizedData": bool(v.curated_storage_key), "qualityReport": bool(crud.get_latest_quality_report(db, v.id))} for v in versions]}
