import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.consultation import Followup
from app.models.user import User

router = APIRouter(prefix="/followup", tags=["随访管理"])


class FollowupCreate(BaseModel):
    patient_id: uuid.UUID
    consultation_id: Optional[uuid.UUID] = None
    scheduled_date: datetime
    notes: Optional[str] = None


class FollowupUpdate(BaseModel):
    scheduled_date: Optional[datetime] = None
    actual_date: Optional[datetime] = None
    status: Optional[str] = None
    symptom_score: Optional[int] = None
    notes: Optional[str] = None
    recovery_status: Optional[str] = None
    images: Optional[list] = None


class FollowupComplete(BaseModel):
    symptom_score: Optional[int] = None
    notes: Optional[str] = None
    recovery_status: Optional[str] = None
    images: Optional[list] = None


@router.get("")
async def list_followups(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    patient_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    upcoming: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Followup).where(Followup.tenant_id == current_user.tenant_id)

    if patient_id:
        query = query.where(Followup.patient_id == patient_id)
    if status_filter:
        query = query.where(Followup.status == status_filter)
    if upcoming:
        now = datetime.now(timezone.utc)
        query = query.where(
            Followup.scheduled_date >= now,
            Followup.status == "scheduled",
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(Followup.scheduled_date)
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    followups = result.scalars().all()

    return {"total": total, "items": followups}


@router.get("/today")
async def get_today_followups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all followups scheduled for today."""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    result = await db.execute(
        select(Followup).where(
            Followup.tenant_id == current_user.tenant_id,
            Followup.scheduled_date >= today_start,
            Followup.scheduled_date < today_end,
            Followup.status == "scheduled",
        ).order_by(Followup.scheduled_date)
    )
    followups = result.scalars().all()
    return {"total": len(followups), "items": followups}


@router.get("/overdue")
async def get_overdue_followups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all overdue followups (scheduled date passed, still in scheduled status)."""
    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(Followup).where(
            Followup.tenant_id == current_user.tenant_id,
            Followup.scheduled_date < now,
            Followup.status == "scheduled",
        ).order_by(Followup.scheduled_date)
    )
    followups = result.scalars().all()
    return {"total": len(followups), "items": followups}


@router.get("/{followup_id}")
async def get_followup(
    followup_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Followup).where(
            Followup.id == followup_id,
            Followup.tenant_id == current_user.tenant_id,
        )
    )
    followup = result.scalar_one_or_none()
    if not followup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="随访记录不存在")
    return followup


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_followup(
    data: FollowupCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    followup = Followup(
        tenant_id=current_user.tenant_id,
        patient_id=data.patient_id,
        consultation_id=data.consultation_id,
        doctor_id=current_user.id,
        scheduled_date=data.scheduled_date,
        notes=data.notes,
        status="scheduled",
    )
    db.add(followup)
    await db.flush()
    await db.refresh(followup)
    return followup


@router.put("/{followup_id}")
async def update_followup(
    followup_id: uuid.UUID,
    data: FollowupUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Followup).where(
            Followup.id == followup_id,
            Followup.tenant_id == current_user.tenant_id,
        )
    )
    followup = result.scalar_one_or_none()
    if not followup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="随访记录不存在")

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(followup, key, value)

    db.add(followup)
    await db.flush()
    await db.refresh(followup)
    return followup


@router.post("/{followup_id}/complete")
async def complete_followup(
    followup_id: uuid.UUID,
    data: FollowupComplete,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a followup as completed."""
    result = await db.execute(
        select(Followup).where(
            Followup.id == followup_id,
            Followup.tenant_id == current_user.tenant_id,
        )
    )
    followup = result.scalar_one_or_none()
    if not followup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="随访记录不存在")

    followup.status = "completed"
    followup.actual_date = datetime.now(timezone.utc)
    if data.symptom_score is not None:
        followup.symptom_score = data.symptom_score
    if data.notes:
        followup.notes = data.notes
    if data.recovery_status:
        followup.recovery_status = data.recovery_status
    if data.images:
        followup.images = data.images

    db.add(followup)
    await db.flush()
    await db.refresh(followup)
    return followup


@router.post("/{followup_id}/cancel")
async def cancel_followup(
    followup_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a scheduled followup."""
    result = await db.execute(
        select(Followup).where(
            Followup.id == followup_id,
            Followup.tenant_id == current_user.tenant_id,
        )
    )
    followup = result.scalar_one_or_none()
    if not followup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="随访记录不存在")

    if followup.status != "scheduled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能取消待执行的随访",
        )

    followup.status = "cancelled"
    db.add(followup)
    await db.flush()
    return {"message": "随访已取消"}
