import uuid
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.inventory import Medicine, MedicineBatch, StockTransaction, StockAlert
from app.models.user import User
from app.schemas.inventory import (
    MedicineCreate,
    MedicineUpdate,
    MedicineResponse,
    StockInRequest,
    StockOutRequest,
    StockTransactionResponse,
    StockAlertResponse,
    InventoryStatsResponse,
)

router = APIRouter(prefix="/inventory", tags=["库存管理"])


# Medicines CRUD
@router.get("/medicines")
async def list_medicines(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    category: Optional[str] = None,
    low_stock: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Medicine).where(
        Medicine.tenant_id == current_user.tenant_id,
        Medicine.is_active == True,
    )

    if search:
        query = query.where(
            or_(
                Medicine.name.ilike(f"%{search}%"),
                Medicine.pinyin.ilike(f"%{search}%"),
            )
        )
    if category:
        query = query.where(Medicine.category == category)
    if low_stock:
        query = query.where(Medicine.stock_quantity <= Medicine.min_stock)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(Medicine.name)
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    medicines = result.scalars().all()

    return {"total": total, "items": medicines}


@router.get("/medicines/{medicine_id}", response_model=MedicineResponse)
async def get_medicine(
    medicine_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Medicine).where(
            Medicine.id == medicine_id,
            Medicine.tenant_id == current_user.tenant_id,
        )
    )
    medicine = result.scalar_one_or_none()
    if not medicine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="药品不存在")
    return medicine


@router.post("/medicines", response_model=MedicineResponse, status_code=status.HTTP_201_CREATED)
async def create_medicine(
    data: MedicineCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    medicine = Medicine(tenant_id=current_user.tenant_id, **data.model_dump(exclude_none=True))
    db.add(medicine)
    await db.flush()
    await db.refresh(medicine)
    return medicine


@router.put("/medicines/{medicine_id}", response_model=MedicineResponse)
async def update_medicine(
    medicine_id: uuid.UUID,
    data: MedicineUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Medicine).where(
            Medicine.id == medicine_id,
            Medicine.tenant_id == current_user.tenant_id,
        )
    )
    medicine = result.scalar_one_or_none()
    if not medicine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="药品不存在")

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(medicine, key, value)

    db.add(medicine)
    await db.flush()
    await db.refresh(medicine)
    return medicine


# Stock Operations
@router.post("/stock-in", response_model=StockTransactionResponse)
async def stock_in(
    data: StockInRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Medicine).where(
            Medicine.id == data.medicine_id,
            Medicine.tenant_id == current_user.tenant_id,
        )
    )
    medicine = result.scalar_one_or_none()
    if not medicine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="药品不存在")

    batch = MedicineBatch(
        tenant_id=current_user.tenant_id,
        medicine_id=data.medicine_id,
        batch_no=data.batch_no,
        quantity=data.quantity,
        remaining_quantity=data.quantity,
        purchase_price=data.purchase_price,
        production_date=data.production_date,
        expiry_date=data.expiry_date,
        supplier=data.supplier,
    )
    db.add(batch)
    await db.flush()

    transaction = StockTransaction(
        tenant_id=current_user.tenant_id,
        medicine_id=data.medicine_id,
        batch_id=batch.id,
        transaction_type="in",
        quantity=data.quantity,
        reason=f"入库批次: {data.batch_no}",
        operator_id=current_user.id,
    )
    db.add(transaction)

    medicine.stock_quantity += data.quantity
    if data.purchase_price:
        medicine.purchase_price = data.purchase_price
    db.add(medicine)

    # Resolve low stock alerts
    if medicine.stock_quantity > medicine.min_stock:
        alerts_result = await db.execute(
            select(StockAlert).where(
                StockAlert.medicine_id == medicine.id,
                StockAlert.alert_type == "low_stock",
                StockAlert.is_resolved == False,
            )
        )
        for alert in alerts_result.scalars().all():
            alert.is_resolved = True
            alert.resolved_at = datetime.now(timezone.utc)
            db.add(alert)

    await db.flush()
    await db.refresh(transaction)
    return transaction


@router.post("/stock-out", response_model=StockTransactionResponse)
async def stock_out(
    data: StockOutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Medicine).where(
            Medicine.id == data.medicine_id,
            Medicine.tenant_id == current_user.tenant_id,
        )
    )
    medicine = result.scalar_one_or_none()
    if not medicine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="药品不存在")

    if medicine.stock_quantity < data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"库存不足，当前库存: {medicine.stock_quantity}",
        )

    transaction = StockTransaction(
        tenant_id=current_user.tenant_id,
        medicine_id=data.medicine_id,
        transaction_type="out",
        quantity=data.quantity,
        reason=data.reason or "处方出库",
        reference_id=data.reference_id,
        operator_id=current_user.id,
    )
    db.add(transaction)

    medicine.stock_quantity -= data.quantity
    db.add(medicine)

    # Generate low stock alert
    if medicine.stock_quantity <= medicine.min_stock:
        existing_alert = await db.execute(
            select(StockAlert).where(
                StockAlert.medicine_id == medicine.id,
                StockAlert.alert_type == "low_stock",
                StockAlert.is_resolved == False,
            )
        )
        if not existing_alert.scalar_one_or_none():
            alert = StockAlert(
                tenant_id=current_user.tenant_id,
                medicine_id=medicine.id,
                alert_type="low_stock",
                message=f"{medicine.name} 库存不足，当前: {medicine.stock_quantity}，最低: {medicine.min_stock}",
            )
            db.add(alert)

    await db.flush()
    await db.refresh(transaction)
    return transaction


# Batches
@router.get("/batches/{medicine_id}")
async def list_batches(
    medicine_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MedicineBatch).where(
            MedicineBatch.medicine_id == medicine_id,
            MedicineBatch.tenant_id == current_user.tenant_id,
            MedicineBatch.remaining_quantity > 0,
        ).order_by(MedicineBatch.expiry_date)
    )
    return result.scalars().all()


# Alerts
@router.get("/alerts", response_model=list[StockAlertResponse])
async def list_alerts(
    resolved: Optional[bool] = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(StockAlert).where(StockAlert.tenant_id == current_user.tenant_id)
    if resolved is not None:
        query = query.where(StockAlert.is_resolved == resolved)
    query = query.order_by(StockAlert.created_at.desc()).limit(100)
    result = await db.execute(query)
    return result.scalars().all()


@router.put("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StockAlert).where(
            StockAlert.id == alert_id,
            StockAlert.tenant_id == current_user.tenant_id,
        )
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="告警不存在")

    alert.is_resolved = True
    alert.resolved_at = datetime.now(timezone.utc)
    db.add(alert)
    await db.flush()
    return {"message": "告警已处理"}


# Stats
@router.get("/stats", response_model=InventoryStatsResponse)
async def get_inventory_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = current_user.tenant_id

    total_result = await db.execute(
        select(func.count()).where(
            Medicine.tenant_id == tenant_id, Medicine.is_active == True
        )
    )
    total_medicines = total_result.scalar()

    low_stock_result = await db.execute(
        select(func.count()).where(
            Medicine.tenant_id == tenant_id,
            Medicine.is_active == True,
            Medicine.stock_quantity <= Medicine.min_stock,
        )
    )
    low_stock_count = low_stock_result.scalar()

    expiring_threshold = date.today() + timedelta(days=90)
    expiring_result = await db.execute(
        select(func.count()).where(
            MedicineBatch.tenant_id == tenant_id,
            MedicineBatch.remaining_quantity > 0,
            MedicineBatch.expiry_date <= expiring_threshold,
            MedicineBatch.expiry_date > date.today(),
        )
    )
    expiring_soon_count = expiring_result.scalar()

    expired_result = await db.execute(
        select(func.count()).where(
            MedicineBatch.tenant_id == tenant_id,
            MedicineBatch.remaining_quantity > 0,
            MedicineBatch.expiry_date <= date.today(),
        )
    )
    expired_count = expired_result.scalar()

    value_result = await db.execute(
        select(
            func.coalesce(
                func.sum(Medicine.stock_quantity * Medicine.purchase_price), 0
            )
        ).where(Medicine.tenant_id == tenant_id, Medicine.is_active == True)
    )
    total_stock_value = value_result.scalar() or Decimal("0.00")

    return InventoryStatsResponse(
        total_medicines=total_medicines,
        low_stock_count=low_stock_count,
        expiring_soon_count=expiring_soon_count,
        expired_count=expired_count,
        total_stock_value=total_stock_value,
    )
