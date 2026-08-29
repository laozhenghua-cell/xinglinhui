"""
直接创建诊断相关表的迁移脚本
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import AsyncSessionLocal


async def migrate():
    """创建诊断相关表"""
    async with AsyncSessionLocal() as session:
        print("开始创建诊断系统表...")

        # 创建症状字典表
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS symptom_dictionary (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                category VARCHAR(50) NOT NULL,
                subcategory VARCHAR(50),
                name VARCHAR(100) NOT NULL,
                display_name VARCHAR(100),
                options JSONB,
                weight INTEGER DEFAULT 1,
                description TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✅ symptom_dictionary 表已创建")

        # 创建辨证规则表
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS syndrome_rules (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                disease_type VARCHAR(50) NOT NULL,
                syndrome_name VARCHAR(100) NOT NULL,
                syndrome_code VARCHAR(50),
                required_symptoms JSONB,
                optional_symptoms JSONB,
                tongue_pulse JSONB,
                treatment_principle TEXT NOT NULL,
                recommended_formulas JSONB,
                confidence_threshold FLOAT DEFAULT 0.6,
                modification_rules JSONB,
                priority INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✅ syndrome_rules 表已创建")

        # 为consultations表添加新字段
        try:
            await session.execute(text("""
                ALTER TABLE consultations
                ADD COLUMN IF NOT EXISTS four_examinations JSONB DEFAULT '{}'::jsonb
            """))
            print("✅ consultations.four_examinations 字段已添加")
        except Exception as e:
            print(f"⚠️  four_examinations 字段可能已存在: {e}")

        try:
            await session.execute(text("""
                ALTER TABLE consultations
                ADD COLUMN IF NOT EXISTS selected_symptoms JSONB DEFAULT '{}'::jsonb
            """))
            print("✅ consultations.selected_symptoms 字段已添加")
        except Exception as e:
            print(f"⚠️  selected_symptoms 字段可能已存在: {e}")

        try:
            await session.execute(text("""
                ALTER TABLE consultations
                ADD COLUMN IF NOT EXISTS syndrome_result JSONB DEFAULT '{}'::jsonb
            """))
            print("✅ consultations.syndrome_result 字段已添加")
        except Exception as e:
            print(f"⚠️  syndrome_result 字段可能已存在: {e}")

        try:
            await session.execute(text("""
                ALTER TABLE consultations
                ADD COLUMN IF NOT EXISTS formula_modifications TEXT
            """))
            print("✅ consultations.formula_modifications 字段已添加")
        except Exception as e:
            print(f"⚠️  formula_modifications 字段可能已存在: {e}")

        await session.commit()
        print("\n🎉 数据库迁移完成！")


if __name__ == "__main__":
    asyncio.run(migrate())
