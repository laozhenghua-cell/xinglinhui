"""
辨证规则种子数据 - 痔疮常见证型
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import AsyncSessionLocal
from app.models.diagnosis import SyndromeRule

# ============ 痔疮辨证规则 ============
HEMORRHOID_SYNDROMES = [
    {
        "disease_type": "痔疮",
        "syndrome_name": "实热内蕴，血热肠燥",
        "syndrome_code": "ZC_SHINY",
        "required_symptoms": {
            "bleeding": {"present": True, "color": "鲜红"},
            "stool_condition": "干结",
            "tongue_color": ["红", "深红"],
            "tongue_coating": ["黄", "黄腻"],
            "pulse_rapid": True
        },
        "optional_symptoms": {
            "pain": {"present": True},
            "urination": "短赤",
            "bitter_mouth": True,
            "pulse_wiry": True
        },
        "tongue_pulse": {
            "tongue": "舌红苔黄",
            "pulse": "脉弦数或数"
        },
        "treatment_principle": "清热止血，润肠通便",
        "recommended_formulas": [
            {"name": "槐花散加味", "priority": 1, "match_rate": 0.95},
            {"name": "地榆散加味", "priority": 2, "match_rate": 0.85}
        ],
        "modification_rules": {
            "便秘严重": {"add": ["大黄6克(后下)", "芒硝10克"]},
            "疼痛明显": {"add": ["延胡索10克", "川楝子10克"]},
            "出血量大": {"add": ["仙鹤草30克", "三七粉3克(冲)"]},
            "伴湿热": {"add": ["黄柏10克", "苍术10克"]}
        },
        "confidence_threshold": 0.7,
        "priority": 1,
        "is_active": 1
    },
    {
        "disease_type": "痔疮",
        "syndrome_name": "湿热下注，气滞血瘀",
        "syndrome_code": "ZC_SRXZ",
        "required_symptoms": {
            "pain": {"present": True, "nature": "胀痛"},
            "swelling_symptom": {"present": True},
            "tongue_color": "红",
            "tongue_coating": ["黄腻", "白厚"],
            "pulse_wiry": True,
            "pulse_slippery": True
        },
        "optional_symptoms": {
            "anal_color": ["暗红", "紫暗"],
            "anal_swelling": ["中度", "重度"],
            "bitter_mouth": True,
            "urination": "短赤",
            "poor_appetite": True
        },
        "tongue_pulse": {
            "tongue": "舌质红，苔黄腻",
            "pulse": "脉弦滑数"
        },
        "treatment_principle": "清热利湿，活血化瘀",
        "recommended_formulas": [
            {"name": "五神汤加味", "priority": 1, "match_rate": 0.95},
            {"name": "活血散瘀汤", "priority": 2, "match_rate": 0.85}
        ],
        "modification_rules": {
            "疼痛剧烈": {"add": ["白芷10克", "乳香10克", "没药10克"]},
            "肿胀明显": {"add": ["泽兰10克", "益母草15克"]},
            "湿热重": {"add": ["薏苡仁30克", "白术10克"]},
            "便秘": {"add": ["大黄6克(后下)"]}
        },
        "confidence_threshold": 0.7,
        "priority": 1,
        "is_active": 1
    },
    {
        "disease_type": "痔疮",
        "syndrome_name": "气血亏损，气不摄血",
        "syndrome_code": "ZC_QXKS",
        "required_symptoms": {
            "bleeding": {"present": True, "volume": ["点滴", "少量"]},
            "fatigue": True,
            "pale_complexion": True,
            "tongue_color": ["淡红", "淡白"],
            "pulse_fine": True,
            "pulse_weak": True
        },
        "optional_symptoms": {
            "poor_appetite": True,
            "lumbar_soreness": True,
            "prolapse_symptom": {"present": True},
            "tongue_coating": "少苔"
        },
        "tongue_pulse": {
            "tongue": "舌淡苔白或少苔",
            "pulse": "脉细弱"
        },
        "treatment_principle": "补气益血",
        "recommended_formulas": [
            {"name": "八珍汤", "priority": 1, "match_rate": 0.95},
            {"name": "归脾汤加味", "priority": 2, "match_rate": 0.90}
        ],
        "modification_rules": {
            "气虚明显": {"add": ["黄芪加至40克", "党参加至20克"]},
            "血虚明显": {"add": ["熟地加至20克", "阿胶10克(烊化)"]},
            "脱肛": {"add": ["升麻6克", "柴胡6克", "补骨脂10克"]},
            "便血不止": {"add": ["灶心土60克(煎汤代水)", "白及10克"]}
        },
        "confidence_threshold": 0.65,
        "priority": 2,
        "is_active": 1
    },
    {
        "disease_type": "痔疮",
        "syndrome_name": "脾虚气陷",
        "syndrome_code": "ZC_PXQX",
        "required_symptoms": {
            "prolapse_symptom": {"present": True, "degree": ["II度", "III度", "IV度"]},
            "fatigue": True,
            "poor_appetite": True,
            "tongue_color": ["淡红", "淡白"],
            "tongue_shape": "胖大齿痕",
            "pulse_weak": True
        },
        "optional_symptoms": {
            "stool_condition": "溏泄",
            "pale_complexion": True,
            "lumbar_soreness": True,
            "bleeding": {"present": True, "volume": "点滴"}
        },
        "tongue_pulse": {
            "tongue": "舌淡胖齿痕，苔薄白",
            "pulse": "脉弱或虚"
        },
        "treatment_principle": "补中益气，升阳举陷",
        "recommended_formulas": [
            {"name": "补中益气汤", "priority": 1, "match_rate": 0.95}
        ],
        "modification_rules": {
            "脱垂严重": {"add": ["补骨脂12克", "肉豆蔻10克", "五倍子10克"]},
            "便血": {"add": ["白及10克", "仙鹤草20克"]},
            "久泻": {"add": ["煨诃子10克", "石榴皮10克"]},
            "腰酸": {"add": ["杜仲12克", "续断10克"]}
        },
        "confidence_threshold": 0.7,
        "priority": 1,
        "is_active": 1
    },
    {
        "disease_type": "痔疮",
        "syndrome_name": "气滞血瘀",
        "syndrome_code": "ZC_QZXY",
        "required_symptoms": {
            "pain": {"present": True, "nature": ["刺痛", "胀痛"]},
            "anal_color": ["紫暗", "暗红"],
            "pulse_wiry": True
        },
        "optional_symptoms": {
            "swelling_symptom": {"present": True},
            "bleeding": {"present": True, "color": "暗红"},
            "tongue_color": "紫暗",
            "stool_condition": "干结"
        },
        "tongue_pulse": {
            "tongue": "舌质紫暗或有瘀斑",
            "pulse": "脉弦或涩"
        },
        "treatment_principle": "活血化瘀，行气止痛",
        "recommended_formulas": [
            {"name": "活血散瘀汤", "priority": 1, "match_rate": 0.90}
        ],
        "modification_rules": {
            "疼痛剧烈": {"add": ["延胡索12克", "川楝子10克", "白芷10克"]},
            "血瘀重": {"add": ["三棱10克", "莪术10克"]},
            "便秘": {"add": ["桃仁12克", "火麻仁15克"]},
            "嵌顿": {"add": ["牛膝15克", "红花10克"]}
        },
        "confidence_threshold": 0.65,
        "priority": 2,
        "is_active": 1
    },
]

# ============ 肛裂辨证规则 ============
ANAL_FISSURE_SYNDROMES = [
    {
        "disease_type": "肛裂",
        "syndrome_name": "血热肠燥",
        "syndrome_code": "GL_XRCZ",
        "required_symptoms": {
            "pain": {"present": True, "nature": ["刺痛", "灼痛"], "timing": "便后持续"},
            "bleeding": {"present": True, "color": "鲜红", "timing": "便时"},
            "stool_condition": "干结",
            "tongue_color": ["红", "深红"],
            "tongue_coating": "黄",
            "pulse_rapid": True
        },
        "optional_symptoms": {
            "urination": "短赤",
            "thirst": "口渴喜冷饮",
            "sphincter": "痉挛"
        },
        "tongue_pulse": {
            "tongue": "舌红苔黄",
            "pulse": "脉数"
        },
        "treatment_principle": "凉血止血，养阴润燥",
        "recommended_formulas": [
            {"name": "凉血地黄汤", "priority": 1, "match_rate": 0.95}
        ],
        "modification_rules": {
            "便秘重": {"add": ["火麻仁15克", "郁李仁10克"]},
            "疼痛剧烈": {"add": ["延胡索10克", "白芷10克"]},
            "括约肌痉挛": {"add": ["白芍15克", "甘草10克"]},
            "出血多": {"add": ["地榆炭15克", "槐花炭12克"]}
        },
        "confidence_threshold": 0.7,
        "priority": 1,
        "is_active": 1
    },
    {
        "disease_type": "肛裂",
        "syndrome_name": "阴虚津亏",
        "syndrome_code": "GL_YXJK",
        "required_symptoms": {
            "pain": {"present": True, "nature": "灼痛"},
            "stool_condition": "干结",
            "tongue_color": "红",
            "tongue_coating": ["少苔", "无苔"],
            "pulse_fine": True
        },
        "optional_symptoms": {
            "thirst": "口干不欲饮",
            "lumbar_soreness": True,
            "insomnia": True
        },
        "tongue_pulse": {
            "tongue": "舌红少苔或无苔",
            "pulse": "脉细数"
        },
        "treatment_principle": "养阴润燥，润肠通便",
        "recommended_formulas": [
            {"name": "润肠汤", "priority": 1, "match_rate": 0.90}
        ],
        "modification_rules": {
            "阴虚重": {"add": ["玄参15克", "麦冬15克", "石斛12克"]},
            "便秘顽固": {"add": ["肉苁蓉15克", "锁阳12克"]},
            "失眠": {"add": ["酸枣仁15克", "柏子仁10克"]},
            "腰酸": {"add": ["枸杞子12克", "女贞子12克"]}
        },
        "confidence_threshold": 0.65,
        "priority": 2,
        "is_active": 1
    },
]

# ============ 肛周脓肿辨证规则 ============
PERIANAL_ABSCESS_SYNDROMES = [
    {
        "disease_type": "肛周脓肿",
        "syndrome_name": "热毒蕴结",
        "syndrome_code": "GZ_RTYJ",
        "required_symptoms": {
            "pain": {"present": True, "degree": ["重度", "剧烈"], "nature": "跳痛"},
            "anal_swelling": ["中度", "重度"],
            "fever": ["高热", "恶寒发热"],
            "tongue_color": "红",
            "tongue_coating": "黄腻",
            "pulse_rapid": True,
            "pulse_surging": True
        },
        "optional_symptoms": {
            "odor": "恶臭",
            "thirst": "口渴喜冷饮",
            "urination": "短赤",
            "stool_condition": "干结"
        },
        "tongue_pulse": {
            "tongue": "舌红苔黄腻",
            "pulse": "脉洪数或弦数"
        },
        "treatment_principle": "清泻实热，宣散郁结",
        "recommended_formulas": [
            {"name": "内疏黄连汤加减", "priority": 1, "match_rate": 0.95},
            {"name": "仙方活命饮", "priority": 2, "match_rate": 0.85}
        ],
        "modification_rules": {
            "高热": {"add": ["石膏30克", "知母12克"]},
            "脓肿未溃": {"add": ["皂角刺15克", "穿山甲10克"]},
            "便秘": {"add": ["大黄10克(后下)", "芒硝10克(冲)"]},
            "热毒重": {"add": ["蒲公英30克", "紫花地丁20克"]}
        },
        "confidence_threshold": 0.75,
        "priority": 1,
        "is_active": 1
    },
]

# ============ 直肠脱垂辨证规则 ============
RECTAL_PROLAPSE_SYNDROMES = [
    {
        "disease_type": "直肠脱垂",
        "syndrome_name": "中气下陷",
        "syndrome_code": "ZC_ZQXX",
        "required_symptoms": {
            "prolapse_symptom": {"present": True, "degree": ["II度", "III度", "IV度"]},
            "fatigue": True,
            "poor_appetite": True,
            "tongue_color": ["淡红", "淡白"],
            "pulse_weak": True
        },
        "optional_symptoms": {
            "pale_complexion": True,
            "stool_condition": "溏泄",
            "lumbar_soreness": True,
            "tongue_shape": "胖大齿痕"
        },
        "tongue_pulse": {
            "tongue": "舌淡苔白或胖大齿痕",
            "pulse": "脉虚弱"
        },
        "treatment_principle": "补中益气，升阳举陷",
        "recommended_formulas": [
            {"name": "补中益气汤", "priority": 1, "match_rate": 0.95}
        ],
        "modification_rules": {
            "脱垂严重": {"add": ["补骨脂15克", "肉豆蔻10克", "五倍子10克"]},
            "气虚重": {"add": ["黄芪加至50克", "党参加至20克"]},
            "久泻": {"add": ["煨诃子10克", "石榴皮10克"]},
            "小儿": {"remove": ["当归"], "add": ["山药15克", "莲子肉12克"]}
        },
        "confidence_threshold": 0.7,
        "priority": 1,
        "is_active": 1
    },
]


async def seed_syndrome_rules():
    """导入辨证规则数据"""
    async with AsyncSessionLocal() as session:
        print("开始清理旧辨证规则...")
        await session.execute(text("DELETE FROM syndrome_rules"))
        print("✅ 旧数据清理完成\n")

        all_rules = (
            HEMORRHOID_SYNDROMES +
            ANAL_FISSURE_SYNDROMES +
            PERIANAL_ABSCESS_SYNDROMES +
            RECTAL_PROLAPSE_SYNDROMES
        )

        print(f"正在导入辨证规则...")
        for rule in all_rules:
            session.add(SyndromeRule(**rule))

        await session.commit()

        print(f"✅ 痔疮辨证规则: {len(HEMORRHOID_SYNDROMES)} 条")
        print(f"✅ 肛裂辨证规则: {len(ANAL_FISSURE_SYNDROMES)} 条")
        print(f"✅ 肛周脓肿辨证规则: {len(PERIANAL_ABSCESS_SYNDROMES)} 条")
        print(f"✅ 直肠脱垂辨证规则: {len(RECTAL_PROLAPSE_SYNDROMES)} 条")
        print(f"\n📊 辨证规则总计: {len(all_rules)} 条")
        print("\n🎉 辨证规则导入完成！")


if __name__ == "__main__":
    asyncio.run(seed_syndrome_rules())
