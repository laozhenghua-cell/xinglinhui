import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AnorectalHerb(Base):
    __tablename__ = "anorectal_herbs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    pinyin: Mapped[str] = mapped_column(String(100), nullable=True)
    category: Mapped[str] = mapped_column(
        String(50), nullable=True
    )  # 清热解毒, 活血化瘀, 收敛止血, 润肠通便, 消肿止痛
    properties: Mapped[str] = mapped_column(Text, nullable=True)  # 性味归经
    meridians: Mapped[dict] = mapped_column(JSONB, default=list)
    effects: Mapped[str] = mapped_column(Text, nullable=True)  # 功效
    indications: Mapped[str] = mapped_column(Text, nullable=True)  # 主治
    contraindications: Mapped[str] = mapped_column(Text, nullable=True)  # 禁忌
    dosage: Mapped[str] = mapped_column(String(100), nullable=True)
    usage_notes: Mapped[str] = mapped_column(Text, nullable=True)
    is_common: Mapped[bool] = mapped_column(default=False)  # 肛肠科常用
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class AnorectalFormula(Base):
    __tablename__ = "anorectal_formulas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(200), nullable=True)  # 方剂来源
    composition: Mapped[dict] = mapped_column(JSONB, default=list)  # 组成药物及用量
    usage: Mapped[str] = mapped_column(Text, nullable=True)  # 用法
    function: Mapped[str] = mapped_column(Text, nullable=True)  # 功效
    indications: Mapped[str] = mapped_column(Text, nullable=True)  # 主治
    syndrome_type: Mapped[str] = mapped_column(String(100), nullable=True)  # 适用证型
    disease_types: Mapped[dict] = mapped_column(JSONB, default=list)  # 适用病种
    modifications: Mapped[str] = mapped_column(Text, nullable=True)  # 加减变化
    formula_type: Mapped[str] = mapped_column(
        String(30), nullable=True
    )  # internal(内服), external(外用), sitz_bath(坐浴), fumigation(熏洗)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class AnorectalCase(Base):
    __tablename__ = "anorectal_cases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    disease_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    patient_info: Mapped[str] = mapped_column(Text, nullable=True)
    chief_complaint: Mapped[str] = mapped_column(Text, nullable=True)
    symptoms: Mapped[str] = mapped_column(Text, nullable=True)
    tongue_pulse: Mapped[str] = mapped_column(Text, nullable=True)
    syndrome: Mapped[str] = mapped_column(String(200), nullable=True)
    treatment_principle: Mapped[str] = mapped_column(Text, nullable=True)
    formula: Mapped[str] = mapped_column(Text, nullable=True)
    treatment_process: Mapped[str] = mapped_column(Text, nullable=True)
    outcome: Mapped[str] = mapped_column(Text, nullable=True)
    follow_up: Mapped[str] = mapped_column(Text, nullable=True)
    key_points: Mapped[str] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class PreventionGuide(Base):
    __tablename__ = "prevention_guides"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True
    )
    disease_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    prevention_points: Mapped[dict] = mapped_column(JSONB, default=list)
    dietary_advice: Mapped[str] = mapped_column(Text, nullable=True)
    lifestyle_advice: Mapped[str] = mapped_column(Text, nullable=True)
    exercise_advice: Mapped[str] = mapped_column(Text, nullable=True)
    postop_care: Mapped[str] = mapped_column(Text, nullable=True)
    acupuncture_points: Mapped[dict] = mapped_column(JSONB, default=list)
    sitz_bath_formula: Mapped[str] = mapped_column(Text, nullable=True)
    warning_signs: Mapped[dict] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
