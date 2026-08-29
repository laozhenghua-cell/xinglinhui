"""
创建演示租户和账号
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta, timezone
from app.database import AsyncSessionLocal, engine, Base
from app.models import Tenant, User
from app.core.security import hash_password
import uuid


async def init_demo():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 数据库表创建完成")

    async with AsyncSessionLocal() as session:
        # 创建演示租户
        tenant_id = uuid.uuid4()
        tenant = Tenant(
            id=tenant_id,
            name="痔瘘专科诊所（演示）",
            plan="pro",
            trial_end=datetime.now(timezone.utc) + timedelta(days=365),
        )
        session.add(tenant)

        # 创建管理员
        admin = User(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            email="admin@zhilou.com",
            name="管理员",
            hashed_password=hash_password("admin123456"),
            role="admin",
            is_active=True,
        )
        session.add(admin)

        # 创建医师
        doctor = User(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            email="doctor@zhilou.com",
            name="王医师",
            hashed_password=hash_password("doctor123456"),
            role="doctor",
            is_active=True,
        )
        session.add(doctor)

        # 创建收银员
        cashier = User(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            email="cashier@zhilou.com",
            name="收银员",
            hashed_password=hash_password("cashier123456"),
            role="cashier",
            is_active=True,
        )
        session.add(cashier)

        await session.commit()
        print(f"✅ 演示租户创建完成：{tenant.name}")
        print(f"   管理员：admin@zhilou.com / admin123456")
        print(f"   医师：doctor@zhilou.com / doctor123456")
        print(f"   收银：cashier@zhilou.com / cashier123456")


if __name__ == "__main__":
    asyncio.run(init_demo())
