import os
import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud
from ..database import get_db
from ..deps import get_current_user
from ..models import UploadJob, User
from ..schemas import UploadCompleteRequest, UploadSessionRequest
from ..storage import storage_put_presigned_url

router = APIRouter(prefix="/api/upload-jobs", tags=["upload-jobs"])
MAX_UPLOAD_BYTES = 500 * 1024 * 1024
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".parquet"}

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://asfnfwafnhdpuxcjjdta.supabase.co")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "datasets")


def _payload(job: UploadJob):
    return {
        "jobId": job.id,
        "datasetVersionId": job.dataset_version_id,
        "fileName": job.file_name,
        "status": job.status,
        "stage": job.stage,
        "progress": job.progress,
        "error": job.error_message,
        "cancelRequested": job.cancel_requested,
    }


def _build_upload_payload(storage_key: str):
    if SUPABASE_SERVICE_ROLE_KEY:
        endpoint = f"{SUPABASE_URL.rstrip('/')}/storage/v1/upload/resumable"
        return {
            "method": "TUS",
            "endpoint": endpoint,
            "token": SUPABASE_SERVICE_ROLE_KEY,
            "bucket": STORAGE_BUCKET,
            "key": storage_key,
        }
    else:
        presigned = storage_put_presigned_url(storage_key, expires_in=3600)
        return {
            "method": "PUT",
            "url": presigned["url"],
            "key": storage_key,
        }


@router.post("")
def create_job(
    body: UploadSessionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not crud.is_workspace_member(db, user.id, body.workspace_id):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "You do not have access to this workspace"
        )

    extension = (
        "." + body.file_name.rsplit(".", 1)[-1].lower() if "." in body.file_name else ""
    )
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Supported formats: CSV, XLSX, XLS, Parquet",
        )

    if body.size_bytes > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            "Maximum file size is 500 MB",
        )

    existing = (
        db.query(UploadJob)
        .filter(
            UploadJob.idempotency_key == body.idempotency_key,
            UploadJob.user_id == user.id,
        )
        .first()
    )

    if existing:
        if existing.status == "created":
            upload = _build_upload_payload(existing.storage_key)
            return {**_payload(existing), "upload": upload, "reused": True}
        return {**_payload(existing), "reused": True}

    storage_key = f"workspaces/{body.workspace_id}/raw/{body.file_name}"
    upload = _build_upload_payload(storage_key)

    job = UploadJob(
        workspace_id=body.workspace_id,
        user_id=user.id,
        file_name=body.file_name,
        storage_key=storage_key,
        idempotency_key=body.idempotency_key,
        size_bytes=body.size_bytes,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    return {**_payload(job), "upload": upload}


@router.post("/complete")
def complete_job(
    body: UploadCompleteRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = (
        db.query(UploadJob)
        .filter(
            UploadJob.id == body.job_id,
            UploadJob.user_id == user.id,
            UploadJob.workspace_id == body.workspace_id,
        )
        .first()
    )
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Upload job not found")

    if job.status not in {"created", "failed"}:
        return _payload(job)

    result = crud.create_dataset_with_first_version(
        db,
        user.id,
        body.workspace_id,
        body.dataset_name or job.file_name,
        body.source_type,
        job.file_name,
        job.storage_key,
    )
    if not result:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "You do not have access to this workspace"
        )

    _, version = result
    job.dataset_version_id = version.id
    job.status = "queued"
    job.stage = "queued"
    job.progress = 2
    job.error_message = None
    db.commit()
    db.refresh(job)
    return _payload(job)


@router.get("/{job_id}")
def get_status(
    job_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = (
        db.query(UploadJob)
        .filter(UploadJob.id == job_id, UploadJob.user_id == user.id)
        .first()
    )
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Upload job not found")
    return _payload(job)


@router.post("/{job_id}/retry")
def retry_job(
    job_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = (
        db.query(UploadJob)
        .filter(UploadJob.id == job_id, UploadJob.user_id == user.id)
        .first()
    )
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Upload job not found")
    if job.status not in {"failed", "cancelled"}:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Only failed or cancelled jobs can be retried",
        )

    job.status, job.stage, job.progress, job.error_message, job.cancel_requested = (
        "queued",
        "queued",
        2,
        None,
        False,
    )
    db.commit()
    return _payload(job)


@router.post("/{job_id}/cancel")
def cancel_job(
    job_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = (
        db.query(UploadJob)
        .filter(UploadJob.id == job_id, UploadJob.user_id == user.id)
        .first()
    )
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Upload job not found")
    if job.status in {"ready", "failed", "cancelled"}:
        return _payload(job)

    job.cancel_requested = True
    job.status = "cancelling"
    db.commit()
    return _payload(job)
