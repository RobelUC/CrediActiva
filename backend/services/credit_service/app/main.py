import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException, status

from app.calculadora import (
    calcular_auditoria_credito,
    construir_mensaje_exito,
    determinar_estado_preaprobacion,
)
from app.cronograma import generar_cronograma
from app.database import init_db
from app.repository import actualizar_solicitud, eliminar_por_dni, guardar_solicitud, listar_solicitudes, obtener_solicitud
from app.schemas import (
    EvaluarSolicitudRequest,
    SolicitudAdminResponse,
    SolicitudCredito,
    SolicitudCreditoResponse,
)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8003")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Credit Service", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "servicio": "credit-service"}


@app.post(
    "/api/v1/solicitudes",
    response_model=SolicitudCreditoResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_solicitud(payload: SolicitudCredito) -> SolicitudCreditoResponse:
    auditoria = calcular_auditoria_credito(payload.monto, payload.plazo_meses, payload.tipo_credito)
    estado = determinar_estado_preaprobacion(payload.monto)
    id_solicitud = str(uuid4())
    fecha = datetime.now(timezone.utc)

    respuesta = SolicitudCreditoResponse(
        id_solicitud=id_solicitud,
        estado=estado,
        mensaje=construir_mensaje_exito(estado, payload.dni_usuario, payload.tipo_credito, payload.monto),
        fecha_registro=fecha,
        auditoria=auditoria,
        monto=payload.monto,
        plazo_meses=payload.plazo_meses,
        tipo_credito=payload.tipo_credito,
        dni_usuario=payload.dni_usuario,
    )

    guardar_solicitud(
        {
            "id_solicitud": id_solicitud,
            "fecha_registro": fecha.isoformat(),
            **respuesta.model_dump(mode="json"),
        }
    )
    return respuesta


@app.get("/api/v1/admin/solicitudes", response_model=list[SolicitudAdminResponse])
def obtener_solicitudes_admin() -> list[SolicitudAdminResponse]:
    return [_map_admin(s) for s in listar_solicitudes()]


@app.get("/api/v1/admin/solicitudes/{id_solicitud}", response_model=SolicitudAdminResponse)
def obtener_solicitud_admin(id_solicitud: str) -> SolicitudAdminResponse:
    solicitud = obtener_solicitud(id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
    return _map_admin(solicitud)


@app.post("/api/v1/admin/solicitudes/{id_solicitud}/evaluar", response_model=SolicitudAdminResponse)
def evaluar_solicitud(id_solicitud: str, payload: EvaluarSolicitudRequest) -> SolicitudAdminResponse:
    solicitud = obtener_solicitud(id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
    if solicitud.get("estado_evaluacion") != "PENDIENTE":
        raise HTTPException(status_code=400, detail="La solicitud ya fue evaluada.")

    cronograma: list[dict] = []
    if payload.decision == "APROBADO":
        cronograma = generar_cronograma(
            solicitud["monto"],
            solicitud["plazo_meses"],
            solicitud["tipo_credito"],
        )

    actualizada = actualizar_solicitud(
        id_solicitud,
        {
            "estado_evaluacion": payload.decision,
            "observaciones": payload.observaciones,
            "cronograma": cronograma,
        },
    )

    if payload.decision == "APROBADO" and actualizada:
        _crear_aportaciones(actualizada)

    return _map_admin(actualizada)  # type: ignore[arg-type]


@app.get("/internal/solicitudes")
def solicitudes_internas(dni: str | None = None) -> list[dict]:
    return listar_solicitudes(dni)


@app.delete("/internal/datos-socio/{dni}")
def eliminar_datos_socio(dni: str) -> dict[str, int]:
    return {"solicitudes_eliminadas": eliminar_por_dni(dni)}


def _crear_aportaciones(solicitud: dict) -> None:
    dni = solicitud["dni_usuario"]
    lote = [
        {
            "id_aportacion": str(uuid4()),
            "id_solicitud": solicitud["id_solicitud"],
            "id_cuota": cuota.get("id_cuota"),
            "dni_socio": dni,
            "numero_cuota": cuota["numero_cuota"],
            "monto_cuota": cuota["cuota"],
            "fecha_vencimiento": cuota["fecha_vencimiento"],
            "fecha_pago": None,
        }
        for cuota in solicitud.get("cronograma", [])
    ]
    with httpx.Client(timeout=10.0) as client:
        resp = client.post(f"{PAYMENT_SERVICE_URL}/internal/aportaciones/lote", json={"items": lote})
        if resp.status_code >= 400:
            raise HTTPException(status_code=502, detail="Error al registrar cuotas en payment-service.")


def _map_admin(s: dict) -> SolicitudAdminResponse:
    return SolicitudAdminResponse(
        id_solicitud=s["id_solicitud"],
        dni_usuario=s.get("dni_usuario", ""),
        monto=s.get("monto", 0),
        plazo_meses=s.get("plazo_meses", 0),
        tipo_credito=s.get("tipo_credito", "Emprendedor"),
        estado_preaprobacion=s.get("estado", "EN_REVISION"),
        estado_evaluacion=s.get("estado_evaluacion", "PENDIENTE"),
        fecha_registro=s.get("fecha_registro", datetime.now(timezone.utc)),
        observaciones=s.get("observaciones", ""),
        cronograma=s.get("cronograma", []),
    )
