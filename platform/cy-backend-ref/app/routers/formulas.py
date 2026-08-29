"""方药(82附方)"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Formula
from ..schemas import FormulaOut

router = APIRouter(prefix="/api/v1/formulas", tags=["formulas"])


@router.get("", response_model=list[FormulaOut])
async def list_formulas(
    method: Optional[str] = Query(None, description="治法:消 / 托 / 补"),
    usage_type: Optional[str] = Query(None, description="内治 / 外治"),
    domain: Optional[str] = Query(None, description="学科领域:疮疡 / 骨伤 / 杂病 / 妇科"),
    q: Optional[str] = Query(None, description="检索:方名/功效/适应证/组成"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Formula).order_by(Formula.id)
    if method:
        stmt = stmt.where(Formula.method == method)
    if usage_type:
        stmt = stmt.where(Formula.usage_type == usage_type)
    if domain:
        stmt = stmt.where(Formula.domain == domain)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            Formula.name.like(like)
            | Formula.function.like(like)
            | Formula.indication.like(like)
            | Formula.composition.like(like)
        )
    result = await db.execute(stmt)
    return list(result.scalars().all())
