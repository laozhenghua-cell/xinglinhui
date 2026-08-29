"""疮疡(外科)模块数据模型 —— SQLAlchemy 2.0 async + PostgreSQL。

由 cy-backend-ref 的 SQLite 模型移植而来，表名统一加 ``surgery_`` 前缀。
主键沿用旧的整数自增 id（保证迁移与前端响应兼容），JSON 字段使用通用
``JSON``（PG 落为 JSON，SQLite 落为 TEXT，便于本地自测）。

注意：疮疡患者复用基座已有的 ``patients`` 表（``app.models.patient.Patient``），
本模块不新建患者表；``SurgeryCase.patient_id`` 仅保留旧数据的整数语义，
不建立外键（避免与 UUID 主键的 patients 表冲突）。
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    """朴素 UTC 时间（与旧版 ``datetime.utcnow`` 行为一致，无时区信息）。"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class SurgeryDisease(Base):
    __tablename__ = "surgery_diseases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    aliases: Mapped[list] = mapped_column(JSON, default=list)
    category: Mapped[str] = mapped_column(String(50), index=True)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    morphology: Mapped[Optional[str]] = mapped_column(Text)
    characteristics: Mapped[Optional[str]] = mapped_column(Text)
    differential: Mapped[Optional[str]] = mapped_column(Text)
    prognosis: Mapped[Optional[str]] = mapped_column(Text)
    western_equiv: Mapped[Optional[str]] = mapped_column(String(200))
    source: Mapped[Optional[str]] = mapped_column(String(200))
    is_dangerous: Mapped[bool] = mapped_column(Boolean, default=False)
    is_sores: Mapped[bool] = mapped_column(Boolean, default=True)
    is_yang: Mapped[bool] = mapped_column(Boolean, default=True)
    differentiation: Mapped[Optional[str]] = mapped_column(String(20), default="消托补")

    images: Mapped[list["SurgeryImage"]] = relationship(
        back_populates="disease", cascade="all, delete-orphan"
    )
    rules: Mapped[list["SurgeryTreatmentRule"]] = relationship(
        back_populates="disease", cascade="all, delete-orphan"
    )


class SurgerySyndrome(Base):
    __tablename__ = "surgery_syndromes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    yin_yang: Mapped[str] = mapped_column(String(10), index=True)
    stage: Mapped[Optional[str]] = mapped_column(String(20), index=True)
    local_signs: Mapped[Optional[str]] = mapped_column(Text)
    systemic_signs: Mapped[Optional[str]] = mapped_column(Text)
    tongue_pulse: Mapped[Optional[str]] = mapped_column(Text)


class SurgeryFormula(Base):
    __tablename__ = "surgery_formulas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    source: Mapped[Optional[str]] = mapped_column(String(200))
    composition: Mapped[Optional[str]] = mapped_column(Text)
    dosage: Mapped[Optional[str]] = mapped_column(Text)
    function: Mapped[Optional[str]] = mapped_column(Text)
    indication: Mapped[Optional[str]] = mapped_column(Text)
    method: Mapped[Optional[str]] = mapped_column(String(20), index=True)
    usage_type: Mapped[Optional[str]] = mapped_column(String(20), index=True)
    usage: Mapped[Optional[str]] = mapped_column(Text)
    contraindications: Mapped[Optional[str]] = mapped_column(Text)
    toxicity: Mapped[Optional[str]] = mapped_column(String(10), index=True)
    modifications: Mapped[Optional[str]] = mapped_column(Text)
    preparation: Mapped[Optional[str]] = mapped_column(Text)
    domain: Mapped[Optional[str]] = mapped_column(String(20), default="疮疡", index=True)


class SurgeryTreatmentRule(Base):
    __tablename__ = "surgery_treatment_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    disease_id: Mapped[int] = mapped_column(
        ForeignKey("surgery_diseases.id"), index=True
    )
    stage: Mapped[str] = mapped_column(String(20), index=True)
    syndrome_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("surgery_syndromes.id"), nullable=True, index=True
    )
    internal_formula_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("surgery_formulas.id"), nullable=True
    )
    external_treatment: Mapped[Optional[str]] = mapped_column(Text)
    nursing: Mapped[Optional[str]] = mapped_column(Text)
    note: Mapped[Optional[str]] = mapped_column(Text)
    is_specific: Mapped[bool] = mapped_column(Boolean, default=False)

    disease: Mapped["SurgeryDisease"] = relationship(back_populates="rules")
    syndrome: Mapped["SurgerySyndrome"] = relationship()
    formula: Mapped["SurgeryFormula"] = relationship()


class SurgeryImage(Base):
    __tablename__ = "surgery_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    disease_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("surgery_diseases.id"), nullable=True, index=True
    )
    image_type: Mapped[str] = mapped_column(String(20), default="book")
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    path: Mapped[str] = mapped_column(String(500))
    caption: Mapped[Optional[str]] = mapped_column(String(500))

    disease: Mapped["SurgeryDisease"] = relationship(back_populates="images")


class SurgeryCase(Base):
    __tablename__ = "surgery_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # 旧数据 patient_id 为整数且全部为空；复用 UUID 主键的 patients 表，
    # 故此处保留整数语义但不建外键。
    patient_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    patient_name: Mapped[Optional[str]] = mapped_column(String(100))
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    age: Mapped[Optional[int]] = mapped_column(Integer)
    disease_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("surgery_diseases.id"), nullable=True
    )
    syndrome_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("surgery_syndromes.id"), nullable=True
    )
    stage: Mapped[Optional[str]] = mapped_column(String(20))
    chief_complaint: Mapped[Optional[str]] = mapped_column(Text)
    history: Mapped[Optional[str]] = mapped_column(Text)
    syndrome: Mapped[Optional[str]] = mapped_column(Text)
    treatment: Mapped[Optional[str]] = mapped_column(Text)
    effect: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[Optional[str]] = mapped_column(String(20), default="临床")
    domain: Mapped[Optional[str]] = mapped_column(String(20), default="疮疡")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    images: Mapped[list["SurgeryCaseImage"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    records: Mapped[list["SurgeryTreatmentRecord"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )


class SurgeryCaseImage(Base):
    __tablename__ = "surgery_case_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("surgery_cases.id"), index=True)
    path: Mapped[str] = mapped_column(String(500))
    taken_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    case: Mapped["SurgeryCase"] = relationship(back_populates="images")


class SurgeryTreatmentRecord(Base):
    __tablename__ = "surgery_treatment_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("surgery_cases.id"), index=True)
    formula_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("surgery_formulas.id"), nullable=True
    )
    external_treatment: Mapped[Optional[str]] = mapped_column(Text)
    effect: Mapped[Optional[str]] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    case: Mapped["SurgeryCase"] = relationship(back_populates="records")
    formula: Mapped["SurgeryFormula"] = relationship()


class SurgeryExpertExperience(Base):
    __tablename__ = "surgery_expert_experiences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(50), index=True)
    expert_name: Mapped[str] = mapped_column(String(50))
    syndrome_points: Mapped[Optional[str]] = mapped_column(Text)
    internal_treatment: Mapped[Optional[str]] = mapped_column(Text)
    external_treatment: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[Optional[str]] = mapped_column(String(200))
    domain: Mapped[Optional[str]] = mapped_column(String(20), default="疮疡")


class SurgeryExpertCase(Base):
    __tablename__ = "surgery_expert_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(50), index=True)
    expert_name: Mapped[str] = mapped_column(String(50))
    diagnosis: Mapped[Optional[str]] = mapped_column(String(200))
    history: Mapped[Optional[str]] = mapped_column(Text)
    syndrome: Mapped[Optional[str]] = mapped_column(Text)
    treatment: Mapped[Optional[str]] = mapped_column(Text)
    effect: Mapped[Optional[str]] = mapped_column(Text)
    domain: Mapped[Optional[str]] = mapped_column(String(20), default="疮疡")


class SurgeryClinicalTip(Base):
    __tablename__ = "surgery_clinical_tips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(50), index=True)
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[Optional[str]] = mapped_column(String(200))
