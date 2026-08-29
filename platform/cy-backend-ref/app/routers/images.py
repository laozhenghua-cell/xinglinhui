"""图片(书本参考图 / 上传图)"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Image
from ..schemas import ImageOut

router = APIRouter(prefix="/api/v1/images", tags=["images"])


@router.get("", response_model=list[ImageOut])
async def list_images(
    image_type: Optional[str] = Query(None, description="book / case"),
    disease_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None, description="图版所属类别"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Image).order_by(Image.id)
    if image_type:
        stmt = stmt.where(Image.image_type == image_type)
    if disease_id is not None:
        stmt = stmt.where(Image.disease_id == disease_id)
    if category:
        stmt = stmt.where(Image.category == category)
    result = await db.execute(stmt)
    return list(result.scalars().all())
