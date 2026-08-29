"""收费管理 API"""
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...core.security import get_current_user
from ...core.database import get_db
from ...models import User, Bill, BillItem, BillPayment, ChargeItem, DailyRevenue, Patient, UlcerConsultation
from ...schemas.billing import (
    ChargeItemCreate, ChargeItemUpdate, ChargeItemResponse,
    BillCreate, BillUpdate, BillResponse,
    BillPaymentCreate, BillPaymentResponse,
    DailyRevenueResponse, RevenueStats
)

router = APIRouter(tags=["收费管理"])


# ========== 收费项目管理 ==========
@router.post("/charge-items", response_model=ChargeItemResponse)
async def create_charge_item(
    item: ChargeItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建收费项目"""
    charge_item = ChargeItem(
        tenant_id=current_user.tenant_id,
        **item.model_dump()
    )
    db.add(charge_item)
    await db.commit()
    await db.refresh(charge_item)
    return charge_item


@router.get("/charge-items", response_model=list[ChargeItemResponse])
async def list_charge_items(
    category: str | None = None,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取收费项目列表"""
    query = select(ChargeItem).where(ChargeItem.tenant_id == current_user.tenant_id)

    if category:
        query = query.where(ChargeItem.category == category)
    if is_active is not None:
        query = query.where(ChargeItem.is_active == is_active)

    query = query.order_by(ChargeItem.category, ChargeItem.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/charge-items/{item_id}", response_model=ChargeItemResponse)
async def get_charge_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取收费项目详情"""
    result = await db.execute(
        select(ChargeItem).where(
            ChargeItem.id == item_id,
            ChargeItem.tenant_id == current_user.tenant_id
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="收费项目不存在")
    return item


@router.put("/charge-items/{item_id}", response_model=ChargeItemResponse)
async def update_charge_item(
    item_id: str,
    item_update: ChargeItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新收费项目"""
    result = await db.execute(
        select(ChargeItem).where(
            ChargeItem.id == item_id,
            ChargeItem.tenant_id == current_user.tenant_id
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="收费项目不存在")

    for key, value in item_update.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/charge-items/{item_id}")
async def delete_charge_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除收费项目（软删除）"""
    result = await db.execute(
        select(ChargeItem).where(
            ChargeItem.id == item_id,
            ChargeItem.tenant_id == current_user.tenant_id
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="收费项目不存在")

    item.is_active = False
    await db.commit()
    return {"message": "收费项目已停用"}


# ========== 账单管理 ==========
def generate_bill_no(tenant_id: str) -> str:
    """生成账单号：BILL-租户ID前8位-时间戳"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"BILL-{tenant_id[:8]}-{timestamp}"


@router.post("/bills", response_model=BillResponse)
async def create_bill(
    bill_create: BillCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建账单"""
    # 检查患者是否存在
    result = await db.execute(
        select(Patient).where(
            Patient.id == bill_create.patient_id,
            Patient.tenant_id == current_user.tenant_id
        )
    )
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")

    # 计算总金额
    total_amount = sum(
        item.unit_price * item.quantity
        for item in bill_create.items
    )

    # 创建账单
    bill = Bill(
        tenant_id=current_user.tenant_id,
        bill_no=generate_bill_no(current_user.tenant_id),
        patient_id=bill_create.patient_id,
        consultation_id=bill_create.consultation_id,
        bill_date=datetime.now(),
        total_amount=total_amount,
        discount_amount=bill_create.discount_amount,
        paid_amount=Decimal(0),
        status="unpaid",
        notes=bill_create.notes,
        doctor_id=current_user.id,
        cashier_id=current_user.id
    )
    db.add(bill)
    await db.flush()

    # 创建账单明细
    for item_data in bill_create.items:
        subtotal = item_data.unit_price * item_data.quantity
        bill_item = BillItem(
            bill_id=bill.id,
            charge_item_id=item_data.charge_item_id,
            item_name=item_data.item_name,
            category=item_data.category,
            unit_price=item_data.unit_price,
            quantity=item_data.quantity,
            unit=item_data.unit,
            subtotal=subtotal,
            notes=item_data.notes
        )
        db.add(bill_item)

    await db.commit()
    await db.refresh(bill)

    # 加载关联数据
    result = await db.execute(
        select(Bill).where(Bill.id == bill.id).options(
            selectinload(Bill.items),
            selectinload(Bill.payments)
        )
    )
    return result.scalar_one()


@router.get("/bills", response_model=list[BillResponse])
async def list_bills(
    patient_id: str | None = None,
    status: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取账单列表"""
    query = select(Bill).where(Bill.tenant_id == current_user.tenant_id)

    if patient_id:
        query = query.where(Bill.patient_id == patient_id)
    if status:
        query = query.where(Bill.status == status)
    if start_date:
        query = query.where(Bill.bill_date >= start_date)
    if end_date:
        query = query.where(Bill.bill_date <= end_date)

    query = query.options(
        selectinload(Bill.items),
        selectinload(Bill.payments)
    ).order_by(Bill.bill_date.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/bills/{bill_id}", response_model=BillResponse)
async def get_bill(
    bill_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取账单详情"""
    result = await db.execute(
        select(Bill).where(
            Bill.id == bill_id,
            Bill.tenant_id == current_user.tenant_id
        ).options(
            selectinload(Bill.items),
            selectinload(Bill.payments)
        )
    )
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    return bill


@router.put("/bills/{bill_id}", response_model=BillResponse)
async def update_bill(
    bill_id: str,
    bill_update: BillUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新账单"""
    result = await db.execute(
        select(Bill).where(
            Bill.id == bill_id,
            Bill.tenant_id == current_user.tenant_id
        )
    )
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")

    for key, value in bill_update.model_dump(exclude_unset=True).items():
        setattr(bill, key, value)

    await db.commit()
    await db.refresh(bill)

    result = await db.execute(
        select(Bill).where(Bill.id == bill.id).options(
            selectinload(Bill.items),
            selectinload(Bill.payments)
        )
    )
    return result.scalar_one()


# ========== 支付管理 ==========
@router.post("/bills/{bill_id}/payments", response_model=BillPaymentResponse)
async def add_payment(
    bill_id: str,
    payment: BillPaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加支付记录"""
    # 获取账单
    result = await db.execute(
        select(Bill).where(
            Bill.id == bill_id,
            Bill.tenant_id == current_user.tenant_id
        )
    )
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")

    # 创建支付记录
    bill_payment = BillPayment(
        bill_id=bill_id,
        payment_date=datetime.now(),
        amount=payment.amount,
        payment_method=payment.payment_method,
        transaction_no=payment.transaction_no,
        notes=payment.notes,
        cashier_id=current_user.id
    )
    db.add(bill_payment)

    # 更新账单已付金额和状态
    bill.paid_amount += payment.amount
    remaining = (bill.total_amount - bill.discount_amount) - bill.paid_amount

    if remaining <= 0:
        bill.status = "paid"
    elif bill.paid_amount > 0:
        bill.status = "partial"

    await db.commit()
    await db.refresh(bill_payment)

    # 更新每日收入统计
    await update_daily_revenue(db, current_user.tenant_id, bill_payment)

    return bill_payment


async def update_daily_revenue(
    db: AsyncSession,
    tenant_id: str,
    payment: BillPayment
):
    """更新每日收入统计"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    result = await db.execute(
        select(DailyRevenue).where(
            DailyRevenue.tenant_id == tenant_id,
            DailyRevenue.revenue_date == today
        )
    )
    daily = result.scalar_one_or_none()

    if not daily:
        daily = DailyRevenue(
            tenant_id=tenant_id,
            revenue_date=today
        )
        db.add(daily)
        await db.flush()

    # 更新收入
    daily.total_revenue += payment.amount
    if payment.payment_method == "cash":
        daily.cash_revenue += payment.amount
    elif payment.payment_method == "wechat":
        daily.wechat_revenue += payment.amount
    elif payment.payment_method == "alipay":
        daily.alipay_revenue += payment.amount
    elif payment.payment_method == "card":
        daily.card_revenue += payment.amount
    elif payment.payment_method == "insurance":
        daily.insurance_revenue += payment.amount

    daily.bill_count += 1

    await db.commit()


# ========== 统计报表 ==========
@router.get("/revenue/daily", response_model=list[DailyRevenueResponse])
async def get_daily_revenue(
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取每日收入统计"""
    query = select(DailyRevenue).where(DailyRevenue.tenant_id == current_user.tenant_id)

    if start_date:
        query = query.where(DailyRevenue.revenue_date >= start_date)
    if end_date:
        query = query.where(DailyRevenue.revenue_date <= end_date)

    query = query.order_by(DailyRevenue.revenue_date.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/revenue/stats", response_model=RevenueStats)
async def get_revenue_stats(
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取收入统计汇总"""
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()

    result = await db.execute(
        select(
            func.sum(DailyRevenue.total_revenue).label("total_revenue"),
            func.sum(DailyRevenue.cash_revenue).label("cash_revenue"),
            func.sum(DailyRevenue.wechat_revenue).label("wechat_revenue"),
            func.sum(DailyRevenue.alipay_revenue).label("alipay_revenue"),
            func.sum(DailyRevenue.card_revenue).label("card_revenue"),
            func.sum(DailyRevenue.insurance_revenue).label("insurance_revenue"),
            func.sum(DailyRevenue.patient_count).label("patient_count"),
            func.sum(DailyRevenue.bill_count).label("bill_count"),
        ).where(
            DailyRevenue.tenant_id == current_user.tenant_id,
            DailyRevenue.revenue_date >= start_date,
            DailyRevenue.revenue_date <= end_date
        )
    )
    row = result.one()

    total = row.total_revenue or Decimal(0)
    bill_count = row.bill_count or 0
    avg_amount = total / bill_count if bill_count > 0 else Decimal(0)

    return RevenueStats(
        date_range=f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
        total_revenue=row.total_revenue or Decimal(0),
        cash_revenue=row.cash_revenue or Decimal(0),
        wechat_revenue=row.wechat_revenue or Decimal(0),
        alipay_revenue=row.alipay_revenue or Decimal(0),
        card_revenue=row.card_revenue or Decimal(0),
        insurance_revenue=row.insurance_revenue or Decimal(0),
        patient_count=row.patient_count or 0,
        bill_count=bill_count,
        avg_bill_amount=avg_amount
    )
