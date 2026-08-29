"""临证心法(外科用药秘诀)"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import ClinicalTip
from ..schemas import ClinicalTipOut

router = APIRouter(prefix="/api/v1/tips", tags=["tips"])


@router.get("", response_model=list[ClinicalTipOut])
async def list_tips(
    category: Optional[str] = Query(None, description="分类筛选"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ClinicalTip).order_by(ClinicalTip.id)
    if category:
        stmt = stmt.where(ClinicalTip.category == category)
    result = await db.execute(stmt)
    return list(result.scalars().all())
