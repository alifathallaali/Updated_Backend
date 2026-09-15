import logging
import os
import time
from datetime import datetime, timedelta, timezone
from sqlalchemy import or_
from app.database import SessionLocal
from app.models import UploadJob
from app.storage import storage_delete
from app.upload_processing import process_upload_job

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("pharmalens-upload-worker")
POLL_SECONDS = int(os.getenv("UPLOAD_WORKER_POLL_SECONDS", "3"))
STALE_HOURS = int(os.getenv("UPLOAD_STALE_HOURS", "24"))

def main():
    if SessionLocal is None: raise RuntimeError("DATABASE_URL is not configured")
    log.info("upload worker started")
    last_cleanup = 0.0
    while True:
        db = SessionLocal()
        try:
            job = db.query(UploadJob).filter(UploadJob.status == "queued").order_by(UploadJob.created_at.asc()).first()
            if job:
                log.info("processing upload job=%s file=%s", job.id, job.file_name)
                process_upload_job(db, job)
            else:
                time.sleep(POLL_SECONDS)
            if time.time() - last_cleanup > 3600:
                cutoff = datetime.now(timezone.utc) - timedelta(hours=STALE_HOURS)
                stale = db.query(UploadJob).filter(UploadJob.created_at < cutoff, or_(UploadJob.status == "created", UploadJob.status == "cancelled")).all()
                for old in stale:
                    try:
                        storage_delete(old.storage_key)
                    except Exception:
                        log.exception("could not clean storage key for job=%s", old.id)
                    db.delete(old)
                db.commit()
                last_cleanup = time.time()
                if stale: log.info("cleaned %s stale upload sessions", len(stale))
        except Exception:
            log.exception("upload worker loop failed")
            time.sleep(POLL_SECONDS)
        finally:
            db.close()

if __name__ == "__main__":
    main()
