from datetime import date, datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import joinedload

from app.database import SessionLocal
from app.models import CuotaCredito, EvaluacionFinanciera, Solicitud, TipoCredito


def _parse_fecha(valor: datetime | str) -> datetime:
    if isinstance(valor, datetime):
        return valor if valor.tzinfo else valor.replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(valor.replace("Z", "+00:00"))


def _parse_date(valor: date | str) -> date:
    if isinstance(valor, date):
        return valor
    return date.fromisoformat(valor)


def _auditoria_dict(evaluacion: EvaluacionFinanciera | None) -> dict[str, Any]:
    if not evaluacion:
        return {}
    return {
        "tea_aplicada": evaluacion.tea_aplicada,
        "tasa_mensual_efectiva": evaluacion.tasa_mensual_efectiva,
        "cuota_mensual": evaluacion.cuota_mensual,
        "interes_total": evaluacion.interes_total,
        "monto_total_a_pagar": evaluacion.monto_total_a_pagar,
    }


def _cronograma_dict(cuotas: list[CuotaCredito]) -> list[dict[str, Any]]:
    return [
        {
            "id_cuota": c.id_cuota,
            "numero_cuota": c.numero_cuota,
            "fecha_vencimiento": c.fecha_vencimiento.isoformat(),
            "cuota": c.cuota,
            "capital": c.capital,
            "interes": c.interes,
            "saldo_restante": c.saldo_restante,
        }
        for c in cuotas
    ]


def _to_dict(solicitud: Solicitud) -> dict[str, Any]:
    return {
        "id_solicitud": solicitud.id_solicitud,
        "dni_usuario": solicitud.dni_usuario,
        "monto": solicitud.monto,
        "plazo_meses": solicitud.plazo_meses,
        "tipo_credito": solicitud.tipo_credito.codigo if solicitud.tipo_credito else solicitud.id_tipo_credito,
        "estado": solicitud.estado_preaprobacion,
        "estado_evaluacion": solicitud.estado_evaluacion,
        "mensaje": solicitud.mensaje,
        "observaciones": solicitud.observaciones,
        "auditoria": _auditoria_dict(solicitud.evaluacion_financiera),
        "cronograma": _cronograma_dict(solicitud.cuotas),
        "fecha_registro": solicitud.fecha_registro,
    }


def _cargar_solicitud(db, id_solicitud: str) -> Solicitud | None:
    return (
        db.query(Solicitud)
        .options(
            joinedload(Solicitud.tipo_credito),
            joinedload(Solicitud.evaluacion_financiera),
            joinedload(Solicitud.cuotas),
        )
        .filter(Solicitud.id_solicitud == id_solicitud)
        .first()
    )


def guardar_solicitud(registro: dict[str, Any]) -> dict[str, Any]:
    registro.setdefault("estado_evaluacion", "PENDIENTE")
    registro.setdefault("observaciones", "")
    registro.setdefault("mensaje", "")

    auditoria = registro.get("auditoria") or {}
    tipo_codigo = registro.get("tipo_credito") or registro.get("id_tipo_credito")

    with SessionLocal() as db:
        tipo = db.query(TipoCredito).filter(TipoCredito.codigo == tipo_codigo).first()
        if not tipo:
            raise ValueError(f"Tipo de crédito '{tipo_codigo}' no existe en catálogo.")

        solicitud = Solicitud(
            id_solicitud=registro["id_solicitud"],
            dni_usuario=registro["dni_usuario"],
            id_tipo_credito=tipo.codigo,
            monto=registro["monto"],
            plazo_meses=registro["plazo_meses"],
            estado_preaprobacion=registro.get("estado") or registro.get("estado_preaprobacion", "EN_REVISION"),
            estado_evaluacion=registro["estado_evaluacion"],
            mensaje=registro.get("mensaje", ""),
            observaciones=registro["observaciones"],
            fecha_registro=_parse_fecha(registro["fecha_registro"]),
        )

        if auditoria:
            solicitud.evaluacion_financiera = EvaluacionFinanciera(
                id_evaluacion=str(uuid4()),
                tea_aplicada=auditoria["tea_aplicada"],
                tasa_mensual_efectiva=auditoria["tasa_mensual_efectiva"],
                cuota_mensual=auditoria["cuota_mensual"],
                interes_total=auditoria["interes_total"],
                monto_total_a_pagar=auditoria["monto_total_a_pagar"],
            )

        db.add(solicitud)
        db.commit()
        return _to_dict(_cargar_solicitud(db, solicitud.id_solicitud))  # type: ignore[arg-type]


def listar_solicitudes(dni: str | None = None) -> list[dict[str, Any]]:
    with SessionLocal() as db:
        query = (
            db.query(Solicitud)
            .options(
                joinedload(Solicitud.tipo_credito),
                joinedload(Solicitud.evaluacion_financiera),
                joinedload(Solicitud.cuotas),
            )
            .order_by(Solicitud.fecha_registro.desc())
        )
        if dni:
            query = query.filter(Solicitud.dni_usuario == dni)
        return [_to_dict(s) for s in query.all()]


def obtener_solicitud(id_solicitud: str) -> dict[str, Any] | None:
    with SessionLocal() as db:
        solicitud = _cargar_solicitud(db, id_solicitud)
        return _to_dict(solicitud) if solicitud else None


def actualizar_solicitud(id_solicitud: str, datos: dict[str, Any]) -> dict[str, Any] | None:
    with SessionLocal() as db:
        solicitud = _cargar_solicitud(db, id_solicitud)
        if not solicitud:
            return None

        if "estado_evaluacion" in datos:
            solicitud.estado_evaluacion = datos["estado_evaluacion"]
        if "observaciones" in datos:
            solicitud.observaciones = datos["observaciones"]
        if "estado" in datos:
            solicitud.estado_preaprobacion = datos["estado"]
        if "mensaje" in datos:
            solicitud.mensaje = datos["mensaje"]

        cronograma = datos.get("cronograma")
        if cronograma is not None:
            solicitud.cuotas.clear()
            for item in cronograma:
                solicitud.cuotas.append(
                    CuotaCredito(
                        id_cuota=item.get("id_cuota") or str(uuid4()),
                        numero_cuota=item["numero_cuota"],
                        fecha_vencimiento=_parse_date(item["fecha_vencimiento"]),
                        cuota=item["cuota"],
                        capital=item["capital"],
                        interes=item["interes"],
                        saldo_restante=item["saldo_restante"],
                    )
                )

        auditoria = datos.get("auditoria")
        if auditoria:
            if solicitud.evaluacion_financiera:
                ev = solicitud.evaluacion_financiera
                ev.tea_aplicada = auditoria["tea_aplicada"]
                ev.tasa_mensual_efectiva = auditoria["tasa_mensual_efectiva"]
                ev.cuota_mensual = auditoria["cuota_mensual"]
                ev.interes_total = auditoria["interes_total"]
                ev.monto_total_a_pagar = auditoria["monto_total_a_pagar"]
            else:
                solicitud.evaluacion_financiera = EvaluacionFinanciera(
                    id_evaluacion=str(uuid4()),
                    tea_aplicada=auditoria["tea_aplicada"],
                    tasa_mensual_efectiva=auditoria["tasa_mensual_efectiva"],
                    cuota_mensual=auditoria["cuota_mensual"],
                    interes_total=auditoria["interes_total"],
                    monto_total_a_pagar=auditoria["monto_total_a_pagar"],
                )

        db.commit()
        return _to_dict(_cargar_solicitud(db, id_solicitud))  # type: ignore[arg-type]
