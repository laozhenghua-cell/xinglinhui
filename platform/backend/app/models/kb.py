"""统一共用知识总库数据模型 —— SQLAlchemy 2.0 async + PostgreSQL 16。

四专科(疮疡 surgery / 痔漏 anorectal / 儿科 pediatrics / 丹药 alchemy)内容
统一落库到 ``kb_*`` 表。所有表均带 ``module`` 字段并约束 ``(module, origin_id)``
联合唯一(迁移脚本据此做幂等 upsert)。

- JSONB 字段:aliases / composition / meridians / extra
- 文本字段:Text
- 主键:UUID(as_uuid=True)
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    """带时区的 UTC 时间(与基座其他模型一致)。"""
    return datetime.now(timezone.utc)


class _KBCommon:
    """kb_* 表通用列。"""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    module: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    origin_id: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )


class KBFormula(_KBCommon, Base):
    """统一方剂(含组成 JSONB)。"""

    __tablename__ = "kb_formulas"
    __table_args__ = (UniqueConstraint("module", "origin_id"),)

    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    aliases: Mapped[list] = mapped_column(JSONB, default=list)
    source: Mapped[Optional[str]] = mapped_column(String(200))
    category: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    composition: Mapped[list] = mapped_column(JSONB, default=list)  # [{name, dose}]
    function: Mapped[Optional[str]] = mapped_column(Text)
    indication: Mapped[Optional[str]] = mapped_column(Text)
    usage: Mapped[Optional[str]] = mapped_column(Text)
    method: Mapped[Optional[str]] = mapped_column(String(20))
    formula_type: Mapped[Optional[str]] = mapped_column(String(30))
    contraindications: Mapped[Optional[str]] = mapped_column(Text)
    modifications: Mapped[Optional[str]] = mapped_column(Text)
    preparation: Mapped[Optional[str]] = mapped_column(Text)
    toxicity: Mapped[Optional[str]] = mapped_column(String(20))
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)


class KBHerb(_KBCommon, Base):
    """统一中药。"""

    __tablename__ = "kb_herbs"
    __table_args__ = (UniqueConstraint("module", "origin_id"),)

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    pinyin: Mapped[Optional[str]] = mapped_column(String(100))
    aliases: Mapped[list] = mapped_column(JSONB, default=list)
    category: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    properties: Mapped[Optional[str]] = mapped_column(Text)  # 性味归经
    meridians: Mapped[list] = mapped_column(JSONB, default=list)  # 归经
    effects: Mapped[Optional[str]] = mapped_column(Text)  # 功效
    indications: Mapped[Optional[str]] = mapped_column(Text)  # 主治
    contraindications: Mapped[Optional[str]] = mapped_column(Text)  # 禁忌
    dosage: Mapped[Optional[str]] = mapped_column(String(100))
    usage_notes: Mapped[Optional[str]] = mapped_column(Text)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)


class KBDisease(_KBCommon, Base):
    """统一病种。"""

    __tablename__ = "kb_diseases"
    __table_args__ = (UniqueConstraint("module", "origin_id"),)

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    aliases: Mapped[list] = mapped_column(JSONB, default=list)
    category: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    morphology: Mapped[Optional[str]] = mapped_column(Text)
    characteristics: Mapped[Optional[str]] = mapped_column(Text)
    differential: Mapped[Optional[str]] = mapped_column(Text)
    prognosis: Mapped[Optional[str]] = mapped_column(Text)
    western_equiv: Mapped[Optional[str]] = mapped_column(String(200))
    source: Mapped[Optional[str]] = mapped_column(String(200))
    is_dangerous: Mapped[bool] = mapped_column(Boolean, default=False)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)


class KBSyndrome(_KBCommon, Base):
    """统一证型。"""

    __tablename__ = "kb_syndromes"
    __table_args__ = (UniqueConstraint("module", "origin_id"),)

    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    aliases: Mapped[list] = mapped_column(JSONB, default=list)
    yin_yang: Mapped[Optional[str]] = mapped_column(String(10))
    stage: Mapped[Optional[str]] = mapped_column(String(20))
    local_signs: Mapped[Optional[str]] = mapped_column(Text)
    systemic_signs: Mapped[Optional[str]] = mapped_column(Text)
    tongue_pulse: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)


class KBCase(_KBCommon, Base):
    """统一医案。"""

    __tablename__ = "kb_cases"
    __table_args__ = (UniqueConstraint("module", "origin_id"),)

    title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    disease: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    syndrome: Mapped[Optional[str]] = mapped_column(String(200))
    patient_info: Mapped[Optional[str]] = mapped_column(Text)
    chief_complaint: Mapped[Optional[str]] = mapped_column(Text)
    history: Mapped[Optional[str]] = mapped_column(Text)
    treatment: Mapped[Optional[str]] = mapped_column(Text)
    effect: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[Optional[str]] = mapped_column(String(200))
    expert_name: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)


class KBTip(_KBCommon, Base):
    """统一要诀 / 训诫 / 安全规则 / 名家经验。"""

    __tablename__ = "kb_tips"
    __table_args__ = (UniqueConstraint("module", "origin_id"),)

    category: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(200))
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)


class KBTerm(_KBCommon, Base):
    """统一术语。"""

    __tablename__ = "kb_terms"
    __table_args__ = (UniqueConstraint("module", "origin_id"),)

    term: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    definition: Mapped[Optional[str]] = mapped_column(Text)
    source: Mapped[Optional[str]] = mapped_column(String(200))
    extra: Mapped[dict] = mapped_column(JSONB, default=dict)


class KBDulong(_KBCommon, Base):
    """丹药·毒龙丹引药(按症引药表)。"""

    __tablename__ = "kb_dulong"
    __table_args__ = (UniqueConstraint("module", "origin_id"),)

    section: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    n: Mapped[int] = mapped_column(Integer, nullable=False)
    disease: Mapped[Optional[str]] = mapped_column(Text)
    guide: Mapped[Optional[str]] = mapped_column(Text)


class KbClassic(Base):
    """经典典籍条文(原文+白话+出处)。"""
    __tablename__ = "kb_classics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    chapter: Mapped[str] = mapped_column(String(200), nullable=False)
    article: Mapped[str] = mapped_column(String(100), default="")
    original: Mapped[str] = mapped_column(Text, nullable=False)
    plain: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(300), default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class KbYifang(Base):
    """方剂库(《医方集解》为主体+后世名方;辨证开方联动)。"""
    __tablename__ = "kb_yifang"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    aliases: Mapped[list] = mapped_column(JSONB, default=list)
    composition: Mapped[list] = mapped_column(JSONB, default=list)  # [{name, dosage}]
    function: Mapped[str] = mapped_column(Text, default="")
    indications: Mapped[str] = mapped_column(Text, default="")
    contraindications: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(300), default="")
    analysis: Mapped[list] = mapped_column(JSONB, default=list)  # 逐药方解 [{name, role, note}]
    derivations: Mapped[list] = mapped_column(JSONB, default=list)  # 加减附方链 [{name, note}]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
