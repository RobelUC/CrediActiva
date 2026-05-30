import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, HTTPException

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
CREDIT_SERVICE_URL = os.getenv("CREDIT_SERVICE_URL", "http://localhost:8002")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8003")

TEA_POR_TIPO = {
    "Emprendedor": 14.5,
    "Vivienda": 10.5,
    "Agrícola": 12.0,
}


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(title="Portal Service", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "servicio": "portal-service"}


@app.get("/api/v1/portal/{dni}/resumen")
def resumen_cuenta(dni: str) -> dict:
    _validar_dni(dni)
    socio = _fetch_socio(dni)
    solicitudes = _fetch_solicitudes(dni)
    aportes = _fetch_aportaciones(dni)

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

    return {
        "dni": dni,
        "nombres": socio.get("nombres", "Socio"),
        "apellidos": socio.get("apellidos", "CrediActiva"),
        "email": socio.get("email", f"socio{dni}@crediactiva.pe"),
        "telefono": socio.get("telefono", ""),
        "aporte_mensual": socio.get("aporte_mensual", 50.0),
        "creditos_activos": len(creditos_aprobados),
        "monto_total_credito": monto_credito,
        "saldo_pendiente": saldo,
        "cuotas_pagadas": len(pagadas),
        "cuotas_pendientes": len(pendientes),
        "cuotas_vencidas": len(vencidas),
        "proxima_cuota": proxima,
        "estado_cuenta": estado,
        "actualizado_en": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/portal/{dni}/creditos")
def mis_creditos(dni: str) -> list[dict]:
    _validar_dni(dni)
    solicitudes = _fetch_solicitudes(dni)
    aportes = _fetch_aportaciones(dni)
    resultado = []

    for s in solicitudes:
        aportes_credito = [a for a in aportes if a["id_solicitud"] == s["id_solicitud"]]
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
                "fecha_registro": s.get("fecha_registro"),
                "cronograma": cronograma,
            }
        )
    return resultado


@app.get("/api/v1/portal/{dni}/aportaciones")
def historial_aportes(dni: str) -> list[dict]:
    _validar_dni(dni)
    solicitudes = {s["id_solicitud"]: s.get("tipo_credito", "") for s in _fetch_solicitudes(dni)}
    items = sorted(
        _fetch_aportaciones(dni),
        key=lambda x: (x["fecha_vencimiento"], x["numero_cuota"]),
        reverse=True,
    )
    return [{**a, "tipo_credito": solicitudes.get(a["id_solicitud"], "")} for a in items]


@app.get("/api/v1/admin/dashboard")
def dashboard_general() -> dict:
    socios = _fetch_socios()
    solicitudes = _fetch_solicitudes()
    aportes_resumen = _fetch_resumen_aportaciones()

    pendientes = [s for s in solicitudes if s.get("estado_evaluacion") == "PENDIENTE"]
    aprobadas = [s for s in solicitudes if s.get("estado_evaluacion") == "APROBADO"]
    rechazadas = [s for s in solicitudes if s.get("estado_evaluacion") == "RECHAZADO"]

    monto_colocado = round(sum(s.get("monto", 0) for s in aprobadas), 2)
    evaluadas = len(aprobadas) + len(rechazadas)
    tasa_aprobacion = round(len(aprobadas) / evaluadas * 100, 1) if evaluadas else 0.0

    return {
        "total_socios": len(socios),
        "total_solicitudes": len(solicitudes),
        "solicitudes_pendientes": len(pendientes),
        "solicitudes_aprobadas": len(aprobadas),
        "solicitudes_rechazadas": len(rechazadas),
        "monto_colocado": monto_colocado,
        "monto_por_cobrar": aportes_resumen.get("monto_pendiente", 0),
        "tasa_aprobacion": tasa_aprobacion,
        "aportaciones": aportes_resumen,
        "actualizado_en": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/admin/reportes/auditoria")
def reportes_auditoria() -> dict:
    solicitudes = _fetch_solicitudes()
    aportes = _fetch_aportaciones()

    cartera: dict[str, dict] = {}
    auditoria = []
    interes_total_sistema = 0.0

    for s in solicitudes:
        tipo = s.get("tipo_credito", "Emprendedor")
        monto = s.get("monto", 0)
        if tipo not in cartera:
            cartera[tipo] = {"cantidad": 0, "monto_total": 0.0}
        cartera[tipo]["cantidad"] += 1
        if s.get("estado_evaluacion") == "APROBADO":
            cartera[tipo]["monto_total"] += monto

        cronograma = s.get("cronograma", [])
        cuota = cronograma[0]["cuota"] if cronograma else None
        tea = TEA_POR_TIPO.get(tipo, 0)
        interes = 0.0
        if cronograma:
            interes = round(sum(c["cuota"] for c in cronograma) - monto, 2)
            interes_total_sistema += interes

        auditoria.append(
            {
                "id_solicitud": s["id_solicitud"],
                "dni_usuario": s.get("dni_usuario", ""),
                "monto": monto,
                "tipo_credito": tipo,
                "estado_evaluacion": s.get("estado_evaluacion", "PENDIENTE"),
                "tea_aplicada": tea if s.get("estado_evaluacion") == "APROBADO" else None,
                "cuota_mensual": cuota,
                "interes_total": interes if interes else None,
                "observaciones": s.get("observaciones", ""),
            }
        )

    pagadas = sum(1 for a in aportes if a["estado"] == "PAGADO")
    vencidas = sum(1 for a in aportes if a["estado"] == "VENCIDO")

    return {
        "actualizado_en": datetime.now(timezone.utc).isoformat(),
        "cartera_por_producto": [
            {"tipo_credito": k, "cantidad": v["cantidad"], "monto_total": round(v["monto_total"], 2)}
            for k, v in cartera.items()
        ],
        "solicitudes": auditoria,
        "resumen_financiero": {
            "monto_colocado": round(
                sum(s.get("monto", 0) for s in solicitudes if s.get("estado_evaluacion") == "APROBADO"),
                2,
            ),
            "interes_generado": round(interes_total_sistema, 2),
            "cuotas_pagadas": pagadas,
            "cuotas_vencidas": vencidas,
            "indice_morosidad": round(vencidas / len(aportes) * 100, 2) if aportes else 0.0,
        },
    }


def _validar_dni(dni: str) -> None:
    if not dni.isdigit() or len(dni) != 8:
        raise HTTPException(status_code=400, detail="DNI inválido.")


def _fetch_socio(dni: str) -> dict:
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{AUTH_SERVICE_URL}/internal/socios/{dni}")
            if resp.status_code == 200:
                return resp.json()
    except httpx.HTTPError:
        pass
    return {}


def _fetch_socios() -> list[dict]:
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{AUTH_SERVICE_URL}/internal/socios")
            if resp.status_code == 200:
                return resp.json()
    except httpx.HTTPError:
        pass
    return []


def _fetch_solicitudes(dni: str | None = None) -> list[dict]:
    with httpx.Client(timeout=5.0) as client:
        params = {"dni": dni} if dni else None
        resp = client.get(f"{CREDIT_SERVICE_URL}/internal/solicitudes", params=params)
        resp.raise_for_status()
        return resp.json()


def _fetch_aportaciones(dni: str | None = None) -> list[dict]:
    with httpx.Client(timeout=5.0) as client:
        params = {"dni": dni} if dni else None
        resp = client.get(f"{PAYMENT_SERVICE_URL}/internal/aportaciones", params=params)
        resp.raise_for_status()
        return resp.json()


def _fetch_resumen_aportaciones() -> dict:
    with httpx.Client(timeout=5.0) as client:
        resp = client.get(f"{PAYMENT_SERVICE_URL}/internal/aportaciones/resumen")
        resp.raise_for_status()
        return resp.json()
