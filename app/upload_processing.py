import json
from sqlalchemy.orm import Session
from . import canonical_service, crud, data_quality, mapping_engine
from .models import DatasetStatus, DatasetVersion, UploadJob
from .storage import storage_put


def _cancelled(db: Session, job: UploadJob) -> bool:
    db.refresh(job)
    if job.cancel_requested:
        job.status = "cancelled"
        job.stage = "cancelled"
        db.commit()
        if job.dataset_version_id:
            crud.set_version_status(db, job.dataset_version_id, DatasetStatus.failed)
        return True
    return False


def process_upload_job(db: Session, job: UploadJob) -> None:
    if job.status in {"cancelled", "ready"}:
        return
    job.status, job.stage, job.progress, job.error_message = "processing", "validating", 10, None
    db.commit()
    try:
        if _cancelled(db, job): return
        version = db.query(DatasetVersion).get(job.dataset_version_id)
        if not version:
            raise ValueError("Dataset version not found")
        raw_df = canonical_service.load_raw_dataframe(version.file_name, version.raw_storage_key)
        crud.set_version_status(db, version.id, DatasetStatus.validating, row_count=len(raw_df))
        job.stage, job.progress = "mapping", 35
        db.commit()
        if _cancelled(db, job): return
        suggestion = mapping_engine.suggest_mapping(list(raw_df.columns))
        raw_rows = raw_df.head(canonical_service.MAX_CANONICAL_ROWS).where(raw_df.head(canonical_service.MAX_CANONICAL_ROWS).notnull(), None).to_dict(orient="records")
        mapping = {field: value["column"] for field, value in suggestion["suggestions"].items() if isinstance(value, dict) and value.get("column")}
        confidence = {field: value.get("confidence", 0) for field, value in suggestion["suggestions"].items() if isinstance(value, dict)}
        mapped_rows = mapping_engine.apply_confirmed_mapping(raw_rows, mapping)
        crud.save_dataset_mapping(db, job.user_id, version.id, json.dumps(mapping), json.dumps(confidence), confirmed=True)
        crud.set_version_status(db, version.id, DatasetStatus.processing)
        job.stage, job.progress = "quality_check", 60
        db.commit()
        if _cancelled(db, job): return
        quality = data_quality.assess_quality(mapped_rows, confidence)
        crud.save_quality_report(db, version.id, quality["qualityScore"], json.dumps(quality["criticalErrors"]), json.dumps(quality["warnings"]), json.dumps(quality["recommendations"]))
        if quality["criticalErrors"]:
            crud.set_version_status(db, version.id, DatasetStatus.failed)
            job.status, job.stage, job.progress, job.error_message = "failed", "quality_check", 100, "Critical data-quality errors prevented processing"
            db.commit(); return
        job.stage, job.progress = "curating", 80
        db.commit()
        if _cancelled(db, job): return
        import pandas as pd
        curated_bytes = pd.DataFrame(mapped_rows).to_parquet(index=False)
        dataset = crud.get_dataset(db, job.user_id, version.dataset_id)
        artifact = storage_put(f"workspaces/{dataset.workspace_id}/curated/{dataset.id}/v{version.version_number}.parquet", curated_bytes, "application/octet-stream")
        crud.set_version_status(db, version.id, DatasetStatus.ready, row_count=len(mapped_rows), curated_storage_key=artifact["key"])
        job.status, job.stage, job.progress = "ready", "complete", 100
        db.commit()
    except Exception as error:
        job.status, job.stage, job.progress, job.error_message = "failed", "failed", 100, str(error)[:1000]
        if job.dataset_version_id:
            try: crud.set_version_status(db, job.dataset_version_id, DatasetStatus.failed)
            except Exception: db.rollback()
        db.commit()
