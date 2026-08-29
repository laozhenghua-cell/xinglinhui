"""
补充最后2个证型，达到100%证型覆盖率
根据临床经验原文
"""
import asyncio
import uuid
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.diagnosis import SyndromeRule


# 补充2个证型
FINAL_SYNDROMES = [
    {
        "id": str(uuid.uuid4()),
        "disease_type": "痔疮",
        "syndrome_code": "ZC_VHAN",
        "syndrome_name": "虚寒证",
        "treatment_principle": "健脾温中，固脱止血",
        "required_symptoms": {
            "fatigue": {"present": True},
            "pale_complexion": True,
            "stool_condition": "稀软",
            "bleeding": {"present": True, "color": "晦暗"}
        },
        "optional_symptoms": {
            "poor_appetite": True,
            "abdominal_distension": True,
            "urination": "清长",
            "prolapse": True,
            "tongue_coating": ["淡白"],
            "pulse_weak": True
        },
        "recommended_formulas": ["归脾汤加味", "黄芪建中汤加减"],
        "modification_rules": {
            "内痔脱出严重": "加升麻10g、柴胡10g升提",
            "长期便血": "加灶心土30g、陈棕炭10g固脱止血",
            "消化不良": "加砂仁6g、木香6g健脾和胃",
            "腹泻": "加煨葛根12g、炒白芍10g止泻"
        },
        "confidence_threshold": 0.65,
        "priority": 75,
        "is_active": 1,
        "tongue_pulse": {
            "tongue": "舌质淡，苔淡白",
            "pulse": "脉沉迟或细弱"
        }
    },
    {
        "id": str(uuid.uuid4()),
        "disease_type": "肛瘘",
        "syndrome_code": "GL_XRNY",
        "syndrome_name": "虚热内蕴",
        "treatment_principle": "滋阴养血，清热通络",
        "required_symptoms": {
            "chronic_fistula": True,
            "discharge": {"present": True, "color": "清稀"},
            "delayed_healing": True
        },
        "optional_symptoms": {
            "fatigue": True,
            "night_sweats": True,
            "low_fever": True,
            "poor_appetite": True,
            "tongue_color": "红",
            "tongue_coating": ["少苔", "无苔"],
            "pulse_thin": True,
            "pulse_weak": True
        },
        "recommended_formulas": ["当归连翘汤", "八珍汤加减"],
        "modification_rules": {
            "脓汁清稀": "加黄芪15g、党参12g托脓外出",
            "潮热盗汗": "加地骨皮10g、青蒿10g清虚热",
            "懒言乏力": "加白术10g、茯苓12g健脾益气",
            "肉芽不良": "加鸡血藤15g、丹参12g活血通络"
        },
        "confidence_threshold": 0.65,
        "priority": 70,
        "is_active": 1,
        "tongue_pulse": {
            "tongue": "舌质红，苔少或无苔",
            "pulse": "脉细弱"
        }
    }
]


async def seed_final_syndromes():
    """补充最后2个证型"""
    async with AsyncSessionLocal() as db:
        print("=" * 60)
        print("补充最后2个证型，达到100%覆盖率")
        print("=" * 60)

        added_count = 0
        skipped_count = 0

        for syndrome_data in FINAL_SYNDROMES:
            # 检查是否已存在
            result = await db.execute(
                select(SyndromeRule).where(
                    SyndromeRule.syndrome_code == syndrome_data["syndrome_code"]
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"\n⚠️  证型已存在，跳过：{syndrome_data['syndrome_name']} ({syndrome_data['syndrome_code']})")
                skipped_count += 1
                continue

            # 创建新证型
            syndrome = SyndromeRule(**syndrome_data)
            db.add(syndrome)
            print(f"\n✅ 新增证型：{syndrome_data['syndrome_name']}")
            print(f"   病种：{syndrome_data['disease_type']}")
            print(f"   治则：{syndrome_data['treatment_principle']}")
            print(f"   推荐方剂：{', '.join(syndrome_data['recommended_formulas'])}")
            added_count += 1

        await db.commit()

        print("\n" + "=" * 60)
        print(f"✅ 导入完成")
        print(f"   新增：{added_count} 个")
        print(f"   跳过：{skipped_count} 个")
        print("=" * 60)

        # 统计最终证型数量
        result = await db.execute(
            select(SyndromeRule).where(SyndromeRule.is_active == 1)
        )
        total = len(result.scalars().all())
        print(f"\n📊 系统证型总数：{total} 个")
        print(f"   目标：16个")
        print(f"   覆盖率：{total/16*100:.1f}%")

        if total >= 16:
            print("\n🎉 恭喜！已达到100%证型覆盖率！")


if __name__ == "__main__":
    asyncio.run(seed_final_syndromes())
