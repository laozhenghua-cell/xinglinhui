"""病种 / 图谱库"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Disease, Image, TreatmentRule
from ..schemas import DiseaseBrief, DiseaseOut

router = APIRouter(prefix="/api/v1/diseases", tags=["diseases"])


def _with_thumbnail(diseases: list[Disease]) -> list[DiseaseBrief]:
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
    # 按病种数量降序,让大类(疔/痈/有头疽)优先显示
    stmt = (
        select(Disease.category, func.count(Disease.id))
        .group_by(Disease.category)
        .order_by(func.count(Disease.id).desc(), Disease.category)
    )
    result = await db.execute(stmt)
    return [row[0] for row in result.all()]


@router.get("", response_model=list[DiseaseBrief])
async def list_diseases(
    category: Optional[str] = Query(None, description="按大类筛选:疖/痈/疽/疔"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Disease).options(selectinload(Disease.images)).order_by(Disease.id)
    if category:
        stmt = stmt.where(Disease.category == category)
    result = await db.execute(stmt)
    return _with_thumbnail(list(result.scalars().all()))


@router.get("/search", response_model=list[DiseaseBrief])
async def search_diseases(
    q: str = Query(..., min_length=1, description="搜索关键词(病名/别名/部位/疮形特点)"),
    db: AsyncSession = Depends(get_db),
):
    """按症状/病名/部位搜索病种"""
    like = f"%{q}%"
    stmt = (
        select(Disease)
        .options(selectinload(Disease.images))
        .where(
            or_(
                Disease.name.like(like),
                Disease.location.like(like),
                Disease.morphology.like(like),
                Disease.characteristics.like(like),
                Disease.western_equiv.like(like),
                Disease.differential.like(like),
            )
        )
        .order_by(Disease.id)
        .limit(30)
    )
    result = await db.execute(stmt)
    return _with_thumbnail(list(result.scalars().all()))


@router.get("/{disease_id}", response_model=DiseaseOut)
async def get_disease(disease_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Disease)
        .options(
            selectinload(Disease.images),
            selectinload(Disease.rules).selectinload(TreatmentRule.syndrome),
            selectinload(Disease.rules).selectinload(TreatmentRule.formula),
        )
        .where(Disease.id == disease_id)
    )
    result = await db.execute(stmt)
    disease = result.scalar_one_or_none()
    if not disease:
        raise HTTPException(status_code=404, detail="病种不存在")
    return disease
