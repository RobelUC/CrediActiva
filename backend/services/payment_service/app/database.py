import sys
from pathlib import Path

from sqlalchemy import inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

_SERVICES_ROOT = Path(__file__).resolve().parents[2]
if str(_SERVICES_ROOT) not in sys.path:
    sys.path.insert(0, str(_SERVICES_ROOT))

from common.db_config import create_db_engine, is_sqlite, resolve_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "payment.db"
DATABASE_URL = resolve_database_url("PAYMENT_DATABASE_URL", DB_PATH)

engine = create_db_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def _migrar_esquema_legacy() -> None:
    inspector = inspect(engine)
    if "aportaciones" not in inspector.get_table_names():
        return

    columnas = {c["name"] for c in inspector.get_columns("aportaciones")}
    if "nombre_socio" not in columnas:
        return

    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE aportaciones RENAME TO aportaciones_legacy"))
        conn.execute(
            text(
                """
                CREATE TABLE aportaciones (
                    id_aportacion VARCHAR(36) PRIMARY KEY,
                    id_solicitud VARCHAR(36) NOT NULL,
                    id_cuota VARCHAR(36),
                    dni_socio VARCHAR(8) NOT NULL,
                    numero_cuota INTEGER NOT NULL,
                    monto_cuota FLOAT NOT NULL,
                    fecha_vencimiento DATE NOT NULL,
                    fecha_pago DATE,
                    estado_pago VARCHAR(10) NOT NULL DEFAULT 'PENDIENTE',
                    UNIQUE (id_solicitud, numero_cuota)
                )
                """
            )
        )
        conn.execute(
            text(
                """
                INSERT INTO aportaciones (
                    id_aportacion, id_solicitud, dni_socio, numero_cuota,
                    monto_cuota, fecha_vencimiento, fecha_pago, estado_pago
                )
                SELECT
                    id_aportacion, id_solicitud, dni_socio, numero_cuota,
                    monto_cuota, fecha_vencimiento,
                    CASE WHEN fecha_pago IS NULL OR fecha_pago = '' THEN NULL ELSE fecha_pago END,
                    CASE
                        WHEN fecha_pago IS NOT NULL AND fecha_pago != '' THEN 'PAGADO'
                        WHEN fecha_vencimiento < date('now') THEN 'VENCIDO'
                        ELSE 'PENDIENTE'
                    END
                FROM aportaciones_legacy
                """
            )
        )
        conn.execute(text("DROP TABLE aportaciones_legacy"))


def init_db() -> None:
    from app import models  # noqa: F401

    if is_sqlite(engine):
        inspector = inspect(engine)
        if "aportaciones" in inspector.get_table_names():
            columnas = {c["name"] for c in inspector.get_columns("aportaciones")}
            if "nombre_socio" in columnas:
                _migrar_esquema_legacy()
                return

    Base.metadata.create_all(bind=engine)
