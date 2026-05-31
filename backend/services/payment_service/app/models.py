from datetime import date

from sqlalchemy import Date, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Aportacion(Base):
    """
    Registro de pago de cuota — 3FN.
    nombre_socio eliminado (dependía de dni_socio, no de id_aportacion).
    dni_socio se conserva como referencia lógica al auth-service (microservicios).
    """

    __tablename__ = "aportaciones"
    __table_args__ = (UniqueConstraint("id_solicitud", "numero_cuota", name="uq_aportacion_cuota"),)

    id_aportacion: Mapped[str] = mapped_column(String(36), primary_key=True)
    id_solicitud: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    id_cuota: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    dni_socio: Mapped[str] = mapped_column(String(8), index=True, nullable=False)
    numero_cuota: Mapped[int] = mapped_column(Integer, nullable=False)
    monto_cuota: Mapped[float] = mapped_column(Float, nullable=False)
    fecha_vencimiento: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_pago: Mapped[date | None] = mapped_column(Date, nullable=True)
    estado_pago: Mapped[str] = mapped_column(String(10), default="PENDIENTE", nullable=False)
