from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_filters
from app.db.database import get_db_session
from app.schemas.auth import CurrentUser
from app.services.analytics_service import (
    AnalyticsFilters,
    get_alerts,
    get_bus_metrics,
    get_charger_metrics,
    get_dashboard_data,
    get_station_metrics,
)

router = APIRouter(tags=["analytics"])


@router.get("/dashboard")
async def dashboard(
    filters: AnalyticsFilters = Depends(get_filters),
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    return await get_dashboard_data(db, filters)


@router.get("/stations")
async def stations(
    filters: AnalyticsFilters = Depends(get_filters),
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    return await get_station_metrics(db, filters)


@router.get("/chargers")
async def chargers(
    filters: AnalyticsFilters = Depends(get_filters),
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    return await get_charger_metrics(db, filters)


@router.get("/buses")
async def buses(
    filters: AnalyticsFilters = Depends(get_filters),
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    return await get_bus_metrics(db, filters)


@router.get("/alerts")
async def alerts(
    filters: AnalyticsFilters = Depends(get_filters),
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    return await get_alerts(db, filters)
