"""学苑 — 学习路径/学习卡/自测/笔记/收藏/AI 助学(免登录,设备级)"""
from __future__ import annotations

import hashlib
import json
import random
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.kb import (
    KBCase,
    KBDisease,
    KBDulong,
    KBFormula,
    KBHerb,
    KBSyndrome,
    KBTerm,
    KBTip,
)
from app.models.learn import LearnFavorite, LearnNote, LearnProgress, QuizAttempt

router = APIRouter(prefix="/learn", tags=["学苑"])

TYPE_REGISTRY = {
    "formulas": KBFormula, "herbs": KBHerb, "diseases": KBDisease,
    "syndromes": KBSyndrome, "cases": KBCase, "tips": KBTip,
    "terms": KBTerm, "dulong": KBDulong,
}
_NAME_FIELD = {
    "formulas": "name", "herbs": "name", "diseases": "name", "syndromes": "name",
    "cases": "title", "tips": "category", "terms": "term", "dulong": "disease",
}

_PATHS: Optional[list[dict]] = None


def _real_ip(request: Request) -> str:
    """nginx 反代下 client.host 恒为网关地址;真实客户端 IP 取自 nginx 覆盖注入的 X-Real-IP。"""
    return (request.headers.get("x-real-ip") or "").strip() or (
        request.client.host if request.client else "unknown"
    )

def _device(request: Request) -> str:
    ip = _real_ip(request)
    ua = request.headers.get("user-agent", "") or ""
    salt = settings.visit_salt
    return hashlib.sha256(f"{salt}:{ip}:{ua}".encode("utf-8")).hexdigest()


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


def _load_paths() -> list[dict]:
    global _PATHS
    if _PATHS is None:
        p = Path(__file__).resolve().parent.parent.parent / "data" / "learn_paths.json"
        _PATHS = json.loads(p.read_text(encoding="utf-8")).get("paths", [])
    return _PATHS


async def _resolve_item(item: dict, db: AsyncSession) -> Optional[dict]:
    """按 (type, module, name) 解析 kb 条目:先精确后子串。"""
    itype = item["type"]
    model = TYPE_REGISTRY.get(itype)
    if model is None:
        return None
    name = item["name"]
    stmt = select(model)
    if item.get("module") and item["module"] != "all":
        stmt = stmt.where(model.module == item["module"])
    objs = (await db.execute(stmt)).scalars().all()
    if not objs:
        return None
    f = _NAME_FIELD[itype]
    for o in objs:
        if getattr(o, f, None) == name:
            return _serialize(o)
    for o in objs:
        v = getattr(o, f, None) or ""
        if name in v or v in name:
            return _serialize(o)
    return None


def _card(obj: dict, itype: str) -> dict:
    """条目 → 学习卡(正面/背面)。"""
    front = obj.get(_NAME_FIELD[itype]) or ""
    back_lines = []
    if itype == "formulas":
        back_lines = [
            f"【出处】{obj.get('source') or '—'}",
            f"【组成】{', '.join(c.get('name', '') for c in (obj.get('composition') or [])[:8])}",
            f"【功效】{obj.get('function') or '—'}",
            f"【主治】{obj.get('indication') or '—'}",
        ]
    elif itype == "herbs":
        back_lines = [f"【性味】{obj.get('properties') or '—'}", f"【功效】{obj.get('effects') or '—'}", f"【主治】{obj.get('indications') or '—'}"]
    elif itype == "diseases":
        back_lines = [f"【特点】{obj.get('characteristics') or '—'}", f"【鉴别】{obj.get('differential') or '—'}", f"【预后】{obj.get('prognosis') or '—'}"]
    elif itype == "syndromes":
        back_lines = [f"【舌脉】{obj.get('tongue_pulse') or '—'}", f"【要点】{obj.get('summary') or obj.get('local_signs') or '—'}"]
    elif itype == "cases":
        back_lines = [f"【病证】{obj.get('disease') or ''} {obj.get('syndrome') or ''}", f"【治法】{(obj.get('treatment') or '')[:120]}"]
    elif itype == "tips":
        back_lines = [(obj.get("content") or "")[:150]]
    elif itype == "terms":
        back_lines = [obj.get("definition") or "—"]
    elif itype == "dulong":
        back_lines = [f"【引药】{obj.get('guide') or '—'}"]
    return {
        "id": obj.get("id"), "type": itype, "module": obj.get("module"),
        "front": front, "back": "\n".join(b for b in back_lines if b),
        "source": obj.get("source") or "",
    }


@router.get("/paths")
async def list_paths(db: AsyncSession = Depends(get_db)):
    """学习路径(含已解析条目与题目数)。"""
    paths = []
    for p in _load_paths():
        items = []
        for it in p.get("items", []):
            obj = await _resolve_item(it, db)
            items.append({
                "key": f"{it['type']}:{it['name']}",
                "type": it["type"],
                "name": it["name"],
                "note": it.get("note", ""),
                "module": it.get("module", ""),
                "id": obj["id"] if obj else None,
                "resolved": obj is not None,
            })
        paths.append({
            "id": p["id"], "title": p["title"], "module": p.get("module", "all"),
            "desc": p.get("desc", ""),
            "total": len(items), "resolved_count": sum(1 for i in items if i["resolved"]),
            "items": items,
        })
    return {"paths": paths}


class ProgressIn(BaseModel):
    path_id: str
    item_key: str
    done: bool = True


@router.post("/progress")
async def save_progress(body: ProgressIn, request: Request, db: AsyncSession = Depends(get_db)):
    dev = _device(request)
    row = (
        await db.execute(
            select(LearnProgress).where(
                LearnProgress.device == dev, LearnProgress.path_id == body.path_id
            )
        )
    ).scalar_one_or_none()
    if row is None:
        row = LearnProgress(device=dev, path_id=body.path_id, done=[])
        db.add(row)
    done = list(row.done or [])
    if body.done and body.item_key not in done:
        done.append(body.item_key)
    if not body.done and body.item_key in done:
        done.remove(body.item_key)
    row.done = done
    await db.commit()
    return {"path_id": body.path_id, "done": done, "count": len(done)}


@router.get("/progress")
async def get_progress(request: Request, path_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    dev = _device(request)
    stmt = select(LearnProgress).where(LearnProgress.device == dev)
    if path_id:
        stmt = stmt.where(LearnProgress.path_id == path_id)
    rows = (await db.execute(stmt)).scalars().all()
    return {"items": [{**_serialize(r), "done": r.done or []} for r in rows]}


@router.get("/card")
async def get_card(
    type: str = Query(...), name: str = Query(...), db: AsyncSession = Depends(get_db)
):
    """学习卡:条目按名称解析(路径条目用)。"""
    obj = await _resolve_item({"type": type, "name": name, "module": ""}, db)
    if obj is None:
        raise HTTPException(status_code=404, detail="条目未找到")
    return _card(obj, type)


class NoteIn(BaseModel):
    item_type: str
    item_id: str
    content: str = Field(..., max_length=5000)


@router.post("/notes")
async def add_note(body: NoteIn, request: Request, db: AsyncSession = Depends(get_db)):
    row = LearnNote(device=_device(request), item_type=body.item_type, item_id=body.item_id, content=body.content)
    db.add(row)
    await db.commit()
    return {"id": str(row.id)}


@router.get("/notes")
async def list_notes(request: Request, db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(LearnNote).where(LearnNote.device == _device(request)).order_by(LearnNote.created_at.desc()).limit(100)
        )
    ).scalars().all()
    return {"items": [_serialize(r) for r in rows]}


@router.delete("/notes/{note_id}")
async def del_note(note_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        uid = uuid.UUID(note_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效 ID")
    row = (
        await db.execute(
            select(LearnNote).where(LearnNote.id == uid, LearnNote.device == _device(request))
        )
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="笔记不存在")
    await db.delete(row)
    await db.commit()
    return {"status": "deleted"}


class FavIn(BaseModel):
    item_type: str
    item_id: str


@router.post("/favorites/toggle")
async def toggle_fav(body: FavIn, request: Request, db: AsyncSession = Depends(get_db)):
    dev = _device(request)
    row = (
        await db.execute(
            select(LearnFavorite).where(
                LearnFavorite.device == dev,
                LearnFavorite.item_type == body.item_type,
                LearnFavorite.item_id == body.item_id,
            )
        )
    ).scalar_one_or_none()
    if row:
        await db.delete(row)
        favorited = False
    else:
        db.add(LearnFavorite(device=dev, item_type=body.item_type, item_id=body.item_id))
        favorited = True
    await db.commit()
    return {"favorited": favorited}


@router.get("/favorites")
async def list_favs(request: Request, db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(LearnFavorite).where(LearnFavorite.device == _device(request)).order_by(LearnFavorite.created_at.desc()).limit(200)
        )
    ).scalars().all()
    items = []
    for r in rows:
        model = TYPE_REGISTRY.get(r.item_type)
        if model is None:
            continue
        try:
            uid = uuid.UUID(r.item_id)
        except ValueError:
            continue
        obj = (await db.execute(select(model).where(model.id == uid))).scalar_one_or_none()
        if obj:
            items.append(_card(_serialize(obj), r.item_type))
    return {"items": items}


# ---------------- 自测 ----------------


def _pick_options(correct: str, pool: list[str], n: int = 3) -> list[str]:
    opts = [correct]
    cands = [p for p in pool if p and p != correct]
    random.shuffle(cands)
    for c in cands:
        if len(opts) >= n + 1:
            break
        opts.append(c)
    while len(opts) < n + 1:
        opts.append("以上均非")
    random.shuffle(opts)
    return opts


async def _gen_quiz(scope: str, n: int, db: AsyncSession) -> list[dict]:
    mods = None if scope in ("", "all") else [scope]
    questions: list[dict] = []

    def _where(model):
        stmt = select(model)
        if mods:
            stmt = stmt.where(model.module.in_(mods))
        return stmt

    formulas = (await db.execute(_where(KBFormula))).scalars().all()
    syndromes = (await db.execute(_where(KBSyndrome))).scalars().all()
    terms = (await db.execute(_where(KBTerm))).scalars().all()
    diseases = (await db.execute(_where(KBDisease))).scalars().all()
    herbs = (await db.execute(_where(KBHerb))).scalars().all()

    random.shuffle(formulas)
    random.shuffle(syndromes)
    random.shuffle(terms)
    random.shuffle(diseases)
    random.shuffle(herbs)

    # 1) 方剂功效题
    for f in formulas:
        if f.function and len(questions) < n:
            pool = [x.function for x in formulas if x.function]
            q = {
                "id": f"q{len(questions)}", "type": "formula-function",
                "q": f"方剂「{f.name}」的功效是?",
                "options": _pick_options(f.function, pool),
                "answer": f.function,
                "item_type": "formulas", "item_id": str(f.id),
                "explain": f"「{f.name}」出自{f.source or '—'}:{f.function};主治 {f.indication or '—'}。",
            }
            questions.append(q)
    # 2) 术语释义题
    for t in terms:
        if t.definition and len(questions) < n:
            pool = [x.definition for x in terms if x.definition]
            q = {
                "id": f"q{len(questions)}", "type": "term-def",
                "q": f"炼丹术语「{t.term}」的含义是?",
                "options": _pick_options(t.definition, pool),
                "answer": t.definition,
                "item_type": "terms", "item_id": str(t.id),
                "explain": f"「{t.term}」:{t.definition}",
            }
            questions.append(q)
    # 3) 证型-方剂题
    for s in syndromes:
        if len(questions) >= n:
            break
        matched = sorted(
            (f for f in formulas if f.indication and s.name in f.indication),
            key=lambda f: f.name or "",
        )
        if not matched:
            continue
        correct = matched[0].name
        pool = [f.name for f in formulas]
        q = {
            "id": f"q{len(questions)}", "type": "syndrome-formula",
            "q": f"证型「{s.name}」宜选何方?",
            "options": _pick_options(correct, pool),
            "answer": correct,
            "item_type": "syndromes", "item_id": str(s.id),
            "explain": f"「{s.name}」——《{matched[0].source or '—'}》{correct}。",
        }
        questions.append(q)
    # 4) 病种分类题
    for d in diseases:
        if d.category and len(questions) < n:
            pool = list({x.category for x in diseases if x.category})
            q = {
                "id": f"q{len(questions)}", "type": "disease-category",
                "q": f"「{d.name}」属于哪一类?",
                "options": _pick_options(d.category, pool),
                "answer": d.category,
                "item_type": "diseases", "item_id": str(d.id),
                "explain": f"「{d.name}」属{d.category};{d.characteristics or ''}",
            }
            questions.append(q)
    # 5) 中药功效题
    for h in herbs:
        if h.effects and len(questions) < n:
            pool = [x.effects for x in herbs if x.effects]
            q = {
                "id": f"q{len(questions)}", "type": "herb-effect",
                "q": f"中药「{h.name}」的功效是?",
                "options": _pick_options(h.effects, pool),
                "answer": h.effects,
                "item_type": "herbs", "item_id": str(h.id),
                "explain": f"「{h.name}」:{h.effects};{h.indications or ''}",
            }
            questions.append(q)
    random.shuffle(questions)
    return questions[:n]


@router.get("/quiz")
async def get_quiz(
    scope: str = Query("all"), n: int = Query(10, ge=3, le=20), db: AsyncSession = Depends(get_db)
):
    qs = await _gen_quiz(scope, n, db)
    out = [{k: v for k, v in q.items() if k not in ("answer",)} for q in qs]
    return {"scope": scope, "questions": out}


class QuizSubmitIn(BaseModel):
    scope: str = "all"
    answers: list[dict] = Field(default_factory=list)  # [{id, chosen}]


async def _derive_answer(item_type: str, item_id: str, db: AsyncSession) -> str | None:
    """按条目确定性推导正确答案(与出题逻辑一致,交卷时重算而非重抽)。"""
    model = TYPE_REGISTRY.get(item_type)
    if model is None:
        return None
    try:
        uid = uuid.UUID(item_id)
    except ValueError:
        return None
    obj = (await db.execute(select(model).where(model.id == uid))).scalar_one_or_none()
    if obj is None:
        return None
    if item_type == "formulas":
        return obj.function
    if item_type == "terms":
        return obj.definition
    if item_type == "diseases":
        return obj.category
    if item_type == "herbs":
        return obj.effects
    if item_type == "syndromes":
        matched = sorted(
            (f for f in (
                await db.execute(select(KBFormula).where(KBFormula.indication.contains(obj.name)))
            ).scalars().all()),
            key=lambda f: f.name or "",
        )
        return matched[0].name if matched else None
    return None


@router.post("/quiz/submit")
async def submit_quiz(body: QuizSubmitIn, request: Request, db: AsyncSession = Depends(get_db)):
    if not body.answers:
        raise HTTPException(status_code=400, detail="没有提交答案")
    detail, correct = [], 0
    for a in body.answers:
        item_type = a.get("item_type")
        item_id = a.get("item_id")
        answer = await _derive_answer(item_type, item_id, db)
        if answer is None:
            continue
        q_text = a.get("q") or ""
        chosen = a.get("chosen")
        ok = bool(chosen) and chosen == answer
        if ok:
            correct += 1
        # 解析说明:按题型生成
        if item_type == "formulas":
            explain = f"「{q_text.replace('方剂「', '').split('」')[0]}」的功效为 {answer}。"
        elif item_type == "terms":
            explain = f"术语释义:{answer}"
        elif item_type == "diseases":
            explain = f"该病属 {answer}。"
        elif item_type == "herbs":
            explain = f"功效:{answer}"
        else:
            explain = f"正确答案:{answer}"
        detail.append({
            "id": a.get("id"), "q": q_text, "chosen": chosen,
            "answer": answer, "ok": ok, "explain": explain,
            "item_type": item_type, "item_id": item_id,
        })
    total = len(detail)
    score = round(correct / total * 100) if total else 0
    db.add(QuizAttempt(
        device=_device(request), scope=body.scope, total=total, correct=correct, detail=detail
    ))
    await db.commit()
    return {"total": total, "correct": correct, "score": score, "detail": detail}


@router.get("/quiz/history")
async def quiz_history(request: Request, limit: int = Query(20, ge=1, le=50), db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(QuizAttempt).where(QuizAttempt.device == _device(request)).order_by(QuizAttempt.created_at.desc()).limit(limit)
        )
    ).scalars().all()
    return {"items": [{**_serialize(r), "score": round(r.correct / r.total * 100) if r.total else 0} for r in rows]}


# ---------------- AI 助学 ----------------


async def _auto_context(question: str, db: AsyncSession) -> str:
    """按提问关键词自动检索知识总库,取最相关条目作为 AI 上下文。"""
    grams = [question[i : i + 2] for i in range(len(question) - 1) if question[i : i + 2].strip()]
    grams = [g for g in grams if g and all(("\u4e00" <= c <= "\u9fff") or c.isalnum() for c in g)]
    grams = list(dict.fromkeys(grams))[:30]
    if not grams:
        return ""
    found: list[tuple[int, str]] = []

    def score_hit(text: str) -> int:
        if not text:
            return 0
        return sum(1 for g in grams if g in text)

    # 名称字段 + 内容字段都检索,保证"八症六字"这类出现在正文里的知识能被找到
    search_fields = {
        "formulas": ("name", "function", "indication"),
        "syndromes": ("name", "summary", "tongue_pulse"),
        "diseases": ("name", "characteristics", "differential"),
        "cases": ("title", "history"),
        "tips": ("category", "content"),
        "terms": ("term", "definition"),
        "dulong": ("disease", "guide"),
    }
    for model, fields in ((KBFormula, search_fields["formulas"]),
                          (KBSyndrome, search_fields["syndromes"]),
                          (KBDisease, search_fields["diseases"]),
                          (KBCase, search_fields["cases"]),
                          (KBTip, search_fields["tips"]),
                          (KBTerm, search_fields["terms"]),
                          (KBDulong, search_fields["dulong"])):
        objs = (await db.execute(select(model).limit(400))).scalars().all()
        for o in objs:
            best_sc, best_field = 0, ""
            for fname in fields:
                sc = score_hit(str(getattr(o, fname, None) or ""))
                if sc > best_sc:
                    best_sc, best_field = sc, fname
            if best_sc > 0:
                obj = _serialize(o)
                snippet = str(getattr(o, best_field, None) or "")
                if len(snippet) > 500:
                    snippet = snippet[:500] + "…"
                found.append((best_sc * 10, f"[{best_field}={snippet}]"))
        if len(found) >= 30:
            break
    found.sort(key=lambda x: -x[0])
    return "\n---\n".join(t for _, t in found[:8])


class AskIn(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000)
    context_type: Optional[str] = None
    context_id: Optional[str] = None


@router.post("/ask")
async def ai_ask(body: AskIn, request: Request, db: AsyncSession = Depends(get_db)):
    from app.core.surgery_security import limit_ai

    limit_ai(request)
    if not settings.DEEPSEEK_API_KEY:
        raise HTTPException(status_code=503, detail="AI 服务未配置")
    ctx_text = ""
    if body.context_type and body.context_id:
        model = TYPE_REGISTRY.get(body.context_type)
        if model:
            try:
                uid = uuid.UUID(body.context_id)
                obj = (await db.execute(select(model).where(model.id == uid))).scalar_one_or_none()
                if obj:
                    ctx_text = json.dumps(_serialize(obj), ensure_ascii=False)[:2500]
            except ValueError:
                pass
    if not ctx_text:
        ctx_text = await _auto_context(body.question, db)
    prompt = f"""你是杏林汇(中医专科辅助诊疗平台)的 AI 助教,面向中医学习者答疑。
要求:通俗易懂、条理清晰;必须优先依据下方"知识库检索上下文"作答并注明出处(如"据《程氏家传儿科秘要》");中医术语附白话解释;如涉及丹药必须附毒性警示;上下文没有覆盖时明确说明,不要臆造。
{('知识库条目上下文:' + ctx_text) if ctx_text else ''}

学生提问:{body.question}"""
    try:
        from app.core.ai_gateway import chat

        result = await chat(
            "learn-ask",
            [
                {"role": "system", "content": "你是严谨耐心的中医学习助教。"},
                {"role": "user", "content": prompt},
            ],
            provider="deepseek",
            timeout=90.0,
            temperature=0.4,
        )
        return {"answer": result["text"]}
    except Exception:
        raise HTTPException(status_code=502, detail="AI 服务暂时不可用,请稍后重试")
