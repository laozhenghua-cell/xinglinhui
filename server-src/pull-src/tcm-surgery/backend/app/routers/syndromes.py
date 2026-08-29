"""证型"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Syndrome
from ..schemas import SyndromeOut

router = APIRouter(prefix="/api/v1/syndromes", tags=["syndromes"])


@router.get("", response_model=list[SyndromeOut])
async def list_syndromes(
    yin_yang: Optional[str] = Query(None, description="阳 / 阴"),
    stage: Optional[str] = Query(None, description="初起 / 成脓 / 溃后"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Syndrome).order_by(Syndrome.id)
    if yin_yang:
        stmt = stmt.where(Syndrome.yin_yang == yin_yang)
    if stage:
        stmt = stmt.where(Syndrome.stage == stage)
    result = await db.execute(stmt)
    return list(result.scalars().all())
