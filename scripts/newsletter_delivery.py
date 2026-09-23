"""Run due newsletter deliveries once. Schedule externally (e.g. hourly cron)."""
from app.database import SessionLocal
from app.services.newsletter import deliver_due_newsletters

if __name__ == "__main__":
    db=SessionLocal()
    try:
        print(deliver_due_newsletters(db))
    finally:
        db.close()
