from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from pydantic import BaseModel, EmailStr
from typing import Optional

from ...core.database import get_db
from ...core.security import verify_password, create_access_token, hash_password
from ...models.user import User
from ...models.expert_profile import ExpertProfile

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "doctor"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
async def register(
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    role: str = Form("doctor"),
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    # Check if email exists
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = User(
        email=email,
        hashed_password=hash_password(password),
        name=name,
        role=role,
        is_active=True,
        is_verified=False
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # If expert, create expert profile
    if role == "expert":
        expert_profile = ExpertProfile(user_id=user.id)
        db.add(expert_profile)
        await db.commit()

    # Generate token
    access_token = create_access_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    }


@router.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    # Find user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Generate token
    access_token = create_access_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "hospital": user.hospital
        }
    }


@router.get("/me")
async def get_current_user_info(
    user: User = Depends(get_db)
):
    """获取当前用户信息"""
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "hospital": user.hospital,
        "department": user.department,
        "is_verified": user.is_verified
    }
