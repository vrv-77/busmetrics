from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    load_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("fuel_loads_processed.id", ondelete="SET NULL"), nullable=True)
    file_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("uploaded_files.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(80), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    fuel_load = relationship("FuelLoadProcessed", back_populates="alerts")

    __table_args__ = (
        Index("ix_alerts_file_id", "file_id"),
        Index("ix_alerts_severity", "severity"),
    )
