from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_filters
from app.db.database import get_db_session
from app.schemas.auth import CurrentUser
from app.services.analytics_service import AnalyticsFilters
from app.services.report_service import build_report_bytes

router = APIRouter(tags=["reports"])


@router.get("/reports/export")
async def export_report(
    scope: str = Query(default="dashboard", pattern="^(dashboard|terminals|shifts|dispensers|buses|people|quality|alerts|operations)$"),
    fmt: str = Query(default="excel", pattern="^(csv|excel|pdf)$"),
    filters: AnalyticsFilters = Depends(get_filters),
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    try:
        filename, media_type, payload = await build_report_bytes(db, scope, fmt, filters)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(iter([payload]), media_type=media_type, headers=headers)
