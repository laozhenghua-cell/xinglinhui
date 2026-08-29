"""数据库引擎与会话"""
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.database_url, echo=False)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    """FastAPI 依赖:提供数据库会话"""
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    """建表(幂等) + 轻量迁移(补充后加字段,兼容已有库)"""
    import os

    if settings.database_url.startswith("sqlite"):
        # 确保 SQLite 数据目录存在
        db_path = settings.database_url.split("///")[-1]
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_migrate)


def _migrate(conn) -> None:
    """为已存在的旧库补充后加列(create_all 不会改动已有表)。"""
    from sqlalchemy import inspect, text

    insp = inspect(conn)

    cols = {c["name"] for c in insp.get_columns("formulas")}
    if "indication" not in cols:
        conn.execute(text("ALTER TABLE formulas ADD COLUMN indication TEXT"))
    if "toxicity" not in cols:
        conn.execute(text("ALTER TABLE formulas ADD COLUMN toxicity VARCHAR(10)"))

    cols = {c["name"] for c in insp.get_columns("diseases")}
    if "differentiation" not in cols:
        conn.execute(text("ALTER TABLE diseases ADD COLUMN differentiation VARCHAR(20)"))
