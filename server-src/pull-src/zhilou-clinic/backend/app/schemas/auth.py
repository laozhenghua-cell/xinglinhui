import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    clinic_name: str
    phone: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserInfo"


class UserInfo(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    tenant_id: uuid.UUID

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    phone: Optional[str] = None
    tenant_id: uuid.UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
