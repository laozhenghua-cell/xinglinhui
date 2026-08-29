#!/usr/bin/env python3
"""
将疮疡知识种子数据导入数据库
"""
import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import async_session_maker
from app.models.ulcer_knowledge import UlcerKnowledge
from sqlalchemy import select


async def seed_ulcer_knowledge():
    """导入疮疡知识库数据"""
    # Load seed data
    seed_file = Path(__file__).parent.parent / "data" / "seed_data" / "ulcer_knowledge.json"

    if not seed_file.exists():
        print("❌ 种子数据文件不存在，请先运行 generate_seed_data.py")
        return

    with open(seed_file, 'r', encoding='utf-8') as f:
        ulcer_data = json.load(f)

    async with async_session_maker() as session:
        count = 0
        for data in ulcer_data:
            # Check if already exists
            stmt = select(UlcerKnowledge).where(UlcerKnowledge.ulcer_type == data['ulcer_type'])
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                print(f"⏭️  跳过已存在: {data['chinese_name']}")
                continue

            # Create new record
            ulcer = UlcerKnowledge(
                ulcer_type=data['ulcer_type'],
                chinese_name=data['chinese_name'],
                english_name=data.get('english_name'),
                aliases=data.get('aliases'),
                category=data['category'],
                location=data['location'],
                location_detail=data.get('location_detail'),
                etiology=data.get('etiology'),
                pathogenesis=data.get('pathogenesis'),
                morphology=data.get('morphology'),
                clinical_features=data.get('clinical_features'),
                systemic_symptoms=data.get('systemic_symptoms'),
                syndrome_types=data.get('syndrome_types'),
                treatment_principle=data.get('treatment_principle'),
                internal_treatment=data.get('internal_treatment'),
                external_treatment=data.get('external_treatment'),
                prevention=data.get('prevention'),
                nursing=data.get('nursing'),
                diet_advice=data.get('diet_advice'),
                prognosis=data.get('prognosis'),
                complications=data.get('complications'),
                differential_diagnosis=data.get('differential_diagnosis'),
                reference_images=data.get('reference_images'),
                source="疮疡图谱_10297907",
                page_number=data.get('page_number'),
                case_count=0
            )
            session.add(ulcer)
            count += 1
            print(f"✅ 导入: {data['chinese_name']}")

        await session.commit()

    print(f"\n🎉 成功导入 {count} 条疮疡知识数据！")


if __name__ == "__main__":
    asyncio.run(seed_ulcer_knowledge())
