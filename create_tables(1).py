"""Creates all tables in the configured Supabase Postgres database using the
SQLAlchemy models in app/models.py. Equivalent to running supabase_schema.sql
by hand. Run once: `python create_tables.py`
"""
from app.database import Base, engine
from app import models  # noqa: F401 (import registers the models on Base.metadata)

if __name__ == "__main__":
    if engine is None:
        raise SystemExit("DATABASE_URL is not set. Copy .env.example to .env and fill it in first.")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")
