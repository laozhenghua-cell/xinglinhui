"""
创建Phase 4新表的数据库迁移脚本
- diagnosis_records: 辨证记录表
- symptom_templates: 症状模板表
- safety_rules: 用药安全规则表
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.database import Base
from app.models import DiagnosisRecord, SymptomTemplate, SafetyRule

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://zhilou_user:Zhilou2024!@db:5432/zhilou_clinic")

async def run_migration():
    """运行数据库迁移"""
    engine = create_async_engine(DATABASE_URL, echo=True)

    print("开始创建Phase 4新表...")

    async with engine.begin() as conn:
        # 创建新表
        await conn.run_sync(DiagnosisRecord.__table__.create, checkfirst=True)
        print("✅ 创建 diagnosis_records 表成功")

        await conn.run_sync(SymptomTemplate.__table__.create, checkfirst=True)
        print("✅ 创建 symptom_templates 表成功")

        await conn.run_sync(SafetyRule.__table__.create, checkfirst=True)
        print("✅ 创建 safety_rules 表成功")

    await engine.dispose()
    print("\n🎉 Phase 4 数据库迁移完成！")

if __name__ == "__main__":
    asyncio.run(run_migration())
