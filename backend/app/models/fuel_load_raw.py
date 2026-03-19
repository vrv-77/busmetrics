from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FuelLoadRaw(Base):
    __tablename__ = "fuel_loads_raw"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    file_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("uploaded_files.id", ondelete="CASCADE"), nullable=False)
    row_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_payload: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_payload: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    file = relationship("UploadedFile", back_populates="raw_loads")

    __table_args__ = (
        Index("ix_fuel_loads_raw_file_id", "file_id"),
        Index("ix_fuel_loads_raw_row_number", "row_number"),
    )
