"""收费管理相关 Schema"""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Optional


# ========== 收费项目 ==========
class ChargeItemBase(BaseModel):
    name: str = Field(..., description="项目名称")
    category: str = Field(..., description="类别：consultation/material/medicine/surgery/exam")
    unit_price: Decimal = Field(..., description="单价（元）")
    unit: str = Field(default="次", description="单位")
    description: Optional[str] = None
    code: Optional[str] = None


class ChargeItemCreate(ChargeItemBase):
    pass


class ChargeItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    unit_price: Optional[Decimal] = None
    unit: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    is_active: Optional[bool] = None


class ChargeItemResponse(ChargeItemBase):
    id: str
    tenant_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 账单明细 ==========
class BillItemBase(BaseModel):
    item_name: str = Field(..., description="项目名称")
    category: str = Field(..., description="类别")
    unit_price: Decimal = Field(..., description="单价")
    quantity: Decimal = Field(default=1, description="数量")
    unit: str = Field(default="次", description="单位")
    notes: Optional[str] = None


class BillItemCreate(BillItemBase):
    charge_item_id: Optional[str] = None


class BillItemResponse(BillItemBase):
    id: str
    bill_id: str
    charge_item_id: Optional[str]
    subtotal: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 支付记录 ==========
class BillPaymentBase(BaseModel):
    amount: Decimal = Field(..., description="支付金额")
    payment_method: str = Field(..., description="支付方式：cash/wechat/alipay/card/insurance")
    transaction_no: Optional[str] = None
    notes: Optional[str] = None


class BillPaymentCreate(BillPaymentBase):
    pass


class BillPaymentResponse(BillPaymentBase):
    id: str
    bill_id: str
    payment_date: datetime
    cashier_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 账单 ==========
class BillBase(BaseModel):
    patient_id: str = Field(..., description="患者ID")
    consultation_id: Optional[str] = None
    notes: Optional[str] = None


class BillCreate(BillBase):
    items: list[BillItemCreate] = Field(..., description="账单明细")
    discount_amount: Decimal = Field(default=0, description="优惠金额")


class BillUpdate(BaseModel):
    notes: Optional[str] = None
    status: Optional[str] = None


class BillResponse(BillBase):
    id: str
    tenant_id: str
    bill_no: str
    bill_date: datetime
    total_amount: Decimal
    discount_amount: Decimal
    paid_amount: Decimal
    status: str
    cashier_id: Optional[str]
    doctor_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: list[BillItemResponse] = []
    payments: list[BillPaymentResponse] = []

    class Config:
        from_attributes = True


# ========== 每日收入 ==========
class DailyRevenueResponse(BaseModel):
    id: str
    tenant_id: str
    revenue_date: datetime
    total_revenue: Decimal
    cash_revenue: Decimal
    wechat_revenue: Decimal
    alipay_revenue: Decimal
    card_revenue: Decimal
    insurance_revenue: Decimal
    patient_count: int
    bill_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 收入统计 ==========
class RevenueStats(BaseModel):
    """收入统计"""
    date_range: str
    total_revenue: Decimal
    cash_revenue: Decimal
    wechat_revenue: Decimal
    alipay_revenue: Decimal
    card_revenue: Decimal
    insurance_revenue: Decimal
    patient_count: int
    bill_count: int
    avg_bill_amount: Decimal
