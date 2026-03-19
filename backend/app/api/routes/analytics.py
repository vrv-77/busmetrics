from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_filters
from app.db.database import get_db_session
from app.schemas.auth import CurrentUser
from app.services.analytics_service import (
    AnalyticsFilters,
    get_alerts,
    get_bus_metrics,
    get_dashboard_data,
    get_dispenser_metrics,
    get_operations_table,
    get_people_metrics,
    get_quality_metrics,
    get_shift_metrics,
    get_terminal_metrics,
)

router = APIRouter(tags=["analytics"])


@router.get("/dashboard")
async def dashboard(
    filters: AnalyticsFilters = Depends(get_filters),
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    return await get_dashboard_data(db, filters)


@router.get("/operations")
async def operations(
    filters: AnalyticsFilters = Depends(get_filters),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=1000),
    sort_by: str = Query(default="datetime_carga"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    return await get_operations_table(db, filters, page=page, page_size=page_size, sort_by=sort_by, sort_dir=sort_dir)


@router.get("/terminals")
async def terminals(
    filters: AnalyticsFilters = Depends(get_filters),
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    return await get_terminal_metrics(db, filters)


@router.get("/shifts")
async def shifts(
    filters: AnalyticsFilters = Depends(get_filters),
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    return await get_shift_metrics(db, filters)


@router.get("/dispensers")
async def dispensers(
    filters: AnalyticsFilters = Depends(get_filters),
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    return await get_dispenser_metrics(db, filters)


@router.get("/buses")
async def buses(
    filters: AnalyticsFilters = Depends(get_filters),
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    return await get_bus_metrics(db, filters)


@router.get("/people")
async def people(
    filters: AnalyticsFilters = Depends(get_filters),
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    return await get_people_metrics(db, filters)


@router.get("/quality")
async def quality(
    filters: AnalyticsFilters = Depends(get_filters),
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    return await get_quality_metrics(db, filters)


@router.get("/alerts")
async def alerts(
    filters: AnalyticsFilters = Depends(get_filters),
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    return await get_alerts(db, filters)


# Legacy aliases to preserve existing frontend routes
@router.get("/stations")
async def stations_alias(
    filters: AnalyticsFilters = Depends(get_filters),
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    return await get_terminal_metrics(db, filters)


@router.get("/chargers")
async def chargers_alias(
    filters: AnalyticsFilters = Depends(get_filters),
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    return await get_dispenser_metrics(db, filters)
