from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

# pool_pre_ping avoids stale-connection errors against Supabase's pooler.
engine = create_engine(settings.database_url, pool_pre_ping=True) if settings.database_url else None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None


class Base(DeclarativeBase):
    pass


def get_db():
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL is not configured. Set it in your .env file.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
