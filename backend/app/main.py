from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.api.routes import analytics, files, health, reports
from app.core.config import get_settings
from app.db.init_db import init_db

settings = get_settings()
logger = logging.getLogger(__name__)


def _normalize_origin(value: str | None) -> str:
    if not value:
        return ""
    return value.strip().rstrip("/")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auto_init_db:
        try:
            await init_db()
        except Exception as exc:
            if settings.fail_on_startup_db_error:
                raise
            logger.exception("Database initialization failed on startup: %s", exc)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

allow_origins = {
    _normalize_origin(settings.frontend_url),
    "http://localhost:3000",
    "https://localhost:3000",
}

if settings.cors_extra_origins:
    for origin in settings.cors_extra_origins.split(","):
        normalized = _normalize_origin(origin)
        if normalized:
            allow_origins.add(normalized)

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(allow_origins),
    allow_origin_regex=settings.cors_allow_origin_regex or None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(files.router)
app.include_router(analytics.router)
app.include_router(reports.router)
