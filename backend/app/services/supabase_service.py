from pathlib import Path

from supabase import Client, create_client

from app.core.config import get_settings
from app.schemas.auth import CurrentUser

settings = get_settings()


def _get_supabase_client(api_key: str) -> Client:
    if not settings.supabase_url or not api_key:
        raise RuntimeError("Supabase configuration is missing. Check SUPABASE_URL and API key.")
    return create_client(settings.supabase_url, api_key)


def get_supabase_admin_client() -> Client:
    key = settings.supabase_service_role_key or settings.supabase_anon_key
    return _get_supabase_client(key)


def get_supabase_anon_client() -> Client:
    return _get_supabase_client(settings.supabase_anon_key)


def validate_user_token(token: str) -> CurrentUser:
    client = get_supabase_admin_client()
    result = client.auth.get_user(token)
    user = result.user
    if not user:
        raise RuntimeError("Invalid Supabase token")
    return CurrentUser(id=user.id, email=user.email)


def upload_file_to_storage(path: str, payload: bytes, content_type: str) -> str:
    client = get_supabase_admin_client()
    client.storage.from_(settings.supabase_storage_bucket).upload(
        path,
        payload,
        {
            "cache-control": "3600",
            "content-type": content_type,
            "upsert": "true",
        },
    )
    return path


def download_file_from_storage(path: str) -> bytes:
    client = get_supabase_admin_client()
    return client.storage.from_(settings.supabase_storage_bucket).download(path)


def persist_file_locally(path: str, payload: bytes) -> str:
    storage_root = Path("storage")
    target = storage_root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    return str(target)


def read_local_file(path: str) -> bytes:
    return Path(path).read_bytes()
