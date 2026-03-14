from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UploadedFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    status: str
    row_count: int
    user_id: str
    upload_date: datetime
    processed_at: datetime | None
    error_message: str | None


class UploadResponse(BaseModel):
    file_id: UUID
    filename: str
    status: str


class ProcessResponse(BaseModel):
    file_id: UUID
    status: str
    rows_processed: int
    alerts_created: int
    warnings_logged: int
    dashboard_snapshot: dict
