from datetime import date, datetime, timezone
from typing import Any

from app.database import SessionLocal
from app.models import Aportacion


def _calcular_estado(aportacion: Aportacion) -> str:
    if aportacion.fecha_pago:
        return "PAGADO"
    if aportacion.fecha_vencimiento < date.today():
        return "VENCIDO"
    return "PENDIENTE"


def _to_dict(aportacion: Aportacion) -> dict[str, Any]:
    estado = aportacion.estado_pago or _calcular_estado(aportacion)
    return {
        "id_aportacion": aportacion.id_aportacion,
        "id_solicitud": aportacion.id_solicitud,
        "id_cuota": aportacion.id_cuota,
        "dni_socio": aportacion.dni_socio,
        "numero_cuota": aportacion.numero_cuota,
        "monto_cuota": aportacion.monto_cuota,
        "fecha_vencimiento": aportacion.fecha_vencimiento.isoformat(),
        "fecha_pago": aportacion.fecha_pago.isoformat() if aportacion.fecha_pago else None,
        "estado": estado,
    }


def _parse_date(valor: date | str | None) -> date | None:
    if valor is None:
        return None
    if isinstance(valor, date):
        return valor
    return date.fromisoformat(valor)


def guardar_lote(lote: list[dict[str, Any]]) -> list[dict[str, Any]]:
    with SessionLocal() as db:
        registros: list[Aportacion] = []
        for item in lote:
            vencimiento = _parse_date(item["fecha_vencimiento"])
            if vencimiento is None:
                continue
            pago = _parse_date(item.get("fecha_pago"))
            aportacion = Aportacion(
                id_aportacion=item["id_aportacion"],
                id_solicitud=item["id_solicitud"],
                id_cuota=item.get("id_cuota"),
                dni_socio=item["dni_socio"],
                numero_cuota=item["numero_cuota"],
                monto_cuota=item["monto_cuota"],
                fecha_vencimiento=vencimiento,
                fecha_pago=pago,
                estado_pago="PAGADO" if pago else "PENDIENTE",
            )
            if not pago and vencimiento < date.today():
                aportacion.estado_pago = "VENCIDO"
            registros.append(aportacion)
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
        items = query.all()
        for item in items:
            item.estado_pago = _calcular_estado(item)
        db.commit()
        return [_to_dict(a) for a in items]


def obtener_aportacion(id_aportacion: str) -> dict[str, Any] | None:
    with SessionLocal() as db:
        aportacion = db.query(Aportacion).filter(Aportacion.id_aportacion == id_aportacion).first()
        if not aportacion:
            return None
        aportacion.estado_pago = _calcular_estado(aportacion)
        db.commit()
        return _to_dict(aportacion)


def actualizar_aportacion(id_aportacion: str, datos: dict[str, Any]) -> dict[str, Any] | None:
    with SessionLocal() as db:
        aportacion = db.query(Aportacion).filter(Aportacion.id_aportacion == id_aportacion).first()
        if not aportacion:
            return None

        if "fecha_pago" in datos:
            aportacion.fecha_pago = _parse_date(datos["fecha_pago"])
        for clave in ("monto_cuota", "numero_cuota", "estado_pago"):
            if clave in datos and datos[clave] is not None:
                setattr(aportacion, clave, datos[clave])

        aportacion.estado_pago = _calcular_estado(aportacion)
        db.commit()
        db.refresh(aportacion)
        return _to_dict(aportacion)


def _estado(aportacion: dict[str, Any]) -> str:
    if aportacion.get("estado"):
        return aportacion["estado"]
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


def eliminar_por_dni(dni: str) -> int:
    with SessionLocal() as db:
        items = db.query(Aportacion).filter(Aportacion.dni_socio == dni).all()
        cantidad = len(items)
        for item in items:
            db.delete(item)
        db.commit()
        return cantidad
