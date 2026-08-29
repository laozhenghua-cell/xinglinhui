#!/usr/bin/env python3
"""构建"统一共用知识总库"(kb_* 表)。

数据源:
  1. PG 疮疡(surgery_*):方剂/病种/证型/医案(含专家医案)/要诀/名家经验,并
     从 surgery_formulas.composition 提取去重中药名 → kb_herbs。
  2. PG 痔漏(anorectal_*/syndrome_rules/safety_rules/prevention_guides/medical_cases)。
  3. 本地 JSON:kb-data/pediatrics.json、kb-data/alchemy.json。

幂等:按 (module, origin_id) 做 upsert(PG ON CONFLICT),可重复执行;
每类输出源行数与写入行数,末尾输出各表对账计数。

用法:
    cd platform/backend
    DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db" python scripts/migrate_kb.py

默认复用 app 的 settings.DATABASE_URL(读 .env / 环境变量)。
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import uuid
from datetime import date, datetime, timezone
from pathlib import Path

# 让 `app` 包可被导入(脚本可能以 `python scripts/migrate_kb.py` 方式运行)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import func, select  # noqa: E402
from sqlalchemy.dialects.postgresql import insert as pg_insert  # noqa: E402

from app.database import AsyncSessionLocal, Base, engine  # noqa: E402
import app.models.kb  # noqa: E402,F401  注册 kb_* 表
import app.models.knowledge  # noqa: E402,F401
import app.models.diagnosis  # noqa: E402,F401
import app.models.medical_case  # noqa: E402,F401
import app.models.surgery  # noqa: E402,F401
from app.models.kb import (  # noqa: E402
    KBCase, KBDisease, KBDulong, KBFormula, KBHerb, KBSyndrome, KBTerm, KBTip,
)
from app.models.knowledge import (  # noqa: E402
    AnorectalCase, AnorectalFormula, AnorectalHerb, PreventionGuide,
)
from app.models.diagnosis import SafetyRule, SyndromeRule  # noqa: E402
from app.models.medical_case import MedicalCase  # noqa: E402
from app.models.surgery import (  # noqa: E402
    SurgeryCase, SurgeryClinicalTip, SurgeryDisease, SurgeryExpertCase,
    SurgeryExpertExperience, SurgeryFormula, SurgerySyndrome,
)

BACKEND_DIR = Path(__file__).resolve().parent.parent
KB_DATA_DIR = Path(
    os.environ.get("KB_DATA_DIR", str(BACKEND_DIR.parent.parent / "kb-data"))
)

_COMP_RE = re.compile(r"[、，,；;]")


# --------------------------------------------------------------------------- #
# 工具函数
# --------------------------------------------------------------------------- #
def split_composition(text) -> list[dict]:
    """把组成文本按中文顿号/逗号切分为 [{name, dose:''}]。"""
    if not text:
        return []
    return [{"name": p.strip(), "dose": ""} for p in _COMP_RE.split(text) if p.strip()]


def _stringify(value):
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def _surgery_patient_info(name, gender, age):
    parts = []
    if name:
        parts.append(str(name))
    if gender:
        parts.append(str(gender))
    if age is not None:
        parts.append(f"{age}岁")
    return "，".join(parts) or None


def _mc_patient_info(pi):
    if not pi:
        return None
    if isinstance(pi, dict):
        parts = []
        if pi.get("gender"):
            parts.append(str(pi["gender"]))
        if pi.get("age"):
            parts.append(f"{pi['age']}岁")
        cc = pi.get("chief_complaint")
        if cc:
            parts.append(str(cc))
        if parts:
            return "，".join(parts)
        return json.dumps(pi, ensure_ascii=False)
    return str(pi)


def _complete_row(model, row: dict) -> dict:
    """补齐所有表列(保证多行 VALUES 键一致),并补 id / created_at。"""
    out: dict = {}
    for col in model.__table__.columns:
        if col.name in row:
            out[col.name] = row[col.name]
        elif col.name == "id":
            out[col.name] = uuid.uuid4()
        elif col.name == "created_at":
            out[col.name] = datetime.now(timezone.utc)
        elif col.name == "is_dangerous":
            out[col.name] = False
        elif col.name == "n":
            out[col.name] = 0
        else:
            out[col.name] = None
    return out


async def upsert_rows(session, model, rows: list[dict]) -> int:
    """按 (module, origin_id) 幂等 upsert,返回写入行数。"""
    if not rows:
        return 0
    completed = [_complete_row(model, r) for r in rows]
    table = model.__table__
    key_cols = [model.module, model.origin_id]
    update_cols = [
        c.name
        for c in table.columns
        if c.name not in ("id", "module", "origin_id", "created_at")
    ]
    stmt = pg_insert(model).values(completed)
    stmt = stmt.on_conflict_do_update(
        index_elements=key_cols,
        set_={c: getattr(stmt.excluded, c) for c in update_cols},
    )
    await session.execute(stmt)
    return len(completed)


# --------------------------------------------------------------------------- #
# 各数据源 → 行字典
# --------------------------------------------------------------------------- #
async def rows_surgery_formulas(session) -> list[dict]:
    objs = (await session.execute(select(SurgeryFormula))).scalars().all()
    return [
        {
            "module": "surgery", "origin_id": f"sf-{o.id}",
            "name": o.name, "aliases": [], "source": o.source,
            "category": o.usage_type, "composition": split_composition(o.composition),
            "function": o.function, "indication": o.indication, "usage": o.usage,
            "method": o.method, "formula_type": o.usage_type,
            "contraindications": o.contraindications,
            "modifications": o.modifications, "preparation": o.preparation,
            "toxicity": o.toxicity,
            "extra": {"dosage": o.dosage, "domain": o.domain},
        }
        for o in objs
    ]


async def rows_surgery_diseases(session) -> list[dict]:
    objs = (await session.execute(select(SurgeryDisease))).scalars().all()
    return [
        {
            "module": "surgery", "origin_id": f"sd-{o.id}",
            "name": o.name, "aliases": o.aliases or [], "category": o.category,
            "location": o.location, "morphology": o.morphology,
            "characteristics": o.characteristics, "differential": o.differential,
            "prognosis": o.prognosis, "western_equiv": o.western_equiv,
            "source": o.source, "is_dangerous": bool(o.is_dangerous),
            "extra": {"is_sores": o.is_sores, "is_yang": o.is_yang,
                      "differentiation": o.differentiation},
        }
        for o in objs
    ]


async def rows_surgery_syndromes(session) -> list[dict]:
    objs = (await session.execute(select(SurgerySyndrome))).scalars().all()
    return [
        {
            "module": "surgery", "origin_id": f"ss-{o.id}",
            "name": o.name, "aliases": [], "yin_yang": o.yin_yang, "stage": o.stage,
            "local_signs": o.local_signs, "systemic_signs": o.systemic_signs,
            "tongue_pulse": o.tongue_pulse, "summary": None, "extra": {},
        }
        for o in objs
    ]


async def rows_surgery_cases(session) -> list[dict]:
    cases = (await session.execute(select(SurgeryCase))).scalars().all()
    diseases = {d.id: d.name for d in (await session.execute(select(SurgeryDisease))).scalars().all()}
    syndromes = {s.id: s.name for s in (await session.execute(select(SurgerySyndrome))).scalars().all()}
    rows = []
    for o in cases:
        rows.append({
            "module": "surgery", "origin_id": f"sc-{o.id}",
            "title": o.patient_name or f"疮疡医案{o.id}",
            "disease": diseases.get(o.disease_id), "syndrome": o.syndrome or syndromes.get(o.syndrome_id),
            "patient_info": _surgery_patient_info(o.patient_name, o.gender, o.age),
            "chief_complaint": o.chief_complaint, "history": o.history,
            "treatment": o.treatment, "effect": o.effect,
            "source": o.source or "临床", "expert_name": None,
            "category": o.domain or o.source,
            "extra": {"patient_name": o.patient_name, "gender": o.gender, "age": o.age,
                      "stage": o.stage, "domain": o.domain,
                      "disease_id": o.disease_id, "syndrome_id": o.syndrome_id},
        })
    return rows


async def rows_surgery_expert_cases(session) -> list[dict]:
    objs = (await session.execute(select(SurgeryExpertCase))).scalars().all()
    return [
        {
            "module": "surgery", "origin_id": f"sec-{o.id}",
            "title": o.diagnosis or o.category or f"名家医案{o.id}",
            "disease": o.diagnosis, "syndrome": o.syndrome, "patient_info": None,
            "chief_complaint": None, "history": o.history, "treatment": o.treatment,
            "effect": o.effect, "source": o.domain, "expert_name": o.expert_name,
            "category": o.category, "extra": {"domain": o.domain},
        }
        for o in objs
    ]


async def rows_surgery_clinical_tips(session) -> list[dict]:
    objs = (await session.execute(select(SurgeryClinicalTip))).scalars().all()
    return [
        {"module": "surgery", "origin_id": f"st-{o.id}", "category": o.category,
         "content": o.content, "source": o.source, "extra": {}}
        for o in objs
    ]


async def rows_surgery_expert_experiences(session) -> list[dict]:
    objs = (await session.execute(select(SurgeryExpertExperience))).scalars().all()
    return [
        {
            "module": "surgery", "origin_id": f"see-{o.id}", "category": "名家经验",
            "content": "；".join(filter(None, [o.syndrome_points, o.internal_treatment, o.external_treatment])),
            "source": o.source or o.expert_name,
            "extra": {"expert_name": o.expert_name, "category": o.category, "domain": o.domain},
        }
        for o in objs
    ]


def rows_surgery_herbs(formula_rows: list[dict]) -> list[dict]:
    """从手术方剂组成提取去重中药名 → kb_herbs。"""
    names: set[str] = set()
    for row in formula_rows:
        for comp in row.get("composition") or []:
            if isinstance(comp, dict) and comp.get("name"):
                names.add(str(comp["name"]).strip())
    return [
        {"module": "surgery", "origin_id": f"herb-{name}", "name": name,
         "pinyin": None, "aliases": [], "category": None, "properties": None,
         "meridians": [], "effects": None, "indications": None,
         "contraindications": None, "dosage": None, "usage_notes": None,
         "extra": {"source": "方剂组成提取"}}
        for name in sorted(names)
    ]


def _anorectal_composition(comp):
    if isinstance(comp, list) and all(
        isinstance(c, dict) and c.get("name") for c in comp
    ):
        return comp, {}
    return [], {"composition_raw": comp}


async def rows_anorectal_formulas(session) -> list[dict]:
    objs = (await session.execute(select(AnorectalFormula))).scalars().all()
    rows = []
    for o in objs:
        comp, comp_extra = _anorectal_composition(o.composition)
        extra = {"disease_types": o.disease_types, "notes": o.notes,
                 "syndrome_type": o.syndrome_type}
        extra.update(comp_extra)
        rows.append({
            "module": "anorectal", "origin_id": f"af-{o.id}",
            "name": o.name, "aliases": [], "source": o.source,
            "category": o.syndrome_type, "composition": comp,
            "function": o.function, "indication": o.indications, "usage": o.usage,
            "method": None, "formula_type": o.formula_type,
            "contraindications": None, "modifications": o.modifications,
            "preparation": None, "toxicity": None, "extra": extra,
        })
    return rows


async def rows_anorectal_herbs(session) -> list[dict]:
    objs = (await session.execute(select(AnorectalHerb))).scalars().all()
    return [
        {
            "module": "anorectal", "origin_id": f"ah-{o.id}",
            "name": o.name, "pinyin": o.pinyin, "aliases": [], "category": o.category,
            "properties": o.properties, "meridians": o.meridians or [],
            "effects": o.effects, "indications": o.indications,
            "contraindications": o.contraindications, "dosage": o.dosage,
            "usage_notes": o.usage_notes, "extra": {"is_common": o.is_common},
        }
        for o in objs
    ]


async def rows_anorectal_cases(session) -> list[dict]:
    objs = (await session.execute(select(AnorectalCase))).scalars().all()
    rows = []
    for o in objs:
        treatment = "；".join(filter(None, [o.formula, o.treatment_process]))
        extra = {"tongue_pulse": o.tongue_pulse, "treatment_principle": o.treatment_principle,
                 "formula": o.formula, "treatment_process": o.treatment_process,
                 "follow_up": o.follow_up, "key_points": o.key_points, "symptoms": o.symptoms}
        rows.append({
            "module": "anorectal", "origin_id": f"ac-{o.id}",
            "title": o.title, "disease": o.disease_type, "syndrome": o.syndrome,
            "patient_info": o.patient_info, "chief_complaint": o.chief_complaint,
            "history": o.symptoms, "treatment": treatment, "effect": o.outcome,
            "source": o.source, "expert_name": None, "category": o.disease_type,
            "extra": extra,
        })
    return rows


async def rows_medical_cases(session) -> list[dict]:
    objs = (await session.execute(select(MedicalCase))).scalars().all()
    rows = []
    for o in objs:
        chief = o.patient_info.get("chief_complaint") if isinstance(o.patient_info, dict) else None
        treatment = "；".join(filter(None, [
            o.treatment_principle, _stringify(o.internal_formula),
            _stringify(o.external_treatment), o.other_treatments,
        ]))
        extra = {"case_number": o.case_number, "case_date": _stringify(o.case_date),
                 "inspection": o.inspection, "auscultation": o.auscultation,
                 "inquiry": o.inquiry, "palpation": o.palpation,
                 "syndrome_analysis": o.syndrome_analysis, "internal_formula": o.internal_formula,
                 "external_treatment": o.external_treatment, "other_treatments": o.other_treatments,
                 "follow_ups": o.follow_ups, "outcome_notes": o.outcome_notes,
                 "key_points": o.key_points, "teaching_notes": o.teaching_notes,
                 "tags": o.tags, "is_classic": o.is_classic,
                 "difficulty_level": o.difficulty_level}
        rows.append({
            "module": "anorectal", "origin_id": f"mc-{o.id}",
            "title": o.case_title, "disease": o.disease_type, "syndrome": o.syndrome_type,
            "patient_info": _mc_patient_info(o.patient_info), "chief_complaint": chief,
            "history": o.syndrome_analysis, "treatment": treatment, "effect": o.outcome,
            "source": o.source, "expert_name": None, "category": o.disease_type,
            "extra": extra,
        })
    return rows


async def rows_syndrome_rules(session) -> list[dict]:
    objs = (await session.execute(select(SyndromeRule))).scalars().all()
    rows = []
    for o in objs:
        extra = {"disease_type": o.disease_type, "syndrome_code": o.syndrome_code,
                 "required_symptoms": o.required_symptoms, "optional_symptoms": o.optional_symptoms,
                 "recommended_formulas": o.recommended_formulas,
                 "confidence_threshold": o.confidence_threshold,
                 "modification_rules": o.modification_rules, "priority": o.priority,
                 "is_active": o.is_active}
        rows.append({
            "module": "anorectal", "origin_id": f"sr-{o.id}",
            "name": o.syndrome_name, "aliases": [], "yin_yang": None, "stage": None,
            "local_signs": None, "systemic_signs": None,
            "tongue_pulse": _stringify(o.tongue_pulse), "summary": o.treatment_principle,
            "extra": extra,
        })
    return rows


async def rows_safety_rules(session) -> list[dict]:
    objs = (await session.execute(select(SafetyRule))).scalars().all()
    return [
        {
            "module": "anorectal", "origin_id": f"safety-{o.id}",
            "category": o.rule_type, "content": o.warning_message, "source": None,
            "extra": {"rule_type": o.rule_type, "severity": o.severity, "herb_name": o.herb_name,
                      "conflicting_herbs": o.conflicting_herbs,
                      "contraindication_info": o.contraindication_info,
                      "max_dosage": o.max_dosage, "suggestion": o.suggestion,
                      "is_active": o.is_active},
        }
        for o in objs
    ]


async def rows_prevention_guides(session) -> list[dict]:
    objs = (await session.execute(select(PreventionGuide))).scalars().all()
    return [
        {
            "module": "anorectal", "origin_id": f"pg-{o.id}",
            "category": "预防调护", "content": o.title, "source": None,
            "extra": {"disease_type": o.disease_type, "prevention_points": o.prevention_points,
                      "dietary_advice": o.dietary_advice, "lifestyle_advice": o.lifestyle_advice,
                      "exercise_advice": o.exercise_advice, "postop_care": o.postop_care,
                      "acupuncture_points": o.acupuncture_points,
                      "sitz_bath_formula": o.sitz_bath_formula,
                      "warning_signs": o.warning_signs},
        }
        for o in objs
    ]


async def rows_anorectal_diseases(session) -> list[dict]:
    formulas = (await session.execute(select(AnorectalFormula))).scalars().all()
    cases = (await session.execute(select(AnorectalCase))).scalars().all()
    names: set[str] = set()
    for f in formulas:
        for d in f.disease_types or []:
            d = str(d).strip()
            if d:
                names.add(d)
    for c in cases:
        if c.disease_type and c.disease_type.strip():
            names.add(c.disease_type.strip())
    return [
        {"module": "anorectal", "origin_id": f"ad-{name}", "name": name,
         "aliases": [], "category": "肛肠", "location": None, "morphology": None,
         "characteristics": None, "differential": None, "prognosis": None,
         "western_equiv": None, "source": None, "is_dangerous": False,
         "extra": {"source": "从方剂/医案提取"}}
        for name in sorted(names)
    ]


# --------------------------------------------------------------------------- #
# JSON 导入
# --------------------------------------------------------------------------- #
def rows_json_formulas(items) -> list[dict]:
    return [
        {"module": f.get("module"), "origin_id": f.get("origin_id"),
         "name": f.get("name"), "aliases": f.get("aliases") or [],
         "source": f.get("source"), "category": f.get("category"),
         "composition": f.get("composition") or [], "function": f.get("function"),
         "indication": f.get("indication"), "usage": f.get("usage"),
         "method": f.get("method"), "formula_type": f.get("formula_type"),
         "contraindications": f.get("contraindications"),
         "modifications": f.get("modifications"), "preparation": f.get("preparation"),
         "toxicity": f.get("toxicity"), "extra": f.get("extra") or {}}
        for f in items
    ]


def rows_json_herbs(items) -> list[dict]:
    return [
        {"module": f.get("module"), "origin_id": f.get("origin_id"),
         "name": f.get("name"), "pinyin": f.get("pinyin"),
         "aliases": f.get("aliases") or [], "category": f.get("category"),
         "properties": f.get("properties"), "meridians": f.get("meridians") or [],
         "effects": f.get("effects"), "indications": f.get("indications"),
         "contraindications": f.get("contraindications"), "dosage": f.get("dosage"),
         "usage_notes": f.get("usage_notes"), "extra": f.get("extra") or {}}
        for f in items
    ]


def rows_json_diseases(items) -> list[dict]:
    return [
        {"module": f.get("module"), "origin_id": f.get("origin_id"),
         "name": f.get("name"), "aliases": f.get("aliases") or [],
         "category": f.get("category"), "location": f.get("location"),
         "morphology": f.get("morphology"), "characteristics": f.get("characteristics"),
         "differential": f.get("differential"), "prognosis": f.get("prognosis"),
         "western_equiv": f.get("western_equiv"), "source": f.get("source"),
         "is_dangerous": bool(f.get("is_dangerous")),
         "extra": f.get("extra") or {}}
        for f in items
    ]


def rows_json_syndromes(items) -> list[dict]:
    return [
        {"module": f.get("module"), "origin_id": f.get("origin_id"),
         "name": f.get("name"), "aliases": f.get("aliases") or [],
         "yin_yang": f.get("yin_yang"), "stage": f.get("stage"),
         "local_signs": f.get("local_signs"), "systemic_signs": f.get("systemic_signs"),
         "tongue_pulse": f.get("tongue_pulse"), "summary": f.get("summary"),
         "extra": f.get("extra") or {}}
        for f in items
    ]


def rows_json_cases(items) -> list[dict]:
    return [
        {"module": f.get("module"), "origin_id": f.get("origin_id"),
         "title": f.get("title"), "disease": f.get("disease"),
         "syndrome": f.get("syndrome"), "patient_info": f.get("patient_info"),
         "chief_complaint": f.get("chief_complaint"), "history": f.get("history"),
         "treatment": f.get("treatment"), "effect": f.get("effect"),
         "source": f.get("source"), "expert_name": f.get("expert_name"),
         "category": f.get("category"), "extra": f.get("extra") or {}}
        for f in items
    ]


def rows_json_tips(items) -> list[dict]:
    return [
        {"module": f.get("module"), "origin_id": f.get("origin_id") or f"tip-{idx}",
         "category": f.get("category"), "content": f.get("content") or "",
         "source": f.get("source"), "extra": f.get("extra") or {}}
        for idx, f in enumerate(items)
    ]


def rows_json_terms(items) -> list[dict]:
    return [
        {"module": f.get("module"), "origin_id": f.get("origin_id") or f"term-{idx}",
         "term": f.get("term"), "definition": f.get("definition"),
         "source": f.get("source"), "extra": f.get("extra") or {}}
        for idx, f in enumerate(items)
    ]


def rows_json_dulong(items) -> list[dict]:
    return [
        {"module": f.get("module"),
         "origin_id": f.get("origin_id") or f"dulong-{f.get('section')}-{f.get('n')}",
         "section": f.get("section"), "n": int(f.get("n") or 0),
         "disease": f.get("disease"), "guide": f.get("guide")}
        for f in items
    ]


# --------------------------------------------------------------------------- #
# 主流程
# --------------------------------------------------------------------------- #
async def main() -> None:
    if not KB_DATA_DIR.exists():
        print(f"错误: kb-data 目录不存在: {KB_DATA_DIR}", file=sys.stderr)
        sys.exit(1)

    # 1) 建 kb_* 表(幂等,复用 ORM 定义)
    kb_tables = [Base.metadata.tables[n] for n in Base.metadata.tables if n.startswith("kb_")]
    async with engine.begin() as conn:
        await conn.run_sync(lambda c: Base.metadata.create_all(c, tables=kb_tables))

    peds = json.loads((KB_DATA_DIR / "pediatrics.json").read_text(encoding="utf-8"))
    alch = json.loads((KB_DATA_DIR / "alchemy.json").read_text(encoding="utf-8"))

    # 2) 读取并组装各源
    async with AsyncSessionLocal() as session:
        surgery_formula_rows = await rows_surgery_formulas(session)
        steps: list[tuple[str, object, list[dict]]] = [
            ("surgery_formulas→kb_formulas", KBFormula, surgery_formula_rows),
            ("surgery_diseases→kb_diseases", KBDisease, await rows_surgery_diseases(session)),
            ("surgery_syndromes→kb_syndromes", KBSyndrome, await rows_surgery_syndromes(session)),
            ("surgery_cases→kb_cases", KBCase, await rows_surgery_cases(session)),
            ("surgery_expert_cases→kb_cases", KBCase, await rows_surgery_expert_cases(session)),
            ("surgery_clinical_tips→kb_tips", KBTip, await rows_surgery_clinical_tips(session)),
            ("surgery_expert_experiences→kb_tips(名家经验)", KBTip, await rows_surgery_expert_experiences(session)),
            ("surgery_formulas组成提取→kb_herbs", KBHerb, rows_surgery_herbs(surgery_formula_rows)),
            ("anorectal_formulas→kb_formulas", KBFormula, await rows_anorectal_formulas(session)),
            ("anorectal_herbs→kb_herbs", KBHerb, await rows_anorectal_herbs(session)),
            ("anorectal_cases→kb_cases", KBCase, await rows_anorectal_cases(session)),
            ("medical_cases→kb_cases", KBCase, await rows_medical_cases(session)),
            ("syndrome_rules→kb_syndromes", KBSyndrome, await rows_syndrome_rules(session)),
            ("safety_rules→kb_tips", KBTip, await rows_safety_rules(session)),
            ("prevention_guides→kb_tips", KBTip, await rows_prevention_guides(session)),
            ("anorectal方剂/医案病种提取→kb_diseases", KBDisease, await rows_anorectal_diseases(session)),
            ("pediatrics.json formulas", KBFormula, rows_json_formulas(peds.get("formulas", []))),
            ("pediatrics.json herbs", KBHerb, rows_json_herbs(peds.get("herbs", []))),
            ("pediatrics.json diseases", KBDisease, rows_json_diseases(peds.get("diseases", []))),
            ("pediatrics.json syndromes", KBSyndrome, rows_json_syndromes(peds.get("syndromes", []))),
            ("pediatrics.json cases", KBCase, rows_json_cases(peds.get("cases", []))),
            ("pediatrics.json tips", KBTip, rows_json_tips(peds.get("tips", []))),
            ("alchemy.json formulas", KBFormula, rows_json_formulas(alch.get("formulas", []))),
            ("alchemy.json herbs", KBHerb, rows_json_herbs(alch.get("herbs", []))),
            ("alchemy.json diseases", KBDisease, rows_json_diseases(alch.get("diseases", []))),
            ("alchemy.json syndromes", KBSyndrome, rows_json_syndromes(alch.get("syndromes", []))),
            ("alchemy.json cases", KBCase, rows_json_cases(alch.get("cases", []))),
            ("alchemy.json tips", KBTip, rows_json_tips(alch.get("tips", []))),
            ("alchemy.json terms", KBTerm, rows_json_terms(alch.get("terms", []))),
            ("alchemy.json dulong", KBDulong, rows_json_dulong(alch.get("dulong", []))),
        ]

        for label, model, rows in steps:
            written = await upsert_rows(session, model, rows)
            print(f"{label}: 源{len(rows)}行 -> 写入{written}行")
        await session.commit()

    # 3) 对账
    async with AsyncSessionLocal() as session:
        print("\n=== 对账(表内最终计数) ===")
        total_all = 0
        for type_name, model in {
            "kb_formulas": KBFormula, "kb_herbs": KBHerb, "kb_diseases": KBDisease,
            "kb_syndromes": KBSyndrome, "kb_cases": KBCase, "kb_tips": KBTip,
            "kb_terms": KBTerm, "kb_dulong": KBDulong,
        }.items():
            total = (await session.execute(select(func.count()).select_from(model))).scalar() or 0
            by_module = dict(
                (await session.execute(select(model.module, func.count()).group_by(model.module))).all()
            )
            total_all += total
            detail = " ".join(f"{m}={c}" for m, c in sorted(by_module.items()))
            print(f"{type_name}: total={total}  {detail}")
        print(f"总计: {total_all} 行")
    await engine.dispose()
    print("迁移完成。")


if __name__ == "__main__":
    asyncio.run(main())
