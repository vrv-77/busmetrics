from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ChargingSession(Base):
    __tablename__ = "charging_sessions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    file_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("uploaded_files.id", ondelete="CASCADE"), nullable=False)

    inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    termino: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    estacion: Mapped[str | None] = mapped_column(String(160), nullable=True)
    cargador: Mapped[str | None] = mapped_column(String(160), nullable=True)
    conector: Mapped[str | None] = mapped_column(String(80), nullable=True)
    vehiculo: Mapped[str | None] = mapped_column(String(160), nullable=True)

    soc_inicial: Mapped[float | None] = mapped_column(Float, nullable=True)
    soc_final: Mapped[float | None] = mapped_column(Float, nullable=True)
    soh: Mapped[float | None] = mapped_column(Float, nullable=True)

    energia_kwh: Mapped[float | None] = mapped_column(Float, nullable=True)
    potencia_promedio: Mapped[float | None] = mapped_column(Float, nullable=True)
    potencia_maxima: Mapped[float | None] = mapped_column(Float, nullable=True)

    rfid_inicio: Mapped[str | None] = mapped_column(String(120), nullable=True)
    rfid_termino: Mapped[str | None] = mapped_column(String(120), nullable=True)
    odometro_km: Mapped[float | None] = mapped_column(Float, nullable=True)

    duracion_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    duracion_horas: Mapped[float | None] = mapped_column(Float, nullable=True)
    alerta_soc_bajo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sesion_incompleta: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    hora_inicio_local: Mapped[str | None] = mapped_column(String(8), nullable=True)
    dia: Mapped[date | None] = mapped_column(Date, nullable=True)
    semana: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hora_dia: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    file = relationship("UploadedFile", back_populates="sessions")
    alerts = relationship("Alert", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_charging_sessions_file_id", "file_id"),
        Index("ix_charging_sessions_estacion", "estacion"),
        Index("ix_charging_sessions_cargador", "cargador"),
        Index("ix_charging_sessions_vehiculo", "vehiculo"),
        Index("ix_charging_sessions_inicio", "inicio"),
    )
