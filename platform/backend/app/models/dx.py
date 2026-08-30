"""统一辨证中心 — 记录表"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DxRecord(Base):
    __tablename__ = "dx_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    module: Mapped[str] = mapped_column(String(50), nullable=False, default="all")
    input: Mapped[dict] = mapped_column(JSONB, default=dict)
    result: Mapped[dict] = mapped_column(JSONB, default=dict)
    ip_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    ua_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )


class DxTongueReading(Base):
    """舌象拍照识别记录 — 设备级匿名,原始特征与归一化标签分开存。"""

    __tablename__ = "dx_tongue_readings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    image_url: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    feats: Mapped[dict] = mapped_column(JSONB, default=dict)   # Qwen-VL 原始特征
    labels: Mapped[dict] = mapped_column(JSONB, default=list)  # 归一化标签列表
    source: Mapped[str] = mapped_column(String(30), nullable=False, default="unavailable")
    confidence: Mapped[float | None] = mapped_column(nullable=True)
    ip_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    ua_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
