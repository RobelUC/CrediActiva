from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, status

from app.schemas.solicitud import (
    EstadoPreaprobacion,
    SolicitudCredito,
    SolicitudCreditoResponse,
)
from app.services.almacen import guardar_solicitud
from app.services.calculadora import (
    calcular_auditoria_credito,
    construir_mensaje_exito,
    determinar_estado_preaprobacion,
)

router = APIRouter(prefix="/api/v1", tags=["Solicitudes"])


@router.post(
    "/solicitudes",
    response_model=SolicitudCreditoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar solicitud de crédito",
)
def crear_solicitud(payload: SolicitudCredito) -> SolicitudCreditoResponse:
    auditoria = calcular_auditoria_credito(
        payload.monto,
        payload.plazo_meses,
        payload.tipo_credito,
    )
    estado = determinar_estado_preaprobacion(payload.monto)
    id_solicitud = str(uuid4())
    fecha = datetime.now(timezone.utc)

    mensaje = construir_mensaje_exito(
        estado,
        payload.dni_usuario,
        payload.tipo_credito,
        payload.monto,
    )

    respuesta = SolicitudCreditoResponse(
        id_solicitud=id_solicitud,
        estado=estado,
        mensaje=mensaje,
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
