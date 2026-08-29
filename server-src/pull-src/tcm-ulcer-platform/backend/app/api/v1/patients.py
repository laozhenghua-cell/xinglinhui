from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional
from datetime import datetime

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User
from ...models.patient import Patient

router = APIRouter()


@router.post("")
async def create_patient(
    name: str,
    gender: str,
    age: Optional[int] = None,
    phone: Optional[str] = None,
    birth_date: Optional[str] = None,
    address: Optional[str] = None,
    allergies: Optional[str] = None,
    medical_history: Optional[str] = None,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建患者档案"""

    patient = Patient(
        name=name,
        gender=gender,
        age=age,
        phone=phone,
        birth_date=datetime.strptime(birth_date, "%Y-%m-%d").date() if birth_date else None,
        address=address,
        allergies=allergies,
        medical_history=medical_history,
        notes=notes
    )

    db.add(patient)
    await db.commit()
    await db.refresh(patient)

    return {
        "id": patient.id,
        "name": patient.name,
        "gender": patient.gender,
        "age": patient.age,
        "created_at": patient.created_at
    }


@router.get("")
async def list_patients(
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取患者列表"""

    query = select(Patient)

    if search:
        query = query.where(
            (Patient.name.contains(search)) |
            (Patient.phone.contains(search))
        )

    query = query.order_by(desc(Patient.created_at)).offset(skip).limit(limit)

    result = await db.execute(query)
    patients = result.scalars().all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "gender": p.gender,
            "age": p.age,
            "phone": p.phone,
            "created_at": p.created_at
        }
        for p in patients
    ]


@router.get("/{patient_id}")
async def get_patient_detail(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取患者详情"""

    result = await db.execute(
        select(Patient).where(Patient.id == patient_id)
    )
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {
        "id": patient.id,
        "name": patient.name,
        "gender": patient.gender,
        "age": patient.age,
        "birth_date": patient.birth_date,
        "phone": patient.phone,
        "address": patient.address,
        "allergies": patient.allergies,
        "medical_history": patient.medical_history,
        "notes": patient.notes,
        "created_at": patient.created_at,
        "updated_at": patient.updated_at
    }


@router.put("/{patient_id}")
async def update_patient(
    patient_id: str,
    name: Optional[str] = None,
    gender: Optional[str] = None,
    age: Optional[int] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    allergies: Optional[str] = None,
    medical_history: Optional[str] = None,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新患者信息"""

    result = await db.execute(
        select(Patient).where(Patient.id == patient_id)
    )
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if name is not None:
        patient.name = name
    if gender is not None:
        patient.gender = gender
    if age is not None:
        patient.age = age
    if phone is not None:
        patient.phone = phone
    if address is not None:
        patient.address = address
    if allergies is not None:
        patient.allergies = allergies
    if medical_history is not None:
        patient.medical_history = medical_history
    if notes is not None:
        patient.notes = notes

    await db.commit()

    return {"message": "Patient updated successfully"}
