"""Conexión compartida: SQLite local o PostgreSQL (Supabase)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

_SERVICES_ROOT = Path(__file__).resolve().parent.parent
_BACKEND_ROOT = _SERVICES_ROOT.parent

if str(_SERVICES_ROOT) not in sys.path:
    sys.path.insert(0, str(_SERVICES_ROOT))

_ENV_LOADED = False


def _ensure_env_loaded() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    load_dotenv(_BACKEND_ROOT / ".env")
    _ENV_LOADED = True


def normalize_database_url(url: str) -> str:
    """Convierte URLs de Supabase/Postgres al dialecto SQLAlchemy + psycopg."""
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://") :]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://") :]

    # Supabase exige SSL; sin esto algunas redes fallan o hacen timeout
    if url.startswith("postgresql") and "sslmode=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"
    return url


def resolve_database_url(
    service_env_key: str,
    sqlite_path: Path,
) -> str:
    """
    Prioridad: variable del servicio → SUPABASE_DATABASE_URL → DATABASE_URL → SQLite local.
    """
    _ensure_env_loaded()
    url = (
        os.getenv(service_env_key)
        or os.getenv("SUPABASE_DATABASE_URL")
        or os.getenv("DATABASE_URL")
    )
    if url:
        return normalize_database_url(url.strip())
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{sqlite_path.as_posix()}"


def create_db_engine(database_url: str) -> Engine:
    kwargs: dict = {}
    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    elif database_url.startswith("postgresql"):
        # Pool pequeño: en Render free varios microservicios comparten ~512 MB RAM.
        kwargs["pool_pre_ping"] = True
        kwargs["pool_size"] = 1
        kwargs["max_overflow"] = 0
        kwargs["connect_args"] = {
            "connect_timeout": 15,
            # Requerido con el pooler de Supabase (puerto 6543 / PgBouncer).
            "prepare_threshold": None,
        }
    return create_engine(database_url, **kwargs)


def is_sqlite(engine: Engine) -> bool:
    return engine.dialect.name == "sqlite"
