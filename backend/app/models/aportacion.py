from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Aportacion(Base):
    __tablename__ = "aportaciones"

    id_aportacion: Mapped[str] = mapped_column(String(36), primary_key=True)
    id_solicitud: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    dni_socio: Mapped[str] = mapped_column(String(8), index=True, nullable=False)
    nombre_socio: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    numero_cuota: Mapped[int] = mapped_column(Integer, nullable=False)
    monto_cuota: Mapped[float] = mapped_column(Float, nullable=False)
    fecha_vencimiento: Mapped[str] = mapped_column(String(10), nullable=False)
    fecha_pago: Mapped[str | None] = mapped_column(String(10), nullable=True)
