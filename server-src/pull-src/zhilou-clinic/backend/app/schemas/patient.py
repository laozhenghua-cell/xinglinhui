import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class PatientCreate(BaseModel):
    name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    id_card: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    tags: Optional[List[str]] = []
    occupation: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    id_card: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    tags: Optional[List[str]] = None
    occupation: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class PatientResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    id_card: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    tags: Optional[List[str]] = []
    occupation: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PatientListResponse(BaseModel):
    total: int
    items: List[PatientResponse]
