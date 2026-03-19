from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.config import get_settings

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/")
async def root(request: Request) -> Any:
    frontend_url = (settings.frontend_url or "").strip()
    if frontend_url and "localhost" not in frontend_url:
        return RedirectResponse(url=frontend_url, status_code=307)

    accepts_html = "text/html" in request.headers.get("accept", "").lower()
    if accepts_html:
        return HTMLResponse(
            content="""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>BusMetric Fuel API</title>
    <style>
      body { font-family: Arial, sans-serif; background: #0b1220; color: #dbeafe; margin: 0; }
      main { max-width: 760px; margin: 60px auto; padding: 24px; background: #111b2e; border: 1px solid #203352; border-radius: 12px; }
      h1 { margin: 0 0 12px; font-size: 24px; }
      p { margin: 8px 0; line-height: 1.4; }
      code { background: #1b2a44; padding: 2px 6px; border-radius: 6px; }
      a { color: #7dd3fc; text-decoration: none; }
    </style>
  </head>
  <body>
    <main>
      <h1>BusMetric Fuel API is running</h1>
      <p>This URL serves the backend API.</p>
      <p>Swagger docs: <a href="/docs">/docs</a></p>
      <p>Health check: <a href="/health">/health</a></p>
      <p>To open the web dashboard, configure <code>FRONTEND_URL</code> in backend environment variables.</p>
    </main>
  </body>
</html>
""".strip()
        )

    return {
        "service": "BusMetric Fuel API",
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
    }


@router.get("/health")
async def healthcheck() -> dict:
    return {"status": "ok"}
