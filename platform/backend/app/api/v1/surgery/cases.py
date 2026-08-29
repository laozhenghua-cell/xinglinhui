"""病例 + 复诊照片时间线 + 诊疗记录(医案沉淀)"""
import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.core.surgery_security import limit_write, is_valid_image, limit_ai, read_limited
from app.database import get_db
from app.models.surgery import SurgeryCase, SurgeryCaseImage, SurgeryTreatmentRecord
from app.schemas.surgery import CaseCreate, CaseOut, TreatmentRecordIn, TreatmentRecordOut
from app.services.surgery_ai import surgery_qwen_vision_service

router = APIRouter(prefix="/api/v1/surgery/cases", tags=["疮疡-病例"])

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


async def _get_case(db: AsyncSession, case_id: int) -> SurgeryCase:
    stmt = (
        select(SurgeryCase)
        .options(
            selectinload(SurgeryCase.images),
            selectinload(SurgeryCase.records).selectinload(SurgeryTreatmentRecord.formula),
        )
        .where(SurgeryCase.id == case_id)
    )
    case = (await db.execute(stmt)).scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="病例不存在")
    return case


@router.get("", response_model=list[CaseOut])
async def list_cases(
    domain: Optional[str] = Query(None, description="学科领域:疮疡 / 骨伤 / 妇科"),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(SurgeryCase)
        .options(
            selectinload(SurgeryCase.images),
            selectinload(SurgeryCase.records).selectinload(SurgeryTreatmentRecord.formula),
        )
        .order_by(SurgeryCase.id.desc())
    )
    if domain:
        stmt = stmt.where(SurgeryCase.domain == domain)
    return list((await db.execute(stmt)).scalars().all())


@router.post("", response_model=CaseOut)
async def create_case(body: CaseCreate, request: Request, db: AsyncSession = Depends(get_db)):
    limit_write(request)
    case = SurgeryCase(**body.model_dump())
    db.add(case)
    await db.commit()
    return await _get_case(db, case.id)


@router.get("/{case_id}", response_model=CaseOut)
async def get_case(case_id: int, db: AsyncSession = Depends(get_db)):
    return await _get_case(db, case_id)


@router.post("/{case_id}/images", response_model=CaseOut)
async def upload_image(
    case_id: int,
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    await _get_case(db, case_id)
    ext = os.path.splitext(image.filename or "")[-1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail="不支持的图片格式")

    data = await read_limited(image)
    if not is_valid_image(data):
        raise HTTPException(status_code=400, detail="无效的图片文件")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    with open(os.path.join(settings.UPLOAD_DIR, filename), "wb") as f:
        f.write(data)

    db.add(SurgeryCaseImage(case_id=case_id, path=f"/uploads/{filename}"))
    await db.commit()
    return await _get_case(db, case_id)


@router.post("/{case_id}/records", response_model=TreatmentRecordOut)
async def add_record(case_id: int, body: TreatmentRecordIn, db: AsyncSession = Depends(get_db)):
    await _get_case(db, case_id)
    rec = SurgeryTreatmentRecord(case_id=case_id, **body.model_dump())
    db.add(rec)
    await db.commit()
    stmt = (
        select(SurgeryTreatmentRecord)
        .options(selectinload(SurgeryTreatmentRecord.formula))
        .where(SurgeryTreatmentRecord.id == rec.id)
    )
    return (await db.execute(stmt)).scalar_one()


@router.post("/{case_id}/compare")
async def compare_case(case_id: int, request: Request = None, db: AsyncSession = Depends(get_db)):
    limit_ai(request)
    case = await _get_case(db, case_id)
    images = sorted(case.images, key=lambda x: x.taken_at or x.id)
    if len(images) < 2:
        raise HTTPException(status_code=400, detail="至少需要 2 张照片才能对比疗效")

    initial, latest = images[0], images[-1]
    days = 0
    if initial.taken_at and latest.taken_at:
        days = (latest.taken_at - initial.taken_at).days

    try:
        result = await surgery_qwen_vision_service.compare_images(
            initial.path.lstrip("/"), latest.path.lstrip("/"), days
        )
    except Exception:
        result = {"error": "AI 对比失败,请稍后重试"}

    return {
        "initial_image": initial.path,
        "current_image": latest.path,
        "days": days,
        "result": result,
    }
