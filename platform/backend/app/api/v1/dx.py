"""统一辨证中心(跨专科,基于知识总库 kb_*)。

POST /api/v1/dx/analyze:症状/四诊 → 证型/病种打分匹配 → 方剂推荐(分专科) → 关联内容 → AI 综合报告 → 存记录。
GET  /api/v1/dx/records:本设备(IP+UA 哈希)近期辨证记录。
GET  /api/v1/dx/records/{id}:单条记录。
GET  /api/v1/dx/quick?q=:症状/病证名快速联想。
"""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import Text, func, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.dx import DxRecord, DxTongueReading
from app.models.kb import (
    KBCase,
    KBDisease,
    KBDulong,
    KBFormula,
    KBSyndrome,
    KBTip,
)

router = APIRouter(prefix="/dx", tags=["统一辨证中心"])

MODULES = {"anorectal", "surgery", "pediatrics", "alchemy"}

_PEDS_DX: Optional[dict] = None


def _load_peds_dx() -> dict:
    """加载《程氏家传儿科秘要》原版辨证引擎数据(望手纹→八症→主方,150 项体征+8 症规则)。"""
    global _PEDS_DX
    if _PEDS_DX is None:
        from pathlib import Path as _Path

        _p = _Path(__file__).resolve().parent.parent.parent / "data" / "pediatrics-dx.json"
        _PEDS_DX = json.loads(_p.read_text(encoding="utf-8"))
    return _PEDS_DX


def _real_ip(request: Request) -> str:
    """nginx 反代下 client.host 恒为网关地址;真实客户端 IP 取自 nginx 覆盖注入的 X-Real-IP。"""
    return (request.headers.get("x-real-ip") or "").strip() or (
        request.client.host if request.client else "unknown"
    )

def _hash_ip(client_ip: str) -> str:
    salt = settings.visit_salt
    return hashlib.sha256(f"{salt}:{client_ip}".encode("utf-8")).hexdigest()


def _hash_ua(user_agent: str) -> str:
    salt = settings.visit_salt
    return hashlib.sha256(f"{salt}:ua:{user_agent or ''}".encode("utf-8")).hexdigest()


def _device_hashes(request: Request) -> tuple[str, str]:
    ip = _real_ip(request)
    ua = request.headers.get("user-agent", "") or ""
    return _hash_ip(ip), _hash_ua(ua)


# ---------------- 打分工具 ----------------


def _bigrams(text: str, cap: int = 60) -> list[str]:
    """中文按 2 字滑窗切词,做模糊匹配关键词。"""
    text = (text or "").strip()
    if not text:
        return []
    grams = [text[i : i + 2] for i in range(len(text) - 1)]
    seen, out = set(), []
    for g in grams:
        if g not in seen:
            seen.add(g)
            out.append(g)
        if len(out) >= cap:
            break
    return out


def _hit(text: Any, keywords: list[str]) -> tuple[int, list[str]]:
    """在文本中统计关键词命中次数,返回 (分数, 命中词)。"""
    if not text or not isinstance(text, str):
        return 0, []
    hits = [k for k in keywords if k and k in text]
    return len(hits), hits


def _json_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _collect_keywords(body: "AnalyzeIn") -> list[str]:
    kw: list[str] = [s for s in (body.symptoms or []) if s]
    for s in (body.tongue, body.pulse, body.local, body.systemic):
        if s and s.strip():
            kw.append(s.strip())
    kw.extend(_bigrams(body.detail))
    seen, out = set(), []
    for k in kw:
        if k and k not in seen:
            seen.add(k)
            out.append(k)
    return out


_SYMPTOM_DICT_LABELS: Optional[list[tuple[str, str, str]]] = None  # (name, display_name, description)


async def _expanded_keywords(keywords: list[str], db: AsyncSession) -> list[str]:
    """用症状字典把用户词翻译为结构化症状键(肛肠证型 extra 里的英文键)。

    例如用户输入"肛门疼痛"→ 命中字典行 display_name,加入该行 name(pain)与中文词。
    缓存全局,避免每次请求都查库。
    """
    global _SYMPTOM_DICT_LABELS
    if _SYMPTOM_DICT_LABELS is None:
        try:
            from app.models.diagnosis import SymptomDictionary

            rows = (await db.execute(select(SymptomDictionary))).scalars().all()
            _SYMPTOM_DICT_LABELS = [
                (r.name or "", r.display_name or "", r.description or "") for r in rows
            ]
        except Exception:
            _SYMPTOM_DICT_LABELS = []
    out = list(keywords)
    grams = [g for k in keywords for g in _bigrams(k, cap=8)] + [k for k in keywords]
    for name, display, desc in _SYMPTOM_DICT_LABELS:
        text = f"{display} {desc}"
        if not text.strip():
            continue
        if any(g and g in text for g in grams):
            if name and name not in out:
                out.append(name)
            if display and display not in out:
                out.append(display)
    return out


def _syndrome_score(s: KBSyndrome, keywords: list[str]) -> tuple[int, list[str]]:
    score, hits = 0, []
    w, h = _hit(s.name, keywords)
    score += w * 3
    hits += h
    aliases = s.aliases or []
    if isinstance(aliases, list):
        for a in aliases:
            w2, h2 = _hit(str(a), keywords)
            score += w2 * 3
            hits += h2
    for field, weight in (
        ("tongue_pulse", 2), ("summary", 1), ("local_signs", 1), ("systemic_signs", 1),
    ):
        w3, h3 = _hit(getattr(s, field, None), keywords)
        score += w3 * weight
        hits += h3
    extra = s.extra or {}
    for key in ("required_symptoms", "optional_symptoms", "required", "symptoms"):
        w4, h4 = _hit(_json_text(extra.get(key)), keywords)
        score += w4
        hits += h4
    return score, list(dict.fromkeys(hits))


def _disease_score(d: KBDisease, keywords: list[str]) -> tuple[int, list[str]]:
    score, hits = 0, []
    w, h = _hit(d.name, keywords)
    score += w * 3
    hits += h
    aliases = d.aliases or []
    if isinstance(aliases, list):
        for a in aliases:
            w2, h2 = _hit(str(a), keywords)
            score += w2 * 3
            hits += h2
    for field, weight in (("characteristics", 1), ("differential", 1), ("location", 1)):
        w3, h3 = _hit(getattr(d, field, None), keywords)
        score += w3 * weight
        hits += h3
    return score, list(dict.fromkeys(hits))


_DICT_CACHE: Optional[dict] = None


async def _load_symptom_dict(db: AsyncSession) -> dict:
    """症状字典 → 中文词映射(键/值),缓存。"""
    global _DICT_CACHE
    if _DICT_CACHE is None:
        from app.models.diagnosis import SymptomDictionary

        rows = (await db.execute(select(SymptomDictionary))).scalars().all()
        direct: dict[str, tuple] = {}   # 中文词 → (key, value)
        for r in rows:
            if r.display_name:
                direct[r.display_name] = (r.name, True)
            opts = r.options or {}
            if isinstance(opts, dict):
                if opts.get("type") == "select":
                    for c in opts.get("choices") or []:
                        direct.setdefault(str(c), (r.name, str(c)))
                fields = opts.get("fields") or {}
                if isinstance(fields, dict):
                    for fname, fcfg in fields.items():
                        if isinstance(fcfg, dict):
                            for c in fcfg.get("choices") or []:
                                direct.setdefault(str(c), (r.name, {fname: str(c), "present": True}))
        _DICT_CACHE = direct
    return _DICT_CACHE


def _match_value(selected_value: Any, required_value: Any) -> bool:
    """仿痔漏原版 _match_symptom 的语义(布尔/列表/字典)。"""
    if required_value is True or required_value is False:
        return bool(selected_value) is required_value
    if isinstance(required_value, list):
        if isinstance(selected_value, list):
            return any(x in required_value for x in selected_value)
        return selected_value in required_value
    if isinstance(required_value, dict):
        if not isinstance(selected_value, dict):
            return False
        return all(selected_value.get(k) == v for k, v in required_value.items())
    if isinstance(selected_value, list):
        return required_value in selected_value
    return selected_value == required_value


async def _anorectal_structured_dx(user_labels: list[str], db: AsyncSession) -> Optional[dict]:
    """痔漏按原版结构化辨证:症状字典逐项核验→置信度+证据链→治则/原文。"""
    from app.models.diagnosis import SyndromeRule

    mapping = await _load_symptom_dict(db)
    selected: dict[str, Any] = {}
    for lab in user_labels:
        hit = mapping.get(lab)
        if hit:
            key, value = hit
            cur = selected.get(key)
            if isinstance(value, dict):
                if isinstance(cur, dict):
                    cur.update(value)
                else:
                    selected[key] = value
            else:
                selected[key] = value
        # 前缀启发:脉X/舌X/苔X
        if lab.startswith("脉"):
            k = mapping.get(lab[1:] + "脉")
            if k:
                selected[k[0]] = True
        elif lab.startswith("舌") and len(lab) >= 2:
            k = mapping.get(lab[1:])
            if k and k[0] == "tongue_color":
                selected.setdefault("tongue_color", k[1])
        elif lab.startswith("苔") and len(lab) >= 2:
            k = mapping.get(lab[1:])
            if k and k[0] == "tongue_coating":
                selected.setdefault("tongue_coating", k[1])
    if not selected:
        return None

    rules = (
        await db.execute(select(SyndromeRule).where(SyndromeRule.is_active == 1))
    ).scalars().all()
    results = []
    for rule in rules:
        required = rule.required_symptoms or {}
        optional = rule.optional_symptoms or {}
        if not required:
            continue
        req_total = len(required)
        req_hit = sum(1 for k, v in required.items() if _match_value(selected.get(k), v))
        partial = req_hit < req_total
        if partial:
            conf = 0.35 + 0.35 * (req_hit / req_total)
        else:
            conf = 0.7
            if optional:
                opt_hit = sum(1 for k, v in optional.items() if _match_value(selected.get(k), v))
                conf += 0.3 * (opt_hit / len(optional))
            else:
                conf += 0.3
        if conf < 0.3:
            continue
        evidence = []
        for k in list(required.keys()) + list(optional.keys()):
            if k in selected:
                label = next((lab for lab in user_labels if mapping.get(lab) and mapping[lab][0] == k), k)
                evidence.append({"key": k, "label": label})
        try:
            original = await _anorectal_original(rule, selected, db)
        except Exception:
            original = {}
        results.append({
            "id": str(rule.id), "name": rule.syndrome_name, "module": "anorectal",
            "disease_type": rule.disease_type, "confidence": round(conf, 2),
            "hits": [e["label"] for e in evidence], "evidence": evidence,
            "original": {
                "治则": rule.treatment_principle or "",
                "舌脉": _json_text(rule.tongue_pulse),
                "推荐方": [f.get("name") if isinstance(f, dict) else (str(f) if f else "") for f in (rule.recommended_formulas or []) if isinstance(f, (dict, str))],
                "原文依据": original.get("original_basis") or "",
            },
        })
    results.sort(key=lambda x: -x["confidence"])
    if not results:
        return None
    return {"syndromes": results[:4], "selected": selected}


async def _anorectal_original(rule, selected: dict, db: AsyncSession) -> dict:
    """周氏原文依据(复用原版 build_original_knowledge)。"""
    from app.services.zhou_knowledge import build_original_knowledge

    return build_original_knowledge(
        rule.disease_type,
        {
            "syndrome_code": rule.syndrome_code or "",
            "syndrome_name": rule.syndrome_name,
            "treatment_principle": rule.treatment_principle or "",
        },
        selected,
    )


def _peds_original_dx(user_labels: list[str]) -> dict | None:
    """儿科按原著辨证:体征→八症打分→主方+原文依据。返回 None 表示无匹配。"""
    data = _load_peds_dx()
    label_to_key: dict[str, str] = {}
    for f in data["findings"]:
        label_to_key.setdefault(f["label"], f["key"])
    selected: set[str] = set()
    for lab in user_labels:
        if lab in label_to_key:
            selected.add(label_to_key[lab])
    if not selected:
        return None

    dangers = [d for d in data["dangers"] if d["key"] in selected]
    combos = [c["label"] for c in data["combos"] if len([k for k in c["keys"] if k in selected]) >= c["min"]]

    key_to_label = {f["key"]: f for f in data["findings"]}
    scored = []
    for rule in data["rules"]:
        score = 0
        hits = []
        for feat in rule["features"]:
            if feat["key"] in selected:
                score += feat["w"]
                fd = key_to_label.get(feat["key"])
                if fd:
                    hits.append({"label": fd["label"], "hint": fd["hint"]})
        if score > 0:
            scored.append((rule["id"], score, hits))
    scored.sort(key=lambda x: -x[1])
    if not scored:
        return None
    top_score = scored[0][1]
    top_rules = [x for x in scored if x[1] >= max(2, top_score * 0.45)]

    syn_by_id = {sy["id"]: sy for sy in data["syndromes"]}
    out_syndromes = []
    for rid, score, hits in top_rules[:3]:
        sy = syn_by_id.get(rid)
        if not sy:
            continue
        out_syndromes.append({
            "id": f"peds-{rid}", "name": sy["name"], "module": "pediatrics",
            "score": score, "pct": round(score / max(top_score, 1) * 100),
            "hits": [h["label"] for h in hits],
            "original": {
                "外候": (sy.get("waihou") or {}).get("original", ""),
                "外候白话": (sy.get("waihou") or {}).get("plain", ""),
                "病因": (sy.get("bingyin") or {}).get("original", ""),
                "治法": (sy.get("zhifa") or {}).get("original", ""),
                "主方": (sy.get("fangyao") or {}).get("name", ""),
                "方义用法": (sy.get("fangyao") or {}).get("usage", ""),
                "方组": [(h.get("name") or "") + (h.get("dose") or "") for h in (sy.get("fangyao") or {}).get("herbs", []) or []],
            },
            "evidence": hits,
        })
    if not out_syndromes:
        return None
    # 兼症加减法(原版 jiajianMapping:命中体征+症下加减条件)
    jiajian_out = []
    for rid, _score, _hits in top_rules[:2]:
        sy = syn_by_id.get(rid)
        if not sy:
            continue
        for j in (sy.get("jiajian") or []):
            if any(m_entry for m_entry in data["jiajian"] if m_entry["key"] in selected and any(w in j.get("cond", "") for w in m_entry["match"])):
                jiajian_out.append({"syndrome": sy["name"], "cond": j.get("cond", ""), "add": j.get("add", ""), "note": j.get("note", "")})
    main = out_syndromes[0]
    return {
        "syndromes": out_syndromes,
        "dangers": [{"label": d["label"], "level": d["level"]} for d in dangers],
        "combos": combos,
        "main_formula": {
            "name": main["original"]["主方"],
            "usage": main["original"]["方义用法"],
            "composition": main["original"]["方组"],
        },
        "methods": syn_by_id.get(top_rules[0][0], {}).get("methods", []),
        "jiajian": jiajian_out,
    }


def _formula_score(f: KBFormula, names: list[str], keywords: list[str]) -> int:
    """方剂相关度:证型/病种名匹配 + 用户关键词直接匹配。"""
    s = 0
    terms = [n for n in names if n] + [k for k in keywords if k and len(k) >= 2]
    for n in terms:
        if f.name and n in f.name:
            s += 4
        if f.indication and n in f.indication:
            s += 2
        if f.function and n in f.function:
            s += 1
        extra = f.extra or {}
        if n in _json_text(extra):
            s += 1
    return s


# ---------------- 请求/响应 ----------------


class AnalyzeIn(BaseModel):
    symptoms: list[str] = Field(default_factory=list)
    tongue: str = ""
    pulse: str = ""
    local: str = ""
    systemic: str = ""
    detail: str = ""
    module: Optional[str] = None  # 空=不限;anorectal/surgery/pediatrics/alchemy
    use_ai: bool = False  # 默认走规则引擎辨证(选择症状);显式开启才生成 AI 报告
    time: str = ""  # 发病/加重时辰(morning/forenoon/afternoon/evening/night/dawn/none)
    sick_year: int = 0  # 发病年(五运六气)
    birth_year: int = 0  # 出生年(运气体质)


def _serialize(obj) -> dict:
    data = {}
    for col in obj.__table__.columns:
        v = getattr(obj, col.name)
        if isinstance(v, uuid.UUID):
            v = str(v)
        elif isinstance(v, datetime):
            v = v.isoformat()
        data[col.name] = v
    return data


async def _ai_report(keywords: list[str], ctx: dict) -> Optional[dict]:
    """DeepSeek 综合辨证报告;任何异常返回 None(静默降级)。"""
    if not settings.DEEPSEEK_API_KEY:
        return None
    ctx_text = json.dumps(ctx, ensure_ascii=False)[:3000]
    systems_text = json.dumps(ctx.get("systems", []), ensure_ascii=False)
    consistency_text = json.dumps(ctx.get("consistency", {}), ensure_ascii=False)
    dynamic_text = json.dumps(ctx.get("dynamic", {}), ensure_ascii=False)
    prompt = f"""你是资深中医师。下面是知识总库按"{"、".join(keywords[:12])}"匹配出的候选结果(JSON):
{ctx_text}

规则引擎还给出六体系辨证对照:八纲/六经/卫气营血/脏腑/三焦/经络各自结论:
{systems_text}

六体系交叉印证(一致性评分):{consistency_text}

动态推理(六经合病/并病、卫气营血同病、三焦传变):{dynamic_text}

请严格依据上述候选中的原文辨证:证型、病种、方剂建议必须引用原文依据并注明出处(如"《医宗金鉴》五味消毒饮:疔疮痈疡"),不得自行发挥;原文未覆盖之处明确说明"原书未见"。请在 syndrome_analysis 中综合六体系结论做交叉印证评述:互洽时点明(如"脏腑↔六经↔经络互洽"),存在冲突时说明取舍理由;dynamic 中有合病/传变提示时一并纳入。只返回 JSON(不要其他文字):
{{"syndrome_analysis":"证型分析(含六体系交叉印证评述)","disease_suggestion":"最可能病种及鉴别","formula_suggestion":"推荐方剂(可跨专科参考,注明出处与加减)","precautions":"注意事项与禁忌","confidence":0.7}}"""
    try:
        from app.core.ai_gateway import chat_json

        result = await chat_json(
            "dx-report",
            [
                {"role": "system", "content": "你是严谨的中医辨证助手,只输出 JSON。"},
                {"role": "user", "content": prompt},
            ],
            provider="deepseek",
            timeout=60.0,
            temperature=0.3,
        )
        return result["json"]
    except Exception:
        return None


@router.post("/analyze")
async def dx_analyze(body: AnalyzeIn, request: Request, db: AsyncSession = Depends(get_db)):
    from app.core.surgery_security import limit_ai

    limit_ai(request)
    module = (body.module or "").strip() or None
    if module and module not in MODULES:
        raise HTTPException(status_code=400, detail=f"未知专科: {module}")
    keywords = await _expanded_keywords(_collect_keywords(body), db)

    # 用户原始标签(逗号/顿号切分,供儿科原版辨证引擎精确匹配体征)
    user_labels: list[str] = [x for x in (body.symptoms or []) if x]
    for v in (body.tongue, body.pulse, body.local, body.systemic, body.detail):
        user_labels.extend(x.strip() for x in (v or "").split("、") if x.strip())

    # 0. 儿科:原版辨证引擎(程氏四步采集→八症→主方+原文)
    peds_result = None
    if module == "pediatrics":
        peds_result = _peds_original_dx(user_labels)

    # 0.5 痔漏:原版结构化辨证(症状字典逐项核验→置信度+证据链+周氏原文)
    anorectal_result = None
    if module == "anorectal":
        anorectal_result = await _anorectal_structured_dx(user_labels, db)

    # 0.7 多辨证体系对照(八纲/六经/卫气营血,所有专科通用)
    from app.services.dx_systems import analyze_systems, extract_symptom_terms

    # 白话主诉解析:从长文本抽取标准证候标签并入辨证(患者只写一句话即可;词库取 DB 版,后台可热更新)
    from app.api.v1.admin import _syn_map

    syn_map = await _syn_map(db)
    extra_terms = extract_symptom_terms([body.detail, body.systemic, *user_labels], synonyms=syn_map)
    for t in extra_terms:
        if t not in user_labels:
            user_labels.append(t)

    systems_result = analyze_systems(user_labels, time_key=body.time, sick_year=body.sick_year, birth_year=body.birth_year, detail_text=body.detail or "")

    # 1. 证型匹配
    synd_stmt = select(KBSyndrome)
    if module:
        synd_stmt = synd_stmt.where(KBSyndrome.module == module)
    syndromes = (await db.execute(synd_stmt)).scalars().all()
    synd_matches = sorted(
        ([_syndrome_score(s, keywords), s] for s in syndromes if _syndrome_score(s, keywords)[0] > 0),
        key=lambda x: x[0][0], reverse=True,
    )[:5]

    # 2. 病种匹配
    dis_stmt = select(KBDisease)
    if module:
        dis_stmt = dis_stmt.where(KBDisease.module == module)
    diseases = (await db.execute(dis_stmt)).scalars().all()
    dis_matches = sorted(
        ([_disease_score(d, keywords), d] for d in diseases if _disease_score(d, keywords)[0] > 0),
        key=lambda x: x[0][0], reverse=True,
    )[:5]

    names = [m[1].name for m in synd_matches] + [m[1].name for m in dis_matches]

    # 3. 方剂推荐(按专科分组)
    formulas: dict[str, list[dict]] = {}
    fstmt = select(KBFormula)
    if module:
        fstmt = fstmt.where(KBFormula.module == module)
    fobjs = (await db.execute(fstmt)).scalars().all()
    if names:
        scored = sorted(
            ((_formula_score(f, names, keywords), f) for f in fobjs if _formula_score(f, names, keywords) > 0),
            key=lambda x: x[0], reverse=True,
        )
        for score, f in scored[:40]:
            formulas.setdefault(f.module, []).append({**_serialize(f), "score": score})
        for k in formulas:
            formulas[k] = formulas[k][:8]

    # 4. 关联内容
    related: dict[str, list[dict]] = {"cases": [], "tips": [], "dulong": []}
    if names or keywords:
        for c in (await db.execute(select(KBCase))).scalars().all():
            if any(n and (n in (c.title or "") or n in (c.disease or "") or n in (c.syndrome or "")) for n in names[:6]):
                related["cases"].append(_serialize(c))
        for t in (await db.execute(select(KBTip))).scalars().all():
            if any(n and (n in (t.category or "") or n in (t.content or "")) for n in names[:6]):
                related["tips"].append(_serialize(t))
        for d in (await db.execute(select(KBDulong))).scalars().all():
            if any(k and k in (d.disease or "") for k in keywords[:20]):
                related["dulong"].append(_serialize(d))
    related["cases"] = related["cases"][:5]
    related["tips"] = related["tips"][:5]
    related["dulong"] = related["dulong"][:5]


    peds_main_formula = None
    if anorectal_result and anorectal_result["syndromes"]:
        synd_out = anorectal_result["syndromes"]
        for so in synd_out:
            for fname in so.get("original", {}).get("推荐方", []) or []:
                if fname and not any(x.get("name") == fname for x in formulas.get("anorectal", [])):
                    formulas.setdefault("anorectal", []).append({
                        "id": None, "name": fname, "source": "痔漏辨证规则推荐",
                        "composition": [], "function": so.get("original", {}).get("治则", ""),
                        "indication": so["name"], "module": "anorectal", "score": 90,
                    })
    elif peds_result and peds_result["syndromes"]:
        synd_out = peds_result["syndromes"]
        peds_main_formula = peds_result["main_formula"]
        # 儿科主方直接进推荐
        if peds_main_formula.get("name"):
            formulas.setdefault("pediatrics", []).insert(0, {
                "id": None, "name": peds_main_formula["name"], "source": "《程氏家传儿科秘要》",
                "composition": [{"name": x, "dose": ""} for x in peds_main_formula["composition"]],
                "function": peds_main_formula["usage"], "indication": synd_out[0]["name"],
                "module": "pediatrics", "score": 99,
            })
    else:
        synd_out = [
            {
                "id": str(s.id), "name": s.name, "module": s.module, "score": sc, "hits": ev,
                "original": {
                    "舌脉": s.tongue_pulse or "",
                    "要点": s.summary or s.local_signs or "",
                },
            }
            for (sc, ev), s in synd_matches
        ]

    # 3.5 疮疡分期治法(初起/成脓/溃后 原文)
    if module == "surgery" and dis_matches:
        from app.models.surgery import SurgeryTreatmentRule as _STR, SurgeryFormula as _SF

        dis_ids = [x[1].id for x in dis_matches[:3]]
        old_ids = []
        id_to_old: dict = {}
        for x in dis_matches[:3]:
            oid = getattr(x[1], "origin_id", None)
            if oid is not None:
                m = re.search(r"(\d+)$", str(oid))
                if m:
                    old_ids.append(int(m.group(1)))
                    id_to_old[x[1].id] = int(m.group(1))
        stage_rows = []
        if old_ids:
            stage_rows = (
                await db.execute(select(_STR).where(_STR.disease_id.in_(old_ids)))
            ).scalars().all()
        fid_set = {r.internal_formula_id for r in stage_rows if r.internal_formula_id}
        fname_map = {}
        if fid_set:
            fobjs = (await db.execute(select(_SF).where(_SF.id.in_(fid_set)))).scalars().all()
            fname_map = {f.id: f.name for f in fobjs}
        stages_by_disease: dict[int, dict] = {}
        order = {"初起": 0, "成脓": 1, "溃后": 2, "分型": 3}
        for r in stage_rows:
            # 规则表 disease_id 是旧整数,反查对应 kb 病种 UUID
            target_id = next((k for k, v in id_to_old.items() if v == r.disease_id), None)
            if target_id is None:
                continue
            stages_by_disease.setdefault(target_id, {}).setdefault(r.stage or "分型", []).append({
                "stage": r.stage or "分型",
                "内治": fname_map.get(r.internal_formula_id, ""),
                "外治": r.external_treatment or "",
                "护理": r.nursing or "",
                "注意": r.note or "",
            })
        for dis in dis_matches:
            d = dis[1]
            st = stages_by_disease.get(d.id, {})
            d._stages = [[item for _k, v in sorted(st.items(), key=lambda kv: order.get(kv[0], 9)) for item in v]]
    else:
        for dis in dis_matches:
            dis[1]._stages = []

    dis_out = [
        {
            "id": str(d.id), "name": d.name, "module": d.module, "score": sc, "hits": ev,
            "original": {
                "出处": d.source or "",
                "特点": d.characteristics or "",
                "鉴别": d.differential or "",
                "预后": d.prognosis or "",
            },
            "stages": (getattr(d, "_stages", None) or [[]])[0],
        }
        for (sc, ev), d in dis_matches
    ]

    ai = None
    if body.use_ai:
        system_keys = ("bagang", "liujing", "weiqiyingxue", "zangfu", "sanjiao", "jingluo")
        ctx = {
            "engine": None,
            "syndromes": [
                {k: v for k, v in x.items() if k in ("name", "module", "confidence", "hits", "original")}
                for x in synd_out[:4]
            ],
            "diseases": [
                {k: v for k, v in x.items() if k in ("name", "module", "stages", "original")}
                for x in dis_out[:3]
            ],
            "formulas": {k: [f["name"] for f in v[:3]] for k, v in formulas.items()},
            "peds": None,
            "systems": [
                {"体系": systems_result[k]["name"], "结论": systems_result[k]["summary"], "置信度": systems_result[k]["confidence"]}
                for k in system_keys
            ],
            "consistency": systems_result.get("consistency"),
            "dynamic": systems_result.get("dynamic"),
        }
        ai = await _ai_report(keywords, ctx)

    system_keys = ("bagang", "liujing", "weiqiyingxue", "zangfu", "sanjiao", "jingluo")
    # 开方建议:按六体系 top1 主方查方剂库(按方名幂等合并 seed)
    formula_suggestions = []
    formula_names: list[str] = []
    zf_clear = systems_result["zangfu"].get("summary") != "信息不足"
    lj_clear = systems_result["liujing"].get("summary") != "信息不足"
    for k in system_keys:
        if systems_result[k].get("summary") == "信息不足":
            continue  # 证据不足的体系不参与开方
        top = systems_result[k].get("top") or []
        if not top:
            continue
        if k == "liujing" and zf_clear and not top[0].get("variant"):
            continue  # 脏腑已明确,六经无分型的通用主方不参与(防风热误荐桂枝汤)
        if k == "bagang" and (zf_clear or lj_clear):
            continue  # 八纲通用主方仅在脏腑/六经均无结论时兜底
        if systems_result["zangfu"].get("summary") == "风寒束肺" and k in ("weiqiyingxue", "sanjiao"):
            continue  # 风寒束肺时,温病卫分/肺卫的辛凉方(银翘桑菊)不参与开方
        lj_top = systems_result["liujing"].get("top") or []
        if k in ("weiqiyingxue", "sanjiao") and lj_top and lj_top[0].get("variant"):
            continue  # 六经分型已明确(伤寒/中风/蓄水/蓄血),卫分辛凉方不参与开方
        for fn in top[0].get("formulas") or []:
            if fn and fn not in formula_names:
                formula_names.append(fn)
        if top[0].get("variant"):
            for fn in top[0]["variant"].get("formulas") or []:
                if fn and fn not in formula_names:
                    formula_names.append(fn)
    if formula_names:
        from app.api.v1.kb import _seed_yifang
        from app.models.kb import KbYifang

        await _seed_yifang(db)
        rows = (await db.execute(select(KbYifang).where(KbYifang.name.in_(formula_names)))).scalars().all()
        by_name = {r.name: r for r in rows}
        for fn in formula_names:
            r = by_name.get(fn)
            if r:
                formula_suggestions.append({
                    "id": str(r.id), "name": r.name, "category": r.category,
                    "composition": r.composition or [], "function": r.function,
                    "indications": r.indications, "contraindications": r.contraindications,
                    "source": r.source, "analysis": r.analysis or [],
                })
    result = {
        "syndromes": synd_out,
        "diseases": dis_out,
        "formulas": formulas,
        "related": related,
        "ai": ai,
        "systems": {k: systems_result[k] for k in system_keys},
        "consistency": systems_result.get("consistency"),
        "dynamic": systems_result.get("dynamic"),
        "care": systems_result.get("care", []),
        "danger": systems_result.get("danger", []),
        "followup": systems_result.get("followup"),
        "ask": systems_result.get("ask", []),
        "modifications": systems_result.get("modifications", []),
        "menlei": systems_result.get("menlei", []),
        "prescription": systems_result.get("prescription"),
        "chief": systems_result.get("chief"),
        "fangzheng": systems_result.get("fangzheng", []),
        "mechanism": systems_result.get("mechanism"),
        "time": systems_result.get("time"),
        "discern": systems_result.get("discern", []),
        "wuyun": systems_result.get("wuyun"),
        "plain": systems_result.get("plain"),
        "formula_suggestions": formula_suggestions,
    }

    if peds_result:
        result["peds"] = {
            "dangers": peds_result["dangers"],
            "combos": peds_result["combos"],
            "methods": peds_result["methods"],
            "main_formula": peds_result["main_formula"],
            "jiajian": peds_result.get("jiajian", []),
        }
        result["engine"] = "original"

    ip_h, ua_h = _device_hashes(request)
    rec = DxRecord(
        module=module or "all",
        input=body.model_dump(),
        result=result,
        ip_hash=ip_h,
        ua_hash=ua_h,
    )
    db.add(rec)
    await db.commit()

    return {"record_id": str(rec.id), **result}


@router.get("/records")
async def dx_records(
    request: Request,
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    ip_h, ua_h = _device_hashes(request)
    objs = (
        await db.execute(
            select(DxRecord)
            .where(DxRecord.ip_hash == ip_h, DxRecord.ua_hash == ua_h)
            .order_by(DxRecord.created_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return {"total": len(objs), "items": [_serialize(o) for o in objs]}


@router.get("/records/{record_id}")
async def dx_record(
    record_id: str, request: Request, db: AsyncSession = Depends(get_db)
):
    try:
        uid = uuid.UUID(record_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的记录 ID")
    ip_h, ua_h = _device_hashes(request)
    obj = (
        await db.execute(
            select(DxRecord).where(
                DxRecord.id == uid, DxRecord.ip_hash == ip_h, DxRecord.ua_hash == ua_h
            )
        )
    ).scalar_one_or_none()
    if obj is None:
        raise HTTPException(status_code=404, detail="记录不存在")
    return _serialize(obj)


@router.post("/vision")
async def dx_vision(
    image: UploadFile = File(...),
    module: str = Form("surgery"),
    symptoms: Optional[str] = Form(None),
    request: Request = None,
):
    """拍照辨病:上传患处照片,Qwen-VL 多模态辨病(疮疡/肛肠)。"""
    from app.core.surgery_security import is_valid_image, limit_ai, read_limited

    limit_ai(request)
    if module not in ("surgery", "anorectal"):
        raise HTTPException(status_code=400, detail="拍照辨病仅支持:外科疮疡 / 肛肠痔漏")
    ext = (image.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ("jpg", "jpeg", "png", "webp", "bmp"):
        raise HTTPException(status_code=400, detail="不支持的图片格式(仅 JPEG/PNG/WebP/BMP)")
    data = await read_limited(image)
    if not is_valid_image(data):
        raise HTTPException(status_code=400, detail="文件内容不是有效图片")
    import base64

    b64 = base64.b64encode(data).decode("utf-8")
    try:
        if module == "surgery":
            from app.services.surgery_ai import SurgeryQwenVisionService

            svc = SurgeryQwenVisionService()
            out = await svc.identify_disease(f"data:image/jpeg;base64,{b64}", symptoms)
        else:
            from app.services.vision_ai import analyze_image

            out = await analyze_image(b64, image_type="lesion", extra_symptoms=symptoms)
    except Exception as _e:
        import logging

        logging.getLogger("uvicorn.error").warning("dx/vision failed: %s", repr(_e))
        raise HTTPException(status_code=502, detail="AI 影像服务暂时不可用,请稍后重试")
    return {"module": module, "result": out}


@router.post("/tongue")
async def dx_tongue(
    image: UploadFile = File(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """拍照识舌:上传舌象照片,Qwen-VL 结构化 + 规则归一化为六体系词表标签。

    返回 labels(直接并入 form.tongue 再辨证);AI 失败/非舌象照片一律 200 降级,前端回退手动点选。
    """
    from app.core.surgery_security import is_valid_image, limit_ai, read_limited

    limit_ai(request)
    ext = (image.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in ("jpg", "jpeg", "png", "webp", "bmp"):
        raise HTTPException(status_code=400, detail="不支持的图片格式(仅 JPEG/PNG/WebP/BMP)")
    data = await read_limited(image, max_size=8 * 1024 * 1024)
    if not is_valid_image(data):
        raise HTTPException(status_code=400, detail="文件内容不是有效图片")
    import base64

    digest = hashlib.sha1(data).hexdigest()[:24]
    fname = f"tongue_{digest}.{ext if ext != 'jpeg' else 'jpg'}"
    from pathlib import Path as _P

    abs_dir = _P(settings.UPLOAD_DIR) / "tongue"
    abs_dir.mkdir(parents=True, exist_ok=True)
    (abs_dir / fname).write_bytes(data)
    image_url = f"/uploads/tongue/{fname}"

    from app.services.tongue_ai import analyze_tongue

    out = await analyze_tongue(base64.b64encode(data).decode("utf-8"))
    ip_h, ua_h = _device_hashes(request)
    rec = DxTongueReading(
        image_url=image_url,
        feats=out.get("feats") or {},
        labels=out.get("labels") or [],
        source=out.get("source", "unavailable"),
        confidence=out.get("confidence"),
        ip_hash=ip_h,
        ua_hash=ua_h,
    )
    db.add(rec)
    await db.commit()
    return {
        "id": str(rec.id),
        "image_url": image_url,
        "labels": out.get("labels") or [],
        "source": out.get("source"),
        "confidence": out.get("confidence"),
        "low_confidence": bool(out.get("low_confidence")),
        "not_tongue": bool(out.get("not_tongue")),
        "message": out.get("message", ""),
        "feats": out.get("feats"),
    }


@router.get("/quick")
async def dx_quick(q: str = Query(..., min_length=1), db: AsyncSession = Depends(get_db)):
    """症状/病证名快速联想(从证型、病种、引药病症中抽词)。"""
    out: list[str] = []
    for model, fields in (
        (KBSyndrome, ("name", "summary")),
        (KBDisease, ("name", "characteristics")),
        (KBDulong, ("disease",)),
    ):
        objs = (await db.execute(select(model).limit(300))).scalars().all()
        for o in objs:
            for f in fields:
                v = getattr(o, f, None)
                if v and q in str(v) and v not in out:
                    out.append(str(v))
                    break
            if len(out) >= 12:
                break
        if len(out) >= 12:
            break
    return out[:12]


@router.get("/eval")
async def dx_eval():
    """辨证引擎评测:对标注样本运行多体系引擎,输出各体系准确率与逐样本明细。"""
    from pathlib import Path as _P

    from app.services.dx_systems import analyze_systems

    p = _P(__file__).resolve().parent.parent.parent / "data" / "eval_samples.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    samples = data["samples"]
    per_system: dict[str, dict] = {}
    detail = []
    for sm in samples:
        result = analyze_systems(sm["labels"], time_key=sm.get("time_key", ""), sick_year=sm.get("sick_year", 0), birth_year=sm.get("birth_year", 0), detail_text=sm.get("detail", ""))
        row = {"id": sm["id"], "desc": sm["desc"]}
        for sys_key in ("bagang", "liujing", "weiqiyingxue", "zangfu", "sanjiao", "jingluo"):
            got = result[sys_key]["summary"]
            exp = sm["expected"].get(sys_key)
            row[sys_key] = {"got": got, "expected": exp}
            if exp:
                st = per_system.setdefault(sys_key, {"total": 0, "correct": 0})
                st["total"] += 1
                if sys_key == "bagang" and isinstance(exp, list):
                    comps = result[sys_key].get("components", [])
                    if all(x in comps for x in exp):
                        st["correct"] += 1
                elif got == exp:
                    st["correct"] += 1
        # 一致性交叉印证
        if sm["expected"].get("consistency") is not None:
            cons = result.get("consistency") or {}
            st = per_system.setdefault("consistency", {"total": 0, "correct": 0})
            st["total"] += 1
            ok = cons.get("score") is not None and cons["score"] >= sm["expected"]["consistency"]
            if ok:
                st["correct"] += 1
            row["consistency"] = {"score": cons.get("score"), "verdict": cons.get("verdict"), "expected": sm["expected"]["consistency"]}
        # 动态推理(合病/并病、卫气营血同病、三焦传变)
        if sm["expected"].get("dynamic"):
            dyn = result.get("dynamic") or {}
            merge_labels = "|".join([m.get("label", "") for m in dyn.get("liujing_merge", [])])
            merge_labels += "|" + "|".join([m.get("label", "") for m in dyn.get("weiqi_merge", [])])
            stage = (dyn.get("sanjiao_trans") or {}).get("stage", "")
            row["dynamic"] = {"merge": merge_labels or None, "stage": stage, "expected": sm["expected"]["dynamic"]}
            for k, want in sm["expected"]["dynamic"].items():
                st = per_system.setdefault("dynamic", {"total": 0, "correct": 0})
                st["total"] += 1
                ok = (want in stage) if k == "sanjiao_trans" else (want in merge_labels)
                if ok:
                    st["correct"] += 1
        # 治则治法(脏腑主结论)
        if sm["expected"].get("treatment_has"):
            st = per_system.setdefault("treatment", {"total": 0, "correct": 0})
            st["total"] += 1
            t = ((result.get("zangfu") or {}).get("top") or [{}])[0].get("treatment", "")
            ok = sm["expected"]["treatment_has"] in t
            if ok:
                st["correct"] += 1
            row["treatment"] = {"got": t, "expected": sm["expected"]["treatment_has"]}
        # 主方联动(六体系 top1.formulas)
        if sm["expected"].get("formula_has"):
            st = per_system.setdefault("formula", {"total": 0, "correct": 0})
            st["total"] += 1
            got = ((result.get("zangfu") or {}).get("top") or [{}])[0].get("formulas", [])
            ok = any(sm["expected"]["formula_has"] in x for x in got)
            if ok:
                st["correct"] += 1
            row["formula"] = {"got": got, "expected": sm["expected"]["formula_has"]}
        # 危候警示
        if sm["expected"].get("danger_has"):
            st = per_system.setdefault("danger", {"total": 0, "correct": 0})
            st["total"] += 1
            joined = "|".join(result.get("danger") or [])
            ok = sm["expected"]["danger_has"] in joined
            if ok:
                st["correct"] += 1
            row["danger"] = {"got": result.get("danger") or [], "expected": sm["expected"]["danger_has"]}
        # 鉴别追问
        if sm["expected"].get("followup"):
            st = per_system.setdefault("followup", {"total": 0, "correct": 0})
            st["total"] += 1
            fu = result.get("followup")
            ok = bool(fu and fu.get("questions"))
            if ok:
                st["correct"] += 1
            row["followup"] = {"got": bool(fu and fu.get("questions")), "expected": True}
        # 白话结论
        if sm["expected"].get("plain_has"):
            st = per_system.setdefault("plain", {"total": 0, "correct": 0})
            st["total"] += 1
            got = (result.get("plain") or {}).get("verdict", "")
            ok = sm["expected"]["plain_has"] in got
            if ok:
                st["correct"] += 1
            row["plain"] = {"got": got[:80], "expected": sm["expected"]["plain_has"]}
        # 口语词库抽取
        if sm["expected"].get("colloquial"):
            from app.services.dx_systems import extract_symptom_terms

            st = per_system.setdefault("colloquial", {"total": 0, "correct": 0})
            st["total"] += 1
            got = extract_symptom_terms(sm["labels"])
            ok = all(x in got for x in sm["expected"]["colloquial"])
            if ok:
                st["correct"] += 1
            row["colloquial"] = {"got": got, "expected": sm["expected"]["colloquial"]}
        # 症状→鉴别问句反向引导
        if sm["expected"].get("ask_has"):
            st = per_system.setdefault("ask", {"total": 0, "correct": 0})
            st["total"] += 1
            ids = [q.get("id", "") for q in (result.get("ask") or [])]
            fu_ids = [q.get("id", "") for q in (result.get("followup") or {}).get("questions", [])]
            ok = sm["expected"]["ask_has"] in ids + fu_ids
            if ok:
                st["correct"] += 1
            row["ask"] = {"got": ids + fu_ids, "expected": sm["expected"]["ask_has"]}
        # 六经/脏腑分型
        if sm["expected"].get("variant_has"):
            st = per_system.setdefault("variant", {"total": 0, "correct": 0})
            st["total"] += 1
            v = ((result.get("liujing") or {}).get("top") or [{}])[0].get("variant") or {}
            v2 = ((result.get("zangfu") or {}).get("top") or [{}])[0].get("variant") or {}
            got = (v.get("formulas") or []) + (v2.get("formulas") or [])
            ok = sm["expected"]["variant_has"] in got
            if ok:
                st["correct"] += 1
            row["variant"] = {"got": got, "expected": sm["expected"]["variant_has"]}
        # 治法门类(医方集解)
        if sm["expected"].get("menlei_has"):
            st = per_system.setdefault("menlei", {"total": 0, "correct": 0})
            st["total"] += 1
            mls = [m.get("menlei", "") for m in (result.get("menlei") or [])]
            ok = sm["expected"]["menlei_has"] in mls
            if ok:
                st["correct"] += 1
            row["menlei"] = {"got": mls, "expected": sm["expected"]["menlei_has"]}
        # 拟方合成
        if sm["expected"].get("prescription_has"):
            st = per_system.setdefault("prescription", {"total": 0, "correct": 0})
            st["total"] += 1
            got = (result.get("prescription") or {}).get("name", "")
            ok = sm["expected"]["prescription_has"] in got
            if ok:
                st["correct"] += 1
            row["prescription"] = {"got": got, "expected": sm["expected"]["prescription_has"]}
        # 病机提要
        if sm["expected"].get("mechanism_has"):
            st = per_system.setdefault("mechanism", {"total": 0, "correct": 0})
            st["total"] += 1
            got = (result.get("mechanism") or {}).get("summary", "")
            ok = sm["expected"]["mechanism_has"] in got
            if ok:
                st["correct"] += 1
            row["mechanism"] = {"got": got[:60], "expected": sm["expected"]["mechanism_has"]}
        # 时间辨证
        if sm["expected"].get("time_hint"):
            st = per_system.setdefault("time", {"total": 0, "correct": 0})
            st["total"] += 1
            got = (result.get("time") or {}).get("hint", "")
            ok = sm["expected"]["time_hint"] in got
            if ok:
                st["correct"] += 1
            row["time"] = {"got": got[:40], "expected": sm["expected"]["time_hint"]}
        # 脉证相参鉴别
        if sm["expected"].get("discern_has"):
            st = per_system.setdefault("discern", {"total": 0, "correct": 0})
            st["total"] += 1
            joined = "|".join(result.get("discern") or [])
            ok = sm["expected"]["discern_has"] in joined
            if ok:
                st["correct"] += 1
            row["discern"] = {"got": (result.get("discern") or [])[:1], "expected": sm["expected"]["discern_has"]}
        # 五运六气
        if sm["expected"].get("wuyun_has"):
            st = per_system.setdefault("wuyun", {"total": 0, "correct": 0})
            st["total"] += 1
            got = (result.get("wuyun") or {}).get("hint", "")
            ok = sm["expected"]["wuyun_has"] in got
            if ok:
                st["correct"] += 1
            row["wuyun"] = {"got": got[:60], "expected": sm["expected"]["wuyun_has"]}
        # 随症加减
        if sm["expected"].get("modification_has"):
            st = per_system.setdefault("modification", {"total": 0, "correct": 0})
            st["total"] += 1
            mods = result.get("modifications") or []
            herbs = [a.get("name", "") for m in mods for e in m["entries"] for a in e.get("add", [])]
            ok = sm["expected"]["modification_has"] in herbs
            if ok:
                st["correct"] += 1
            row["modification"] = {"got": herbs, "expected": sm["expected"]["modification_has"]}
        # 抓主证(多问题主诉:主次判定/治则/同源/合方)
        if sm["expected"].get("chief_has"):
            c = result.get("chief") or {}
            st = per_system.setdefault("chief", {"total": 0, "correct": 0})
            st["total"] += 1
            chief_text = (c.get("problems") or [{}])[c.get("chief_index") or 0].get("text", "")
            ok = sm["expected"]["chief_has"] in chief_text
            if ok:
                st["correct"] += 1
            row["chief"] = {"got": chief_text, "expected": sm["expected"]["chief_has"]}
        if sm["expected"].get("strategy_has"):
            c = result.get("chief") or {}
            st = per_system.setdefault("strategy", {"total": 0, "correct": 0})
            st["total"] += 1
            got = c.get("zhice", "")
            ok = sm["expected"]["strategy_has"] in got
            if ok:
                st["correct"] += 1
            row["strategy"] = {"got": got[:50], "expected": sm["expected"]["strategy_has"]}
        if sm["expected"].get("tongyuan") is not None:
            c = result.get("chief") or {}
            st = per_system.setdefault("tongyuan", {"total": 0, "correct": 0})
            st["total"] += 1
            ok = bool(c.get("tongyuan")) == bool(sm["expected"]["tongyuan"])
            if ok:
                st["correct"] += 1
            row["tongyuan"] = {"got": c.get("tongyuan"), "expected": sm["expected"]["tongyuan"]}
        if sm["expected"].get("hefang_has"):
            st = per_system.setdefault("hefang", {"total": 0, "correct": 0})
            st["total"] += 1
            got = ((result.get("prescription") or {}).get("hefang") or {}).get("formulas", "")
            ok = sm["expected"]["hefang_has"] in got
            if ok:
                st["correct"] += 1
            row["hefang"] = {"got": got, "expected": sm["expected"]["hefang_has"]}
        # 方证层(经典方证直接对应)
        if sm["expected"].get("fangzheng_has"):
            st = per_system.setdefault("fangzheng", {"total": 0, "correct": 0})
            st["total"] += 1
            got = "|".join(f.get("formula", "") for f in (result.get("fangzheng") or []))
            ok = sm["expected"]["fangzheng_has"] in got
            if ok:
                st["correct"] += 1
            row["fangzheng"] = {"got": got[:60], "expected": sm["expected"]["fangzheng_has"]}
        detail.append(row)
    # 舌象归一化评测(VL 特征 → 引擎词表标签,纯规则层;图像识别准确率另以医师标注集评估)
    tongue_cases = [
        {"desc": "红舌黄腻苔齿痕舌尖红", "feats": {"tongue_color": "红", "coating_color": "黄", "coating_texture": "腻", "shape": "齿痕", "state": "正常", "zones": {"tip": "红", "center": "正常", "root": "腻", "sides": "正常"}}, "expect": ["舌红", "苔黄腻", "齿痕舌", "舌尖红"]},
        {"desc": "淡白舌胖大白苔", "feats": {"tongue_color": "淡白", "coating_color": "白", "coating_texture": "薄", "shape": "胖大", "state": "正常", "zones": {}}, "expect": ["舌淡", "苔白", "胖大舌"]},
        {"desc": "紫暗舌剥苔瘀斑裂纹", "feats": {"tongue_color": "紫", "coating_color": "无苔", "coating_texture": "剥", "shape": "裂纹", "state": "正常", "zones": {"sides": "瘀斑"}}, "expect": ["舌紫暗", "少苔", "舌有瘀斑", "裂纹舌"]},
        {"desc": "正常淡红舌薄白苔", "feats": {"tongue_color": "淡红", "coating_color": "白", "coating_texture": "薄", "shape": "正常", "state": "正常", "zones": {}}, "expect": ["苔白"]},
        {"desc": "绛舌黄燥苔", "feats": {"tongue_color": "绛", "coating_color": "黄", "coating_texture": "燥", "shape": "正常", "state": "正常", "zones": {}}, "expect": ["舌绛", "苔黄燥"]},
        {"desc": "矛盾校验:黄苔+剥苔只留舌红", "feats": {"tongue_color": "红", "coating_color": "黄", "coating_texture": "剥", "shape": "正常", "state": "正常", "zones": {}}, "expect": ["舌红"]},
        {"desc": "深绛舌点刺", "feats": {"tongue_color": "深绛", "coating_color": "无", "coating_texture": "无", "shape": "点刺", "state": "正常", "zones": {}}, "expect": ["舌深绛", "少苔", "点刺舌"]},
    ]
    from app.services.tongue_ai import normalize_tongue

    for tc in tongue_cases:
        st = per_system.setdefault("tongue", {"total": 0, "correct": 0})
        st["total"] += 1
        got = sorted(normalize_tongue(tc["feats"])["labels"])
        ok = got == sorted(tc["expect"])
        if ok:
            st["correct"] += 1
        detail.append({"id": f"tongue-{tc['desc']}", "desc": tc["desc"], "tongue": {"got": got, "expected": tc["expect"]}})
    acc = {}
    for k, v in per_system.items():
        acc[k] = {"total": v["total"], "correct": v["correct"], "accuracy": round(v["correct"] / v["total"], 4) if v["total"] else None}
    total_correct = sum(v["correct"] for v in per_system.values())
    total_n = sum(v["total"] for v in per_system.values())
    return {
        "meta": data["meta"],
        "samples": len(samples),
        "accuracy": acc,
        "overall": round(total_correct / total_n, 4) if total_n else None,
        "detail": detail,
    }
