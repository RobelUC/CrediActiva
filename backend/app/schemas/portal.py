from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.admin import CuotaCronograma
from app.schemas.solicitud import TipoCredito


class ProximaCuota(BaseModel):
    fecha_vencimiento: str
    monto: float
    numero_cuota: int


class ResumenCuentaSocio(BaseModel):
    dni: str
    nombres: str
    apellidos: str
    email: str
    telefono: str = ""
    aporte_mensual: float = 0
    creditos_activos: int
    monto_total_credito: float
    saldo_pendiente: float
    cuotas_pagadas: int
    cuotas_pendientes: int
    cuotas_vencidas: int
    proxima_cuota: ProximaCuota | None = None
    estado_cuenta: str  # AL_DIA | PENDIENTE | MOROSO
    actualizado_en: datetime


class CreditoSocio(BaseModel):
    id_solicitud: str
    tipo_credito: TipoCredito
    monto: float
    plazo_meses: int
    estado_evaluacion: str
    estado_preaprobacion: str
    cuota_mensual: float
    saldo_pendiente: float
    cuotas_pagadas: int
    fecha_registro: datetime
    cronograma: list[CuotaCronograma] = []


class AporteHistorialItem(BaseModel):
    id_aportacion: str
    id_solicitud: str
    numero_cuota: int
    monto_cuota: float
    fecha_vencimiento: str
    fecha_pago: str | None
    estado: str
    tipo_credito: str = ""


class PerfilSocioResponse(BaseModel):
    id_socio: str | None = None
    nombres: str
    apellidos: str
    dni: str
    email: str
    telefono: str = ""
    aporte_mensual: float = 50.0
    fecha_registro: datetime | None = None


class PerfilSocioUpdate(BaseModel):
    nombres: str = Field(..., min_length=2)
    apellidos: str = Field(..., min_length=2)
    email: str = Field(..., min_length=5)
    telefono: str = Field(..., min_length=9, max_length=9)
    aporte_mensual: float = Field(default=50.0, ge=0)
