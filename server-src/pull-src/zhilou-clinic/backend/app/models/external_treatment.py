"""
外治法数据模型
External Treatment Models
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ExternalTreatment(Base):
    """外治法基础表"""
    __tablename__ = "external_treatments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    treatment_type: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True
    )  # fumigation(熏洗), ointment(外敷), suppository(栓剂), injection(注射)

    composition: Mapped[dict] = mapped_column(JSONB, default=list)  # 组成药物及用量
    preparation: Mapped[str] = mapped_column(Text, nullable=True)  # 制备方法
    usage: Mapped[str] = mapped_column(Text, nullable=False)  # 使用方法
    frequency: Mapped[str] = mapped_column(String(100), nullable=True)  # 使用频次
    duration: Mapped[str] = mapped_column(String(100), nullable=True)  # 疗程

    function: Mapped[str] = mapped_column(Text, nullable=True)  # 功效
    indications: Mapped[str] = mapped_column(Text, nullable=True)  # 适应症
    syndrome_types: Mapped[dict] = mapped_column(JSONB, default=list)  # 适用证型列表
    disease_types: Mapped[dict] = mapped_column(JSONB, default=list)  # 适用病种列表

    contraindications: Mapped[str] = mapped_column(Text, nullable=True)  # 禁忌症
    precautions: Mapped[str] = mapped_column(Text, nullable=True)  # 注意事项
    source: Mapped[str] = mapped_column(String(200), nullable=True)  # 来源
    priority: Mapped[int] = mapped_column(Integer, default=0)  # 推荐优先级

    notes: Mapped[str] = mapped_column(Text, nullable=True)  # 临床备注
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ExternalTreatmentRecord(Base):
    """外治法使用记录"""
    __tablename__ = "external_treatment_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True
    )
    consultation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("consultations.id"), nullable=True, index=True
    )
    treatment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("external_treatments.id"), nullable=False
    )

    treatment_name: Mapped[str] = mapped_column(String(200), nullable=False)
    treatment_type: Mapped[str] = mapped_column(String(30), nullable=False)
    usage_instruction: Mapped[str] = mapped_column(Text, nullable=True)

    prescribed_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
