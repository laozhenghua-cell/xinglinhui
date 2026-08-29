"""库存管理 API"""
from datetime import datetime, timedelta, date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...core.security import get_current_user
from ...core.database import get_db
from ...models import User, Medicine, MedicineBatch, StockTransaction, StockAlert
from ...schemas.inventory import (
    MedicineCreate, MedicineUpdate, MedicineResponse,
    MedicineBatchCreate, MedicineBatchUpdate, MedicineBatchResponse,
    StockTransactionCreate, StockTransactionResponse,
    StockAlertResponse, StockAlertAcknowledge,
    StockInRequest, StockOutRequest, StockStats
)

router = APIRouter(tags=["库存管理"])


# ========== 药品管理 ==========
@router.post("/medicines", response_model=MedicineResponse)
async def create_medicine(
    medicine: MedicineCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建药品"""
    # 检查名称是否重复
    result = await db.execute(
        select(Medicine).where(
            Medicine.tenant_id == current_user.tenant_id,
            Medicine.name == medicine.name
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="药品名称已存在")

    med = Medicine(
        tenant_id=current_user.tenant_id,
        **medicine.model_dump()
    )
    db.add(med)
    await db.commit()
    await db.refresh(med)
    return med


@router.get("/medicines", response_model=list[MedicineResponse])
async def list_medicines(
    category: str | None = None,
    is_active: bool = True,
    keyword: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取药品列表"""
    query = select(Medicine).where(Medicine.tenant_id == current_user.tenant_id)

    if category:
        query = query.where(Medicine.category == category)
    if is_active is not None:
        query = query.where(Medicine.is_active == is_active)
    if keyword:
        query = query.where(
            or_(
                Medicine.name.contains(keyword),
                Medicine.alias.contains(keyword)
            )
        )

    query = query.order_by(Medicine.category, Medicine.name).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/medicines/low-stock", response_model=list[MedicineResponse])
async def list_low_stock_medicines(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取低库存药品"""
    result = await db.execute(
        select(Medicine).where(
            Medicine.tenant_id == current_user.tenant_id,
            Medicine.is_active == True,
            Medicine.total_stock <= Medicine.min_stock
        ).order_by(Medicine.total_stock)
    )
    return result.scalars().all()


@router.get("/medicines/{medicine_id}", response_model=MedicineResponse)
async def get_medicine(
    medicine_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取药品详情"""
    result = await db.execute(
        select(Medicine).where(
            Medicine.id == medicine_id,
            Medicine.tenant_id == current_user.tenant_id
        )
    )
    med = result.scalar_one_or_none()
    if not med:
        raise HTTPException(status_code=404, detail="药品不存在")
    return med


@router.put("/medicines/{medicine_id}", response_model=MedicineResponse)
async def update_medicine(
    medicine_id: str,
    medicine_update: MedicineUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新药品信息"""
    result = await db.execute(
        select(Medicine).where(
            Medicine.id == medicine_id,
            Medicine.tenant_id == current_user.tenant_id
        )
    )
    med = result.scalar_one_or_none()
    if not med:
        raise HTTPException(status_code=404, detail="药品不存在")

    for key, value in medicine_update.model_dump(exclude_unset=True).items():
        setattr(med, key, value)

    await db.commit()
    await db.refresh(med)
    return med


@router.delete("/medicines/{medicine_id}")
async def delete_medicine(
    medicine_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除药品（软删除）"""
    result = await db.execute(
        select(Medicine).where(
            Medicine.id == medicine_id,
            Medicine.tenant_id == current_user.tenant_id
        )
    )
    med = result.scalar_one_or_none()
    if not med:
        raise HTTPException(status_code=404, detail="药品不存在")

    med.is_active = False
    await db.commit()
    return {"message": "药品已停用"}


# ========== 批次管理 ==========
@router.post("/batches", response_model=MedicineBatchResponse)
async def create_batch(
    batch: MedicineBatchCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建药品批次（入库）"""
    # 检查药品是否存在
    result = await db.execute(
        select(Medicine).where(
            Medicine.id == batch.medicine_id,
            Medicine.tenant_id == current_user.tenant_id
        )
    )
    medicine = result.scalar_one_or_none()
    if not medicine:
        raise HTTPException(status_code=404, detail="药品不存在")

    # 计算总成本
    total_cost = batch.purchase_price * batch.initial_stock

    # 创建批次
    med_batch = MedicineBatch(
        medicine_id=batch.medicine_id,
        batch_no=batch.batch_no,
        supplier=batch.supplier,
        purchase_date=batch.purchase_date,
        expiry_date=batch.expiry_date,
        initial_stock=batch.initial_stock,
        current_stock=batch.initial_stock,
        purchase_price=batch.purchase_price,
        total_cost=total_cost,
        notes=batch.notes
    )
    db.add(med_batch)

    # 更新药品总库存
    medicine.total_stock += batch.initial_stock

    # 记录入库事务
    transaction = StockTransaction(
        medicine_id=batch.medicine_id,
        batch_id=med_batch.id,
        transaction_type="in",
        quantity=batch.initial_stock,
        unit=medicine.unit,
        transaction_date=datetime.now(),
        operator_id=current_user.id,
        notes=f"批次入库：{batch.batch_no}"
    )
    db.add(transaction)

    await db.commit()
    await db.refresh(med_batch)
    return med_batch


@router.get("/medicines/{medicine_id}/batches", response_model=list[MedicineBatchResponse])
async def list_medicine_batches(
    medicine_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取药品批次列表"""
    # 先检查药品权限
    result = await db.execute(
        select(Medicine).where(
            Medicine.id == medicine_id,
            Medicine.tenant_id == current_user.tenant_id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="药品不存在")

    result = await db.execute(
        select(MedicineBatch).where(
            MedicineBatch.medicine_id == medicine_id,
            MedicineBatch.current_stock > 0
        ).order_by(MedicineBatch.expiry_date)
    )
    return result.scalars().all()


@router.get("/batches/expiring", response_model=list[MedicineBatchResponse])
async def list_expiring_batches(
    days: int = Query(30, description="多少天内过期"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取即将过期的批次"""
    expiry_threshold = date.today() + timedelta(days=days)

    result = await db.execute(
        select(MedicineBatch).join(Medicine).where(
            Medicine.tenant_id == current_user.tenant_id,
            MedicineBatch.current_stock > 0,
            MedicineBatch.expiry_date <= expiry_threshold,
            MedicineBatch.expiry_date >= date.today()
        ).order_by(MedicineBatch.expiry_date)
    )
    return result.scalars().all()


# ========== 库存事务 ==========
@router.post("/stock/in", response_model=StockTransactionResponse)
async def stock_in(
    request: StockInRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """入库"""
    # 检查药品
    result = await db.execute(
        select(Medicine).where(
            Medicine.id == request.medicine_id,
            Medicine.tenant_id == current_user.tenant_id
        )
    )
    medicine = result.scalar_one_or_none()
    if not medicine:
        raise HTTPException(status_code=404, detail="药品不存在")

    # 创建批次
    batch_create = MedicineBatchCreate(
        medicine_id=request.medicine_id,
        batch_no=request.batch_no,
        supplier=request.supplier,
        purchase_date=request.purchase_date,
        expiry_date=request.expiry_date,
        initial_stock=request.quantity,
        purchase_price=request.purchase_price,
        notes=request.notes
    )

    batch = await create_batch(batch_create, db, current_user)

    # 返回入库事务记录
    result = await db.execute(
        select(StockTransaction).where(
            StockTransaction.medicine_id == request.medicine_id,
            StockTransaction.batch_id == batch.id
        ).order_by(StockTransaction.created_at.desc()).limit(1)
    )
    return result.scalar_one()


@router.post("/stock/out", response_model=StockTransactionResponse)
async def stock_out(
    request: StockOutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """出库"""
    # 检查药品
    result = await db.execute(
        select(Medicine).where(
            Medicine.id == request.medicine_id,
            Medicine.tenant_id == current_user.tenant_id
        )
    )
    medicine = result.scalar_one_or_none()
    if not medicine:
        raise HTTPException(status_code=404, detail="药品不存在")

    # 检查库存
    if medicine.total_stock < request.quantity:
        raise HTTPException(status_code=400, detail=f"库存不足，当前库存：{medicine.total_stock}{medicine.unit}")

    # 如果指定了批次，从该批次出库
    if request.batch_id:
        result = await db.execute(
            select(MedicineBatch).where(MedicineBatch.id == request.batch_id)
        )
        batch = result.scalar_one_or_none()
        if not batch:
            raise HTTPException(status_code=404, detail="批次不存在")
        if batch.current_stock < request.quantity:
            raise HTTPException(status_code=400, detail=f"批次库存不足，当前库存：{batch.current_stock}{medicine.unit}")

        batch.current_stock -= request.quantity
    else:
        # 否则按先进先出原则出库
        result = await db.execute(
            select(MedicineBatch).where(
                MedicineBatch.medicine_id == request.medicine_id,
                MedicineBatch.current_stock > 0
            ).order_by(MedicineBatch.purchase_date)
        )
        batches = result.scalars().all()

        remaining = request.quantity
        for batch in batches:
            if remaining <= 0:
                break
            deduct = min(batch.current_stock, remaining)
            batch.current_stock -= deduct
            remaining -= deduct

    # 更新药品总库存
    medicine.total_stock -= request.quantity

    # 记录出库事务
    transaction = StockTransaction(
        medicine_id=request.medicine_id,
        batch_id=request.batch_id,
        transaction_type="out",
        quantity=-request.quantity,
        unit=medicine.unit,
        transaction_date=datetime.now(),
        related_prescription_id=request.related_prescription_id,
        related_bill_id=request.related_bill_id,
        operator_id=current_user.id,
        notes=request.notes
    )
    db.add(transaction)

    await db.commit()
    await db.refresh(transaction)

    # 检查是否需要库存预警
    await check_stock_alert(db, medicine)

    return transaction


@router.get("/transactions", response_model=list[StockTransactionResponse])
async def list_transactions(
    medicine_id: str | None = None,
    transaction_type: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取库存事务列表"""
    query = select(StockTransaction).join(Medicine).where(
        Medicine.tenant_id == current_user.tenant_id
    )

    if medicine_id:
        query = query.where(StockTransaction.medicine_id == medicine_id)
    if transaction_type:
        query = query.where(StockTransaction.transaction_type == transaction_type)
    if start_date:
        query = query.where(StockTransaction.transaction_date >= start_date)
    if end_date:
        query = query.where(StockTransaction.transaction_date <= end_date)

    query = query.order_by(StockTransaction.transaction_date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


# ========== 库存预警 ==========
async def check_stock_alert(db: AsyncSession, medicine: Medicine):
    """检查库存预警"""
    # 低库存预警
    if medicine.total_stock <= medicine.min_stock:
        # 检查是否已有未处理的预警
        result = await db.execute(
            select(StockAlert).where(
                StockAlert.medicine_id == medicine.id,
                StockAlert.alert_type == "low_stock",
                StockAlert.status == "pending"
            )
        )
        if not result.scalar_one_or_none():
            alert = StockAlert(
                medicine_id=medicine.id,
                alert_type="low_stock",
                current_stock=medicine.total_stock,
                min_stock=medicine.min_stock,
                status="pending"
            )
            db.add(alert)

    # 过期预警
    result = await db.execute(
        select(MedicineBatch).where(
            MedicineBatch.medicine_id == medicine.id,
            MedicineBatch.current_stock > 0,
            MedicineBatch.expiry_date <= date.today() + timedelta(days=30)
        )
    )
    expiring_batches = result.scalars().all()

    for batch in expiring_batches:
        alert_type = "expired" if batch.expiry_date <= date.today() else "expiring_soon"
        result = await db.execute(
            select(StockAlert).where(
                StockAlert.medicine_id == medicine.id,
                StockAlert.alert_type == alert_type,
                StockAlert.status == "pending",
                StockAlert.expiry_date == batch.expiry_date
            )
        )
        if not result.scalar_one_or_none():
            alert = StockAlert(
                medicine_id=medicine.id,
                alert_type=alert_type,
                current_stock=batch.current_stock,
                expiry_date=batch.expiry_date,
                status="pending"
            )
            db.add(alert)

    await db.commit()


@router.get("/alerts", response_model=list[StockAlertResponse])
async def list_alerts(
    alert_type: str | None = None,
    status: str = "pending",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取库存预警列表"""
    query = select(StockAlert).join(Medicine).where(
        Medicine.tenant_id == current_user.tenant_id
    )

    if alert_type:
        query = query.where(StockAlert.alert_type == alert_type)
    if status:
        query = query.where(StockAlert.status == status)

    query = query.order_by(StockAlert.alert_date.desc())
    result = await db.execute(query)
    alerts = result.scalars().all()

    # 加载药品名称
    response = []
    for alert in alerts:
        alert_dict = {
            "id": alert.id,
            "medicine_id": alert.medicine_id,
            "medicine_name": "",
            "alert_type": alert.alert_type,
            "alert_date": alert.alert_date,
            "current_stock": alert.current_stock,
            "min_stock": alert.min_stock,
            "expiry_date": alert.expiry_date,
            "status": alert.status,
            "acknowledged_by": alert.acknowledged_by,
            "acknowledged_at": alert.acknowledged_at,
            "notes": alert.notes,
            "created_at": alert.created_at,
            "updated_at": alert.updated_at
        }
        result = await db.execute(select(Medicine).where(Medicine.id == alert.medicine_id))
        med = result.scalar_one_or_none()
        if med:
            alert_dict["medicine_name"] = med.name
        response.append(StockAlertResponse(**alert_dict))

    return response


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    ack: StockAlertAcknowledge,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """确认预警"""
    result = await db.execute(
        select(StockAlert).join(Medicine).where(
            StockAlert.id == alert_id,
            Medicine.tenant_id == current_user.tenant_id
        )
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="预警不存在")

    alert.status = "acknowledged"
    alert.acknowledged_by = current_user.id
    alert.acknowledged_at = datetime.now()
    alert.notes = ack.notes

    await db.commit()
    return {"message": "预警已确认"}


# ========== 统计 ==========
@router.get("/stats", response_model=StockStats)
async def get_stock_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取库存统计"""
    # 总药品数
    result = await db.execute(
        select(func.count(Medicine.id)).where(
            Medicine.tenant_id == current_user.tenant_id,
            Medicine.is_active == True
        )
    )
    total_medicines = result.scalar() or 0

    # 低库存数
    result = await db.execute(
        select(func.count(Medicine.id)).where(
            Medicine.tenant_id == current_user.tenant_id,
            Medicine.is_active == True,
            Medicine.total_stock <= Medicine.min_stock
        )
    )
    low_stock_count = result.scalar() or 0

    # 已过期数
    result = await db.execute(
        select(func.count(func.distinct(MedicineBatch.medicine_id))).join(Medicine).where(
            Medicine.tenant_id == current_user.tenant_id,
            MedicineBatch.current_stock > 0,
            MedicineBatch.expiry_date < date.today()
        )
    )
    expired_count = result.scalar() or 0

    # 即将过期数（30天内）
    result = await db.execute(
        select(func.count(func.distinct(MedicineBatch.medicine_id))).join(Medicine).where(
            Medicine.tenant_id == current_user.tenant_id,
            MedicineBatch.current_stock > 0,
            MedicineBatch.expiry_date >= date.today(),
            MedicineBatch.expiry_date <= date.today() + timedelta(days=30)
        )
    )
    expiring_soon_count = result.scalar() or 0

    # 库存总价值
    result = await db.execute(
        select(func.sum(Medicine.total_stock * Medicine.purchase_price)).where(
            Medicine.tenant_id == current_user.tenant_id,
            Medicine.is_active == True,
            Medicine.purchase_price.isnot(None)
        )
    )
    total_value = result.scalar() or Decimal(0)

    return StockStats(
        total_medicines=total_medicines,
        low_stock_count=low_stock_count,
        expired_count=expired_count,
        expiring_soon_count=expiring_soon_count,
        total_value=total_value
    )
