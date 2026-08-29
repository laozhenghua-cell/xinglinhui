"""库存管理模型"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Numeric, Boolean, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid


class Medicine(Base):
    """药品基础信息"""
    __tablename__ = "medicines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)  # Removed FK constraint
    name = Column(String(100), nullable=False, index=True)
    alias = Column(String(100))
    category = Column(String(50), nullable=False, index=True)  # herb/patent/western
    specification = Column(String(100))
    unit = Column(String(20), nullable=False, default="克")
    purchase_price = Column(Numeric(10, 2), nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)
    min_stock = Column(Numeric(10, 2), default=100, nullable=False)
    max_stock = Column(Numeric(10, 2), default=10000)

    # 中药属性
    nature = Column(String(50))  # 性味：寒/热/温/凉
    flavor = Column(String(100))  # 味：辛/甘/酸/苦/咸
    meridian = Column(String(200))  # 归经
    efficacy = Column(Text)  # 功效

    is_active = Column(Boolean, default=True, nullable=False, index=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    batches = relationship("MedicineBatch", back_populates="medicine", lazy="selectin")


class MedicineBatch(Base):
    """药品批次"""
    __tablename__ = "medicine_batches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    medicine_id = Column(String(36), ForeignKey("medicines.id"), nullable=False, index=True)
    batch_no = Column(String(50), nullable=False, index=True)
    supplier = Column(String(200))
    purchase_date = Column(DateTime, nullable=False, index=True)
    expiry_date = Column(DateTime, index=True)
    purchase_price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    remaining = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="available", nullable=False, index=True)  # available/depleted/expired
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    medicine = relationship("Medicine", back_populates="batches")


class StockTransaction(Base):
    """库存事务记录"""
    __tablename__ = "stock_transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)  # Removed FK constraint
    medicine_id = Column(String(36), ForeignKey("medicines.id"), nullable=False, index=True)
    batch_id = Column(String(36), ForeignKey("medicine_batches.id"))
    transaction_type = Column(String(20), nullable=False, index=True)  # in/out/adjust
    transaction_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(20), nullable=False)
    reference_type = Column(String(50))  # prescription/inventory_check/waste/purchase
    reference_id = Column(String(36))
    notes = Column(Text)
    operator_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class StockAlert(Base):
    """库存预警"""
    __tablename__ = "stock_alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)  # Removed FK constraint
    medicine_id = Column(String(36), ForeignKey("medicines.id"), nullable=False, index=True)
    batch_id = Column(String(36), ForeignKey("medicine_batches.id"))
    alert_type = Column(String(50), nullable=False, index=True)  # low_stock/expired/expiring_soon
    alert_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    status = Column(String(20), default="pending", nullable=False, index=True)  # pending/acknowledged/resolved
    acknowledged_by = Column(String(36), ForeignKey("users.id"))
    acknowledged_at = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
