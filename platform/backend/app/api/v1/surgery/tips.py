"""临证心法(外科用药秘诀)"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.surgery import SurgeryClinicalTip
from app.schemas.surgery import ClinicalTipOut

router = APIRouter(prefix="/api/v1/surgery/tips", tags=["疮疡-临证心法"])


@router.get("", response_model=list[ClinicalTipOut])
async def list_tips(
    category: Optional[str] = Query(None, description="分类筛选"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SurgeryClinicalTip).order_by(SurgeryClinicalTip.id)
    if category:
        stmt = stmt.where(SurgeryClinicalTip.category == category)
    result = await db.execute(stmt)
    return list(result.scalars().all())
