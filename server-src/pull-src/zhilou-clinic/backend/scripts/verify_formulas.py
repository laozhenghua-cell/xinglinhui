import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.knowledge import AnorectalFormula

async def verify():
    async with AsyncSessionLocal() as session:
        # 检查枯痔散系列
        result = await session.execute(
            select(AnorectalFormula).where(AnorectalFormula.name.like('%枯痔%'))
        )
        kuozhi_formulas = result.scalars().all()
        print(f"✅ 枯痔散系列方剂: {len(kuozhi_formulas)} 首")
        for f in kuozhi_formulas:
            print(f"  - {f.name}")
            if f.notes:
                print(f"    制作方法: {'有' if len(f.notes) > 20 else '缺失'}")

        # 检查明矾注射液
        result = await session.execute(
            select(AnorectalFormula).where(AnorectalFormula.name.like('%明矾%'))
        )
        mingfan_formulas = result.scalars().all()
        print(f"\n✅ 明矾注射液系列: {len(mingfan_formulas)} 首")
        for f in mingfan_formulas:
            print(f"  - {f.name}")

        # 检查外用方剂总数
        result = await session.execute(
            select(AnorectalFormula).where(AnorectalFormula.formula_type == 'external')
        )
        external_formulas = result.scalars().all()
        print(f"\n✅ 外用方剂总计: {len(external_formulas)} 首")

        # 检查熏洗方剂总数
        result = await session.execute(
            select(AnorectalFormula).where(AnorectalFormula.formula_type == 'fumigation')
        )
        fumigation_formulas = result.scalars().all()
        print(f"✅ 熏洗方剂总计: {len(fumigation_formulas)} 首")

        # 方剂总数
        result = await session.execute(select(AnorectalFormula))
        all_formulas = result.scalars().all()
        print(f"\n📊 方剂总数: {len(all_formulas)} 首")

if __name__ == "__main__":
    asyncio.run(verify())
