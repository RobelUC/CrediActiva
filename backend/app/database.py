"""Configuración de SQLite y sesiones SQLAlchemy."""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "crediactiva.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    """Crea las tablas si no existen."""
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db():
    """Generador de sesión para dependencias FastAPI (uso opcional)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
