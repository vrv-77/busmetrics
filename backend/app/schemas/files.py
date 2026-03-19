from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UploadedFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    status: str
    row_count: int
    user_id: str
    detected_format: str | None = None
    upload_date: datetime
    processed_at: datetime | None
    error_message: str | None


class UploadResponse(BaseModel):
    file_id: UUID
    filename: str
    status: str


class FilePreviewResponse(BaseModel):
    file_id: UUID
    filename: str
    detected_format: str
    header_row_index: int
    source_columns: list[str]
    suggested_mapping: dict[str, str]
    missing_columns: list[str]
    preview_rows: list[dict]


class ProcessRequest(BaseModel):
    column_mapping: dict[str, str] = Field(default_factory=dict)


class ProcessResponse(BaseModel):
    file_id: UUID
    status: str
    rows_processed: int
    rows_raw: int
    duplicates_avoided: int
    alerts_created: int
    warnings_logged: int
    dashboard_snapshot: dict
