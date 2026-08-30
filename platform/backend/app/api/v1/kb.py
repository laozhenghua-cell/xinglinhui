"""统一共用知识总库 API(免鉴权)。

前缀 /api/v1/kb,提供:
- /stats                      各表计数 + 按 module 计数
- /{type}                     各类型列表(q/module/category/page/size,返回 {total, items})
- /{type}/{id}                详情
- /search                     跨类型 ILIKE 检索(q,type)
- /linked                     关联条目启发式匹配(type,id)
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Text, func, or_, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.kb import (
    KBCase,
    KbClassic,
    KBDisease,
    KBDulong,
    KBFormula,
    KBHerb,
    KBSyndrome,
    KBTerm,
    KBTip,
    KbYifang,
)

router = APIRouter(prefix="/kb", tags=["知识总库"])

# type → 模型
TYPE_REGISTRY = {
    "formulas": KBFormula,
    "herbs": KBHerb,
    "diseases": KBDisease,
    "syndromes": KBSyndrome,
    "cases": KBCase,
    "tips": KBTip,
    "terms": KBTerm,
    "dulong": KBDulong,
    "classics": KbClassic,
    "yifang": KbYifang,
}

# type → 展示主字段(用于 search 结果标签)
TYPE_LABEL_FIELD = {
    "formulas": "name",
    "herbs": "name",
    "diseases": "name",
    "syndromes": "name",
    "cases": "title",
    "tips": "content",
    "terms": "term",
    "dulong": "disease",
    "classics": "article",
    "yifang": "name",
}

# type → 可检索字段:(字段名, 是否 JSONB)
SEARCH_FIELDS = {
    "formulas": [
        ("name", False), ("aliases", True), ("source", False),
        ("indication", False), ("function", False), ("composition", True),
    ],
    "herbs": [
        ("name", False), ("pinyin", False), ("aliases", True),
        ("effects", False), ("indications", False),
    ],
    "diseases": [
        ("name", False), ("aliases", True),
        ("characteristics", False), ("differential", False),
    ],
    "syndromes": [
        ("name", False), ("aliases", True), ("summary", False),
    ],
    "cases": [
        ("title", False), ("disease", False), ("syndrome", False),
        ("chief_complaint", False), ("history", False),
    ],
    "tips": [("content", False), ("source", False)],
    "terms": [("term", False), ("definition", False)],
    "dulong": [("disease", False), ("guide", False)],
    "classics": [("original", False), ("plain", False), ("article", False), ("book", False)],
    "yifang": [
        ("name", False), ("aliases", True), ("category", False),
        ("function", False), ("indications", False), ("composition", True), ("source", False),
    ],
}


def _get_model(type_name: str):
    model = TYPE_REGISTRY.get(type_name)
    if model is None:
        raise HTTPException(
            status_code=400,
            detail=f"未知类型: {type_name};可用: {', '.join(TYPE_REGISTRY)}",
        )
    return model


def _escape_like(q: str) -> str:
    """对 ILIKE 通配符做转义(配合 ESCAPE '\\')。"""
    return q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _ilike(col, q: str):
    """列 ILIKE 检索,JSONB 列先转 text。"""
    target = func.cast(col, Text) if isinstance(col.type, JSONB) else col
    return target.ilike(f"%{_escape_like(q)}%", escape="\\")


def _serialize(obj) -> dict:
    """ORM 对象 → JSON 可序列化 dict(通用,基于表列)。"""
    data = {}
    for col in obj.__table__.columns:
        value = getattr(obj, col.name)
        if isinstance(value, uuid.UUID):
            value = str(value)
        elif isinstance(value, datetime):
            value = value.isoformat()
        data[col.name] = value
    return data


@router.get("/stats")
async def kb_stats(db: AsyncSession = Depends(get_db)):
    """各表计数 + 按 module 计数。"""
    tables: dict[str, int] = {}
    modules: dict[str, int] = {}
    total = 0
    for type_name, model in TYPE_REGISTRY.items():
        count = (await db.execute(select(func.count()).select_from(model))).scalar() or 0
        tables[type_name] = count
        total += count
        # 无 module 列的表(如典籍库)跳过按专科聚合
        if "module" not in model.__table__.columns:
            continue
        rows = (await db.execute(
            select(model.module, func.count()).group_by(model.module)
        )).all()
        for module, cnt in rows:
            modules[module] = modules.get(module, 0) + (cnt or 0)
    return {
        "total": total,
        "tables": tables,
        "modules": modules,
        "counts": tables,          # 兼容前端统计卡片
        "by_module": modules,      # 兼容前端专科计数
    }


def _item_text(item: dict) -> str:
    """条目 → 检索文本(供向量化)。"""
    parts = [
        item.get("name") or item.get("title") or item.get("term") or item.get("disease") or "",
        (item.get("aliases") or []) if isinstance(item.get("aliases"), list) else [],
        item.get("indication") or item.get("function") or item.get("definition") or item.get("guide") or "",
    ]
    out = []
    for p in parts:
        if isinstance(p, list):
            out.extend(str(x) for x in p if x)
        elif p:
            out.append(str(p))
    return " ".join(out)[:400]


async def _semantic_rerank(query: str, items: list[dict], top: int = 20) -> list[dict]:
    """ILIKE 候选 + 向量余弦重排(混合检索)。向量服务不可用时静默回退 ILIKE 顺序。"""
    try:
        from app.core.ai_gateway import embed

        candidates = items[:40]
        pairs = [(idx, _item_text(i)) for idx, i in enumerate(candidates)]
        pairs = [(idx, t) for idx, t in pairs if t]
        if not pairs:
            return items
        texts = [t for _, t in pairs]
        vectors = await embed([query] + texts, provider="qwen", timeout=30.0)
        if not vectors or len(vectors) != len(texts) + 1:
            return items
        qv = vectors[0]
        item_vecs = list(zip(pairs, vectors[1:]))

        def cosine(a, b):
            dot = sum(x * y for x, y in zip(a, b))
            na = sum(x * x for x in a) ** 0.5
            nb = sum(y * y for y in b) ** 0.5
            return dot / (na * nb) if na and nb else 0.0

        scored = sorted(
            ((cosine(qv, v), candidates[idx]) for (idx, _t), v in item_vecs),
            key=lambda x: -x[0],
        )
        for sim, it in scored:
            it["sim"] = round(sim, 4)
        reranked = [it for _, it in scored[:top]]
        # 未参与重排的候选(40 名之后)保持原顺序,排在后面
        return reranked + items[len(candidates):]
    except Exception:
        return items



@router.get("/search")
async def kb_search(
    q: str = Query(..., min_length=1, description="检索词"),
    type: Optional[str] = Query(None, description="限定类型"),
    semantic: bool = Query(False, description="启用语义重排(向量,可能产生少量 API 成本)"),
    db: AsyncSession = Depends(get_db),
):
    """跨类型全文检索(ILIKE,每类前 20 条,带类型标签)。"""
    if type is not None and type not in TYPE_REGISTRY:
        raise HTTPException(status_code=400, detail=f"未知类型: {type}")
    types = [type] if type else list(TYPE_REGISTRY)
    results = []
    for type_name in types:
        model = _get_model(type_name)
        conds = [
            _ilike(getattr(model, field), q) for field, _ in SEARCH_FIELDS[type_name]
        ]
        stmt = (
            select(model)
            .where(or_(*conds))
            .order_by(model.created_at.desc())
            .limit(20)
        )
        objs = (await db.execute(stmt)).scalars().all()
        for obj in objs:
            item = _serialize(obj)
            item["type"] = type_name
            label = item.get(TYPE_LABEL_FIELD.get(type_name, "name")) or ""
            item["snippet"] = str(label)[:80] if label else ""
            results.append(item)
    if semantic and results:
        results = await _semantic_rerank(q, results)
    return {"query": q, "type": type, "semantic": semantic, "count": len(results), "results": results}


@router.get("/linked")
async def kb_linked(
    type: str = Query(..., description="源类型"),
    id: str = Query(..., description="源条目 UUID"),
    db: AsyncSession = Depends(get_db),
):
    """返回与指定条目相关的其他类型条目(名称相等/包含、组成药物名相交)。"""
    model = _get_model(type)
    try:
        uid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的 ID(UUID)")
    obj = (await db.execute(select(model).where(model.id == uid))).scalar_one_or_none()
    if obj is None:
        raise HTTPException(status_code=404, detail="条目不存在")
    src = _serialize(obj)
    src_names = _extract_names(type, src)

    results = []
    for other_type, other_model in TYPE_REGISTRY.items():
        if other_type == type:
            continue
        objs = (await db.execute(select(other_model))).scalars().all()
        for other in objs:
            data = _serialize(other)
            matched = _match_names(src_names, _extract_names(other_type, data))
            if matched:
                data["type"] = other_type
                data["matched_by"] = matched
                results.append(data)
    # 稳定的相关性排序:命中越多越靠前
    results.sort(key=lambda r: len(r.get("matched_by", [])), reverse=True)
    return {"type": type, "id": id, "count": len(results), "results": results, "items": results}


def _extract_names(type_name: str, data: dict) -> list[str]:
    """抽取条目用于关联匹配的名称集合。"""
    names: list[str] = []
    if type_name == "formulas":
        names.append(data.get("name"))
        names.extend(data.get("aliases") or [])
        for comp in data.get("composition") or []:
            if isinstance(comp, dict) and comp.get("name"):
                names.append(comp["name"])
    elif type_name in ("herbs", "diseases", "syndromes"):
        names.append(data.get("name"))
        names.extend(data.get("aliases") or [])
    elif type_name == "cases":
        names.extend([data.get("title"), data.get("disease"), data.get("syndrome")])
    elif type_name == "terms":
        names.append(data.get("term"))
    elif type_name == "dulong":
        names.append(data.get("disease"))
    # tips 无名称,跳过
    return [str(n).strip() for n in names if n]


def _match_names(src_names: list[str], cand_names: list[str]) -> list[str]:
    """名称相等优先,其次互相包含(长度>=2 避免单字误配)。"""
    if not src_names or not cand_names:
        return []
    matched: list[str] = []
    for s in src_names:
        for c in cand_names:
            if s == c:
                matched.append(s)
                break
    if not matched:
        for s in src_names:
            for c in cand_names:
                if len(s) >= 2 and len(c) >= 2 and (s in c or c in s):
                    matched.append(f"{s}≈{c}")
    # 去重、截断
    return list(dict.fromkeys(matched))[:5]


async def _seed_classics(db: AsyncSession) -> int:
    """按 (book, article, original) 幂等合并导入种子条文(已存在的跳过)。"""
    from pathlib import Path as _P
    import json as _j

    p = _P(__file__).resolve().parent.parent.parent / "data" / "classics_seed.json"
    data = _j.loads(p.read_text(encoding="utf-8"))
    rows = (await db.execute(select(KbClassic.book, KbClassic.article, KbClassic.original))).all()
    existing = {(b, a, o) for b, a, o in rows}
    added = 0
    for c in data["classics"]:
        key = (c.get("book", ""), c.get("article", ""), c.get("original", ""))
        if key in existing:
            continue
        db.add(KbClassic(**{k: c.get(k, "") for k in ("book", "chapter", "article", "original", "plain", "source")}))
        existing.add(key)
        added += 1
    if added:
        await db.commit()
    return added


async def _seed_yifang(db: AsyncSession) -> int:
    """方剂库种子幂等 upsert(按方名;已存在则更新,便于维护数据文件后重部署刷新)。"""
    from pathlib import Path as _P
    import json as _j

    p = _P(__file__).resolve().parent.parent.parent / "data" / "yifang_seed.json"
    data = _j.loads(p.read_text(encoding="utf-8"))
    rows = (await db.execute(select(KbYifang))).scalars().all()
    by_name = {r.name: r for r in rows}
    added = 0
    for f in data["formulas"]:
        name = f.get("name")
        if not name:
            continue
        obj = by_name.get(name)
        if obj is None:
            db.add(KbYifang(
                name=name, category=f.get("category", ""), aliases=f.get("aliases", []),
                composition=f.get("composition", []), function=f.get("function", ""),
                indications=f.get("indications", ""), contraindications=f.get("contraindications", ""),
                source=f.get("source", ""),
            ))
            added += 1
        else:
            obj.category = f.get("category", obj.category)
            obj.aliases = f.get("aliases", obj.aliases)
            obj.composition = f.get("composition", obj.composition)
            obj.function = f.get("function", obj.function)
            obj.indications = f.get("indications", obj.indications)
            obj.contraindications = f.get("contraindications", obj.contraindications)
            obj.source = f.get("source", obj.source)
    await db.commit()
    return added


@router.get("/classics")
async def kb_classics(
    q: Optional[str] = Query(None, description="检索词(原文/白话/条文号)"),
    book: Optional[str] = Query(None, description="典籍名"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """经典典籍条文检索。"""
    await _seed_classics(db)
    stmt = select(KbClassic)
    if book:
        stmt = stmt.where(KbClassic.book == book)
    if q:
        like = f"%{_escape_like(q)}%"
        stmt = stmt.where(or_(KbClassic.original.ilike(like, escape="\\"), KbClassic.plain.ilike(like, escape="\\"), KbClassic.article.ilike(like, escape="\\")))
    rows = (await db.execute(stmt.order_by(KbClassic.created_at).limit(limit))).scalars().all()
    return {"total": len(rows), "items": [_serialize(r) for r in rows]}

@router.get("/{type}")
async def kb_list(
    type: str,
    q: Optional[str] = Query(None, description="检索词"),
    module: Optional[str] = Query(None, description="专科: surgery/anorectal/pediatrics/alchemy"),
    category: Optional[str] = Query(None, description="分类过滤"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """各类型列表(统一返回 {total, items})。"""
    model = _get_model(type)
    if type == "yifang":
        await _seed_yifang(db)
    filters = []
    if module and "module" in model.__table__.columns:
        filters.append(model.module == module)
    if category and hasattr(model, "category"):
        filters.append(model.category == category)
    if q:
        conds = [_ilike(getattr(model, field), q) for field, _ in SEARCH_FIELDS[type]]
        filters.append(or_(*conds))

    total = (await db.execute(
        select(func.count()).select_from(model).where(*filters)
    )).scalar() or 0
    stmt = (
        select(model)
        .where(*filters)
        .order_by(model.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    items = [_serialize(obj) for obj in (await db.execute(stmt)).scalars().all()]
    return {"total": total, "items": items}


@router.get("/{type}/{id}")
async def kb_detail(
    type: str,
    id: str,
    db: AsyncSession = Depends(get_db),
):
    """详情。"""
    model = _get_model(type)
    try:
        uid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的 ID(UUID)")
    obj = (await db.execute(select(model).where(model.id == uid))).scalar_one_or_none()
    if obj is None:
        raise HTTPException(status_code=404, detail="条目不存在")
    return _serialize(obj)
