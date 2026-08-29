"""收费管理模型"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Numeric, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid


class ChargeItem(Base):
    """收费项目"""
    __tablename__ = "charge_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)  # Removed FK constraint
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, index=True)  # consultation/exam/surgery/material/medicine
    unit_price = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(20), nullable=False, default="次")
    description = Column(Text)
    code = Column(String(50))
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Bill(Base):
    """账单"""
    __tablename__ = "bills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)  # Removed FK constraint
    bill_no = Column(String(50), nullable=False, unique=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    consultation_id = Column(String(36), nullable=True)  # Removed FK constraint
    bill_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0, nullable=False)
    paid_amount = Column(Numeric(10, 2), default=0, nullable=False)
    status = Column(String(20), default="unpaid", nullable=False, index=True)  # unpaid/partial/paid/cancelled
    notes = Column(Text)
    cashier_id = Column(String(36), ForeignKey("users.id"))
    doctor_id = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    items = relationship("BillItem", back_populates="bill", lazy="selectin")
    payments = relationship("BillPayment", back_populates="bill", lazy="selectin")


class BillItem(Base):
    """账单明细"""
    __tablename__ = "bill_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bill_id = Column(String(36), ForeignKey("bills.id"), nullable=False, index=True)
    charge_item_id = Column(String(36), ForeignKey("charge_items.id"))
    item_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Numeric(10, 2), default=1, nullable=False)
    unit = Column(String(20), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    bill = relationship("Bill", back_populates="items")


class BillPayment(Base):
    """账单支付记录"""
    __tablename__ = "bill_payments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bill_id = Column(String(36), ForeignKey("bills.id"), nullable=False, index=True)
    payment_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)  # cash/wechat/alipay/card/insurance
    transaction_no = Column(String(100))
    notes = Column(Text)
    cashier_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    bill = relationship("Bill", back_populates="payments")


class DailyRevenue(Base):
    """每日收入汇总"""
    __tablename__ = "daily_revenues"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)  # Removed FK constraint
    revenue_date = Column(DateTime, nullable=False, index=True)
    total_revenue = Column(Numeric(10, 2), default=0, nullable=False)
    cash_revenue = Column(Numeric(10, 2), default=0, nullable=False)
    wechat_revenue = Column(Numeric(10, 2), default=0, nullable=False)
    alipay_revenue = Column(Numeric(10, 2), default=0, nullable=False)
    card_revenue = Column(Numeric(10, 2), default=0, nullable=False)
    insurance_revenue = Column(Numeric(10, 2), default=0, nullable=False)
    patient_count = Column(Numeric(10, 0), default=0, nullable=False)
    bill_count = Column(Numeric(10, 0), default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
