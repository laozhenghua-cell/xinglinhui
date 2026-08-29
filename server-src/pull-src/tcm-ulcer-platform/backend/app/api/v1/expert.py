from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from typing import Optional
from datetime import datetime

from ...core.database import get_db
from ...core.security import get_current_user, require_role
from ...models.user import User
from ...models.consultation_request import ConsultationRequest
from ...models.expert_response import ExpertResponse
from ...models.expert_profile import ExpertProfile
from ...models.ulcer_consultation import UlcerConsultation
from ...models.ulcer_image import UlcerImage

router = APIRouter()


@router.get("/queue")
async def get_expert_queue(
    status: str = "pending",
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["expert"]))
):
    """获取专家会诊队列"""

    # 获取分配给当前专家或未分配的会诊请求
    query = (
        select(ConsultationRequest, UlcerConsultation)
        .join(UlcerConsultation, ConsultationRequest.consultation_id == UlcerConsultation.id)
        .where(
            and_(
                ConsultationRequest.status == status,
                (
                    (ConsultationRequest.expert_id == current_user.id) |
                    (ConsultationRequest.expert_id == None)
                )
            )
        )
        .order_by(desc(ConsultationRequest.priority), ConsultationRequest.requested_at)
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(query)
    items = result.all()

    queue_items = []
    for request, consultation in items:
        # 获取第一张图片
        image_result = await db.execute(
            select(UlcerImage).where(
                UlcerImage.consultation_id == consultation.id
            ).limit(1)
        )
        first_image = image_result.scalar_one_or_none()

        queue_items.append({
            "request_id": request.id,
            "consultation_id": consultation.id,
            "patient_id": consultation.patient_id,
            "ulcer_type": consultation.ulcer_type,
            "location": consultation.location,
            "chief_complaint": consultation.chief_complaint,
            "urgency_level": consultation.urgency_level,
            "priority": request.priority,
            "request_reason": request.request_reason,
            "ai_suggestion": request.ai_suggestion,
            "first_image_url": first_image.image_url if first_image else None,
            "requested_at": request.requested_at,
            "consultation_fee": request.consultation_fee
        })

    return queue_items


@router.post("/queue/{request_id}/accept")
async def accept_consultation_request(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["expert"]))
):
    """接受会诊请求"""

    # 获取会诊请求
    result = await db.execute(
        select(ConsultationRequest).where(ConsultationRequest.id == request_id)
    )
    request = result.scalar_one_or_none()

    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.status != "pending":
        raise HTTPException(status_code=400, detail="Request already processed")

    # 更新请求状态
    request.expert_id = current_user.id
    request.status = "accepted"
    request.accepted_at = datetime.utcnow()

    # 更新会诊记录状态
    consultation_result = await db.execute(
        select(UlcerConsultation).where(UlcerConsultation.id == request.consultation_id)
    )
    consultation = consultation_result.scalar_one()
    consultation.status = "expert_reviewing"

    await db.commit()

    return {
        "request_id": request.id,
        "status": request.status,
        "accepted_at": request.accepted_at
    }


@router.post("/consultations/{request_id}/respond")
async def submit_expert_response(
    request_id: str,
    expert_diagnosis: str,
    syndrome_differentiation: str,
    treatment_principle: Optional[str] = None,
    internal_prescription: Optional[dict] = None,
    external_treatment: Optional[dict] = None,
    image_annotations: Optional[dict] = None,
    clinical_advice: Optional[str] = None,
    follow_up_plan: Optional[str] = None,
    precautions: Optional[str] = None,
    diet_advice: Optional[str] = None,
    need_referral: bool = False,
    referral_reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["expert"]))
):
    """提交专家会诊意见"""

    # 验证会诊请求
    request_result = await db.execute(
        select(ConsultationRequest).where(
            and_(
                ConsultationRequest.id == request_id,
                ConsultationRequest.expert_id == current_user.id,
                ConsultationRequest.status == "accepted"
            )
        )
    )
    request = request_result.scalar_one_or_none()

    if not request:
        raise HTTPException(status_code=404, detail="Request not found or not accepted by you")

    # 计算响应时间
    response_time_minutes = int((datetime.utcnow() - request.accepted_at).total_seconds() / 60)

    # 创建专家回复
    expert_response = ExpertResponse(
        request_id=request_id,
        expert_id=current_user.id,
        expert_diagnosis=expert_diagnosis,
        syndrome_differentiation=syndrome_differentiation,
        treatment_principle=treatment_principle,
        internal_prescription=internal_prescription,
        external_treatment=external_treatment,
        image_annotations=image_annotations,
        clinical_advice=clinical_advice,
        follow_up_plan=follow_up_plan,
        precautions=precautions,
        diet_advice=diet_advice,
        need_referral=need_referral,
        referral_reason=referral_reason,
        response_time_minutes=response_time_minutes
    )

    db.add(expert_response)

    # 更新请求状态
    request.status = "completed"
    request.completed_at = datetime.utcnow()
    request.response_time_minutes = response_time_minutes

    # 更新会诊记录
    consultation_result = await db.execute(
        select(UlcerConsultation).where(UlcerConsultation.id == request.consultation_id)
    )
    consultation = consultation_result.scalar_one()
    consultation.status = "completed"
    consultation.doctor_diagnosis = expert_diagnosis
    consultation.syndrome_differentiation = syndrome_differentiation
    consultation.internal_treatment = internal_prescription
    consultation.external_treatment = external_treatment

    # 更新专家统计
    profile_result = await db.execute(
        select(ExpertProfile).where(ExpertProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one()
    profile.completed_count += 1

    # 更新平均响应时间
    if profile.average_response_minutes:
        profile.average_response_minutes = int(
            (profile.average_response_minutes * (profile.completed_count - 1) + response_time_minutes) / profile.completed_count
        )
    else:
        profile.average_response_minutes = response_time_minutes

    await db.commit()
    await db.refresh(expert_response)

    return {
        "response_id": expert_response.id,
        "request_id": request_id,
        "consultation_id": request.consultation_id,
        "status": "completed",
        "response_time_minutes": response_time_minutes
    }


@router.get("/profile")
async def get_expert_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["expert"]))
):
    """获取专家资料"""

    result = await db.execute(
        select(ExpertProfile).where(ExpertProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Expert profile not found")

    return {
        "user_id": profile.user_id,
        "title": profile.title,
        "specialty": profile.specialty,
        "experience_years": profile.experience_years,
        "bio": profile.bio,
        "hospital": current_user.hospital,
        "department": current_user.department,
        "consultation_fee": profile.consultation_fee,
        "available_hours": profile.available_hours,
        "max_daily_consultations": profile.max_daily_consultations,
        "is_active": profile.is_active,
        "auto_accept": profile.auto_accept,
        "consultation_count": profile.consultation_count,
        "completed_count": profile.completed_count,
        "average_rating": profile.average_rating,
        "total_earnings": profile.total_earnings,
        "average_response_minutes": profile.average_response_minutes,
        "expertise_ulcer_types": profile.expertise_ulcer_types,
        "is_verified": profile.is_verified
    }


@router.put("/profile")
async def update_expert_profile(
    title: Optional[str] = None,
    specialty: Optional[list] = None,
    bio: Optional[str] = None,
    consultation_fee: Optional[int] = None,
    available_hours: Optional[dict] = None,
    is_active: Optional[bool] = None,
    auto_accept: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["expert"]))
):
    """更新专家资料"""

    result = await db.execute(
        select(ExpertProfile).where(ExpertProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Expert profile not found")

    # 更新字段
    if title is not None:
        profile.title = title
    if specialty is not None:
        profile.specialty = specialty
    if bio is not None:
        profile.bio = bio
    if consultation_fee is not None:
        profile.consultation_fee = consultation_fee
    if available_hours is not None:
        profile.available_hours = available_hours
    if is_active is not None:
        profile.is_active = is_active
    if auto_accept is not None:
        profile.auto_accept = auto_accept

    await db.commit()
    await db.refresh(profile)

    return {"message": "Profile updated successfully"}


@router.get("/statistics")
async def get_expert_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["expert"]))
):
    """获取专家统计数据"""

    # 总会诊数
    total_result = await db.execute(
        select(func.count(ConsultationRequest.id)).where(
            ConsultationRequest.expert_id == current_user.id
        )
    )
    total_consultations = total_result.scalar()

    # 本月会诊数
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_result = await db.execute(
        select(func.count(ConsultationRequest.id)).where(
            and_(
                ConsultationRequest.expert_id == current_user.id,
                ConsultationRequest.requested_at >= current_month_start
            )
        )
    )
    monthly_consultations = monthly_result.scalar()

    # 待处理数
    pending_result = await db.execute(
        select(func.count(ConsultationRequest.id)).where(
            and_(
                ConsultationRequest.expert_id == current_user.id,
                ConsultationRequest.status == "accepted"
            )
        )
    )
    pending_consultations = pending_result.scalar()

    # 获取专家资料
    profile_result = await db.execute(
        select(ExpertProfile).where(ExpertProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one()

    return {
        "total_consultations": total_consultations,
        "monthly_consultations": monthly_consultations,
        "pending_consultations": pending_consultations,
        "completed_count": profile.completed_count,
        "average_rating": profile.average_rating,
        "average_response_minutes": profile.average_response_minutes,
        "total_earnings": profile.total_earnings,
        "expertise_ulcer_types": profile.expertise_ulcer_types
    }
