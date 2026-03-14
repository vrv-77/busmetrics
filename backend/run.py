import os

import uvicorn

from app.core.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    render_port = int(os.getenv("PORT", settings.app_port))
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=render_port,
        reload=settings.app_env == "development",
    )
