"""证型"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.surgery import SurgerySyndrome
from app.schemas.surgery import SyndromeOut

router = APIRouter(prefix="/api/v1/surgery/syndromes", tags=["疮疡-证型"])


@router.get("", response_model=list[SyndromeOut])
async def list_syndromes(
    yin_yang: Optional[str] = Query(None, description="阳 / 阴"),
    stage: Optional[str] = Query(None, description="初起 / 成脓 / 溃后"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SurgerySyndrome).order_by(SurgerySyndrome.id)
    if yin_yang:
        stmt = stmt.where(SurgerySyndrome.yin_yang == yin_yang)
    if stage:
        stmt = stmt.where(SurgerySyndrome.stage == stage)
    result = await db.execute(stmt)
    return list(result.scalars().all())
