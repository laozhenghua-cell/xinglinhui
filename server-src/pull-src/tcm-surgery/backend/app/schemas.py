"""Pydantic 请求/响应模型"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ---------- 知识层 ----------

class FormulaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    source: Optional[str] = None
    composition: Optional[str] = None
    dosage: Optional[str] = None
    function: Optional[str] = None
    indication: Optional[str] = None
    method: Optional[str] = None
    usage_type: Optional[str] = None
    usage: Optional[str] = None
    contraindications: Optional[str] = None
    toxicity: Optional[str] = None
    modifications: Optional[str] = None
    preparation: Optional[str] = None
    domain: Optional[str] = None


class SyndromeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    yin_yang: str
    stage: Optional[str] = None
    local_signs: Optional[str] = None
    systemic_signs: Optional[str] = None
    tongue_pulse: Optional[str] = None


class ImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    disease_id: Optional[int] = None
    image_type: str
    category: Optional[str] = None
    path: str
    caption: Optional[str] = None


class RuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    stage: str
    syndrome_id: Optional[int] = None
    internal_formula_id: Optional[int] = None
    external_treatment: Optional[str] = None
    nursing: Optional[str] = None
    note: Optional[str] = None
    syndrome: Optional[SyndromeOut] = None
    formula: Optional[FormulaOut] = None


class DiseaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    aliases: list = []
    category: str
    location: Optional[str] = None
    morphology: Optional[str] = None
    characteristics: Optional[str] = None
    differential: Optional[str] = None
    prognosis: Optional[str] = None
    western_equiv: Optional[str] = None
    source: Optional[str] = None
    is_dangerous: bool = False
    is_sores: bool = True
    is_yang: bool = True
    differentiation: Optional[str] = "消托补"
    images: list[ImageOut] = []
    rules: list[RuleOut] = []


class DiseaseBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    aliases: list = []
    category: str
    location: Optional[str] = None
    is_dangerous: bool = False
    is_sores: bool = True
    is_yang: bool = True
    differentiation: Optional[str] = "消托补"
    thumbnail: Optional[str] = None


# ---------- 辨证论治核心 ----------

class TreatmentRecommendIn(BaseModel):
    """辨证论治请求:病种 + 阶段 + 证型"""

    disease_id: int
    stage: str  # 初起 / 成脓 / 溃后
    syndrome_id: Optional[int] = None  # 可选,为空则按阶段通用规则


class TreatmentRecommendOut(BaseModel):
    disease: DiseaseBrief
    stage: str
    syndrome: Optional[SyndromeOut] = None
    rules: list[RuleOut] = []
    external_formulas: list[FormulaOut] = []  # 马培之《外科传薪集》外治方参考(按阶段)
    experience_formulas: list[FormulaOut] = []  # 文琢之《中医外科经验论集》内服经验方(按病种)
    summary: str = ""  # 系统生成的一句话建议


class DifferentiateIn(BaseModel):
    """辨证导航请求(结构化问答)"""

    disease_id: Optional[int] = None
    yin_yang: Optional[str] = None  # 阳 / 阴
    stage: Optional[str] = None  # 初起 / 成脓 / 溃后
    symptoms: list[str] = []  # 勾选的症状/指标


class DifferentiateOut(BaseModel):
    matched_syndromes: list[SyndromeOut] = []
    suggestion: str = ""


# ---------- 方证对应(按证选方) ----------

class MatchSyndrome(BaseModel):
    """按证选方的证候选项"""
    key: str
    label: str
    desc: str = ""
    symptoms: list[str] = []  # 本证候的四诊/表现关键词(用于辅助辨证)


class MatchDomain(BaseModel):
    domain: str
    label: str
    syndromes: list[MatchSyndrome] = []


class MatchFormulaOut(BaseModel):
    formula: FormulaOut
    matched: list[str] = []  # 命中关键词
    score: int = 0


class MatchFormulaIn(BaseModel):
    keys: list[str] = []  # 选中的证候 key
    domain: Optional[str] = None  # 可选:限定病域


class MatchFormulaResponse(BaseModel):
    items: list[MatchFormulaOut] = []
    summary: str = ""


class MatchSyndromeIn(BaseModel):
    """四诊驱动辨证:勾选症状/舌脉 → 自动评分证候"""
    domain: Optional[str] = None
    symptoms: list[str] = []


class MatchSyndromeScore(BaseModel):
    key: str
    label: str
    desc: str = ""
    score: int = 0
    matched: list[str] = []  # 命中依据


class MatchSyndromeResponse(BaseModel):
    matched: list[MatchSyndromeScore] = []
    suggestion: str = ""


# ---------- 应用层 ----------

class PatientCreate(BaseModel):
    name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    note: Optional[str] = None


class CaseCreate(BaseModel):
    patient_id: Optional[int] = None
    patient_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    disease_id: Optional[int] = None
    syndrome_id: Optional[int] = None
    stage: Optional[str] = None
    chief_complaint: Optional[str] = None
    syndrome: Optional[str] = None
    treatment: Optional[str] = None
    effect: Optional[str] = None
    source: Optional[str] = None


class CaseImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    path: str
    taken_at: datetime


class TreatmentRecordIn(BaseModel):
    formula_id: Optional[int] = None
    external_treatment: Optional[str] = None
    effect: Optional[str] = None


class TreatmentRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    formula_id: Optional[int] = None
    external_treatment: Optional[str] = None
    effect: Optional[str] = None
    recorded_at: datetime
    formula: Optional[FormulaOut] = None


class CaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    patient_id: Optional[int] = None
    patient_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    disease_id: Optional[int] = None
    syndrome_id: Optional[int] = None
    stage: Optional[str] = None
    chief_complaint: Optional[str] = None
    history: Optional[str] = None
    syndrome: Optional[str] = None
    treatment: Optional[str] = None
    effect: Optional[str] = None
    source: Optional[str] = None
    domain: Optional[str] = None
    created_at: datetime
    images: list[CaseImageOut] = []
    records: list[TreatmentRecordOut] = []


class PatientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime
    cases: list[CaseOut] = []


class ExpertExperienceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category: str
    expert_name: str
    syndrome_points: Optional[str] = None
    internal_treatment: Optional[str] = None
    external_treatment: Optional[str] = None
    source: Optional[str] = None
    domain: Optional[str] = None


class ExpertCaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category: str
    expert_name: str
    diagnosis: Optional[str] = None
    history: Optional[str] = None
    syndrome: Optional[str] = None
    treatment: Optional[str] = None
    effect: Optional[str] = None
    domain: Optional[str] = None


class ClinicalTipOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category: str
    content: str
    source: Optional[str] = None


class DiagnosisOut(BaseModel):
    """拍照辨病结果"""
    image_url: str = ""
    ai: dict = {}
    matched_diseases: list[DiseaseBrief] = []
    hint: str = ""
