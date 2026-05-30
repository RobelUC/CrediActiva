from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.solicitud import TipoCredito

EstadoEvaluacion = Literal["PENDIENTE", "APROBADO", "RECHAZADO"]
EstadoAportacion = Literal["PAGADO", "PENDIENTE", "VENCIDO"]


class CuotaCronograma(BaseModel):
    numero_cuota: int
    fecha_vencimiento: str
    cuota: float
    capital: float
    interes: float
    saldo_restante: float


class EvaluarSolicitudRequest(BaseModel):
    decision: Literal["APROBADO", "RECHAZADO"]
    observaciones: str = Field(default="", max_length=500)


class SolicitudAdminResponse(BaseModel):
    id_solicitud: str
    dni_usuario: str
    monto: float
    plazo_meses: int
    tipo_credito: TipoCredito
    estado_preaprobacion: str
    estado_evaluacion: EstadoEvaluacion
    fecha_registro: datetime
    observaciones: str = ""
    cronograma: list[CuotaCronograma] = []


class AportacionResponse(BaseModel):
    id_aportacion: str
    id_solicitud: str
    dni_socio: str
    nombre_socio: str
    numero_cuota: int
    monto_cuota: float
    fecha_vencimiento: str
    estado: EstadoAportacion
    fecha_pago: str | None = None


class ResumenAportaciones(BaseModel):
    total: int
    pagadas: int
    pendientes: int
    vencidas: int
    monto_pagado: float
    monto_pendiente: float
    actualizado_en: datetime
