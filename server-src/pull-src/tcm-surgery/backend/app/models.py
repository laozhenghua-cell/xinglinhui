"""数据模型 —— 知识层(书本) + 应用层(诊疗)

知识层:
  diseases        病种(90)    —— 疮形特点、鉴别、命名考证
  syndromes       证型        —— 阴阳、阶段、辨证指标
  formulas        方药(82附方) —— 组成、功效、治法(消/托/补)、内治/外治
  treatment_rules 论治规则     —— 病种 × 阶段 × 证型 → 内治方 + 外治 + 调护
  images          图片        —— 书本标准图 / 医生上传图

应用层:
  cases           病例
  case_images     复诊照片(时间线)
  treatment_records 诊疗记录(用药 + 疗效)
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Disease(Base):
    __tablename__ = "diseases"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)  # 病名
    aliases: Mapped[list] = mapped_column(JSON, default=list)  # 别名(命名考证)
    category: Mapped[str] = mapped_column(String(50), index=True)  # 疖/痈/疽/疔/...
    location: Mapped[Optional[str]] = mapped_column(String(200))  # 好发部位
    morphology: Mapped[Optional[str]] = mapped_column(Text)  # 疮形特点(形态)
    characteristics: Mapped[Optional[str]] = mapped_column(Text)  # 疮形特点(详细)
    differential: Mapped[Optional[str]] = mapped_column(Text)  # 鉴别要点
    prognosis: Mapped[Optional[str]] = mapped_column(Text)  # 预后 / 顺逆
    western_equiv: Mapped[Optional[str]] = mapped_column(String(200))  # 相当于西医
    source: Mapped[Optional[str]] = mapped_column(String(200))  # 病名出处
    is_dangerous: Mapped[bool] = mapped_column(Boolean, default=False)  # 危险证(需转诊)
    is_sores: Mapped[bool] = mapped_column(Boolean, default=True)  # 是否疮疡类(适用阴阳/阶段辨证)
    is_yang: Mapped[bool] = mapped_column(Boolean, default=True)  # 是否阳证(阴证病种用温通/补益辨证)
    differentiation: Mapped[Optional[str]] = mapped_column(String(20), default="消托补")  # 辨证框架:消托补(阴阳+阶段) / 分型(病机分型)

    images: Mapped[list["Image"]] = relationship(
        back_populates="disease", cascade="all, delete-orphan"
    )
    rules: Mapped[list["TreatmentRule"]] = relationship(
        back_populates="disease", cascade="all, delete-orphan"
    )


class Syndrome(Base):
    __tablename__ = "syndromes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)  # 证型名
    yin_yang: Mapped[str] = mapped_column(String(10), index=True)  # 阳 / 阴
    stage: Mapped[Optional[str]] = mapped_column(String(20), index=True)  # 初起/成脓/溃后
    local_signs: Mapped[Optional[str]] = mapped_column(Text)  # 局部辨证指标
    systemic_signs: Mapped[Optional[str]] = mapped_column(Text)  # 全身症状
    tongue_pulse: Mapped[Optional[str]] = mapped_column(Text)  # 舌脉


class Formula(Base):
    __tablename__ = "formulas"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)  # 方名
    source: Mapped[Optional[str]] = mapped_column(String(200))  # 出处
    composition: Mapped[Optional[str]] = mapped_column(Text)  # 组成
    dosage: Mapped[Optional[str]] = mapped_column(Text)  # 剂量(标准用量)
    function: Mapped[Optional[str]] = mapped_column(Text)  # 功效
    indication: Mapped[Optional[str]] = mapped_column(Text)  # 适应证/主治(证候)
    method: Mapped[Optional[str]] = mapped_column(String(20), index=True)  # 消/托/补
    usage_type: Mapped[Optional[str]] = mapped_column(String(20), index=True)  # 内治/外治
    usage: Mapped[Optional[str]] = mapped_column(Text)  # 用法
    contraindications: Mapped[Optional[str]] = mapped_column(Text)  # 禁忌
    toxicity: Mapped[Optional[str]] = mapped_column(String(10), index=True)  # 毒性分级:剧毒/有毒/慎用
    modifications: Mapped[Optional[str]] = mapped_column(Text)  # 随证加减
    preparation: Mapped[Optional[str]] = mapped_column(Text)  # 炼制方法(丹药)
    domain: Mapped[Optional[str]] = mapped_column(String(20), default="疮疡", index=True)  # 学科领域:疮疡/骨伤/妇科


class TreatmentRule(Base):
    """论治规则:某个病、某个阶段、某种证型 → 用什么药"""

    __tablename__ = "treatment_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    disease_id: Mapped[int] = mapped_column(ForeignKey("diseases.id"), index=True)
    stage: Mapped[str] = mapped_column(String(20), index=True)  # 初起/成脓/溃后
    syndrome_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("syndromes.id"), nullable=True, index=True
    )  # 可为空=该阶段通用
    internal_formula_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("formulas.id"), nullable=True
    )  # 内治方
    external_treatment: Mapped[Optional[str]] = mapped_column(Text)  # 外治法
    nursing: Mapped[Optional[str]] = mapped_column(Text)  # 调护
    note: Mapped[Optional[str]] = mapped_column(Text)
    is_specific: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否证型细分规则

    disease: Mapped["Disease"] = relationship(back_populates="rules")
    syndrome: Mapped["Syndrome"] = relationship()
    formula: Mapped["Formula"] = relationship()


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True)
    disease_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("diseases.id"), nullable=True, index=True
    )
    image_type: Mapped[str] = mapped_column(String(20), default="book")  # book / case
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)  # 图版所属类别
    path: Mapped[str] = mapped_column(String(500))  # 图片路径或 URL
    caption: Mapped[Optional[str]] = mapped_column(String(500))  # 图注

    disease: Mapped["Disease"] = relationship(back_populates="images")


# ---------- 应用层 ----------

class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    age: Mapped[Optional[int]] = mapped_column()
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    note: Mapped[Optional[str]] = mapped_column(Text)  # 备注(过敏史等)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    cases: Mapped[list["Case"]] = relationship(back_populates="patient")


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[Optional[int]] = mapped_column(ForeignKey("patients.id"), nullable=True, index=True)
    patient_name: Mapped[Optional[str]] = mapped_column(String(100))
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    age: Mapped[Optional[int]] = mapped_column()
    disease_id: Mapped[Optional[int]] = mapped_column(ForeignKey("diseases.id"), nullable=True)
    syndrome_id: Mapped[Optional[int]] = mapped_column(ForeignKey("syndromes.id"), nullable=True)
    stage: Mapped[Optional[str]] = mapped_column(String(20))  # 当前阶段
    chief_complaint: Mapped[Optional[str]] = mapped_column(Text)  # 主诉
    history: Mapped[Optional[str]] = mapped_column(Text)  # 现病史+四诊
    syndrome: Mapped[Optional[str]] = mapped_column(Text)  # 辨证(名家医案/病历)
    treatment: Mapped[Optional[str]] = mapped_column(Text)  # 治则方药(多诊经过)
    effect: Mapped[Optional[str]] = mapped_column(Text)  # 疗效
    source: Mapped[Optional[str]] = mapped_column(String(20), default="临床")  # 临床/名家
    domain: Mapped[Optional[str]] = mapped_column(String(20), default="疮疡")  # 学科领域
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    patient: Mapped["Patient"] = relationship(back_populates="cases")
    images: Mapped[list["CaseImage"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )
    records: Mapped[list["TreatmentRecord"]] = relationship(
        back_populates="case", cascade="all, delete-orphan"
    )


class CaseImage(Base):
    __tablename__ = "case_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    path: Mapped[str] = mapped_column(String(500))
    taken_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped["Case"] = relationship(back_populates="images")


class TreatmentRecord(Base):
    __tablename__ = "treatment_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    formula_id: Mapped[Optional[int]] = mapped_column(ForeignKey("formulas.id"), nullable=True)
    external_treatment: Mapped[Optional[str]] = mapped_column(Text)
    effect: Mapped[Optional[str]] = mapped_column(Text)  # 疗效反馈
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped["Case"] = relationship(back_populates="records")
    formula: Mapped["Formula"] = relationship()


# ---------- 名家经验 ----------

class ExpertExperience(Base):
    """名家经验(辨证施治经验,按病种大类关联)"""

    __tablename__ = "expert_experiences"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(50), index=True)  # 关联大类(痈/疔/…)
    expert_name: Mapped[str] = mapped_column(String(50))  # 名家()
    syndrome_points: Mapped[Optional[str]] = mapped_column(Text)  # 辨证要点
    internal_treatment: Mapped[Optional[str]] = mapped_column(Text)  # 内治法(经验方+加减)
    external_treatment: Mapped[Optional[str]] = mapped_column(Text)  # 外治法
    source: Mapped[Optional[str]] = mapped_column(String(200))  # 出处
    domain: Mapped[Optional[str]] = mapped_column(String(20), default="疮疡")  # 学科领域


class ExpertCase(Base):
    """名家医案(验案)"""

    __tablename__ = "expert_cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(50), index=True)
    expert_name: Mapped[str] = mapped_column(String(50))
    diagnosis: Mapped[Optional[str]] = mapped_column(String(200))  # 诊断(病名)
    history: Mapped[Optional[str]] = mapped_column(Text)  # 主诉+现病史+四诊
    syndrome: Mapped[Optional[str]] = mapped_column(Text)  # 辨证
    treatment: Mapped[Optional[str]] = mapped_column(Text)  # 治则+方剂+药物(多诊经过)
    effect: Mapped[Optional[str]] = mapped_column(Text)  # 疗效
    domain: Mapped[Optional[str]] = mapped_column(String(20), default="疮疡")  # 学科领域


class ClinicalTip(Base):
    """临证心法(外科用药秘诀/临证要诀)"""

    __tablename__ = "clinical_tips"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(50), index=True)  # 辨阴阳/引经/丹药/围药/洗药/预后/气血...
    content: Mapped[str] = mapped_column(Text)  # 秘诀内容
    source: Mapped[Optional[str]] = mapped_column(String(200))  # 出处
