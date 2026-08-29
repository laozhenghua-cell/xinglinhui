"""名家经验"""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.surgery import SurgeryExpertCase, SurgeryExpertExperience
from app.schemas.surgery import ExpertCaseOut, ExpertExperienceOut

router = APIRouter(prefix="/api/v1/surgery/expert", tags=["疮疡-名家经验"])


@router.get("/{category}")
async def get_expert(category: str, db: AsyncSession = Depends(get_db)):
    exps = (await db.execute(
        select(SurgeryExpertExperience).where(SurgeryExpertExperience.category == category)
    )).scalars().all()
    cases = (await db.execute(
        select(SurgeryExpertCase).where(SurgeryExpertCase.category == category).order_by(SurgeryExpertCase.id)
    )).scalars().all()
    return {
        "category": category,
        "experiences": [ExpertExperienceOut.model_validate(e) for e in exps],
        "cases": [ExpertCaseOut.model_validate(c) for c in cases],
    }
