"""统一门诊模块(跨专科就诊,免登录设备级)

POST /api/v1/clinic/visits            新建就诊
GET  /api/v1/clinic/visits            就诊列表(本设备)
GET  /api/v1/clinic/visits/{id}       就诊详情
PUT  /api/v1/clinic/visits/{id}       更新(处方/随访)
GET  /api/v1/clinic/dashboard         工作台聚合
"""
from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from datetime import date, timedelta
import json as _json
import csv as _csv
from io import StringIO
from urllib.parse import quote
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.clinic import ClinicVisit
from app.models.kb import KBFormula
from app.models.visit import Visit

router = APIRouter(prefix="/clinic", tags=["统一门诊"])

SPECIALTIES = {"surgery": "外科疮疡", "anorectal": "肛肠痔漏", "pediatrics": "儿科", "alchemy": "丹药研究"}


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


class VisitIn(BaseModel):
    patient_name: str = Field(..., min_length=1, max_length=100)
    gender: str = ""
    age: Optional[int] = None
    specialty: str
    chief_complaint: str = ""
    four_diagnosis: dict = Field(default_factory=dict)
    dx_result: dict = Field(default_factory=dict)
    prescription: dict = Field(default_factory=dict)
    followup: dict = Field(default_factory=dict)


@router.post("/visits")
async def create_visit(body: VisitIn, request: Request, db: AsyncSession = Depends(get_db)):
    if body.specialty not in SPECIALTIES:
        raise HTTPException(status_code=400, detail="未知专科")
    v = ClinicVisit(
        patient_name=body.patient_name,
        gender=body.gender,
        age=body.age,
        specialty=body.specialty,
        chief_complaint=body.chief_complaint,
        four_diagnosis=body.four_diagnosis,
        dx_result=body.dx_result,
        prescription=body.prescription,
        followup=body.followup,
        device=_device(request),
    )
    db.add(v)
    await db.commit()
    return _serialize(v)


@router.get("/visits")
async def list_visits(
    request: Request,
    specialty: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ClinicVisit).where(ClinicVisit.device == _device(request))
    if specialty:
        stmt = stmt.where(ClinicVisit.specialty == specialty)
    if q:
        stmt = stmt.where(ClinicVisit.patient_name.ilike(f"%{q}%"))
    rows = (
        await db.execute(stmt.order_by(desc(ClinicVisit.created_at)).limit(limit))
    ).scalars().all()
    return {"total": len(rows), "items": [_serialize(r) for r in rows]}


@router.get("/visits/{visit_id}")
async def get_visit(visit_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        uid = uuid.UUID(visit_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效 ID")
    v = (
        await db.execute(
            select(ClinicVisit).where(ClinicVisit.id == uid, ClinicVisit.device == _device(request))
        )
    ).scalar_one_or_none()
    if v is None:
        raise HTTPException(status_code=404, detail="就诊不存在")
    return _serialize(v)


class VisitUpdate(BaseModel):
    prescription: Optional[dict] = None
    followup: Optional[dict] = None


@router.put("/visits/{visit_id}")
async def update_visit(
    visit_id: str, body: VisitUpdate, request: Request, db: AsyncSession = Depends(get_db)
):
    try:
        uid = uuid.UUID(visit_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效 ID")
    v = (
        await db.execute(
            select(ClinicVisit).where(ClinicVisit.id == uid, ClinicVisit.device == _device(request))
        )
    ).scalar_one_or_none()
    if v is None:
        raise HTTPException(status_code=404, detail="就诊不存在")
    if body.prescription is not None:
        v.prescription = body.prescription
    if body.followup is not None:
        v.followup = body.followup
    await db.commit()
    return _serialize(v)


@router.get("/visits/{visit_id}/pdf")
async def visit_pdf(visit_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """处方笺 PDF(打印/下载)。"""
    try:
        uid = uuid.UUID(visit_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效 ID")
    v = (
        await db.execute(
            select(ClinicVisit).where(ClinicVisit.id == uid, ClinicVisit.device == _device(request))
        )
    ).scalar_one_or_none()
    if v is None:
        raise HTTPException(status_code=404, detail="就诊不存在")
    from app.services.clinic_pdf import build_clinic_pdf

    pdf = build_clinic_pdf(_serialize(v))
    fname_ascii = f"xinglin-rx-{v.created_at.strftime('%Y%m%d') if v.created_at else 'rx'}.pdf"
    fname_utf8 = quote(f"杏林汇处方-{v.patient_name}.pdf")
    return Response(
        content=pdf, media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=\"{fname_ascii}\"; filename*=UTF-8''{fname_utf8}"},
    )


@router.get("/followups")
async def followups(
    request: Request,
    days: int = Query(14, ge=0, le=365),
    db: AsyncSession = Depends(get_db),
):
    """随访提醒:本设备就诊中已设复诊日期且未完成的记录(逾期 + 未来 days 天内)。"""
    rows = (
        await db.execute(
            select(ClinicVisit).where(ClinicVisit.device == _device(request)).order_by(desc(ClinicVisit.created_at)).limit(300)
        )
    ).scalars().all()
    today = date.today()
    items = []
    for v in rows:
        fu = v.followup or {}
        fdate = fu.get("followup_date") or ""
        if fu.get("done") or not fdate:
            continue
        try:
            d = date.fromisoformat(str(fdate)[:10])
        except ValueError:
            continue
        delta = (d - today).days
        if delta <= days:
            items.append({
                "visit_id": str(v.id),
                "patient_name": v.patient_name,
                "specialty": v.specialty,
                "chief_complaint": v.chief_complaint,
                "followup_date": str(fdate)[:10],
                "overdue": delta < 0,
                "days_left": delta,
                "note": fu.get("note") or "",
            })
    items.sort(key=lambda x: x["followup_date"])
    return {"total": len(items), "items": items}


@router.get("/export")
async def export_visits(
    request: Request,
    format: str = Query("csv", pattern="^(csv|json)$"),
    db: AsyncSession = Depends(get_db),
):
    """就诊数据导出(CSV 带 UTF-8 BOM 兼容 Excel / JSON)。"""
    rows = (
        await db.execute(
            select(ClinicVisit).where(ClinicVisit.device == _device(request)).order_by(desc(ClinicVisit.created_at)).limit(1000)
        )
    ).scalars().all()
    spec_names = {k: v for k, v in SPECIALTIES.items()}
    data = []
    for v in rows:
        dx = v.dx_result or {}
        rx = v.prescription or {}
        fu = v.followup or {}
        data.append({
            "时间": (v.created_at.isoformat() if v.created_at else ""),
            "患者": v.patient_name,
            "性别": v.gender or "",
            "年龄": str(v.age) if v.age is not None else "",
            "专科": spec_names.get(v.specialty, v.specialty),
            "主诉": v.chief_complaint or "",
            "证型": "、".join(s.get("name", "") for s in dx.get("syndromes") or []),
            "病种": "、".join(d.get("name", "") for d in dx.get("diseases") or []),
            "方剂": "、".join(rx.get("formulas") or []),
            "加减": rx.get("modification") or "",
            "外治": rx.get("external") or "",
            "医嘱": rx.get("advice") or "",
            "随访": fu.get("note") or "",
            "复诊日期": fu.get("followup_date") or "",
        })
    if format == "json":
        return Response(
            content=_json.dumps(data, ensure_ascii=False, indent=1),
            media_type="application/json",
            headers={"Content-Disposition": 'attachment; filename="xinglin-visits.json"'},
        )
    buf = StringIO()
    writer = _csv.DictWriter(buf, fieldnames=list(data[0].keys()) if data else [])
    writer.writeheader()
    writer.writerows(data)
    csv_text = "\ufeff" + buf.getvalue()  # BOM for Excel
    return Response(
        content=csv_text.encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="xinglin-visits.csv"'},
    )


@router.get("/dashboard")
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    dev = _device(request)
    visits = (
        await db.execute(select(ClinicVisit).where(ClinicVisit.device == dev))
    ).scalars().all()
    today = datetime.now(timezone.utc).date()
    today_n = sum(1 for v in visits if v.created_at and v.created_at.date() == today)
    by_spec: dict[str, int] = {}
    for v in visits:
        by_spec[v.specialty] = by_spec.get(v.specialty, 0) + 1
    # 平台级统计
    pv = (await db.execute(select(func.count()).select_from(Visit))).scalar() or 0
    uv = (
        await db.execute(
            select(func.count(func.distinct(func.concat(Visit.ip_hash, ":", Visit.ua_hash)))).select_from(Visit)
        )
    ).scalar() or 0
    kb_counts = {
        "formulas": (await db.execute(select(func.count()).select_from(KBFormula))).scalar() or 0,
    }
    return {
        "my_visits_total": len(visits),
        "my_visits_today": today_n,
        "by_specialty": by_spec,
        "platform": {"pv": pv, "uv": uv, "kb_formulas": kb_counts["formulas"]},
        "specialties": SPECIALTIES,
        "recent": [_serialize(v) for v in sorted(visits, key=lambda x: x.created_at, reverse=True)[:6]],
    }
