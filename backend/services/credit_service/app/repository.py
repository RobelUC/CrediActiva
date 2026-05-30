from datetime import datetime, timezone
from typing import Any

from app.database import SessionLocal
from app.models import Solicitud


def _parse_fecha(valor: datetime | str) -> datetime:
    if isinstance(valor, datetime):
        return valor if valor.tzinfo else valor.replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(valor.replace("Z", "+00:00"))


def _to_dict(solicitud: Solicitud) -> dict[str, Any]:
    return {
        "id_solicitud": solicitud.id_solicitud,
        "dni_usuario": solicitud.dni_usuario,
        "monto": solicitud.monto,
        "plazo_meses": solicitud.plazo_meses,
        "tipo_credito": solicitud.tipo_credito,
        "estado": solicitud.estado,
        "estado_evaluacion": solicitud.estado_evaluacion,
        "mensaje": solicitud.mensaje,
        "observaciones": solicitud.observaciones,
        "auditoria": solicitud.auditoria or {},
        "cronograma": solicitud.cronograma or [],
        "fecha_registro": solicitud.fecha_registro,
    }


def guardar_solicitud(registro: dict[str, Any]) -> dict[str, Any]:
    registro.setdefault("estado_evaluacion", "PENDIENTE")
    registro.setdefault("observaciones", "")
    registro.setdefault("cronograma", [])
    registro.setdefault("mensaje", "")

    with SessionLocal() as db:
        solicitud = Solicitud(
            id_solicitud=registro["id_solicitud"],
            dni_usuario=registro["dni_usuario"],
            monto=registro["monto"],
            plazo_meses=registro["plazo_meses"],
            tipo_credito=registro["tipo_credito"],
            estado=registro["estado"],
            estado_evaluacion=registro["estado_evaluacion"],
            mensaje=registro.get("mensaje", ""),
            observaciones=registro["observaciones"],
            auditoria=registro.get("auditoria"),
            cronograma=registro["cronograma"],
            fecha_registro=_parse_fecha(registro["fecha_registro"]),
        )
        db.add(solicitud)
        db.commit()
        db.refresh(solicitud)
        return _to_dict(solicitud)


def listar_solicitudes(dni: str | None = None) -> list[dict[str, Any]]:
    with SessionLocal() as db:
        query = db.query(Solicitud).order_by(Solicitud.fecha_registro.desc())
        if dni:
            query = query.filter(Solicitud.dni_usuario == dni)
        return [_to_dict(s) for s in query.all()]


def obtener_solicitud(id_solicitud: str) -> dict[str, Any] | None:
    with SessionLocal() as db:
        solicitud = db.query(Solicitud).filter(Solicitud.id_solicitud == id_solicitud).first()
        return _to_dict(solicitud) if solicitud else None


def actualizar_solicitud(id_solicitud: str, datos: dict[str, Any]) -> dict[str, Any] | None:
    with SessionLocal() as db:
        solicitud = db.query(Solicitud).filter(Solicitud.id_solicitud == id_solicitud).first()
        if not solicitud:
            return None

        for clave, valor in datos.items():
            if clave == "fecha_registro" and valor is not None:
                setattr(solicitud, clave, _parse_fecha(valor))
            elif hasattr(solicitud, clave):
                setattr(solicitud, clave, valor)

        db.commit()
        db.refresh(solicitud)
        return _to_dict(solicitud)
