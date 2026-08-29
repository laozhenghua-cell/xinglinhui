"""名家经验(等)"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import ExpertCase, ExpertExperience
from ..schemas import ExpertCaseOut, ExpertExperienceOut

router = APIRouter(prefix="/api/v1/expert", tags=["expert"])


@router.get("/{category}")
async def get_expert(category: str, db: AsyncSession = Depends(get_db)):
    """按病种大类获取名家经验 + 医案"""
    exps = (await db.execute(
        select(ExpertExperience).where(ExpertExperience.category == category)
    )).scalars().all()
    cases = (await db.execute(
        select(ExpertCase).where(ExpertCase.category == category).order_by(ExpertCase.id)
    )).scalars().all()
    return {
        "category": category,
        "experiences": [ExpertExperienceOut.model_validate(e) for e in exps],
        "cases": [ExpertCaseOut.model_validate(c) for c in cases],
    }
