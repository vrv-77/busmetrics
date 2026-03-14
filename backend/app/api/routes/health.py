from typing import Any

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.core.config import get_settings

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/")
async def root() -> Any:
    frontend_url = (settings.frontend_url or "").strip()
    if frontend_url and "localhost" not in frontend_url:
        return RedirectResponse(url=frontend_url, status_code=307)

    return {
        "service": "BusMetric API",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
    }


@router.get("/health")
async def healthcheck() -> dict:
    return {"status": "ok"}
