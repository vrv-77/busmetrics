from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

import pandas as pd
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.alert import Alert
from app.models.charging_session import ChargingSession
from app.models.processing_log import ProcessingLog
from app.models.uploaded_file import UploadedFile
from app.services.excel_processor import ExcelProcessingError, process_excel
from app.services.supabase_service import (
    download_file_from_storage,
    persist_file_locally,
    read_local_file,
    upload_file_to_storage,
)

settings = get_settings()


async def create_uploaded_file(
    db: AsyncSession,
    filename: str,
    payload: bytes,
    user_id: str,
    content_type: str,
) -> UploadedFile:
    path = _build_storage_path(user_id=user_id, filename=filename)

    storage_path = _store_payload(path=path, payload=payload, content_type=content_type)

    file_model = UploadedFile(
        filename=filename,
        storage_path=storage_path,
        user_id=user_id,
        status="uploaded",
    )
    db.add(file_model)
    await db.commit()
    await db.refresh(file_model)
    return file_model


def _build_storage_path(user_id: str, filename: str) -> str:
    return f"{user_id}/{uuid4().hex}-{filename}"


def _store_payload(path: str, payload: bytes, content_type: str) -> str:
    try:
        uploaded_path = upload_file_to_storage(path=path, payload=payload, content_type=content_type)
        return f"supabase://{uploaded_path}"
    except Exception:
        local_path = persist_file_locally(path=path, payload=payload)
        return f"local://{local_path}"


def _read_storage_payload(storage_path: str) -> bytes:
    if storage_path.startswith("supabase://"):
        clean_path = storage_path.replace("supabase://", "", 1)
        return download_file_from_storage(clean_path)
    if storage_path.startswith("local://"):
        clean_path = storage_path.replace("local://", "", 1)
        return read_local_file(clean_path)
    raise RuntimeError("Ruta de storage inválida")


async def process_uploaded_file(db: AsyncSession, file_id: UUID) -> dict:
    file_stmt = select(UploadedFile).where(UploadedFile.id == file_id)
    file_result = await db.execute(file_stmt)
    file_model = file_result.scalar_one_or_none()

    if not file_model:
        raise ValueError("Archivo no encontrado")

    file_model.status = "processing"
    file_model.error_message = None
    await db.commit()

    try:
        payload = _read_storage_payload(file_model.storage_path)
        processed = process_excel(payload)

        await _clean_previous_processing(db, file_model.id)
        inserted = await _insert_sessions(db, file_model.id, processed.sessions_df)
        alerts_inserted = await _insert_alerts(db, file_model.id, processed.alerts_df)
        logs_inserted = await _insert_logs(db, file_model.id, processed.logs_df)

        file_model.status = "processed"
        file_model.row_count = inserted
        file_model.processed_at = datetime.now(timezone.utc)
        file_model.error_message = None

        await db.commit()

        return {
            "file_id": file_model.id,
            "status": file_model.status,
            "rows_processed": inserted,
            "alerts_created": alerts_inserted,
            "warnings_logged": logs_inserted,
            "dashboard_snapshot": processed.dashboard_snapshot,
        }
    except ExcelProcessingError as exc:
        await db.rollback()
        await _mark_as_failed(db, file_model, str(exc))
        raise
    except Exception as exc:  # pragma: no cover - runtime defensive path
        await db.rollback()
        await _mark_as_failed(db, file_model, f"Fallo inesperado: {exc}")
        raise


async def _mark_as_failed(db: AsyncSession, file_model: UploadedFile, message: str) -> None:
    file_model.status = "failed"
    file_model.error_message = message
    file_model.processed_at = datetime.now(timezone.utc)
    await db.commit()


async def _clean_previous_processing(db: AsyncSession, file_id: UUID) -> None:
    await db.execute(delete(Alert).where(Alert.file_id == file_id))
    await db.execute(delete(ProcessingLog).where(ProcessingLog.file_id == file_id))
    await db.execute(delete(ChargingSession).where(ChargingSession.file_id == file_id))


async def _insert_sessions(db: AsyncSession, file_id: UUID, df: pd.DataFrame) -> int:
    if df.empty:
        return 0

    records = _prepare_records(df)
    for row in records:
        row["file_id"] = file_id

    for chunk in _batched(records, settings.batch_insert_size):
        await db.execute(insert(ChargingSession), chunk)
    return len(records)


async def _insert_alerts(db: AsyncSession, file_id: UUID, df: pd.DataFrame) -> int:
    if df.empty:
        return 0

    records = []
    for record in _prepare_records(df):
        records.append(
            {
                "session_id": None,
                "file_id": file_id,
                "type": record["type"],
                "severity": record["severity"],
                "message": record["message"],
            }
        )

    for chunk in _batched(records, settings.batch_insert_size):
        await db.execute(insert(Alert), chunk)
    return len(records)


async def _insert_logs(db: AsyncSession, file_id: UUID, df: pd.DataFrame) -> int:
    if df.empty:
        return 0

    records = []
    for record in _prepare_records(df):
        records.append(
            {
                "file_id": file_id,
                "level": record["level"],
                "code": record["code"],
                "message": record["message"],
                "row_index": record["row_index"],
            }
        )

    for chunk in _batched(records, settings.batch_insert_size):
        await db.execute(insert(ProcessingLog), chunk)
    return len(records)


def _prepare_records(df: pd.DataFrame) -> list[dict]:
    normalized = df.where(pd.notnull(df), None).copy()

    if "semana" in normalized.columns:
        normalized["semana"] = normalized["semana"].apply(lambda v: int(v) if v is not None else None)
    if "mes" in normalized.columns:
        normalized["mes"] = normalized["mes"].apply(lambda v: int(v) if v is not None else None)
    if "hora_dia" in normalized.columns:
        normalized["hora_dia"] = normalized["hora_dia"].apply(lambda v: int(v) if v is not None else None)

    return normalized.to_dict(orient="records")


def _batched(items: list[dict], batch_size: int) -> list[list[dict]]:
    return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]
