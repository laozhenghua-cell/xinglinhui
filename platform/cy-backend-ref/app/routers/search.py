"""全库搜索(病种/方剂/医案/临证心法)"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Case, ClinicalTip, Disease, ExpertCase, Formula

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("")
async def search(q: str = Query(..., min_length=1), db: AsyncSession = Depends(get_db)):
    q = q.strip()
    if not q:
        return {"diseases": [], "formulas": [], "tips": [], "cases": []}
    like = f"%{q}%"

    diseases = (await db.execute(
        select(Disease).where(or_(
            Disease.name.like(like),
            Disease.location.like(like),
            Disease.western_equiv.like(like),
        )).limit(20)
    )).scalars().all()

    formulas = (await db.execute(
        select(Formula).where(or_(
            Formula.name.like(like),
            Formula.composition.like(like),
        )).limit(20)
    )).scalars().all()

    tips = (await db.execute(
        select(ClinicalTip).where(or_(
            ClinicalTip.content.like(like),
            ClinicalTip.category.like(like),
        )).limit(20)
    )).scalars().all()

    cases = (await db.execute(
        select(ExpertCase).where(or_(
            ExpertCase.diagnosis.like(like),
            ExpertCase.syndrome.like(like),
            ExpertCase.treatment.like(like),
        )).limit(20)
    )).scalars().all()

    return {
        "diseases": [{"id": d.id, "name": d.name, "category": d.category} for d in diseases],
        "formulas": [{"id": f.id, "name": f.name, "composition": f.composition or ""} for f in formulas],
        "tips": [{"id": t.id, "category": t.category, "content": t.content[:80]} for t in tips],
        "cases": [{"id": c.id, "diagnosis": c.diagnosis, "category": c.category} for c in cases],
    }
