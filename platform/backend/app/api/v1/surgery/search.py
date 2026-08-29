"""全库搜索(病种/方剂/医案/临证心法)"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.surgery import (
    SurgeryCase,
    SurgeryClinicalTip,
    SurgeryDisease,
    SurgeryExpertCase,
    SurgeryFormula,
)

router = APIRouter(prefix="/api/v1/surgery/search", tags=["疮疡-搜索"])


@router.get("")
async def search(q: str = Query(..., min_length=1), db: AsyncSession = Depends(get_db)):
    q = q.strip()
    if not q:
        return {"diseases": [], "formulas": [], "tips": [], "cases": []}
    q_esc = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    like = f"%{q_esc}%"

    diseases = (await db.execute(
        select(SurgeryDisease).where(or_(
            SurgeryDisease.name.like(like),
            SurgeryDisease.location.like(like),
            SurgeryDisease.western_equiv.like(like),
        )).limit(20)
    )).scalars().all()

    formulas = (await db.execute(
        select(SurgeryFormula).where(or_(
            SurgeryFormula.name.like(like),
            SurgeryFormula.composition.like(like),
        )).limit(20)
    )).scalars().all()

    tips = (await db.execute(
        select(SurgeryClinicalTip).where(or_(
            SurgeryClinicalTip.content.like(like),
            SurgeryClinicalTip.category.like(like),
        )).limit(20)
    )).scalars().all()

    cases = (await db.execute(
        select(SurgeryExpertCase).where(or_(
            SurgeryExpertCase.diagnosis.like(like),
            SurgeryExpertCase.syndrome.like(like),
            SurgeryExpertCase.treatment.like(like),
        )).limit(20)
    )).scalars().all()

    return {
        "diseases": [{"id": d.id, "name": d.name, "category": d.category} for d in diseases],
        "formulas": [{"id": f.id, "name": f.name, "composition": f.composition or ""} for f in formulas],
        "tips": [{"id": t.id, "category": t.category, "content": t.content[:80]} for t in tips],
        "cases": [{"id": c.id, "diagnosis": c.diagnosis, "category": c.category} for c in cases],
    }
