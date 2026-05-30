import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

TipoCredito = Literal["Emprendedor", "Vivienda", "Agrícola"]
EstadoPreaprobacion = Literal["APROBADO_PRELIMINAR", "EN_REVISION"]
EstadoEvaluacion = Literal["PENDIENTE", "APROBADO", "RECHAZADO"]
_DNI = re.compile(r"^\d{8}$")


class SolicitudCredito(BaseModel):
    monto: float = Field(..., ge=1000)
    plazo_meses: int = Field(..., ge=12, le=48)
    tipo_credito: TipoCredito
    dni_usuario: str = Field(..., min_length=8, max_length=8)

    @field_validator("dni_usuario")
    @classmethod
    def validar_dni(cls, valor: str) -> str:
        if not _DNI.match(valor):
            raise ValueError("El DNI debe contener exactamente 8 dígitos numéricos.")
        return valor

    @field_validator("monto")
    @classmethod
    def redondear_monto(cls, valor: float) -> float:
        return round(valor, 2)


class AuditoriaInteres(BaseModel):
    tea_aplicada: float
    tasa_mensual_efectiva: float
    cuota_mensual: float
    interes_total: float
    monto_total_a_pagar: float


class SolicitudCreditoResponse(BaseModel):
    id_solicitud: str
    estado: EstadoPreaprobacion
    mensaje: str
    fecha_registro: datetime
    auditoria: AuditoriaInteres
    monto: float
    plazo_meses: int
    tipo_credito: TipoCredito
    dni_usuario: str


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
