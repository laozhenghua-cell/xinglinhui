"""全开放模式(OPEN_ACCESS)的"公开租户 / 公开用户"保障。

当 ``settings.OPEN_ACCESS`` 为 true 且请求未携带 Authorization 头时，
``get_current_user`` 会降级到这里的公开用户；启动时 ``init_db`` 也会
调用 :func:`ensure_public_user` 提前建好，避免首个请求的并发竞争。

公开租户 / 公开用户使用固定的 UUID 作为主键，天然幂等：
    - 公开租户 id: 00000000-0000-0000-0000-000000000001
    - 公开用户 id: 00000000-0000-0000-0000-000000000002
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.models.user import User

if TYPE_CHECKING:  # pragma: no cover - 仅类型提示
    pass

PUBLIC_TENANT_NAME = "公开诊所"
PUBLIC_TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

PUBLIC_USER_EMAIL = "open@tcm-platform.local"
PUBLIC_USER_NAME = "访客"
PUBLIC_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")

# 公开用户不可登录，密码为一个不可逆的占位哈希（bcrypt 对随机串）。
# 惰性生成，避免模块导入时付出 bcrypt 成本。
_public_password_hash: str | None = None


def _get_public_password_hash() -> str:
    global _public_password_hash
    if _public_password_hash is None:
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        _public_password_hash = pwd_context.hash(f"open-access-{uuid.uuid4().hex}")
    return _public_password_hash


async def ensure_public_user(db: AsyncSession) -> User:
    """确保公开租户与公开用户存在并返回该用户（幂等、并发安全）。"""
    tenant = await db.get(Tenant, PUBLIC_TENANT_ID)
    if tenant is None:
        tenant = Tenant(id=PUBLIC_TENANT_ID, name=PUBLIC_TENANT_NAME, plan="open")
        db.add(tenant)
        try:
            await db.flush()
        except IntegrityError:
            # 并发初始化：他人已建，回滚本次并复用已有记录
            await db.rollback()
            tenant = await db.get(Tenant, PUBLIC_TENANT_ID)

    user = await db.get(User, PUBLIC_USER_ID)
    if user is None:
        user = User(
            id=PUBLIC_USER_ID,
            tenant_id=PUBLIC_TENANT_ID,
            email=PUBLIC_USER_EMAIL,
            name=PUBLIC_USER_NAME,
            hashed_password=_get_public_password_hash(),
            role="doctor",
            is_active=True,
        )
        db.add(user)
        try:
            await db.flush()
        except IntegrityError:
            await db.rollback()
            user = (
                await db.execute(select(User).where(User.email == PUBLIC_USER_EMAIL))
            ).scalar_one()

    return user


def public_tenant_id() -> uuid.UUID:
    """公开租户的固定 UUID（供疮疡等免鉴权模块写入患者/记录时使用）。"""
    return PUBLIC_TENANT_ID
