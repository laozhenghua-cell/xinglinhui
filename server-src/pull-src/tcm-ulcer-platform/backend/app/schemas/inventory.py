"""库存管理相关 Schema"""
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Optional


# ========== 药品基础信息 ==========
class MedicineBase(BaseModel):
    name: str = Field(..., description="药品名称")
    alias: Optional[str] = None
    category: str = Field(..., description="类别：herb/patent/material")
    unit: str = Field(default="克", description="单位")
    min_stock: Decimal = Field(default=0, description="最低库存预警值")
    purchase_price: Optional[Decimal] = None
    sale_price: Optional[Decimal] = None
    properties: Optional[str] = None
    meridians: Optional[str] = None
    functions: Optional[str] = None
    indications: Optional[str] = None
    contraindications: Optional[str] = None
    notes: Optional[str] = None


class MedicineCreate(MedicineBase):
    pass


class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    alias: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    min_stock: Optional[Decimal] = None
    purchase_price: Optional[Decimal] = None
    sale_price: Optional[Decimal] = None
    properties: Optional[str] = None
    meridians: Optional[str] = None
    functions: Optional[str] = None
    indications: Optional[str] = None
    contraindications: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class MedicineResponse(MedicineBase):
    id: str
    tenant_id: str
    total_stock: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 药品批次 ==========
class MedicineBatchBase(BaseModel):
    batch_no: str = Field(..., description="批次号")
    supplier: Optional[str] = None
    purchase_date: date = Field(..., description="进货日期")
    expiry_date: Optional[date] = None
    initial_stock: Decimal = Field(..., description="初始库存")
    purchase_price: Decimal = Field(..., description="进货单价")
    notes: Optional[str] = None


class MedicineBatchCreate(MedicineBatchBase):
    medicine_id: str = Field(..., description="药品ID")


class MedicineBatchUpdate(BaseModel):
    supplier: Optional[str] = None
    expiry_date: Optional[date] = None
    notes: Optional[str] = None


class MedicineBatchResponse(MedicineBatchBase):
    id: str
    medicine_id: str
    current_stock: Decimal
    total_cost: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 库存事务 ==========
class StockTransactionBase(BaseModel):
    transaction_type: str = Field(..., description="类型：in/out/adjust/loss")
    quantity: Decimal = Field(..., description="数量")
    unit: str = Field(..., description="单位")
    notes: Optional[str] = None


class StockTransactionCreate(StockTransactionBase):
    medicine_id: str = Field(..., description="药品ID")
    batch_id: Optional[str] = None
    related_bill_id: Optional[str] = None
    related_prescription_id: Optional[str] = None


class StockTransactionResponse(StockTransactionBase):
    id: str
    medicine_id: str
    batch_id: Optional[str]
    transaction_date: datetime
    related_bill_id: Optional[str]
    related_prescription_id: Optional[str]
    operator_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 库存预警 ==========
class StockAlertResponse(BaseModel):
    id: str
    medicine_id: str
    medicine_name: str
    alert_type: str
    alert_date: datetime
    current_stock: Optional[Decimal]
    min_stock: Optional[Decimal]
    expiry_date: Optional[date]
    status: str
    acknowledged_by: Optional[str]
    acknowledged_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StockAlertAcknowledge(BaseModel):
    notes: Optional[str] = None


# ========== 入库单 ==========
class StockInRequest(BaseModel):
    """入库请求"""
    medicine_id: str
    batch_no: str
    supplier: Optional[str]
    purchase_date: date
    expiry_date: Optional[date]
    quantity: Decimal
    purchase_price: Decimal
    notes: Optional[str]


# ========== 出库单 ==========
class StockOutRequest(BaseModel):
    """出库请求（开方时自动扣减）"""
    medicine_id: str
    batch_id: Optional[str]
    quantity: Decimal
    related_prescription_id: Optional[str]
    related_bill_id: Optional[str]
    notes: Optional[str]


# ========== 库存统计 ==========
class StockStats(BaseModel):
    """库存统计"""
    total_medicines: int
    low_stock_count: int
    expired_count: int
    expiring_soon_count: int
    total_value: Decimal
