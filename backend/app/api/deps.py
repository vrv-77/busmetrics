from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Query, status

from app.core.config import get_settings
from app.schemas.auth import CurrentUser
from app.services.analytics_service import AnalyticsFilters
from app.services.supabase_service import validate_user_token

settings = get_settings()


async def get_current_user(authorization: str | None = Header(default=None)) -> CurrentUser:
    if not settings.auth_required:
        return CurrentUser(id="local-dev-user", email="dev@local")

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
        )

    try:
        return validate_user_token(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Supabase auth error: {exc}",
        ) from exc


async def get_filters(
    file_id: UUID | None = Query(default=None),
    estacion: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
) -> AnalyticsFilters:
    return AnalyticsFilters(
        file_id=file_id,
        estacion=estacion,
        date_from=date_from,
        date_to=date_to,
    )
