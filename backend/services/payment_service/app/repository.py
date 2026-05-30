from datetime import date, datetime, timezone
from typing import Any

from app.database import SessionLocal
from app.models import Aportacion


def _to_dict(aportacion: Aportacion) -> dict[str, Any]:
    return {
        "id_aportacion": aportacion.id_aportacion,
        "id_solicitud": aportacion.id_solicitud,
        "dni_socio": aportacion.dni_socio,
        "nombre_socio": aportacion.nombre_socio,
        "numero_cuota": aportacion.numero_cuota,
        "monto_cuota": aportacion.monto_cuota,
        "fecha_vencimiento": aportacion.fecha_vencimiento,
        "fecha_pago": aportacion.fecha_pago,
    }


def guardar_lote(lote: list[dict[str, Any]]) -> list[dict[str, Any]]:
    with SessionLocal() as db:
        registros = [
            Aportacion(
                id_aportacion=item["id_aportacion"],
                id_solicitud=item["id_solicitud"],
                dni_socio=item["dni_socio"],
                nombre_socio=item.get("nombre_socio", ""),
                numero_cuota=item["numero_cuota"],
                monto_cuota=item["monto_cuota"],
                fecha_vencimiento=item["fecha_vencimiento"],
                fecha_pago=item.get("fecha_pago"),
            )
            for item in lote
        ]
        db.add_all(registros)
        db.commit()
        return lote


def listar_aportaciones(dni: str | None = None) -> list[dict[str, Any]]:
    with SessionLocal() as db:
        query = db.query(Aportacion).order_by(
            Aportacion.fecha_vencimiento.desc(),
            Aportacion.numero_cuota.desc(),
        )
        if dni:
            query = query.filter(Aportacion.dni_socio == dni)
        return [_to_dict(a) for a in query.all()]


def obtener_aportacion(id_aportacion: str) -> dict[str, Any] | None:
    with SessionLocal() as db:
        aportacion = db.query(Aportacion).filter(Aportacion.id_aportacion == id_aportacion).first()
        return _to_dict(aportacion) if aportacion else None


def actualizar_aportacion(id_aportacion: str, datos: dict[str, Any]) -> dict[str, Any] | None:
    with SessionLocal() as db:
        aportacion = db.query(Aportacion).filter(Aportacion.id_aportacion == id_aportacion).first()
        if not aportacion:
            return None
        for clave, valor in datos.items():
            if hasattr(aportacion, clave):
                setattr(aportacion, clave, valor)
        db.commit()
        db.refresh(aportacion)
        return _to_dict(aportacion)


def _estado(aportacion: dict[str, Any]) -> str:
    if aportacion.get("fecha_pago"):
        return "PAGADO"
    vencimiento = date.fromisoformat(aportacion["fecha_vencimiento"])
    if vencimiento < date.today():
        return "VENCIDO"
    return "PENDIENTE"


def listar_con_estado(dni: str | None = None) -> list[dict[str, Any]]:
    return [{**a, "estado": _estado(a)} for a in listar_aportaciones(dni)]


def resumen_aportaciones() -> dict[str, Any]:
    items = listar_con_estado()
    pagadas = [a for a in items if a["estado"] == "PAGADO"]
    pendientes = [a for a in items if a["estado"] == "PENDIENTE"]
    vencidas = [a for a in items if a["estado"] == "VENCIDO"]
    return {
        "total": len(items),
        "pagadas": len(pagadas),
        "pendientes": len(pendientes),
        "vencidas": len(vencidas),
        "monto_pagado": round(sum(a["monto_cuota"] for a in pagadas), 2),
        "monto_pendiente": round(sum(a["monto_cuota"] for a in pendientes + vencidas), 2),
        "actualizado_en": datetime.now(timezone.utc),
    }
