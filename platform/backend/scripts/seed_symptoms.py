"""
症状字典种子数据 - 四诊采集系统
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import AsyncSessionLocal
from app.models.diagnosis import SymptomDictionary

# ============ 望诊症状 ============
INSPECTION_SYMPTOMS = [
    # 舌诊
    {
        "category": "望诊",
        "subcategory": "舌质",
        "name": "tongue_color",
        "display_name": "舌质",
        "options": {
            "type": "select",
            "choices": ["淡红", "红", "深红", "淡白", "紫暗", "青紫"]
        },
        "weight": 3
    },
    {
        "category": "望诊",
        "subcategory": "舌苔",
        "name": "tongue_coating",
        "display_name": "舌苔",
        "options": {
            "type": "select",
            "choices": ["薄白", "黄", "黄腻", "白厚", "少苔", "无苔", "腻苔"]
        },
        "weight": 3
    },
    {
        "category": "望诊",
        "subcategory": "舌形",
        "name": "tongue_shape",
        "display_name": "舌形",
        "options": {
            "type": "select",
            "choices": ["正常", "胖大齿痕", "瘦薄", "裂纹"]
        },
        "weight": 2
    },
    # 肛门局部望诊
    {
        "category": "望诊",
        "subcategory": "肛门局部",
        "name": "anal_color",
        "display_name": "肛门色泽",
        "options": {
            "type": "select",
            "choices": ["鲜红", "暗红", "紫暗", "淡白", "正常"]
        },
        "weight": 2
    },
    {
        "category": "望诊",
        "subcategory": "肛门局部",
        "name": "anal_swelling",
        "display_name": "肿胀程度",
        "options": {
            "type": "select",
            "choices": ["无", "轻度", "中度", "重度"]
        },
        "weight": 2
    },
    {
        "category": "望诊",
        "subcategory": "肛门局部",
        "name": "prolapse",
        "display_name": "有无脱出",
        "options": {
            "type": "select",
            "choices": ["无", "便时脱出自回", "便时脱出需手托", "常脱出"]
        },
        "weight": 3
    },
    {
        "category": "望诊",
        "subcategory": "肛门局部",
        "name": "secretion",
        "display_name": "分泌物",
        "options": {
            "type": "select",
            "choices": ["无", "血性", "脓性", "粘液性"]
        },
        "weight": 2
    },
    {
        "category": "望诊",
        "subcategory": "肛门局部",
        "name": "ulceration",
        "display_name": "糜烂溃疡",
        "options": {
            "type": "select",
            "choices": ["无", "轻度", "明显"]
        },
        "weight": 2
    },
]

# ============ 闻诊症状 ============
AUSCULTATION_SYMPTOMS = [
    {
        "category": "闻诊",
        "subcategory": "气味",
        "name": "odor",
        "display_name": "气味",
        "options": {
            "type": "select",
            "choices": ["无异味", "腥臭", "恶臭"]
        },
        "weight": 2
    },
    {
        "category": "闻诊",
        "subcategory": "语声",
        "name": "voice",
        "display_name": "语声",
        "options": {
            "type": "select",
            "choices": ["洪亮", "低微", "气短懒言"]
        },
        "weight": 1
    },
]

# ============ 问诊症状（主症）============
MAIN_SYMPTOMS = [
    {
        "category": "问诊",
        "subcategory": "主症",
        "name": "bleeding",
        "display_name": "便血",
        "options": {
            "type": "compound",
            "fields": {
                "present": {"type": "boolean", "label": "是否便血"},
                "color": {"type": "select", "label": "颜色", "choices": ["鲜红", "暗红", "紫黑"]},
                "volume": {"type": "select", "label": "量", "choices": ["点滴", "少量", "中量", "大量", "射血"]},
                "timing": {"type": "select", "label": "时机", "choices": ["便前", "便中", "便后", "不定"]}
            }
        },
        "weight": 5
    },
    {
        "category": "问诊",
        "subcategory": "主症",
        "name": "pain",
        "display_name": "疼痛",
        "options": {
            "type": "compound",
            "fields": {
                "present": {"type": "boolean", "label": "是否疼痛"},
                "degree": {"type": "select", "label": "程度", "choices": ["轻度", "中度", "重度", "剧烈"]},
                "nature": {"type": "select", "label": "性质", "choices": ["刺痛", "胀痛", "灼痛", "隐痛", "跳痛"]},
                "timing": {"type": "select", "label": "时机", "choices": ["便时", "便后持续", "夜间加重", "持续痛"]}
            }
        },
        "weight": 5
    },
    {
        "category": "问诊",
        "subcategory": "主症",
        "name": "prolapse_symptom",
        "display_name": "脱出",
        "options": {
            "type": "compound",
            "fields": {
                "present": {"type": "boolean", "label": "是否脱出"},
                "degree": {"type": "select", "label": "程度", "choices": ["I度", "II度", "III度", "IV度"]}
            }
        },
        "weight": 4
    },
    {
        "category": "问诊",
        "subcategory": "主症",
        "name": "swelling_symptom",
        "display_name": "肿胀",
        "options": {
            "type": "compound",
            "fields": {
                "present": {"type": "boolean", "label": "是否肿胀"},
                "location": {"type": "select", "label": "部位", "choices": ["内痔", "外痔", "混合痔", "肛周"]}
            }
        },
        "weight": 3
    },
    {
        "category": "问诊",
        "subcategory": "主症",
        "name": "itching",
        "display_name": "瘙痒",
        "options": {
            "type": "compound",
            "fields": {
                "present": {"type": "boolean", "label": "是否瘙痒"},
                "degree": {"type": "select", "label": "程度", "choices": ["轻度", "中度", "重度"]}
            }
        },
        "weight": 3
    },
]

# ============ 问诊症状（次症）============
SECONDARY_SYMPTOMS = [
    {
        "category": "问诊",
        "subcategory": "次症",
        "name": "stool_condition",
        "display_name": "大便",
        "options": {
            "type": "select",
            "choices": ["正常", "干结", "溏泄", "秘结", "先干后溏"]
        },
        "weight": 2
    },
    {
        "category": "问诊",
        "subcategory": "次症",
        "name": "urination",
        "display_name": "小便",
        "options": {
            "type": "select",
            "choices": ["正常", "短赤", "清长", "频数"]
        },
        "weight": 2
    },
    {
        "category": "问诊",
        "subcategory": "次症",
        "name": "thirst",
        "display_name": "口渴",
        "options": {
            "type": "select",
            "choices": ["不渴", "口渴喜冷饮", "口渴喜热饮", "口干不欲饮"]
        },
        "weight": 2
    },
    {
        "category": "问诊",
        "subcategory": "次症",
        "name": "fever",
        "display_name": "发热",
        "options": {
            "type": "select",
            "choices": ["无", "低热", "高热", "恶寒发热", "潮热"]
        },
        "weight": 2
    },
    {
        "category": "问诊",
        "subcategory": "次症",
        "name": "fatigue",
        "display_name": "神疲乏力",
        "options": {
            "type": "boolean"
        },
        "weight": 2
    },
    {
        "category": "问诊",
        "subcategory": "次症",
        "name": "pale_complexion",
        "display_name": "面色无华",
        "options": {
            "type": "boolean"
        },
        "weight": 2
    },
    {
        "category": "问诊",
        "subcategory": "次症",
        "name": "poor_appetite",
        "display_name": "食欲不振",
        "options": {
            "type": "boolean"
        },
        "weight": 1
    },
    {
        "category": "问诊",
        "subcategory": "次症",
        "name": "insomnia",
        "display_name": "心烦失眠",
        "options": {
            "type": "boolean"
        },
        "weight": 1
    },
    {
        "category": "问诊",
        "subcategory": "次症",
        "name": "lumbar_soreness",
        "display_name": "腰膝酸软",
        "options": {
            "type": "boolean"
        },
        "weight": 2
    },
    {
        "category": "问诊",
        "subcategory": "次症",
        "name": "bitter_mouth",
        "display_name": "口苦",
        "options": {
            "type": "boolean"
        },
        "weight": 2
    },
]

# ============ 切诊症状 ============
PALPATION_SYMPTOMS = [
    {
        "category": "切诊",
        "subcategory": "脉象",
        "name": "pulse_floating",
        "display_name": "浮脉",
        "options": {"type": "boolean"},
        "weight": 2
    },
    {
        "category": "切诊",
        "subcategory": "脉象",
        "name": "pulse_deep",
        "display_name": "沉脉",
        "options": {"type": "boolean"},
        "weight": 2
    },
    {
        "category": "切诊",
        "subcategory": "脉象",
        "name": "pulse_slow",
        "display_name": "迟脉",
        "options": {"type": "boolean"},
        "weight": 2
    },
    {
        "category": "切诊",
        "subcategory": "脉象",
        "name": "pulse_rapid",
        "display_name": "数脉",
        "options": {"type": "boolean"},
        "weight": 3
    },
    {
        "category": "切诊",
        "subcategory": "脉象",
        "name": "pulse_wiry",
        "display_name": "弦脉",
        "options": {"type": "boolean"},
        "weight": 2
    },
    {
        "category": "切诊",
        "subcategory": "脉象",
        "name": "pulse_slippery",
        "display_name": "滑脉",
        "options": {"type": "boolean"},
        "weight": 2
    },
    {
        "category": "切诊",
        "subcategory": "脉象",
        "name": "pulse_fine",
        "display_name": "细脉",
        "options": {"type": "boolean"},
        "weight": 2
    },
    {
        "category": "切诊",
        "subcategory": "脉象",
        "name": "pulse_weak",
        "display_name": "弱脉",
        "options": {"type": "boolean"},
        "weight": 2
    },
    {
        "category": "切诊",
        "subcategory": "脉象",
        "name": "pulse_surging",
        "display_name": "洪脉",
        "options": {"type": "boolean"},
        "weight": 2
    },
    {
        "category": "切诊",
        "subcategory": "脉象",
        "name": "pulse_full",
        "display_name": "实脉",
        "options": {"type": "boolean"},
        "weight": 2
    },
    {
        "category": "切诊",
        "subcategory": "腹诊",
        "name": "abdomen",
        "display_name": "腹部",
        "options": {
            "type": "select",
            "choices": ["腹部柔软", "腹胀", "按之痛"]
        },
        "weight": 1
    },
    {
        "category": "切诊",
        "subcategory": "肛门指诊",
        "name": "sphincter",
        "display_name": "括约肌",
        "options": {
            "type": "select",
            "choices": ["正常", "松弛", "痉挛"]
        },
        "weight": 2
    },
    {
        "category": "切诊",
        "subcategory": "肛门指诊",
        "name": "mass",
        "display_name": "触及肿块",
        "options": {
            "type": "compound",
            "fields": {
                "present": {"type": "boolean", "label": "有无肿块"},
                "location": {"type": "text", "label": "位置"},
                "size": {"type": "text", "label": "大小"},
                "texture": {"type": "select", "label": "质地", "choices": ["软", "中等", "硬"]}
            }
        },
        "weight": 2
    },
]


async def seed_symptoms():
    """导入症状字典数据"""
    async with AsyncSessionLocal() as session:
        print("开始清理旧症状数据...")
        await session.execute(text("DELETE FROM symptom_dictionary"))
        print("✅ 旧数据清理完成\n")

        all_symptoms = (
            INSPECTION_SYMPTOMS +
            AUSCULTATION_SYMPTOMS +
            MAIN_SYMPTOMS +
            SECONDARY_SYMPTOMS +
            PALPATION_SYMPTOMS
        )

        print(f"正在导入症状字典...")
        for symptom in all_symptoms:
            session.add(SymptomDictionary(**symptom))

        await session.commit()

        print(f"✅ 望诊症状: {len(INSPECTION_SYMPTOMS)} 项")
        print(f"✅ 闻诊症状: {len(AUSCULTATION_SYMPTOMS)} 项")
        print(f"✅ 问诊主症: {len(MAIN_SYMPTOMS)} 项")
        print(f"✅ 问诊次症: {len(SECONDARY_SYMPTOMS)} 项")
        print(f"✅ 切诊症状: {len(PALPATION_SYMPTOMS)} 项")
        print(f"\n📊 症状字典总计: {len(all_symptoms)} 项")
        print("\n🎉 症状字典导入完成！")


if __name__ == "__main__":
    asyncio.run(seed_symptoms())
