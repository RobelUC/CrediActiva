from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Socio(Base):
    """
    Entidad socio — 3FN.
    Cada atributo depende únicamente de la clave primaria id_socio.
    dni y email son candidatos a clave alternativa (UNIQUE).
    """

    __tablename__ = "socios"
    __table_args__ = (
        UniqueConstraint("dni", name="uq_socios_dni"),
        UniqueConstraint("email", name="uq_socios_email"),
    )

    id_socio: Mapped[str] = mapped_column(String(36), primary_key=True)
    dni: Mapped[str] = mapped_column(String(8), index=True, nullable=False)
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    telefono: Mapped[str] = mapped_column(String(20), default="", nullable=False)
    aporte_mensual: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
