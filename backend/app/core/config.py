from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "BusMetric API"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    auto_init_db: bool = True
    fail_on_startup_db_error: bool = False

    database_url: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_storage_bucket: str = "charging-files"

    timezone: str = "America/Santiago"

    max_upload_size_mb: int = 50
    batch_insert_size: int = 5000

    power_min_kw: float = 0.0
    power_max_kw: float = 700.0

    duration_anomaly_min_minutes: float = 2.0
    duration_anomaly_max_minutes: float = 720.0

    auth_required: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
