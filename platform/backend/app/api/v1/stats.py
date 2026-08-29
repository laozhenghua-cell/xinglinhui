from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.billing import Bill, BillPayment, DailyRevenue
from app.models.consultation import Consultation
from app.models.inventory import Medicine, StockAlert
from app.models.patient import Patient
from app.models.user import User

router = APIRouter(prefix="/stats", tags=["统计概览"])


@router.get("/overview")
async def get_overview_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard overview statistics."""
    tenant_id = current_user.tenant_id
    today = date.today()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)

    # Patient counts
    total_patients_result = await db.execute(
        select(func.count()).where(Patient.tenant_id == tenant_id)
    )
    total_patients = total_patients_result.scalar()

    new_patients_today_result = await db.execute(
        select(func.count()).where(
            Patient.tenant_id == tenant_id,
            func.date(Patient.created_at) == today,
        )
    )
    new_patients_today = new_patients_today_result.scalar()

    new_patients_month_result = await db.execute(
        select(func.count()).where(
            Patient.tenant_id == tenant_id,
            Patient.created_at >= datetime.combine(this_month_start, datetime.min.time()),
        )
    )
    new_patients_month = new_patients_month_result.scalar()

    # Consultation counts
    total_consultations_result = await db.execute(
        select(func.count()).where(Consultation.tenant_id == tenant_id)
    )
    total_consultations = total_consultations_result.scalar()

    consultations_today_result = await db.execute(
        select(func.count()).where(
            Consultation.tenant_id == tenant_id,
            func.date(Consultation.created_at) == today,
        )
    )
    consultations_today = consultations_today_result.scalar()

    consultations_month_result = await db.execute(
        select(func.count()).where(
            Consultation.tenant_id == tenant_id,
            Consultation.created_at >= datetime.combine(this_month_start, datetime.min.time()),
        )
    )
    consultations_month = consultations_month_result.scalar()

    # Revenue
    today_revenue_result = await db.execute(
        select(func.coalesce(func.sum(BillPayment.amount), 0)).where(
            BillPayment.tenant_id == tenant_id,
            func.date(BillPayment.created_at) == today,
        )
    )
    today_revenue = today_revenue_result.scalar() or Decimal("0.00")

    month_revenue_result = await db.execute(
        select(func.coalesce(func.sum(BillPayment.amount), 0)).where(
            BillPayment.tenant_id == tenant_id,
            BillPayment.created_at >= datetime.combine(this_month_start, datetime.min.time()),
        )
    )
    month_revenue = month_revenue_result.scalar() or Decimal("0.00")

    # Pending bills
    pending_bills_result = await db.execute(
        select(func.count()).where(
            Bill.tenant_id == tenant_id,
            Bill.status.in_(["pending", "partial"]),
        )
    )
    pending_bills = pending_bills_result.scalar()

    # Inventory alerts
    active_alerts_result = await db.execute(
        select(func.count()).where(
            StockAlert.tenant_id == tenant_id,
            StockAlert.is_resolved == False,
        )
    )
    active_alerts = active_alerts_result.scalar()

    low_stock_result = await db.execute(
        select(func.count()).where(
            Medicine.tenant_id == tenant_id,
            Medicine.is_active == True,
            Medicine.stock_quantity <= Medicine.min_stock,
        )
    )
    low_stock_count = low_stock_result.scalar()

    # Disease type distribution (this month)
    disease_dist_result = await db.execute(
        select(Consultation.disease_type, func.count()).where(
            Consultation.tenant_id == tenant_id,
            Consultation.created_at >= datetime.combine(this_month_start, datetime.min.time()),
            Consultation.disease_type.isnot(None),
        ).group_by(Consultation.disease_type)
    )
    disease_distribution = [
        {"disease_type": row[0], "count": row[1]}
        for row in disease_dist_result.all()
    ]

    return {
        "patients": {
            "total": total_patients,
            "today": new_patients_today,
            "this_month": new_patients_month,
        },
        "consultations": {
            "total": total_consultations,
            "today": consultations_today,
            "this_month": consultations_month,
        },
        "revenue": {
            "today": float(today_revenue),
            "this_month": float(month_revenue),
            "pending_bills": pending_bills,
        },
        "inventory": {
            "active_alerts": active_alerts,
            "low_stock_count": low_stock_count,
        },
        "disease_distribution": disease_distribution,
    }


@router.get("/trends")
async def get_trends(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get daily trends for the past N days."""
    tenant_id = current_user.tenant_id
    start_date = date.today() - timedelta(days=days)

    # Daily consultations
    consultations_by_day = await db.execute(
        select(
            func.date(Consultation.created_at).label("day"),
            func.count().label("count"),
        )
        .where(
            Consultation.tenant_id == tenant_id,
            func.date(Consultation.created_at) >= start_date,
        )
        .group_by(func.date(Consultation.created_at))
        .order_by(func.date(Consultation.created_at))
    )

    # Daily revenue
    revenue_by_day = await db.execute(
        select(
            func.date(BillPayment.created_at).label("day"),
            func.sum(BillPayment.amount).label("revenue"),
        )
        .where(
            BillPayment.tenant_id == tenant_id,
            func.date(BillPayment.created_at) >= start_date,
        )
        .group_by(func.date(BillPayment.created_at))
        .order_by(func.date(BillPayment.created_at))
    )

    return {
        "consultations_trend": [
            {"date": str(row.day), "count": row.count}
            for row in consultations_by_day.all()
        ],
        "revenue_trend": [
            {"date": str(row.day), "revenue": float(row.revenue)}
            for row in revenue_by_day.all()
        ],
    }
