"""病种 / 图谱库"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.surgery import SurgeryDisease, SurgeryImage, SurgeryTreatmentRule
from app.schemas.surgery import DiseaseBrief, DiseaseOut

router = APIRouter(prefix="/api/v1/surgery/diseases", tags=["疮疡-病种"])


def _with_thumbnail(diseases: list[SurgeryDisease]) -> list[DiseaseBrief]:
    """给病种列表附加缩略图(第一张病种照片)"""
    out = []
    for d in diseases:
        brief = DiseaseBrief.model_validate(d)
        photo = next(
            (i for i in (d.images or []) if i.image_type == "book" and i.caption and i.caption.startswith("图")),
            None,
        )
        brief.thumbnail = photo.path if photo else None
        out.append(brief)
    return out


@router.get("/categories", response_model=list[str])
async def list_categories(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(SurgeryDisease.category, func.count(SurgeryDisease.id))
        .group_by(SurgeryDisease.category)
        .order_by(func.count(SurgeryDisease.id).desc(), SurgeryDisease.category)
    )
    result = await db.execute(stmt)
    return [row[0] for row in result.all()]


@router.get("", response_model=list[DiseaseBrief])
async def list_diseases(
    category: Optional[str] = Query(None, description="按大类筛选:疖/痈/疽/疔"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SurgeryDisease).options(selectinload(SurgeryDisease.images)).order_by(SurgeryDisease.id)
    if category:
        stmt = stmt.where(SurgeryDisease.category == category)
    result = await db.execute(stmt)
    return _with_thumbnail(list(result.scalars().all()))


@router.get("/search", response_model=list[DiseaseBrief])
async def search_diseases(
    q: str = Query(..., min_length=1, description="搜索关键词(病名/别名/部位/疮形特点)"),
    db: AsyncSession = Depends(get_db),
):
    like = f"%{q}%"
    stmt = (
        select(SurgeryDisease)
        .options(selectinload(SurgeryDisease.images))
        .where(
            or_(
                SurgeryDisease.name.like(like),
                SurgeryDisease.location.like(like),
                SurgeryDisease.morphology.like(like),
                SurgeryDisease.characteristics.like(like),
                SurgeryDisease.western_equiv.like(like),
                SurgeryDisease.differential.like(like),
            )
        )
        .order_by(SurgeryDisease.id)
        .limit(30)
    )
    result = await db.execute(stmt)
    return _with_thumbnail(list(result.scalars().all()))


@router.get("/{disease_id}", response_model=DiseaseOut)
async def get_disease(disease_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(SurgeryDisease)
        .options(
            selectinload(SurgeryDisease.images),
            selectinload(SurgeryDisease.rules).selectinload(SurgeryTreatmentRule.syndrome),
            selectinload(SurgeryDisease.rules).selectinload(SurgeryTreatmentRule.formula),
        )
        .where(SurgeryDisease.id == disease_id)
    )
    result = await db.execute(stmt)
    disease = result.scalar_one_or_none()
    if not disease:
        raise HTTPException(status_code=404, detail="病种不存在")
    return disease
