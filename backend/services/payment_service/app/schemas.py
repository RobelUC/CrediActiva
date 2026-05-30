from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

EstadoAportacion = Literal["PAGADO", "PENDIENTE", "VENCIDO"]


class AportacionItem(BaseModel):
    id_aportacion: str
    id_solicitud: str
    dni_socio: str
    nombre_socio: str
    numero_cuota: int
    monto_cuota: float
    fecha_vencimiento: str
    fecha_pago: str | None = None


class LoteAportaciones(BaseModel):
    items: list[AportacionItem]


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
