import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel


class MedicineCreate(BaseModel):
    name: str
    pinyin: Optional[str] = None
    category: Optional[str] = None
    specification: Optional[str] = None
    unit: str = "g"
    purchase_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    min_stock: int = 10
    max_stock: int = 1000
    supplier: Optional[str] = None
    storage_condition: Optional[str] = None
    notes: Optional[str] = None


class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    pinyin: Optional[str] = None
    category: Optional[str] = None
    specification: Optional[str] = None
    unit: Optional[str] = None
    purchase_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    min_stock: Optional[int] = None
    max_stock: Optional[int] = None
    supplier: Optional[str] = None
    storage_condition: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class MedicineResponse(BaseModel):
    id: uuid.UUID
    name: str
    pinyin: Optional[str] = None
    category: Optional[str] = None
    specification: Optional[str] = None
    unit: str
    purchase_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    stock_quantity: int
    min_stock: int
    max_stock: int
    supplier: Optional[str] = None
    storage_condition: Optional[str] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StockInRequest(BaseModel):
    medicine_id: uuid.UUID
    batch_no: str
    quantity: int
    purchase_price: Optional[Decimal] = None
    production_date: Optional[date] = None
    expiry_date: Optional[date] = None
    supplier: Optional[str] = None


class StockOutRequest(BaseModel):
    medicine_id: uuid.UUID
    quantity: int
    reason: Optional[str] = None
    reference_id: Optional[uuid.UUID] = None


class StockTransactionResponse(BaseModel):
    id: uuid.UUID
    medicine_id: uuid.UUID
    transaction_type: str
    quantity: int
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StockAlertResponse(BaseModel):
    id: uuid.UUID
    medicine_id: uuid.UUID
    alert_type: str
    message: Optional[str] = None
    is_resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class InventoryStatsResponse(BaseModel):
    total_medicines: int
    low_stock_count: int
    expiring_soon_count: int
    expired_count: int
    total_stock_value: Decimal
