"""
医案库表结构迁移脚本
经典医案数据库设计
"""
import asyncio
from sqlalchemy import text
from app.database import AsyncSessionLocal


CREATE_MEDICAL_CASES_TABLE = """
CREATE TABLE IF NOT EXISTS medical_cases (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),

    -- 基本信息
    case_number VARCHAR(50) UNIQUE NOT NULL,
    case_title VARCHAR(200) NOT NULL,
    source VARCHAR(100) DEFAULT '临床经验',
    case_date DATE,

    -- 患者信息
    patient_info JSONB DEFAULT '{}',  -- {age, gender, occupation, chief_complaint, duration}

    -- 四诊信息
    inspection JSONB DEFAULT '{}',    -- 望诊数据
    auscultation JSONB DEFAULT '{}',  -- 闻诊数据
    inquiry JSONB DEFAULT '{}',       -- 问诊数据
    palpation JSONB DEFAULT '{}',     -- 切诊数据

    -- 辨证过程
    disease_type VARCHAR(50) NOT NULL,
    syndrome_analysis TEXT,           -- 辨证分析过程
    syndrome_type VARCHAR(100),       -- 最终证型
    treatment_principle VARCHAR(200), -- 治则

    -- 治疗方案
    internal_formula JSONB DEFAULT '{}',  -- 内服方剂 {name, composition, dosage, modifications}
    external_treatment JSONB DEFAULT '[]', -- 外治法 [{name, usage, frequency}]
    other_treatments TEXT,                 -- 其他治疗

    -- 疗效追踪
    follow_ups JSONB DEFAULT '[]',    -- 复诊记录 [{date, symptoms_change, adjustment, notes}]
    outcome VARCHAR(50),              -- 疗效：痊愈/显效/好转/无效
    outcome_notes TEXT,               -- 疗效说明

    -- 教学要点
    key_points TEXT,                  -- 点评/关键要点
    teaching_notes TEXT,              -- 教学说明
    tags JSONB DEFAULT '[]',          -- 标签：['典型案例', '疑难病例', '创新疗法']

    -- 元数据
    is_classic BOOLEAN DEFAULT FALSE, -- 是否经典案例
    difficulty_level INTEGER DEFAULT 2, -- 难度：1简单 2中等 3困难
    view_count INTEGER DEFAULT 0,
    reference_count INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_medical_cases_tenant ON medical_cases(tenant_id);
CREATE INDEX IF NOT EXISTS idx_medical_cases_disease ON medical_cases(disease_type);
CREATE INDEX IF NOT EXISTS idx_medical_cases_syndrome ON medical_cases(syndrome_type);
CREATE INDEX IF NOT EXISTS idx_medical_cases_classic ON medical_cases(is_classic) WHERE is_classic = TRUE;
CREATE INDEX IF NOT EXISTS idx_medical_cases_tags ON medical_cases USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_medical_cases_date ON medical_cases(case_date DESC);

-- 全文搜索索引（症状描述）
CREATE INDEX IF NOT EXISTS idx_medical_cases_inquiry_gin ON medical_cases USING GIN(inquiry);

COMMENT ON TABLE medical_cases IS '经典医案库';
COMMENT ON COLUMN medical_cases.case_number IS '案例编号，如：ZJM-ZC-001';
COMMENT ON COLUMN medical_cases.syndrome_analysis IS '辨证分析过程（教学重点）';
COMMENT ON COLUMN medical_cases.key_points IS '点评与关键要点';
"""


CREATE_CASE_SIMILARITY_INDEX = """
-- 创建症状相似度匹配所需的GIN索引
CREATE INDEX IF NOT EXISTS idx_medical_cases_symptoms_gin
ON medical_cases USING GIN(
    (inquiry || inspection || palpation)
);
"""


async def migrate():
    """执行医案库表结构迁移"""
    async with AsyncSessionLocal() as db:
        print("=" * 60)
        print("开始创建医案库表结构")
        print("=" * 60)

        try:
            # 拆分SQL语句，逐条执行
            statements = [s.strip() for s in CREATE_MEDICAL_CASES_TABLE.split(';') if s.strip()]

            for i, stmt in enumerate(statements, 1):
                if stmt:
                    await db.execute(text(stmt))
                    if 'CREATE TABLE' in stmt:
                        print(f"✅ 步骤 {i}: 医案表创建成功")
                    elif 'CREATE INDEX' in stmt:
                        print(f"✅ 步骤 {i}: 索引创建成功")
                    elif 'COMMENT' in stmt:
                        print(f"✅ 步骤 {i}: 注释添加成功")

            # 创建相似度索引
            await db.execute(text(CREATE_CASE_SIMILARITY_INDEX.strip()))
            print("✅ 症状相似度索引创建成功")

            await db.commit()
            print("\n" + "=" * 60)
            print("✅ 医案库表结构迁移完成")
            print("=" * 60)

        except Exception as e:
            await db.rollback()
            print(f"\n❌ 迁移失败：{e}")
            raise


if __name__ == "__main__":
    asyncio.run(migrate())
