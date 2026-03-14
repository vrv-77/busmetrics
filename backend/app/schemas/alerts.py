from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    session_id: int | None
    file_id: str
    type: str
    severity: str
    message: str
    created_at: datetime


class AlertSummary(BaseModel):
    total: int
    critical: int
    warning: int
    incomplete: int
