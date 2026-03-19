from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from uuid import UUID, uuid4

import pandas as pd
from sqlalchemy import delete, insert, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.alert import Alert
from app.models.fuel_load_processed import FuelLoadProcessed
from app.models.fuel_load_raw import FuelLoadRaw
from app.models.processing_log import ProcessingLog
from app.models.uploaded_file import UploadedFile
from app.services.excel_processor import (
    ExcelProcessingError,
    detect_real_file_type,
    preview_excel,
    process_excel,
)
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
    detected_format = detect_real_file_type(payload, filename)

    file_model = UploadedFile(
        filename=filename,
        storage_path=storage_path,
        user_id=user_id,
        detected_format=detected_format,
        status="uploaded",
    )
    db.add(file_model)
    await db.commit()
    await db.refresh(file_model)
    return file_model


async def preview_uploaded_file(db: AsyncSession, file_id: UUID) -> dict:
    file_model = await _get_file_or_raise(db, file_id)
    payload = _read_storage_payload(file_model.storage_path)

    preview = preview_excel(payload, file_model.filename)

    return {
        "file_id": file_model.id,
        "filename": file_model.filename,
        "detected_format": preview.detected_format,
        "header_row_index": preview.header_row_index,
        "source_columns": preview.source_columns,
        "suggested_mapping": preview.suggested_mapping,
        "missing_columns": preview.missing_columns,
        "preview_rows": preview.preview_rows,
    }


async def process_uploaded_file(db: AsyncSession, file_id: UUID, column_mapping: dict[str, str] | None = None) -> dict:
    file_model = await _get_file_or_raise(db, file_id)

    file_model.status = "processing"
    file_model.error_message = None
    await db.commit()

    try:
        payload = _read_storage_payload(file_model.storage_path)
        processed = process_excel(payload, file_model.filename, column_mapping)

        await _clean_previous_processing(db, file_model.id)

        raw_inserted = await _insert_raw_rows(db, file_model.id, processed.raw_df)
        processed_inserted = await _insert_processed_rows(db, file_model.id, processed.processed_df)
        alerts_inserted = await _insert_alerts(db, file_model.id, processed.alerts_df)
        logs_inserted = await _insert_logs(db, file_model.id, processed.logs_df)

        processed_file_path = _store_processed_dataframe(file_model, processed.processed_df)

        file_model.status = "processed"
        file_model.row_count = processed_inserted
        file_model.processed_at = datetime.now(timezone.utc)
        file_model.error_message = None
        file_model.processed_storage_path = processed_file_path
        file_model.detected_format = processed.preview.detected_format

        await db.commit()

        total_rows = int(len(processed.processed_df))
        duplicates_avoided = max(total_rows - processed_inserted, 0)

        return {
            "file_id": file_model.id,
            "status": file_model.status,
            "rows_processed": processed_inserted,
            "rows_raw": raw_inserted,
            "duplicates_avoided": duplicates_avoided,
            "alerts_created": alerts_inserted,
            "warnings_logged": logs_inserted,
            "dashboard_snapshot": processed.dashboard_snapshot,
        }
    except ExcelProcessingError as exc:
        await db.rollback()
        await _mark_as_failed(db, file_model, str(exc))
        raise
    except Exception as exc:  # pragma: no cover
        await db.rollback()
        await _mark_as_failed(db, file_model, f"Fallo inesperado: {exc}")
        raise


async def _get_file_or_raise(db: AsyncSession, file_id: UUID) -> UploadedFile:
    file_stmt = select(UploadedFile).where(UploadedFile.id == file_id)
    file_result = await db.execute(file_stmt)
    file_model = file_result.scalar_one_or_none()

    if not file_model:
        raise ValueError("Archivo no encontrado")
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
    raise RuntimeError("Ruta de storage invalida")


def _store_processed_dataframe(file_model: UploadedFile, processed_df: pd.DataFrame) -> str:
    csv_buffer = BytesIO()
    processed_df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue()

    path = f"processed/{file_model.user_id}/{uuid4().hex}-{file_model.filename}.csv"
    return _store_payload(path, csv_bytes, "text/csv")


async def _mark_as_failed(db: AsyncSession, file_model: UploadedFile, message: str) -> None:
    file_model.status = "failed"
    file_model.error_message = message
    file_model.processed_at = datetime.now(timezone.utc)
    await db.commit()


async def _clean_previous_processing(db: AsyncSession, file_id: UUID) -> None:
    await db.execute(delete(Alert).where(Alert.file_id == file_id))
    await db.execute(delete(ProcessingLog).where(ProcessingLog.file_id == file_id))
    await db.execute(delete(FuelLoadRaw).where(FuelLoadRaw.file_id == file_id))
    await db.execute(delete(FuelLoadProcessed).where(FuelLoadProcessed.file_id == file_id))


async def _insert_raw_rows(db: AsyncSession, file_id: UUID, df: pd.DataFrame) -> int:
    if df.empty:
        return 0

    records = _prepare_records(df)
    for row in records:
        row["file_id"] = file_id

    for chunk in _batched(records, settings.batch_insert_size):
        await db.execute(insert(FuelLoadRaw), chunk)

    return len(records)


async def _insert_processed_rows(db: AsyncSession, file_id: UUID, df: pd.DataFrame) -> int:
    if df.empty:
        return 0

    allowed_columns = set(FuelLoadProcessed.__table__.columns.keys())
    records = [{k: v for k, v in rec.items() if k in allowed_columns} for rec in _prepare_records(df)]
    for row in records:
        row["file_id"] = file_id

    inserted = 0
    for chunk in _batched(records, settings.batch_insert_size):
        stmt = (
            pg_insert(FuelLoadProcessed)
            .values(chunk)
            .on_conflict_do_nothing(index_elements=["clave_unica_registro"])
            .returning(FuelLoadProcessed.clave_unica_registro)
        )
        result = await db.execute(stmt)
        inserted += len(result.scalars().all())

    return inserted


async def _insert_alerts(db: AsyncSession, file_id: UUID, df: pd.DataFrame) -> int:
    if df.empty:
        return 0

    keys = [str(k) for k in df["clave_unica_registro"].dropna().unique().tolist()]
    load_id_by_key: dict[str, int] = {}
    if keys:
        stmt = select(FuelLoadProcessed.id, FuelLoadProcessed.clave_unica_registro).where(
            FuelLoadProcessed.clave_unica_registro.in_(keys)
        )
        result = await db.execute(stmt)
        rows = result.mappings().all()
        load_id_by_key = {str(row["clave_unica_registro"]): int(row["id"]) for row in rows}

    records = []
    for record in _prepare_records(df):
        key = str(record.get("clave_unica_registro") or "")
        records.append(
            {
                "load_id": load_id_by_key.get(key),
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

    int_columns = {"anio", "mes", "semana", "dia", "hora_numero", "litros_redondeados", "dias_desde_ultima_carga", "row_number"}
    bool_columns = {"registro_duplicado", "alerta_odometro", "alerta_consumo", "out_of_shift"}

    for col in int_columns:
        if col in normalized.columns:
            normalized[col] = normalized[col].apply(lambda v: int(v) if v is not None else None)

    for col in bool_columns:
        if col in normalized.columns:
            normalized[col] = normalized[col].apply(lambda v: bool(v) if v is not None else False)

    return normalized.to_dict(orient="records")


def _batched(items: list[dict], batch_size: int) -> list[list[dict]]:
    return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]
