from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TipoCredito(Base):
    """Catálogo de productos crediticios (3FN — atributos dependen solo de codigo)."""

    __tablename__ = "tipos_credito"

    codigo: Mapped[str] = mapped_column(String(20), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    tea_anual: Mapped[float] = mapped_column(Float, nullable=False)

    solicitudes: Mapped[list["Solicitud"]] = relationship(back_populates="tipo_credito")


class Solicitud(Base):
    """Solicitud de crédito — referencia catálogo y socio por DNI (clave externa lógica)."""

    __tablename__ = "solicitudes"

    id_solicitud: Mapped[str] = mapped_column(String(36), primary_key=True)
    dni_usuario: Mapped[str] = mapped_column(String(8), index=True, nullable=False)
    id_tipo_credito: Mapped[str] = mapped_column(
        String(20), ForeignKey("tipos_credito.codigo"), nullable=False
    )
    monto: Mapped[float] = mapped_column(Float, nullable=False)
    plazo_meses: Mapped[int] = mapped_column(Integer, nullable=False)
    estado_preaprobacion: Mapped[str] = mapped_column(String(30), nullable=False)
    estado_evaluacion: Mapped[str] = mapped_column(String(20), default="PENDIENTE", nullable=False)
    mensaje: Mapped[str] = mapped_column(Text, default="", nullable=False)
    observaciones: Mapped[str] = mapped_column(Text, default="", nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    tipo_credito: Mapped["TipoCredito"] = relationship(back_populates="solicitudes")
    evaluacion_financiera: Mapped["EvaluacionFinanciera | None"] = relationship(
        back_populates="solicitud", uselist=False, cascade="all, delete-orphan"
    )
    cuotas: Mapped[list["CuotaCredito"]] = relationship(
        back_populates="solicitud", cascade="all, delete-orphan", order_by="CuotaCredito.numero_cuota"
    )


class EvaluacionFinanciera(Base):
    """Desglose financiero de la solicitud (1:1) — sustituye columna JSON auditoria."""

    __tablename__ = "evaluaciones_financieras"

    id_evaluacion: Mapped[str] = mapped_column(String(36), primary_key=True)
    id_solicitud: Mapped[str] = mapped_column(
        String(36), ForeignKey("solicitudes.id_solicitud"), unique=True, nullable=False
    )
    tea_aplicada: Mapped[float] = mapped_column(Float, nullable=False)
    tasa_mensual_efectiva: Mapped[float] = mapped_column(Float, nullable=False)
    cuota_mensual: Mapped[float] = mapped_column(Float, nullable=False)
    interes_total: Mapped[float] = mapped_column(Float, nullable=False)
    monto_total_a_pagar: Mapped[float] = mapped_column(Float, nullable=False)

    solicitud: Mapped["Solicitud"] = relationship(back_populates="evaluacion_financiera")


class CuotaCredito(Base):
    """Cronograma normalizado — una fila por cuota (sustituye columna JSON cronograma)."""

    __tablename__ = "cuotas_credito"
    __table_args__ = (UniqueConstraint("id_solicitud", "numero_cuota", name="uq_solicitud_cuota"),)

    id_cuota: Mapped[str] = mapped_column(String(36), primary_key=True)
    id_solicitud: Mapped[str] = mapped_column(
        String(36), ForeignKey("solicitudes.id_solicitud"), index=True, nullable=False
    )
    numero_cuota: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_vencimiento: Mapped[date] = mapped_column(Date, nullable=False)
    cuota: Mapped[float] = mapped_column(Float, nullable=False)
    capital: Mapped[float] = mapped_column(Float, nullable=False)
    interes: Mapped[float] = mapped_column(Float, nullable=False)
    saldo_restante: Mapped[float] = mapped_column(Float, nullable=False)

    solicitud: Mapped["Solicitud"] = relationship(back_populates="cuotas")
