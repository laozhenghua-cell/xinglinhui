"""
华夏痔瘘辅助诊疗系统 - 收费项目种子数据
24个肛肠科常用收费项目
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, select
from app.database import AsyncSessionLocal
from app.models import ChargeItem, Tenant

CHARGE_ITEMS = [
    # 诊疗费
    {"name": "挂号费", "category": "诊疗费", "price": 10.0, "unit": "次"},
    {"name": "诊疗费", "category": "诊疗费", "price": 50.0, "unit": "次"},
    {"name": "专家诊疗费", "category": "诊疗费", "price": 100.0, "unit": "次"},
    {"name": "换药费", "category": "诊疗费", "price": 30.0, "unit": "次"},
    {"name": "复查费", "category": "诊疗费", "price": 20.0, "unit": "次"},
    # 检查费
    {"name": "肛门镜检查", "category": "检查费", "price": 80.0, "unit": "次"},
    {"name": "直肠指检", "category": "检查费", "price": 30.0, "unit": "次"},
    # 治疗费
    {"name": "痔疮注射术", "category": "手术费", "price": 500.0, "unit": "次"},
    {"name": "套扎术", "category": "手术费", "price": 600.0, "unit": "次"},
    {"name": "脓肿切开引流术", "category": "手术费", "price": 800.0, "unit": "次"},
    {"name": "肛裂切除术", "category": "手术费", "price": 1200.0, "unit": "次"},
    {"name": "混合痔外剥内扎术", "category": "手术费", "price": 2000.0, "unit": "次"},
    {"name": "针灸治疗", "category": "治疗费", "price": 60.0, "unit": "次"},
    {"name": "艾灸治疗", "category": "治疗费", "price": 40.0, "unit": "次"},
    {"name": "中药熏洗", "category": "治疗费", "price": 50.0, "unit": "次"},
    {"name": "中药坐浴", "category": "治疗费", "price": 40.0, "unit": "次"},
    # 材料费
    {"name": "一次性肛门镜", "category": "材料费", "price": 15.0, "unit": "个"},
    {"name": "手术包", "category": "材料费", "price": 80.0, "unit": "套"},
    {"name": "换药包", "category": "材料费", "price": 20.0, "unit": "套"},
    {"name": "油纱条", "category": "材料费", "price": 5.0, "unit": "条"},
    # 药品费
    {"name": "中药饮片", "category": "药费", "price": 0.5, "unit": "克"},
    {"name": "痔疮膏", "category": "药费", "price": 25.0, "unit": "支"},
    {"name": "化痔栓", "category": "药费", "price": 30.0, "unit": "盒"},
    {"name": "九华膏", "category": "药费", "price": 35.0, "unit": "支"},
]


async def seed():
    async with AsyncSessionLocal() as session:
        # 获取所有租户
        result = await session.execute(select(Tenant))
        tenants = result.scalars().all()

        if not tenants:
            print("⚠️  没有找到租户，请先注册账号")
            return

        for tenant in tenants:
            # 清空该租户已有的收费项目
            await session.execute(
                text("DELETE FROM charge_items WHERE tenant_id = :tid"),
                {"tid": str(tenant.id)}
            )
            # 插入收费项目
            for item in CHARGE_ITEMS:
                session.add(ChargeItem(tenant_id=tenant.id, **item))

            print(f"✅ 租户「{tenant.name}」导入 {len(CHARGE_ITEMS)} 个收费项目")

        await session.commit()
        print("\n🎉 收费项目初始化完成！")


if __name__ == "__main__":
    asyncio.run(seed())
