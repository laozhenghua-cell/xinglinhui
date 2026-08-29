"""患者档案管理"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Case, CaseImage, Patient, TreatmentRecord
from ..schemas import PatientCreate, PatientOut

router = APIRouter(prefix="/api/v1/patients", tags=["patients"])


async def _get_patient(db: AsyncSession, patient_id: int) -> Patient:
    stmt = (
        select(Patient)
        .options(
            selectinload(Patient.cases).selectinload(Case.images),
            selectinload(Patient.cases).selectinload(Case.records).selectinload(TreatmentRecord.formula),
        )
        .where(Patient.id == patient_id)
    )
    patient = (await db.execute(stmt)).scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    return patient


@router.get("", response_model=list[PatientOut])
async def list_patients(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Patient)
        .options(
            selectinload(Patient.cases).selectinload(Case.images),
            selectinload(Patient.cases).selectinload(Case.records).selectinload(TreatmentRecord.formula),
        )
        .order_by(Patient.id.desc())
    )
    return list((await db.execute(stmt)).scalars().all())


@router.post("", response_model=PatientOut)
async def create_patient(body: PatientCreate, db: AsyncSession = Depends(get_db)):
    patient = Patient(**body.model_dump())
    db.add(patient)
    await db.commit()
    return await _get_patient(db, patient.id)


@router.get("/{patient_id}", response_model=PatientOut)
async def get_patient(patient_id: int, db: AsyncSession = Depends(get_db)):
    return await _get_patient(db, patient_id)
