from datetime import datetime

from pydantic import BaseModel

from app.schemas.admin import ResumenAportaciones


class DashboardAdmin(BaseModel):
    total_socios: int
    total_solicitudes: int
    solicitudes_pendientes: int
    solicitudes_aprobadas: int
    solicitudes_rechazadas: int
    monto_colocado: float
    monto_por_cobrar: float
    tasa_aprobacion: float
    aportaciones: ResumenAportaciones
    actualizado_en: datetime


class CarteraProducto(BaseModel):
    tipo_credito: str
    cantidad: int
    monto_total: float


class AuditoriaSolicitud(BaseModel):
    id_solicitud: str
    dni_usuario: str
    monto: float
    tipo_credito: str
    estado_evaluacion: str
    tea_aplicada: float | None = None
    cuota_mensual: float | None = None
    interes_total: float | None = None
    observaciones: str = ""


class ReporteAuditoria(BaseModel):
    actualizado_en: datetime
    cartera_por_producto: list[CarteraProducto]
    solicitudes: list[AuditoriaSolicitud]
    resumen_financiero: dict[str, float]
