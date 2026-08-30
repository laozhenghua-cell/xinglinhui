"""词库管理 API:口语→证候标签映射的可视化管理。

GET  /api/v1/admin/synonyms          列出全部词条
POST /api/v1/admin/synonyms          新增/更新 {keyword, labels:[...]}
DELETE /api/v1/admin/synonyms/{kw}   删除词条
"""
from __future__ import annotations

from pathlib import Path
import json as _j

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.surgery_security import limit_write
from app.database import get_db
from app.models.kb import KbSynonym

router = APIRouter(prefix="/admin", tags=["词库管理"])


class SynonymIn(BaseModel):
    keyword: str
    labels: list[str]


async def _seed_synonyms(db: AsyncSession) -> int:
    """首次访问时从 data/synonyms.json 导入缺失词条(不覆盖后台已改条目)。"""
    p = Path(__file__).resolve().parent.parent.parent / "data" / "synonyms.json"
    try:
        data = _j.loads(p.read_text(encoding="utf-8"))["synonyms"]
    except Exception:
        return 0
    rows = (await db.execute(select(KbSynonym.keyword))).scalars().all()
    existing = set(rows)
    added = 0
    for kw, labels in data.items():
        if kw in existing:
            continue
        db.add(KbSynonym(keyword=kw, labels=list(labels)))
        existing.add(kw)
        added += 1
    if added:
        await db.commit()
    return added


async def _syn_map(db: AsyncSession) -> dict:
    await _seed_synonyms(db)
    rows = (await db.execute(select(KbSynonym))).scalars().all()
    return {r.keyword: (r.labels or []) for r in rows}


@router.get("/synonyms")
async def list_synonyms(
    q: str = Query("", description="按关键词过滤"),
    db: AsyncSession = Depends(get_db),
):
    await _seed_synonyms(db)
    stmt = select(KbSynonym).order_by(KbSynonym.keyword)
    if q:
        stmt = stmt.where(KbSynonym.keyword.ilike(f"%{q}%"))
    rows = (await db.execute(stmt)).scalars().all()
    return {
        "total": len(rows),
        "items": [{"keyword": r.keyword, "labels": r.labels or []} for r in rows],
    }


@router.post("/synonyms")
async def upsert_synonym(body: SynonymIn, request: Request, db: AsyncSession = Depends(get_db)):
    limit_write(request)
    kw = (body.keyword or "").strip()
    labels = [str(x).strip() for x in body.labels if str(x).strip()]
    if not kw or not labels:
        raise HTTPException(status_code=400, detail="关键词与标签不能为空")
    await _seed_synonyms(db)
    row = (await db.execute(select(KbSynonym).where(KbSynonym.keyword == kw))).scalars().first()
    if row:
        row.labels = labels
    else:
        db.add(KbSynonym(keyword=kw, labels=labels))
    await db.commit()
    from app.services.dx_systems import invalidate_synonyms_cache

    invalidate_synonyms_cache()
    return {"ok": True, "keyword": kw, "labels": labels}


@router.delete("/synonyms/{keyword}")
async def delete_synonym(keyword: str, request: Request, db: AsyncSession = Depends(get_db)):
    limit_write(request)
    row = (await db.execute(select(KbSynonym).where(KbSynonym.keyword == keyword))).scalars().first()
    if row:
        await db.delete(row)
        await db.commit()
    from app.services.dx_systems import invalidate_synonyms_cache

    invalidate_synonyms_cache()
    return {"ok": True}
