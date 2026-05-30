"""Auth Service — gestión de socios."""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "auth.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DATABASE_URL = os.getenv("AUTH_DATABASE_URL", f"sqlite:///{DB_PATH.as_posix()}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    from sqlalchemy import inspect, text

    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    if "socios" in inspector.get_table_names():
        columnas = {c["name"] for c in inspector.get_columns("socios")}
        if "password_hash" not in columnas:
            with engine.begin() as conn:
                conn.execute(
                    text("ALTER TABLE socios ADD COLUMN password_hash VARCHAR(255)")
                )
