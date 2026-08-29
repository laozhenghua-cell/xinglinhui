"""数据统计面板"""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.surgery import (
    SurgeryCase,
    SurgeryDisease,
    SurgeryFormula,
    SurgerySyndrome,
    SurgeryTreatmentRecord,
)

router = APIRouter(prefix="/api/v1/surgery/stats", tags=["疮疡-统计"])


@router.get("/overview")
async def overview(db: AsyncSession = Depends(get_db)):
    cases = (await db.execute(select(func.count()).select_from(SurgeryCase))).scalar()
    diseases = (await db.execute(select(func.count()).select_from(SurgeryDisease))).scalar()
    formulas = (await db.execute(select(func.count()).select_from(SurgeryFormula))).scalar()
    syndromes = (await db.execute(select(func.count()).select_from(SurgerySyndrome))).scalar()

    disease_dist = (
        await db.execute(
            select(SurgeryDisease.name, func.count(SurgeryCase.id))
            .join(SurgeryCase, SurgeryCase.disease_id == SurgeryDisease.id)
            .group_by(SurgeryDisease.id)
            .order_by(func.count(SurgeryCase.id).desc())
            .limit(10)
        )
    ).all()

    syndrome_dist = (
        await db.execute(
            select(SurgerySyndrome.name, func.count(SurgeryCase.id))
            .join(SurgeryCase, SurgeryCase.syndrome_id == SurgerySyndrome.id)
            .group_by(SurgerySyndrome.id)
            .order_by(func.count(SurgeryCase.id).desc())
        )
    ).all()

    formula_usage = (
        await db.execute(
            select(SurgeryFormula.name, func.count(SurgeryTreatmentRecord.id))
            .join(SurgeryTreatmentRecord, SurgeryTreatmentRecord.formula_id == SurgeryFormula.id)
            .group_by(SurgeryFormula.id)
            .order_by(func.count(SurgeryTreatmentRecord.id).desc())
            .limit(10)
        )
    ).all()

    effect_dist = (
        await db.execute(
            select(SurgeryTreatmentRecord.effect, func.count(SurgeryTreatmentRecord.id))
            .where(SurgeryTreatmentRecord.effect.isnot(None))
            .group_by(SurgeryTreatmentRecord.effect)
            .order_by(func.count(SurgeryTreatmentRecord.id).desc())
        )
    ).all()

    return {
        "counts": {
            "patients": 0,  # 复用基座 patients 表，此统计不含疮疡患者数
            "cases": cases,
            "diseases": diseases,
            "formulas": formulas,
            "syndromes": syndromes,
        },
        "disease_distribution": [{"name": n, "count": c} for n, c in disease_dist],
        "syndrome_distribution": [{"name": n, "count": c} for n, c in syndrome_dist],
        "formula_usage": [{"name": n, "count": c} for n, c in formula_usage],
        "effect_distribution": [{"effect": e, "count": c} for e, c in effect_dist],
    }
