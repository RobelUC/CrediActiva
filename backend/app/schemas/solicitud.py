import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

TipoCredito = Literal["Emprendedor", "Vivienda", "Agrícola"]
EstadoPreaprobacion = Literal["APROBADO_PRELIMINAR", "EN_REVISION"]

_DNI_PATTERN = re.compile(r"^\d{8}$")


class SolicitudCredito(BaseModel):
    """Esquema de entrada — validación Pydantic v2."""

    monto: float = Field(..., ge=1000, description="Monto solicitado en soles (mín. S/. 1,000)")
    plazo_meses: int = Field(..., ge=12, le=48, description="Plazo en meses (12 a 48)")
    tipo_credito: TipoCredito
    dni_usuario: str = Field(..., min_length=8, max_length=8, description="DNI peruano (8 dígitos)")

    @field_validator("dni_usuario")
    @classmethod
    def validar_dni_peruano(cls, valor: str) -> str:
        if not _DNI_PATTERN.match(valor):
            raise ValueError("El DNI debe contener exactamente 8 dígitos numéricos.")
        return valor

    @field_validator("monto")
    @classmethod
    def redondear_monto(cls, valor: float) -> float:
        return round(valor, 2)


class AuditoriaInteres(BaseModel):
    """Cálculo servidor — amortización francesa + interés total (auditoría)."""

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
