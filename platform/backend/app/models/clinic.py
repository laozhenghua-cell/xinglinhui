"""统一门诊 — 跨专科就诊记录"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ClinicVisit(Base):
    __tablename__ = "clinic_visits"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    patient_name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), default="")
    age: Mapped[int | None] = mapped_column(nullable=True)
    specialty: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # surgery/anorectal/pediatrics/alchemy
    chief_complaint: Mapped[str] = mapped_column(String(500), default="")
    four_diagnosis: Mapped[dict] = mapped_column(JSONB, default=dict)  # 症状/舌/脉/局部/全身/描述
    dx_result: Mapped[dict] = mapped_column(JSONB, default=dict)      # 辨证结果(证型/病种/方剂/AI)
    prescription: Mapped[dict] = mapped_column(JSONB, default=dict)   # 处方(方剂/加减/外治/医嘱)
    followup: Mapped[dict] = mapped_column(JSONB, default=dict)       # 随访(复诊日期/疗效/备注)
    device: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
