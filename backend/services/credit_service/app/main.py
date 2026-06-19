import os
import re
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException, Query, status

from app.calculadora import (
    calcular_auditoria_credito,
    construir_mensaje_exito,
    determinar_estado_preaprobacion,
)
from app.cronograma import generar_cronograma
from app.database import init_db
from app.repository import (
    MAX_SOLICITUDES_PENDIENTES,
    actualizar_solicitud,
    contar_pendientes_por_dni,
    contar_solicitudes_por_estado,
    eliminar_por_dni,
    eliminar_solicitud_socio,
    guardar_solicitud,
    listar_solicitudes,
    obtener_solicitud,
)
from app.schemas import (
    CrearCreditoAdminRequest,
    DisponibilidadSolicitudResponse,
    EstadoEvaluacion,
    EvaluarSolicitudRequest,
    ResumenSolicitudesResponse,
    SolicitudAdminResponse,
    SolicitudCredito,
    SolicitudCreditoResponse,
)

_DNI = re.compile(r"^\d{8}$")

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


@app.get(
    "/api/v1/solicitudes/disponibilidad/{dni}",
    response_model=DisponibilidadSolicitudResponse,
)
def disponibilidad_solicitud(dni: str) -> DisponibilidadSolicitudResponse:
    if not _DNI.match(dni):
        raise HTTPException(status_code=400, detail="DNI inválido.")
    pendientes = contar_pendientes_por_dni(dni)
    return DisponibilidadSolicitudResponse(
        dni_usuario=dni,
        pendientes=pendientes,
        maximo_pendientes=MAX_SOLICITUDES_PENDIENTES,
        puede_solicitar=pendientes < MAX_SOLICITUDES_PENDIENTES,
    )


@app.post(
    "/api/v1/solicitudes",
    response_model=SolicitudCreditoResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_solicitud(payload: SolicitudCredito) -> SolicitudCreditoResponse:
    return _registrar_solicitud(payload)


def _registrar_solicitud(
    payload: SolicitudCredito,
    *,
    omitir_limite_pendientes: bool = False,
) -> SolicitudCreditoResponse:
    if not omitir_limite_pendientes:
        pendientes = contar_pendientes_por_dni(payload.dni_usuario)
        if pendientes >= MAX_SOLICITUDES_PENDIENTES:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Ya tiene {pendientes} solicitudes pendientes (máximo {MAX_SOLICITUDES_PENDIENTES}). "
                    "Espere a que una sea aprobada o rechazada, o elimine una solicitud pendiente."
                ),
            )

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


@app.post(
    "/api/v1/admin/solicitudes",
    response_model=SolicitudAdminResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_credito_admin(payload: CrearCreditoAdminRequest) -> SolicitudAdminResponse:
    """Crea una solicitud y la aprueba automáticamente (cronograma + cuotas en payment-service)."""
    _verificar_socio_existe(payload.dni_usuario)

    respuesta = _registrar_solicitud(
        SolicitudCredito(
            monto=payload.monto,
            plazo_meses=payload.plazo_meses,
            tipo_credito=payload.tipo_credito,
            dni_usuario=payload.dni_usuario,
        ),
        omitir_limite_pendientes=True,
    )

    return _evaluar_solicitud_interna(
        respuesta.id_solicitud,
        decision="APROBADO",
        observaciones=payload.observaciones,
    )


@app.get("/api/v1/admin/solicitudes/resumen", response_model=ResumenSolicitudesResponse)
def obtener_resumen_solicitudes_admin() -> ResumenSolicitudesResponse:
    conteos = contar_solicitudes_por_estado()
    return ResumenSolicitudesResponse(
        pendiente=conteos["PENDIENTE"],
        aprobado=conteos["APROBADO"],
        rechazado=conteos["RECHAZADO"],
    )


@app.get("/api/v1/admin/solicitudes", response_model=list[SolicitudAdminResponse])
def obtener_solicitudes_admin(
    dni: str | None = Query(default=None, min_length=8, max_length=8),
    estado: EstadoEvaluacion | None = Query(default=None),
) -> list[SolicitudAdminResponse]:
    if dni and not re.fullmatch(r"\d{8}", dni):
        raise HTTPException(status_code=422, detail="El DNI debe contener exactamente 8 dígitos.")
    solicitudes = listar_solicitudes(
        dni=dni,
        estado=estado,
        incluir_cronograma=False,
    )
    return [_map_admin(s) for s in solicitudes]


@app.get("/api/v1/admin/solicitudes/{id_solicitud}", response_model=SolicitudAdminResponse)
def obtener_solicitud_admin(id_solicitud: str) -> SolicitudAdminResponse:
    solicitud = obtener_solicitud(id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
    return _map_admin(solicitud)


@app.post("/api/v1/admin/solicitudes/{id_solicitud}/evaluar", response_model=SolicitudAdminResponse)
def evaluar_solicitud(id_solicitud: str, payload: EvaluarSolicitudRequest) -> SolicitudAdminResponse:
    return _evaluar_solicitud_interna(
        id_solicitud,
        decision=payload.decision,
        observaciones=payload.observaciones,
    )


def _evaluar_solicitud_interna(
    id_solicitud: str,
    *,
    decision: str,
    observaciones: str,
) -> SolicitudAdminResponse:
    solicitud = obtener_solicitud(id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
    if solicitud.get("estado_evaluacion") != "PENDIENTE":
        raise HTTPException(status_code=400, detail="La solicitud ya fue evaluada.")

    cronograma: list[dict] = []
    if decision == "APROBADO":
        cronograma = generar_cronograma(
            solicitud["monto"],
            solicitud["plazo_meses"],
            solicitud["tipo_credito"],
        )

    actualizada = actualizar_solicitud(
        id_solicitud,
        {
            "estado_evaluacion": decision,
            "observaciones": observaciones,
            "cronograma": cronograma,
        },
    )

    if decision == "APROBADO" and actualizada:
        _crear_aportaciones(actualizada)

    return _map_admin(actualizada)  # type: ignore[arg-type]


def _verificar_socio_existe(dni: str) -> None:
    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(f"{AUTH_SERVICE_URL}/internal/socios/{dni}")
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="No se pudo verificar el socio en auth-service.",
        ) from exc

    if resp.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="El socio no está registrado. Créelo primero en Gestión de socios.",
        )
    if resp.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail="No se pudo verificar el socio.",
        )


@app.delete("/api/v1/solicitudes/{id_solicitud}", status_code=status.HTTP_200_OK)
def eliminar_solicitud(
    id_solicitud: str,
    dni_usuario: str = Query(..., min_length=8, max_length=8),
) -> dict[str, str]:
    if not _DNI.match(dni_usuario):
        raise HTTPException(status_code=400, detail="DNI inválido.")
    ok, mensaje = eliminar_solicitud_socio(id_solicitud, dni_usuario)
    if not ok:
        codigo = 404 if mensaje == "Solicitud no encontrada." else 400
        raise HTTPException(status_code=codigo, detail=mensaje)
    return {"mensaje": "Solicitud eliminada correctamente."}


@app.get("/internal/solicitudes")
def solicitudes_internas(
    dni: str | None = None,
    incluir_cronograma: bool = Query(default=True),
) -> list[dict]:
    return listar_solicitudes(dni, incluir_cronograma=incluir_cronograma)


@app.get("/internal/solicitudes/{id_solicitud}")
def solicitud_interna(id_solicitud: str, dni: str | None = None) -> dict:
    solicitud = obtener_solicitud(id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
    if dni and solicitud.get("dni_usuario") != dni:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada.")
    return solicitud


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
