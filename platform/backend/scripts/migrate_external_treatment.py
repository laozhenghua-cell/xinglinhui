"""
创建外治法数据表
Migration: Create external_treatments tables
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import AsyncSessionLocal


async def create_external_treatment_tables():
    """创建外治法相关数据表"""

    # 分离SQL语句，每次执行一条
    sqls = [
        # 创建 external_treatments 表
        """
        CREATE TABLE IF NOT EXISTS external_treatments (
            id UUID PRIMARY KEY,
            tenant_id UUID REFERENCES tenants(id),
            name VARCHAR(200) NOT NULL,
            treatment_type VARCHAR(30) NOT NULL,
            composition JSONB DEFAULT '[]',
            preparation TEXT,
            usage TEXT NOT NULL,
            frequency VARCHAR(100),
            duration VARCHAR(100),
            function TEXT,
            indications TEXT,
            syndrome_types JSONB DEFAULT '[]',
            disease_types JSONB DEFAULT '[]',
            contraindications TEXT,
            precautions TEXT,
            source VARCHAR(200),
            priority INTEGER DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """,
        "CREATE INDEX IF NOT EXISTS idx_external_treatments_name ON external_treatments(name)",
        "CREATE INDEX IF NOT EXISTS idx_external_treatments_type ON external_treatments(treatment_type)",
        "CREATE INDEX IF NOT EXISTS idx_external_treatments_tenant ON external_treatments(tenant_id)",

        # 创建 external_treatment_records 表
        """
        CREATE TABLE IF NOT EXISTS external_treatment_records (
            id UUID PRIMARY KEY,
            tenant_id UUID NOT NULL REFERENCES tenants(id),
            patient_id UUID NOT NULL REFERENCES patients(id),
            consultation_id UUID REFERENCES consultations(id),
            treatment_id UUID NOT NULL REFERENCES external_treatments(id),
            treatment_name VARCHAR(200) NOT NULL,
            treatment_type VARCHAR(30) NOT NULL,
            usage_instruction TEXT,
            prescribed_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """,
        "CREATE INDEX IF NOT EXISTS idx_external_records_tenant ON external_treatment_records(tenant_id)",
        "CREATE INDEX IF NOT EXISTS idx_external_records_patient ON external_treatment_records(patient_id)",
        "CREATE INDEX IF NOT EXISTS idx_external_records_consultation ON external_treatment_records(consultation_id)"
    ]

    async with AsyncSessionLocal() as session:
        try:
            print("🔧 开始创建外治法数据表...")

            # 逐条执行SQL
            for sql in sqls:
                await session.execute(text(sql))

            print("✅ external_treatments 表创建完成")
            print("✅ external_treatment_records 表创建完成")

            await session.commit()
            print("\n🎉 外治法数据表创建成功！")

        except Exception as e:
            await session.rollback()
            print(f"❌ 创建失败：{str(e)}")
            raise


if __name__ == "__main__":
    print("="*60)
    print("外治法数据表迁移脚本")
    print("="*60)
    asyncio.run(create_external_treatment_tables())
