import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel


class ChargeItemCreate(BaseModel):
    name: str
    category: str
    unit: str = "次"
    price: Decimal
    description: Optional[str] = None


class ChargeItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    price: Optional[Decimal] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ChargeItemResponse(BaseModel):
    id: uuid.UUID
    name: str
    category: str
    unit: str
    price: Decimal
    description: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class BillItemCreate(BaseModel):
    charge_item_id: Optional[uuid.UUID] = None
    name: str
    category: Optional[str] = None
    unit: str = "次"
    quantity: int = 1
    unit_price: Decimal


class BillCreate(BaseModel):
    patient_id: uuid.UUID
    consultation_id: Optional[uuid.UUID] = None
    items: List[BillItemCreate]
    discount_amount: Decimal = Decimal("0.00")
    notes: Optional[str] = None


class BillItemResponse(BaseModel):
    id: uuid.UUID
    name: str
    category: Optional[str] = None
    unit: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    class Config:
        from_attributes = True


class BillResponse(BaseModel):
    id: uuid.UUID
    bill_no: str
    patient_id: uuid.UUID
    consultation_id: Optional[uuid.UUID] = None
    total_amount: Decimal
    discount_amount: Decimal
    paid_amount: Decimal
    status: str
    notes: Optional[str] = None
    items: Optional[List[BillItemResponse]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    bill_id: uuid.UUID
    amount: Decimal
    payment_method: str  # cash, wechat, alipay, card, insurance
    reference_no: Optional[str] = None
    notes: Optional[str] = None


class PaymentResponse(BaseModel):
    id: uuid.UUID
    bill_id: uuid.UUID
    amount: Decimal
    payment_method: str
    reference_no: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RevenueStatsResponse(BaseModel):
    date: date
    total_revenue: Decimal
    cash_amount: Decimal
    wechat_amount: Decimal
    alipay_amount: Decimal
    card_amount: Decimal
    insurance_amount: Decimal
    bill_count: int
    patient_count: int
