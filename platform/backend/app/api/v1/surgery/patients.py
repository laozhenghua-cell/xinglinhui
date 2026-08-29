"""患者档案管理 —— 复用基座 patients 表(不新建手术患者表)。

说明：基座 patients 表为 UUID 主键、tenant_id 必填、无 ``note`` 字段(对应
``notes``)、且与疮疡病例无关系，因此响应与旧版有两点差异：
    1) ``id`` 为 UUID；2) ``cases`` 恒为空列表。
疮疡病例本身通过 ``patient_name`` 反规范化存储，不依赖本表。
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.open_access import public_tenant_id
from app.database import get_db
from app.models.patient import Patient
from app.schemas.surgery import PatientCreate, PatientOut

router = APIRouter(prefix="/api/v1/surgery/patients", tags=["疮疡-患者"])


def _to_out(p: Patient) -> PatientOut:
    return PatientOut(
        id=p.id,
        name=p.name,
        gender=p.gender,
        age=p.age,
        phone=p.phone,
        note=p.notes,
        created_at=p.created_at,
        cases=[],
    )


@router.get("", response_model=list[PatientOut])
async def list_patients(
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Patient).where(Patient.tenant_id == public_tenant_id())
    if search:
        stmt = stmt.where(or_(Patient.name.ilike(f"%{search}%"), Patient.phone.ilike(f"%{search}%")))
    stmt = stmt.order_by(Patient.created_at.desc())
    result = await db.execute(stmt)
    return [_to_out(p) for p in result.scalars().all()]


@router.post("", response_model=PatientOut)
async def create_patient(body: PatientCreate, request: Request, db: AsyncSession = Depends(get_db)):
    limit_write(request)
    patient = Patient(
        tenant_id=public_tenant_id(),
        name=body.name,
        gender=body.gender,
        age=body.age,
        phone=body.phone,
        notes=body.note,
    )
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return _to_out(patient)


@router.get("/{patient_id}", response_model=PatientOut)
async def get_patient(patient_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    patient = await db.get(Patient, patient_id)
    if not patient or patient.tenant_id != public_tenant_id():
        raise HTTPException(status_code=404, detail="患者不存在")
    return _to_out(patient)
