"""Lógica de negocio del portal del socio."""

from datetime import datetime, timezone

from app.services.almacen import (
    listar_aportaciones_con_estado,
    listar_solicitudes,
    obtener_socio_por_dni,
)


def solicitudes_por_dni(dni: str) -> list[dict]:
    return [s for s in listar_solicitudes() if s.get("dni_usuario") == dni]


def aportaciones_por_dni(dni: str) -> list[dict]:
    return [a for a in listar_aportaciones_con_estado() if a.get("dni_socio") == dni]


def _tipo_credito_solicitud(id_solicitud: str) -> str:
    for s in listar_solicitudes():
        if s["id_solicitud"] == id_solicitud:
            return s.get("tipo_credito", "")
    return ""


def calcular_resumen_cuenta(dni: str) -> dict:
    socio = obtener_socio_por_dni(dni)
    solicitudes = solicitudes_por_dni(dni)
    aportes = aportaciones_por_dni(dni)

    creditos_aprobados = [s for s in solicitudes if s.get("estado_evaluacion") == "APROBADO"]
    pagadas = [a for a in aportes if a["estado"] == "PAGADO"]
    pendientes = [a for a in aportes if a["estado"] == "PENDIENTE"]
    vencidas = [a for a in aportes if a["estado"] == "VENCIDO"]

    saldo = round(sum(a["monto_cuota"] for a in pendientes + vencidas), 2)
    monto_credito = round(sum(s.get("monto", 0) for s in creditos_aprobados), 2)

    proxima = None
    if pendientes:
        prox = min(pendientes, key=lambda x: x["fecha_vencimiento"])
        proxima = {
            "fecha_vencimiento": prox["fecha_vencimiento"],
            "monto": prox["monto_cuota"],
            "numero_cuota": prox["numero_cuota"],
        }

    if vencidas:
        estado = "MOROSO"
    elif pendientes:
        estado = "PENDIENTE"
    else:
        estado = "AL_DIA"

    nombres = socio["nombres"] if socio else "Socio"
    apellidos = socio["apellidos"] if socio else "CrediActiva"
    email = socio["email"] if socio else f"socio{dni}@crediactiva.pe"
    telefono = socio.get("telefono", "") if socio else ""
    aporte = socio.get("aporte_mensual", 50.0) if socio else 50.0

    return {
        "dni": dni,
        "nombres": nombres,
        "apellidos": apellidos,
        "email": email,
        "telefono": telefono,
        "aporte_mensual": aporte,
        "creditos_activos": len(creditos_aprobados),
        "monto_total_credito": monto_credito,
        "saldo_pendiente": saldo,
        "cuotas_pagadas": len(pagadas),
        "cuotas_pendientes": len(pendientes),
        "cuotas_vencidas": len(vencidas),
        "proxima_cuota": proxima,
        "estado_cuenta": estado,
        "actualizado_en": datetime.now(timezone.utc),
    }


def listar_creditos_socio(dni: str) -> list[dict]:
    resultado = []
    for s in solicitudes_por_dni(dni):
        aportes_credito = [a for a in aportaciones_por_dni(dni) if a["id_solicitud"] == s["id_solicitud"]]
        pagadas = sum(1 for a in aportes_credito if a["estado"] == "PAGADO")
        saldo = round(sum(a["monto_cuota"] for a in aportes_credito if a["estado"] != "PAGADO"), 2)
        cronograma = s.get("cronograma", [])
        cuota = cronograma[0]["cuota"] if cronograma else 0

        resultado.append(
            {
                "id_solicitud": s["id_solicitud"],
                "tipo_credito": s.get("tipo_credito", "Emprendedor"),
                "monto": s.get("monto", 0),
                "plazo_meses": s.get("plazo_meses", 0),
                "estado_evaluacion": s.get("estado_evaluacion", "PENDIENTE"),
                "estado_preaprobacion": s.get("estado", "EN_REVISION"),
                "cuota_mensual": cuota,
                "saldo_pendiente": saldo,
                "cuotas_pagadas": pagadas,
                "fecha_registro": s.get("fecha_registro", datetime.now(timezone.utc)),
                "cronograma": cronograma,
            }
        )
    return resultado


def historial_aportes_socio(dni: str) -> list[dict]:
    items = sorted(
        aportaciones_por_dni(dni),
        key=lambda x: (x["fecha_vencimiento"], x["numero_cuota"]),
        reverse=True,
    )
    return [
        {
            **a,
            "tipo_credito": _tipo_credito_solicitud(a["id_solicitud"]),
        }
        for a in items
    ]


def obtener_perfil_socio(dni: str) -> dict:
    socio = obtener_socio_por_dni(dni)
    if socio:
        return {
            "id_socio": socio["id_socio"],
            "nombres": socio["nombres"],
            "apellidos": socio["apellidos"],
            "dni": socio["dni"],
            "email": socio["email"],
            "telefono": socio.get("telefono", ""),
            "aporte_mensual": socio.get("aporte_mensual", 50.0),
            "fecha_registro": socio.get("fecha_registro"),
        }
    return {
        "id_socio": None,
        "nombres": "Socio",
        "apellidos": "CrediActiva",
        "dni": dni,
        "email": f"socio{dni}@crediactiva.pe",
        "telefono": "",
        "aporte_mensual": 50.0,
        "fecha_registro": None,
    }
