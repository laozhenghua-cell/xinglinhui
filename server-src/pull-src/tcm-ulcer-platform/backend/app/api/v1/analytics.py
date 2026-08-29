from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User
from ...models.ulcer_consultation import UlcerConsultation
from ...models.consultation_request import ConsultationRequest
from ...models.treatment_outcome import TreatmentOutcome

router = APIRouter()


@router.get("/overview")
async def get_analytics_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取数据分析概览"""

    # 总会诊数
    total_consultations_result = await db.execute(
        select(func.count(UlcerConsultation.id)).where(
            UlcerConsultation.doctor_id == current_user.id
        )
    )
    total_consultations = total_consultations_result.scalar()

    # 本月会诊数
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_result = await db.execute(
        select(func.count(UlcerConsultation.id)).where(
            and_(
                UlcerConsultation.doctor_id == current_user.id,
                UlcerConsultation.created_at >= current_month_start
            )
        )
    )
    monthly_consultations = monthly_result.scalar()

    # 待处理会诊
    pending_result = await db.execute(
        select(func.count(UlcerConsultation.id)).where(
            and_(
                UlcerConsultation.doctor_id == current_user.id,
                UlcerConsultation.status.in_(["draft", "ai_analyzing", "pending_expert"])
            )
        )
    )
    pending_consultations = pending_result.scalar()

    # 专家会诊请求数
    expert_requests_result = await db.execute(
        select(func.count(ConsultationRequest.id)).where(
            ConsultationRequest.requesting_doctor_id == current_user.id
        )
    )
    expert_requests = expert_requests_result.scalar()

    # 治愈病例数
    cured_result = await db.execute(
        select(func.count(TreatmentOutcome.id)).where(
            TreatmentOutcome.cured == True
        )
    )
    cured_cases = cured_result.scalar()

    # 按疮疡类型统计
    ulcer_type_stats = await db.execute(
        select(
            UlcerConsultation.ulcer_type,
            func.count(UlcerConsultation.id).label('count')
        ).where(
            UlcerConsultation.doctor_id == current_user.id
        ).group_by(UlcerConsultation.ulcer_type)
    )
    ulcer_types = [
        {"type": row.ulcer_type or "未分类", "count": row.count}
        for row in ulcer_type_stats
    ]

    return {
        "total_consultations": total_consultations,
        "monthly_consultations": monthly_consultations,
        "pending_consultations": pending_consultations,
        "expert_requests": expert_requests,
        "cured_cases": cured_cases,
        "ulcer_type_distribution": ulcer_types
    }


@router.get("/trends")
async def get_consultation_trends(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取会诊趋势（最近N天）"""

    start_date = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(
            func.date(UlcerConsultation.created_at).label('date'),
            func.count(UlcerConsultation.id).label('count')
        ).where(
            and_(
                UlcerConsultation.doctor_id == current_user.id,
                UlcerConsultation.created_at >= start_date
            )
        ).group_by(func.date(UlcerConsultation.created_at))
        .order_by('date')
    )

    trends = [
        {"date": str(row.date), "count": row.count}
        for row in result
    ]

    return trends
