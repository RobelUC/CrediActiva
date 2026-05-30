from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id_solicitud: Mapped[str] = mapped_column(String(36), primary_key=True)
    dni_usuario: Mapped[str] = mapped_column(String(8), index=True, nullable=False)
    monto: Mapped[float] = mapped_column(Float, nullable=False)
    plazo_meses: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_credito: Mapped[str] = mapped_column(String(20), nullable=False)
    estado: Mapped[str] = mapped_column(String(30), nullable=False)
    estado_evaluacion: Mapped[str] = mapped_column(String(20), default="PENDIENTE", nullable=False)
    mensaje: Mapped[str] = mapped_column(Text, default="", nullable=False)
    observaciones: Mapped[str] = mapped_column(Text, default="", nullable=False)
    auditoria: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    cronograma: Mapped[list | None] = mapped_column(JSON, default=list, nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
