"""图片(书本参考图 / 上传图)"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.surgery import SurgeryImage
from app.schemas.surgery import ImageOut

router = APIRouter(prefix="/api/v1/surgery/images", tags=["疮疡-图片"])


@router.get("", response_model=list[ImageOut])
async def list_images(
    image_type: Optional[str] = Query(None, description="book / case"),
    disease_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None, description="图版所属类别"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SurgeryImage).order_by(SurgeryImage.id)
    if image_type:
        stmt = stmt.where(SurgeryImage.image_type == image_type)
    if disease_id is not None:
        stmt = stmt.where(SurgeryImage.disease_id == disease_id)
    if category:
        stmt = stmt.where(SurgeryImage.category == category)
    result = await db.execute(stmt)
    return list(result.scalars().all())
