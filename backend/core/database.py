"""
Conexión a PostgreSQL vía SQLAlchemy (core, según AGENTS.md).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from core.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependencia FastAPI. Se propaga la misma Session entre services
    cuando una feature necesita atomicidad entre módulos (RN-10, ver plan.md de 001)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
