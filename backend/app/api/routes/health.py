from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/")
async def root() -> dict:
    return {
        "service": "BusMetric API",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
    }


@router.get("/health")
async def healthcheck() -> dict:
    return {"status": "ok"}
