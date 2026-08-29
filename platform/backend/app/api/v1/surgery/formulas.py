"""方药"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.surgery import SurgeryFormula
from app.schemas.surgery import FormulaOut

router = APIRouter(prefix="/api/v1/surgery/formulas", tags=["疮疡-方药"])


@router.get("", response_model=list[FormulaOut])
async def list_formulas(
    method: Optional[str] = Query(None, description="治法:消 / 托 / 补"),
    usage_type: Optional[str] = Query(None, description="内治 / 外治"),
    domain: Optional[str] = Query(None, description="学科领域:疮疡 / 骨伤 / 杂病 / 妇科"),
    q: Optional[str] = Query(None, description="检索:方名/功效/适应证/组成"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SurgeryFormula).order_by(SurgeryFormula.id)
    if method:
        stmt = stmt.where(SurgeryFormula.method == method)
    if usage_type:
        stmt = stmt.where(SurgeryFormula.usage_type == usage_type)
    if domain:
        stmt = stmt.where(SurgeryFormula.domain == domain)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            SurgeryFormula.name.like(like)
            | SurgeryFormula.function.like(like)
            | SurgeryFormula.indication.like(like)
            | SurgeryFormula.composition.like(like)
        )
    result = await db.execute(stmt)
    return list(result.scalars().all())
