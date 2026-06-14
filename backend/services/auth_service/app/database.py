"""Auth Service — gestión de socios."""

import sys
from pathlib import Path

from sqlalchemy import inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

_SERVICES_ROOT = Path(__file__).resolve().parents[2]
if str(_SERVICES_ROOT) not in sys.path:
    sys.path.insert(0, str(_SERVICES_ROOT))

from common.db_config import create_db_engine, is_sqlite, resolve_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "auth.db"
DATABASE_URL = resolve_database_url("AUTH_DATABASE_URL", DB_PATH)

engine = create_db_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    if "socios" not in inspector.get_table_names():
        return

    columnas = {c["name"] for c in inspector.get_columns("socios")}
    if "password_hash" not in columnas:
        with engine.begin() as conn:
            if is_sqlite(engine):
                conn.execute(text("ALTER TABLE socios ADD COLUMN password_hash VARCHAR(255)"))
            else:
                conn.execute(text("ALTER TABLE socios ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)"))

    columnas = {c["name"] for c in inspector.get_columns("socios")}
    if "rol" not in columnas:
        with engine.begin() as conn:
            if is_sqlite(engine):
                conn.execute(text("ALTER TABLE socios ADD COLUMN rol VARCHAR(10) NOT NULL DEFAULT 'socio'"))
            else:
                conn.execute(text("ALTER TABLE socios ADD COLUMN IF NOT EXISTS rol VARCHAR(10) NOT NULL DEFAULT 'socio'"))
