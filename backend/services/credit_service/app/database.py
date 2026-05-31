import sys
from pathlib import Path

from sqlalchemy import inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

_SERVICES_ROOT = Path(__file__).resolve().parents[2]
if str(_SERVICES_ROOT) not in sys.path:
    sys.path.insert(0, str(_SERVICES_ROOT))

from common.db_config import create_db_engine, is_sqlite, resolve_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "credit.db"
DATABASE_URL = resolve_database_url("CREDIT_DATABASE_URL", DB_PATH)

engine = create_db_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


CATALOGO_TIPOS = [
    {"codigo": "Emprendedor", "nombre": "Crédito Emprendedor", "tea_anual": 14.5},
    {"codigo": "Vivienda", "nombre": "Crédito Vivienda", "tea_anual": 10.5},
    {"codigo": "Agrícola", "nombre": "Crédito Agrícola", "tea_anual": 12.0},
]


def _sembrar_catalogo() -> None:
    from app.models import TipoCredito

    with SessionLocal() as db:
        for item in CATALOGO_TIPOS:
            if not db.query(TipoCredito).filter(TipoCredito.codigo == item["codigo"]).first():
                db.add(TipoCredito(**item))
        db.commit()


def _migrar_esquema_legacy() -> None:
    """Migra solicitudes con JSON (cronograma/auditoria) al esquema relacional 3FN (solo SQLite)."""
    import json
    from datetime import date, datetime
    from uuid import uuid4

    from app.models import CuotaCredito, EvaluacionFinanciera, Solicitud, TipoCredito

    inspector = inspect(engine)
    if "solicitudes" not in inspector.get_table_names():
        return

    columnas = {c["name"] for c in inspector.get_columns("solicitudes")}
    if "cronograma" not in columnas and "auditoria" not in columnas:
        return

    with engine.connect() as conn:
        filas = conn.execute(
            text(
                "SELECT id_solicitud, dni_usuario, monto, plazo_meses, tipo_credito, "
                "estado, estado_evaluacion, mensaje, observaciones, auditoria, cronograma, fecha_registro "
                "FROM solicitudes"
            )
        ).mappings().all()

    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS solicitudes"))

    Base.metadata.create_all(bind=engine)
    _sembrar_catalogo()

    with SessionLocal() as db:
        for fila in filas:
            codigo_tipo = fila["tipo_credito"]
            if not db.query(TipoCredito).filter(TipoCredito.codigo == codigo_tipo).first():
                catalogo = next((t for t in CATALOGO_TIPOS if t["codigo"] == codigo_tipo), None)
                if catalogo:
                    db.add(TipoCredito(**catalogo))
                else:
                    db.add(TipoCredito(codigo=codigo_tipo, nombre=codigo_tipo, tea_anual=14.5))
                db.commit()

            fecha_raw = fila["fecha_registro"]
            if isinstance(fecha_raw, str):
                fecha_registro = datetime.fromisoformat(fecha_raw.replace("Z", "+00:00"))
            else:
                fecha_registro = fecha_raw

            solicitud = Solicitud(
                id_solicitud=fila["id_solicitud"],
                dni_usuario=fila["dni_usuario"],
                id_tipo_credito=fila["tipo_credito"],
                monto=fila["monto"],
                plazo_meses=fila["plazo_meses"],
                estado_preaprobacion=fila["estado"],
                estado_evaluacion=fila["estado_evaluacion"],
                mensaje=fila["mensaje"] or "",
                observaciones=fila["observaciones"] or "",
                fecha_registro=fecha_registro,
            )

            auditoria_raw = fila["auditoria"]
            if auditoria_raw:
                auditoria = json.loads(auditoria_raw) if isinstance(auditoria_raw, str) else auditoria_raw
                if auditoria:
                    solicitud.evaluacion_financiera = EvaluacionFinanciera(
                        id_evaluacion=str(uuid4()),
                        tea_aplicada=auditoria.get("tea_aplicada", 0),
                        tasa_mensual_efectiva=auditoria.get("tasa_mensual_efectiva", 0),
                        cuota_mensual=auditoria.get("cuota_mensual", 0),
                        interes_total=auditoria.get("interes_total", 0),
                        monto_total_a_pagar=auditoria.get("monto_total_a_pagar", 0),
                    )

            cronograma_raw = fila["cronograma"]
            if cronograma_raw:
                cronograma = json.loads(cronograma_raw) if isinstance(cronograma_raw, str) else cronograma_raw
                for item in cronograma or []:
                    solicitud.cuotas.append(
                        CuotaCredito(
                            id_cuota=str(uuid4()),
                            numero_cuota=item["numero_cuota"],
                            fecha_vencimiento=date.fromisoformat(str(item["fecha_vencimiento"])[:10]),
                            cuota=item["cuota"],
                            capital=item["capital"],
                            interes=item["interes"],
                            saldo_restante=item["saldo_restante"],
                        )
                    )

            db.add(solicitud)
        db.commit()


def init_db() -> None:
    from app import models  # noqa: F401

    if is_sqlite(engine):
        inspector = inspect(engine)
        tablas = inspector.get_table_names()
        if "solicitudes" in tablas:
            columnas = {c["name"] for c in inspector.get_columns("solicitudes")}
            if "cronograma" in columnas or "auditoria" in columnas:
                _migrar_esquema_legacy()
                return

    Base.metadata.create_all(bind=engine)
    _sembrar_catalogo()
