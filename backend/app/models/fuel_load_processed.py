from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FuelLoadProcessed(Base):
    __tablename__ = "fuel_loads_processed"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    file_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("uploaded_files.id", ondelete="CASCADE"), nullable=False)

    turno: Mapped[str | None] = mapped_column(String(80), nullable=True)
    fecha: Mapped[date | None] = mapped_column(Date, nullable=True)
    hora: Mapped[str | None] = mapped_column(String(16), nullable=True)
    terminal: Mapped[str | None] = mapped_column(String(120), nullable=True)
    numero_interno: Mapped[str | None] = mapped_column(String(80), nullable=True)
    patente: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cantidad_litros: Mapped[float | None] = mapped_column(Float, nullable=True)
    tipo: Mapped[str | None] = mapped_column(String(80), nullable=True)
    tapa: Mapped[str | None] = mapped_column(String(80), nullable=True)
    filtracion: Mapped[str | None] = mapped_column(String(80), nullable=True)
    modelo_chasis: Mapped[str | None] = mapped_column(String(120), nullable=True)
    estanque: Mapped[str | None] = mapped_column(String(80), nullable=True)
    llenado: Mapped[str | None] = mapped_column(String(80), nullable=True)
    exeso: Mapped[str | None] = mapped_column(String(80), nullable=True)
    odometro: Mapped[float | None] = mapped_column(Float, nullable=True)

    rut_planillero: Mapped[str | None] = mapped_column(String(20), nullable=True)
    nombre_planillero: Mapped[str | None] = mapped_column(String(180), nullable=True)
    rut_supervisor: Mapped[str | None] = mapped_column(String(20), nullable=True)
    nombre_supervisor: Mapped[str | None] = mapped_column(String(180), nullable=True)
    rut_conductor: Mapped[str | None] = mapped_column(String(20), nullable=True)
    nombre_conductor: Mapped[str | None] = mapped_column(String(180), nullable=True)

    surtidor: Mapped[str | None] = mapped_column(String(120), nullable=True)
    capturador: Mapped[str | None] = mapped_column(String(120), nullable=True)
    cargado_por: Mapped[str | None] = mapped_column(String(120), nullable=True)

    datetime_carga: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    anio: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nombre_mes: Mapped[str | None] = mapped_column(String(20), nullable=True)
    semana: Mapped[int | None] = mapped_column(Integer, nullable=True)
    dia: Mapped[int | None] = mapped_column(Integer, nullable=True)
    dia_semana: Mapped[str | None] = mapped_column(String(20), nullable=True)
    hora_numero: Mapped[int | None] = mapped_column(Integer, nullable=True)
    franja_horaria: Mapped[str | None] = mapped_column(String(40), nullable=True)
    periodo: Mapped[str | None] = mapped_column(String(32), nullable=True)

    litros_redondeados: Mapped[int | None] = mapped_column(Integer, nullable=True)
    registro_duplicado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    alerta_odometro: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    alerta_consumo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    out_of_shift: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    clave_unica_registro: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    dias_desde_ultima_carga: Mapped[int | None] = mapped_column(Integer, nullable=True)

    data_quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    validation_flags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    file = relationship("UploadedFile", back_populates="processed_loads")
    alerts = relationship("Alert", back_populates="fuel_load", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_fuel_loads_processed_file_id", "file_id"),
        Index("ix_fuel_loads_processed_datetime", "datetime_carga"),
        Index("ix_fuel_loads_processed_terminal", "terminal"),
        Index("ix_fuel_loads_processed_turno", "turno"),
        Index("ix_fuel_loads_processed_patente", "patente"),
        Index("ix_fuel_loads_processed_numero_interno", "numero_interno"),
        Index("ix_fuel_loads_processed_surtidor", "surtidor"),
        Index("ix_fuel_loads_processed_conductor", "nombre_conductor"),
    )
