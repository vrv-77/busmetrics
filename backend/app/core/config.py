from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "BusMetric Fuel API"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    cors_allow_origin_regex: str = r"^https://.*\.onrender\.com$"
    cors_extra_origins: str = Field(
        default="",
        validation_alias=AliasChoices("CORS_EXTRA_ORIGINS", "CORS_EXTRA_ORIGIN"),
    )
    auto_init_db: bool = True
    fail_on_startup_db_error: bool = False

    database_url: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_storage_bucket: str = "fuel-files"

    timezone: str = "America/Santiago"

    max_upload_size_mb: int = 50
    batch_insert_size: int = 3000

    litros_min_validos: float = 5.0
    litros_max_validos: float = 550.0
    variacion_consumo_pct_alerta: float = 0.35

    auth_required: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
