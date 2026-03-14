from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.database import get_db_session
from app.models.processing_log import ProcessingLog
from app.schemas.auth import CurrentUser
from app.schemas.files import ProcessResponse, UploadResponse, UploadedFileResponse
from app.services.file_service import create_uploaded_file, process_uploaded_file
from app.services.analytics_service import get_uploaded_files
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(tags=["files"])


@router.post("/upload-file", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> UploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Archivo sin nombre")

    allowed_ext = (".xlsx", ".xls")
    if not file.filename.lower().endswith(allowed_ext):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos Excel (.xlsx, .xls)")

    payload = await file.read()
    if len(payload) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"Archivo supera {settings.max_upload_size_mb} MB")

    uploaded = await create_uploaded_file(
        db=db,
        filename=file.filename,
        payload=payload,
        user_id=user.id,
        content_type=file.content_type or "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    return UploadResponse(file_id=uploaded.id, filename=uploaded.filename, status=uploaded.status)


@router.post("/process-file/{file_id}", response_model=ProcessResponse)
async def process_file(
    file_id: UUID,
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> ProcessResponse:
    try:
        result = await process_uploaded_file(db, file_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ProcessResponse(**result)


@router.get("/files", response_model=list[UploadedFileResponse])
async def list_files(
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[UploadedFileResponse]:
    files = await get_uploaded_files(db, limit=500)
    return [UploadedFileResponse.model_validate(f) for f in files]


@router.get("/files/{file_id}/logs")
async def get_file_logs(
    file_id: UUID,
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    stmt = (
        select(ProcessingLog)
        .where(ProcessingLog.file_id == file_id)
        .order_by(desc(ProcessingLog.created_at), ProcessingLog.row_index)
        .limit(5000)
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()

    return [
        {
            "id": log.id,
            "level": log.level,
            "code": log.code,
            "message": log.message,
            "row_index": log.row_index,
            "created_at": log.created_at,
        }
        for log in logs
    ]
