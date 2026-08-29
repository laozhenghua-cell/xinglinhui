import os
import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/uploads", tags=["文件上传"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def get_upload_dir(tenant_id: uuid.UUID, subfolder: str = "images") -> Path:
    upload_path = Path(settings.UPLOAD_DIR) / str(tenant_id) / subfolder
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a clinical image file."""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {file.content_type}。支持: JPEG, PNG, WebP, BMP",
        )

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制 ({settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB)",
        )

    ext = Path(file.filename).suffix.lower() if file.filename else ".jpg"
    if ext not in ALLOWED_EXTENSIONS:
        ext = ".jpg"

    file_id = uuid.uuid4()
    filename = f"{file_id}{ext}"
    upload_dir = get_upload_dir(current_user.tenant_id)
    file_path = upload_dir / filename

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return {
        "file_id": str(file_id),
        "filename": filename,
        "file_path": str(file_path),
        "file_size": len(content),
        "content_type": file.content_type,
        "url": f"/api/v1/uploads/files/{current_user.tenant_id}/{filename}",
    }


@router.post("/document")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a document (PDF, etc.)."""
    allowed_doc_types = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    if file.content_type not in allowed_doc_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的文件类型，仅支持PDF和Word文档",
        )

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小超过限制",
        )

    ext = Path(file.filename).suffix.lower() if file.filename else ".pdf"
    file_id = uuid.uuid4()
    filename = f"{file_id}{ext}"
    upload_dir = get_upload_dir(current_user.tenant_id, subfolder="documents")
    file_path = upload_dir / filename

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return {
        "file_id": str(file_id),
        "filename": filename,
        "file_path": str(file_path),
        "file_size": len(content),
        "content_type": file.content_type,
    }


def _safe_filename(filename: str) -> str:
    """拒绝路径穿越：文件名只允许 uuid.扩展名 形式。"""
    if not filename or "/" in filename or "\\" in filename or ".." in filename or filename.startswith("."):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="非法文件名")
    return filename


@router.get("/files/{tenant_id}/{filename}")
async def get_file(
    tenant_id: uuid.UUID,
    filename: str,
    current_user: User = Depends(get_current_user),
):
    """Download/serve a previously uploaded file."""
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此文件",
        )
    filename = _safe_filename(filename)

    # Check images directory first, then documents
    for subfolder in ["images", "documents"]:
        file_path = Path(settings.UPLOAD_DIR) / str(tenant_id) / subfolder / filename
        if file_path.exists():
            return FileResponse(
                path=str(file_path),
                filename=filename,
            )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")


@router.delete("/files/{tenant_id}/{filename}")
async def delete_file(
    tenant_id: uuid.UUID,
    filename: str,
    current_user: User = Depends(get_current_user),
):
    """Delete an uploaded file."""
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此文件",
        )
    filename = _safe_filename(filename)

    for subfolder in ["images", "documents"]:
        file_path = Path(settings.UPLOAD_DIR) / str(tenant_id) / subfolder / filename
        if file_path.exists():
            os.remove(file_path)
            return {"message": "文件已删除"}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")
