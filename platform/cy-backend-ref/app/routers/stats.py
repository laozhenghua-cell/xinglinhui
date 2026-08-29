"""数据统计面板"""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Case, Disease, Formula, Patient, Syndrome, TreatmentRecord

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])


@router.get("/overview")
async def overview(db: AsyncSession = Depends(get_db)):
    # 基础计数
    patients = (await db.execute(select(func.count()).select_from(Patient))).scalar()
    cases = (await db.execute(select(func.count()).select_from(Case))).scalar()
    diseases = (await db.execute(select(func.count()).select_from(Disease))).scalar()
    formulas = (await db.execute(select(func.count()).select_from(Formula))).scalar()
    syndromes = (await db.execute(select(func.count()).select_from(Syndrome))).scalar()

    # 病种分布(病例数)
    disease_dist = (
        await db.execute(
            select(Disease.name, func.count(Case.id))
            .join(Case, Case.disease_id == Disease.id)
            .group_by(Disease.id)
            .order_by(func.count(Case.id).desc())
            .limit(10)
        )
    ).all()

    # 证型分布
    syndrome_dist = (
        await db.execute(
            select(Syndrome.name, func.count(Case.id))
            .join(Case, Case.syndrome_id == Syndrome.id)
            .group_by(Syndrome.id)
            .order_by(func.count(Case.id).desc())
        )
    ).all()

    # 常用方剂(诊疗记录内治方)
    formula_usage = (
        await db.execute(
            select(Formula.name, func.count(TreatmentRecord.id))
            .join(TreatmentRecord, TreatmentRecord.formula_id == Formula.id)
            .group_by(Formula.id)
            .order_by(func.count(TreatmentRecord.id).desc())
            .limit(10)
        )
    ).all()

    # 疗效分布
    effect_dist = (
        await db.execute(
            select(TreatmentRecord.effect, func.count(TreatmentRecord.id))
            .where(TreatmentRecord.effect.isnot(None))
            .group_by(TreatmentRecord.effect)
            .order_by(func.count(TreatmentRecord.id).desc())
        )
    ).all()

    return {
        "counts": {
            "patients": patients,
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
