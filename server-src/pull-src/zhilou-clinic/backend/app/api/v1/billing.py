import uuid
from datetime import datetime, date, timezone, timedelta
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.billing import ChargeItem, Bill, BillItem, BillPayment, DailyRevenue
from app.models.user import User
from app.schemas.billing import (
    ChargeItemCreate,
    ChargeItemUpdate,
    ChargeItemResponse,
    BillCreate,
    BillResponse,
    PaymentCreate,
    PaymentResponse,
)

router = APIRouter(prefix="/billing", tags=["收费管理"])


def generate_bill_no() -> str:
    now = datetime.now(timezone.utc)
    return f"B{now.strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"


# Charge Items CRUD
@router.get("/charge-items", response_model=list[ChargeItemResponse])
async def list_charge_items(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(ChargeItem).where(
        ChargeItem.tenant_id == current_user.tenant_id,
        ChargeItem.is_active == True,
    )
    if category:
        query = query.where(ChargeItem.category == category)
    query = query.order_by(ChargeItem.category, ChargeItem.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/charge-items", response_model=ChargeItemResponse, status_code=status.HTTP_201_CREATED)
async def create_charge_item(
    data: ChargeItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = ChargeItem(tenant_id=current_user.tenant_id, **data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


@router.put("/charge-items/{item_id}", response_model=ChargeItemResponse)
async def update_charge_item(
    item_id: uuid.UUID,
    data: ChargeItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChargeItem).where(
            ChargeItem.id == item_id,
            ChargeItem.tenant_id == current_user.tenant_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="收费项目不存在")

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(item, key, value)

    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


# Bills CRUD
@router.get("/bills")
async def list_bills(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    patient_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Bill).where(Bill.tenant_id == current_user.tenant_id)

    if patient_id:
        query = query.where(Bill.patient_id == patient_id)
    if status_filter:
        query = query.where(Bill.status == status_filter)
    if date_from:
        query = query.where(Bill.created_at >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.where(
            Bill.created_at <= datetime.combine(date_to, datetime.max.time())
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(Bill.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    bills = result.scalars().all()

    return {"total": total, "items": bills}


@router.get("/bills/{bill_id}")
async def get_bill(
    bill_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Bill).where(Bill.id == bill_id, Bill.tenant_id == current_user.tenant_id)
    )
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="账单不存在")

    items_result = await db.execute(select(BillItem).where(BillItem.bill_id == bill_id))
    items = items_result.scalars().all()

    payments_result = await db.execute(
        select(BillPayment).where(BillPayment.bill_id == bill_id)
    )
    payments = payments_result.scalars().all()

    return {"bill": bill, "items": items, "payments": payments}


@router.post("/bills", status_code=status.HTTP_201_CREATED)
async def create_bill(
    data: BillCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    total_amount = sum(
        item.unit_price * item.quantity for item in data.items
    )

    bill = Bill(
        tenant_id=current_user.tenant_id,
        patient_id=data.patient_id,
        consultation_id=data.consultation_id,
        bill_no=generate_bill_no(),
        total_amount=total_amount,
        discount_amount=data.discount_amount,
        created_by=current_user.id,
        notes=data.notes,
    )
    db.add(bill)
    await db.flush()

    for item_data in data.items:
        bill_item = BillItem(
            bill_id=bill.id,
            charge_item_id=item_data.charge_item_id,
            name=item_data.name,
            category=item_data.category,
            unit=item_data.unit,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            subtotal=item_data.unit_price * item_data.quantity,
        )
        db.add(bill_item)

    await db.flush()
    await db.refresh(bill)
    return bill


@router.post("/payments", response_model=PaymentResponse)
async def create_payment(
    data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Bill).where(Bill.id == data.bill_id, Bill.tenant_id == current_user.tenant_id)
    )
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="账单不存在")

    if bill.status in ("paid", "cancelled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"账单状态为{bill.status}，无法收款",
        )

    payment = BillPayment(
        tenant_id=current_user.tenant_id,
        bill_id=data.bill_id,
        amount=data.amount,
        payment_method=data.payment_method,
        reference_no=data.reference_no,
        notes=data.notes,
        created_by=current_user.id,
    )
    db.add(payment)

    bill.paid_amount = bill.paid_amount + data.amount
    actual_due = bill.total_amount - bill.discount_amount
    if bill.paid_amount >= actual_due:
        bill.status = "paid"
    else:
        bill.status = "partial"

    db.add(bill)

    # 更新日收入统计
    today = datetime.now(timezone.utc).date()
    daily_res = await db.execute(
        select(DailyRevenue).where(
            DailyRevenue.tenant_id == current_user.tenant_id,
            DailyRevenue.date == today,
        )
    )
    daily = daily_res.scalar_one_or_none()
    if not daily:
        daily = DailyRevenue(
            tenant_id=current_user.tenant_id,
            date=today,
            total_revenue=Decimal("0.00"),
            cash_amount=Decimal("0.00"),
            wechat_amount=Decimal("0.00"),
            alipay_amount=Decimal("0.00"),
            card_amount=Decimal("0.00"),
            insurance_amount=Decimal("0.00"),
            bill_count=0,
            patient_count=0,
        )
        db.add(daily)
        await db.flush()

    daily.total_revenue = (daily.total_revenue or Decimal("0.00")) + data.amount
    method_field = {
        "cash": "cash_amount",
        "wechat": "wechat_amount",
        "alipay": "alipay_amount",
        "card": "card_amount",
        "insurance": "insurance_amount",
    }.get(data.payment_method)
    if method_field:
        setattr(daily, method_field, (getattr(daily, method_field) or Decimal("0.00")) + data.amount)
    daily.bill_count = (daily.bill_count or 0) + 1
    db.add(daily)

    await db.flush()
    await db.refresh(payment)
    return payment


# Revenue Stats
@router.get("/revenue")
async def get_revenue_stats(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not date_from:
        date_from = date.today() - timedelta(days=30)
    if not date_to:
        date_to = date.today()

    query = select(DailyRevenue).where(
        DailyRevenue.tenant_id == current_user.tenant_id,
        DailyRevenue.date >= date_from,
        DailyRevenue.date <= date_to,
    ).order_by(DailyRevenue.date)

    result = await db.execute(query)
    records = result.scalars().all()

    total_revenue = sum(r.total_revenue for r in records)
    total_bills = sum(r.bill_count for r in records)
    total_patients = sum(r.patient_count for r in records)

    return {
        "summary": {
            "total_revenue": float(total_revenue),
            "total_bills": total_bills,
            "total_patients": total_patients,
            "period_days": (date_to - date_from).days + 1,
        },
        "daily": [
            {
                "date": str(r.date),
                "total_revenue": float(r.total_revenue),
                "cash": float(r.cash_amount),
                "wechat": float(r.wechat_amount),
                "alipay": float(r.alipay_amount),
                "card": float(r.card_amount),
                "insurance": float(r.insurance_amount),
                "bill_count": r.bill_count,
                "patient_count": r.patient_count,
            }
            for r in records
        ],
    }
