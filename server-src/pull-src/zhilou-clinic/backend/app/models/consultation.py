import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Consultation(Base):
    __tablename__ = "consultations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    disease_type: Mapped[str] = mapped_column(
        String(50), nullable=True
    )  # 痔疮/肛裂/肛瘘/肛周脓肿/直肠脱垂/肛周湿疹/尖锐湿疣
    chief_complaint: Mapped[str] = mapped_column(Text, nullable=True)
    symptoms: Mapped[dict] = mapped_column(JSONB, default=dict)
    tongue: Mapped[str] = mapped_column(Text, nullable=True)
    pulse: Mapped[str] = mapped_column(Text, nullable=True)
    diagnosis: Mapped[str] = mapped_column(Text, nullable=True)
    syndrome: Mapped[str] = mapped_column(Text, nullable=True)  # 辨证
    treatment_principle: Mapped[str] = mapped_column(Text, nullable=True)  # 治法
    treatment: Mapped[str] = mapped_column(Text, nullable=True)
    prescription_text: Mapped[str] = mapped_column(Text, nullable=True)
    symptom_score: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending, in_progress, completed
    images: Mapped[dict] = mapped_column(JSONB, default=list)
    ai_analysis: Mapped[dict] = mapped_column(JSONB, default=dict)
    physical_exam: Mapped[dict] = mapped_column(JSONB, default=dict)

    # 四诊采集数据
    four_examinations: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=True, comment="四诊数据结构化存储")
    selected_symptoms: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=True, comment="用户选择的症状")
    syndrome_result: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=True, comment="辨证结果及置信度")
    formula_modifications: Mapped[str] = mapped_column(Text, nullable=True, comment="加减化裁说明")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # 关系
    diagnosis_records = relationship("DiagnosisRecord", back_populates="consultation")


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    consultation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("consultations.id"), nullable=True
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    formula_name: Mapped[str] = mapped_column(String(200), nullable=True)
    medicines: Mapped[dict] = mapped_column(JSONB, default=list)
    dosage_instructions: Mapped[str] = mapped_column(Text, nullable=True)
    duration_days: Mapped[int] = mapped_column(Integer, default=7)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class Followup(Base):
    __tablename__ = "followups"

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
        UUID(as_uuid=True), ForeignKey("consultations.id"), nullable=True
    )
    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    scheduled_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actual_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="scheduled"
    )  # scheduled, completed, missed, cancelled
    symptom_score: Mapped[int] = mapped_column(Integer, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    recovery_status: Mapped[str] = mapped_column(String(50), nullable=True)
    images: Mapped[dict] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
