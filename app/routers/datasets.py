import json

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .. import canonical_service, crud, data_quality, mapping_engine
from ..database import get_db
from ..deps import get_current_user
from ..models import DatasetStatus, User
from ..schemas import DatasetCreate, DatasetVersionCreate, MappingConfirm
from ..storage import storage_put, storage_put_presigned_url

router = APIRouter(prefix="/api/v1/datasets", tags=["datasets"])

MAX_PROFILE_ROWS = 25_000


@router.post("/presign")
def presign_dataset_upload(workspace_id: int, file_name: str, user: User = Depends(get_current_user)):
    return storage_put_presigned_url(f"workspaces/{workspace_id}/raw/{file_name}")
    
@router.post("/upload")
async def upload_dataset_file(workspace_id: int, file: UploadFile = File(...), user: User = Depends(get_current_user)):
    """Server-side upload: browser → Render → R2 (bypasses blocked direct R2 access)."""
    data = await file.read()
    return storage_put(f"workspaces/{workspace_id}/raw/{file.filename}", data, file.content_type or "application/octet-stream")


@router.get("")
def list_datasets(workspace_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    datasets = crud.list_datasets(db, user.id, workspace_id)
    result = []
    for dataset in datasets:
        report = crud.get_latest_quality_report(db, dataset.latest_version_id) if dataset.latest_version_id else None
        result.append({
            "id": dataset.id, "name": dataset.name, "sourceType": dataset.source_type,
            "status": dataset.status, "latestVersionId": dataset.latest_version_id,
            "qualityScore": report.quality_score if report else None, "updatedAt": dataset.updated_at,
        })
    return result


@router.post("")
def create_dataset(body: DatasetCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Registers metadata for a file already uploaded to R2 via /presign (Part 5:
    the file itself lives in Cloudflare R2; only metadata is written to Postgres)."""
    result = crud.create_dataset_with_first_version(db, user.id, body.workspace_id, body.name, body.source_type, body.file_name, body.storage_key)
    if not result:
        raise HTTPException(403, "You do not have access to this workspace")
    dataset, version = result
    return {"datasetId": dataset.id, "versionId": version.id, "versionNumber": version.version_number, "status": version.status}


@router.post("/{dataset_id}/versions")
def add_version(dataset_id: int, body: DatasetVersionCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    version = crud.add_dataset_version(db, user.id, dataset_id, body.file_name, body.storage_key)
    if not version:
        raise HTTPException(404, "Dataset not found or no access")
    return {"versionId": version.id, "versionNumber": version.version_number, "status": version.status}


@router.get("/{dataset_id}/versions")
def list_versions(dataset_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    versions = crud.list_dataset_versions(db, user.id, dataset_id)
    return [{"id": v.id, "versionNumber": v.version_number, "fileName": v.file_name, "status": v.status, "rowCount": v.row_count, "createdAt": v.created_at} for v in versions]


@router.post("/versions/{version_id}/profile")
def profile_version(version_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Step 1 of the onboarding workflow (Part 2 of the corrective upgrade):
    detect schema/columns and suggest a mapping with confidence + warnings."""
    version = crud.get_dataset_version(db, user.id, version_id)
    if not version:
        raise HTTPException(404, "Dataset version not found or no access")
    try:
        df = canonical_service.load_raw_dataframe(version.file_name, version.raw_storage_key)
    except ValueError as error:
        crud.set_version_status(db, version_id, DatasetStatus.failed)
        raise HTTPException(400, str(error))

    crud.set_version_status(db, version_id, DatasetStatus.validating, row_count=len(df))
    suggestion = mapping_engine.suggest_mapping(list(df.columns))
    crud.set_version_status(db, version_id, DatasetStatus.mapping)
    sample_rows = df.head(5).where(df.head(5).notnull(), None).to_dict(orient="records")
    return {
        "versionId": version_id, "rowCount": len(df), "columns": list(df.columns),
        "sampleRows": sample_rows, "suggestedMapping": suggestion["suggestions"],
        "unmatchedColumns": suggestion["unmatchedColumns"], "coverage": suggestion["coverage"],
        "warnings": suggestion["warnings"],
    }


@router.post("/versions/{version_id}/mapping")
def confirm_mapping(version_id: int, body: MappingConfirm, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Step 2: user confirms/edits the suggested mapping. Runs the Data Quality Engine,
    writes the curated Parquet output to R2, and persists both (Parts 6, 8, 19)."""
    version = crud.get_dataset_version(db, user.id, version_id)
    if not version:
        raise HTTPException(404, "Dataset version not found or no access")

    try:
        df = canonical_service.load_raw_dataframe(version.file_name, version.raw_storage_key)
    except ValueError as error:
        raise HTTPException(400, str(error))

    raw_rows = df.head(MAX_PROFILE_ROWS).where(df.head(MAX_PROFILE_ROWS).notnull(), None).to_dict(orient="records")
    mapped_rows = mapping_engine.apply_confirmed_mapping(raw_rows, body.mapping)

    crud.save_dataset_mapping(db, user.id, version_id, json.dumps(body.mapping), json.dumps(body.confidence), confirmed=True)

    quality = data_quality.assess_quality(mapped_rows, body.confidence)
    crud.save_quality_report(
        db, version_id, quality["qualityScore"], json.dumps(quality["criticalErrors"]),
        json.dumps(quality["warnings"]), json.dumps(quality["recommendations"]),
    )

    parent_dataset = crud.get_dataset(db, user.id, version.dataset_id)
    curated = None
    if not quality["criticalErrors"]:
        import pandas as pd

        curated_df = pd.DataFrame(mapped_rows)
        curated_bytes = curated_df.to_parquet(index=False)
        artifact = storage_put(
            f"workspaces/{parent_dataset.workspace_id}/curated/{version.dataset_id}/v{version.version_number}.parquet",
            curated_bytes, "application/octet-stream",
        )
        curated = artifact["key"]

    final_status = DatasetStatus.ready if not quality["criticalErrors"] else DatasetStatus.failed
    crud.set_version_status(db, version_id, final_status, row_count=len(mapped_rows), curated_storage_key=curated)

    return {
        "versionId": version_id, "status": final_status, "qualityScore": quality["qualityScore"],
        "criticalErrors": quality["criticalErrors"], "warnings": quality["warnings"],
        "recommendations": quality["recommendations"], "curatedStorageKey": curated,
    }


@router.get("/versions/{version_id}/quality-report")
def quality_report(version_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    version = crud.get_dataset_version(db, user.id, version_id)
    if not version:
        raise HTTPException(404, "Dataset version not found or no access")
    report = crud.get_latest_quality_report(db, version_id)
    if not report:
        raise HTTPException(404, "No quality report yet — confirm a mapping first")
    return {
        "qualityScore": report.quality_score, "criticalErrors": json.loads(report.critical_errors_json),
        "warnings": json.loads(report.warnings_json), "recommendations": json.loads(report.recommendations_json),
        "createdAt": report.created_at,
    }
