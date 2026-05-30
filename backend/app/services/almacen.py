"""Capa de persistencia — SQLite vía SQLAlchemy."""

from datetime import date, datetime, timezone
from typing import Any

from app.database import SessionLocal
from app.models.aportacion import Aportacion
from app.models.socio import Socio
from app.models.solicitud import Solicitud


def _parse_fecha_registro(valor: datetime | str) -> datetime:
    if isinstance(valor, datetime):
        return valor if valor.tzinfo else valor.replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(valor.replace("Z", "+00:00"))


def _socio_a_dict(socio: Socio) -> dict[str, Any]:
    return {
        "id_socio": socio.id_socio,
        "nombres": socio.nombres,
        "apellidos": socio.apellidos,
        "dni": socio.dni,
        "email": socio.email,
        "telefono": socio.telefono,
        "aporte_mensual": socio.aporte_mensual,
        "fecha_registro": socio.fecha_registro,
        "activo": socio.activo,
    }


def _solicitud_a_dict(solicitud: Solicitud) -> dict[str, Any]:
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


def _aportacion_a_dict(aportacion: Aportacion) -> dict[str, Any]:
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


def guardar_socio(registro: dict[str, Any]) -> dict[str, Any]:
    with SessionLocal() as db:
        socio = db.query(Socio).filter(Socio.dni == registro["dni"]).first()
        fecha = _parse_fecha_registro(registro.get("fecha_registro", datetime.now(timezone.utc)))

        if socio:
            socio.id_socio = registro.get("id_socio", socio.id_socio)
            socio.nombres = registro["nombres"]
            socio.apellidos = registro["apellidos"]
            socio.email = registro["email"]
            socio.telefono = registro.get("telefono", socio.telefono)
            socio.aporte_mensual = round(registro.get("aporte_mensual", socio.aporte_mensual), 2)
            socio.activo = registro.get("activo", socio.activo)
        else:
            socio = Socio(
                id_socio=registro["id_socio"],
                dni=registro["dni"],
                nombres=registro["nombres"],
                apellidos=registro["apellidos"],
                email=registro["email"],
                telefono=registro.get("telefono", ""),
                aporte_mensual=round(registro.get("aporte_mensual", 50.0), 2),
                fecha_registro=fecha,
                activo=registro.get("activo", True),
            )
            db.add(socio)

        db.commit()
        db.refresh(socio)
        return _socio_a_dict(socio)


def obtener_socio_por_dni(dni: str) -> dict[str, Any] | None:
    with SessionLocal() as db:
        socio = db.query(Socio).filter(Socio.dni == dni).first()
        return _socio_a_dict(socio) if socio else None


def listar_socios() -> list[dict[str, Any]]:
    with SessionLocal() as db:
        socios = db.query(Socio).order_by(Socio.fecha_registro.desc()).all()
        return [_socio_a_dict(s) for s in socios]


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
            fecha_registro=_parse_fecha_registro(registro["fecha_registro"]),
        )
        db.add(solicitud)
        db.commit()
        db.refresh(solicitud)
        return _solicitud_a_dict(solicitud)


def listar_solicitudes() -> list[dict[str, Any]]:
    with SessionLocal() as db:
        solicitudes = db.query(Solicitud).order_by(Solicitud.fecha_registro.desc()).all()
        return [_solicitud_a_dict(s) for s in solicitudes]


def obtener_solicitud(id_solicitud: str) -> dict[str, Any] | None:
    with SessionLocal() as db:
        solicitud = db.query(Solicitud).filter(Solicitud.id_solicitud == id_solicitud).first()
        return _solicitud_a_dict(solicitud) if solicitud else None


def actualizar_solicitud(id_solicitud: str, datos: dict[str, Any]) -> dict[str, Any] | None:
    with SessionLocal() as db:
        solicitud = db.query(Solicitud).filter(Solicitud.id_solicitud == id_solicitud).first()
        if not solicitud:
            return None

        for clave, valor in datos.items():
            if clave == "fecha_registro" and valor is not None:
                setattr(solicitud, clave, _parse_fecha_registro(valor))
            elif hasattr(solicitud, clave):
                setattr(solicitud, clave, valor)

        db.commit()
        db.refresh(solicitud)
        return _solicitud_a_dict(solicitud)


def guardar_aportaciones(lote: list[dict[str, Any]]) -> list[dict[str, Any]]:
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


def listar_aportaciones() -> list[dict[str, Any]]:
    with SessionLocal() as db:
        aportaciones = (
            db.query(Aportacion)
            .order_by(Aportacion.fecha_vencimiento.desc(), Aportacion.numero_cuota.desc())
            .all()
        )
        return [_aportacion_a_dict(a) for a in aportaciones]


def obtener_aportacion(id_aportacion: str) -> dict[str, Any] | None:
    with SessionLocal() as db:
        aportacion = db.query(Aportacion).filter(Aportacion.id_aportacion == id_aportacion).first()
        return _aportacion_a_dict(aportacion) if aportacion else None


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
        return _aportacion_a_dict(aportacion)


def _estado_aportacion_en_fecha(aportacion: dict[str, Any]) -> str:
    if aportacion.get("fecha_pago"):
        return "PAGADO"
    vencimiento = date.fromisoformat(aportacion["fecha_vencimiento"])
    if vencimiento < date.today():
        return "VENCIDO"
    return "PENDIENTE"


def listar_aportaciones_con_estado() -> list[dict[str, Any]]:
    return [
        {**aportacion, "estado": _estado_aportacion_en_fecha(aportacion)}
        for aportacion in listar_aportaciones()
    ]


def resumen_aportaciones() -> dict[str, Any]:
    items = listar_aportaciones_con_estado()
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
