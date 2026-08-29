"""
「便秘七型」与「肛门湿疹/瘙痒」辨证模块补全。

在学术思想中明确强调：便秘分大肠津亏、大肠寒结、胃肠热结、气虚便结、
气滞不行、气血两亏、阴虚便结七型，治疗须「审证求因、因人而异、有其证而用其药」。
肛门瘙痒则强调脾失健运、中气下陷、痰浊流注，常以补中益气丸合三妙丸化裁。

本脚本：
1. 补充便秘七型 + 肛门湿疹三型的辨证规则（经典方均标注「经典方参考·非原文证治方」）
2. 补充相应经典方剂
幂等：按 syndrome_code / name upsert。
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.diagnosis import SyndromeRule
from app.models.knowledge import AnorectalFormula


def _c(items):
    return [{"name": n, "unit": u, "dosage": d} for n, u, d in items]


FORMULAS = [
    {
        "name": "增液汤",
        "source": "经典方参考（非原文证治方）",
        "formula_type": "internal", "syndrome_type": "肠燥津亏",
        "disease_types": ["便秘"],
        "function": "增液润燥，滋阴通便",
        "indications": "津亏肠燥便秘：大便秘结、口干咽燥、舌红少津。",
        "usage": "水煎服，日服一剂。",
        "composition": _c([("玄参", "g", 30), ("麦冬", "g", 24), ("生地", "g", 24)]),
    },
    {
        "name": "大黄附子汤",
        "source": "经典方参考（非原文证治方）",
        "formula_type": "internal", "syndrome_type": "寒结",
        "disease_types": ["便秘"],
        "function": "温里散寒，通便止痛",
        "indications": "寒积便秘：大便艰涩、腹冷痛、苔白、脉沉迟。",
        "usage": "水煎服，日服一剂。",
        "composition": _c([("大黄", "g", 9), ("炮附子", "g", 9), ("细辛", "g", 3)]),
    },
    {
        "name": "麻子仁丸",
        "source": "经典方参考（非原文证治方）",
        "formula_type": "internal", "syndrome_type": "胃肠热结",
        "disease_types": ["便秘"],
        "function": "润肠泄热，行气通便",
        "indications": "肠胃燥热、脾约便秘：大便干结、小便频数。",
        "usage": "蜜丸，每服9克，日1-2次。",
        "composition": _c([("火麻仁", "g", 20), ("白芍", "g", 9), ("枳实", "g", 9), ("大黄", "g", 12), ("厚朴", "g", 9), ("杏仁", "g", 10)]),
    },
    {
        "name": "黄芪汤",
        "source": "经典方参考（非原文证治方）",
        "formula_type": "internal", "syndrome_type": "气虚便结",
        "disease_types": ["便秘"],
        "function": "益气润肠通便",
        "indications": "气虚便秘：排便无力、汗出气短、便后乏力。",
        "usage": "水煎服，日服一剂。",
        "composition": _c([("黄芪", "g", 20), ("陈皮", "g", 10), ("火麻仁", "g", 15), ("白蜜", "g", 30)]),
    },
    {
        "name": "六磨汤",
        "source": "经典方参考（非原文证治方）",
        "formula_type": "internal", "syndrome_type": "气滞不行",
        "disease_types": ["便秘"],
        "function": "行气导滞通便",
        "indications": "气滞便秘：排便不畅、腹胀嗳气、胸胁痞满。",
        "usage": "水煎服，日服一剂。",
        "composition": _c([("木香", "g", 6), ("沉香", "g", 3), ("乌药", "g", 9), ("槟榔", "g", 9), ("枳实", "g", 9), ("大黄", "g", 6)]),
    },
    {
        "name": "三妙丸",
        "source": "经典方（用于肛门瘙痒中气下陷之兼湿热者）",
        "formula_type": "internal", "syndrome_type": "湿热下注",
        "disease_types": ["肛门湿疹"],
        "function": "清热燥湿",
        "indications": "湿热下注之肛门瘙痒、下肢痿痹。以补中益气丸合三妙丸化裁治顽固肛门瘙痒。",
        "usage": "水煎服，日服一剂。",
        "composition": _c([("黄柏", "g", 12), ("苍术", "g", 12), ("牛膝", "g", 10)]),
    },
    {
        "name": "当归饮子",
        "source": "经典方参考（非原文证治方）",
        "formula_type": "internal", "syndrome_type": "血虚风燥",
        "disease_types": ["肛门湿疹"],
        "function": "养血润燥，祛风止痒",
        "indications": "血虚风燥型肛门湿疹/瘙痒：皮肤干燥肥厚、入夜痒甚、面色无华。",
        "usage": "水煎服，日服一剂。",
        "composition": _c([("当归", "g", 12), ("生地", "g", 15), ("白芍", "g", 12), ("川芎", "g", 6), ("何首乌", "g", 15), ("荆芥", "g", 6), ("防风", "g", 6), ("白蒺藜", "g", 10), ("黄芪", "g", 15), ("甘草", "g", 6)]),
    },
]

SYNDROMES = [
    # ============ 便秘七型 ============
    {"disease_type": "便秘", "syndrome_code": "BM_DCJJ", "syndrome_name": "大肠津亏",
     "treatment_principle": "增液润肠，通便导下",
     "required_symptoms": {"stool_condition": ["干结", "秘结"], "tongue_coating": ["少苔", "无苔"]},
     "optional_symptoms": {"thirst": True, "tongue_color": "红", "pulse_fine": True},
     "tongue_pulse": "舌红少津，脉细", "recommended_formulas": ["增液汤", "麻仁润肠丸"],
     "modification_rules": {"口干明显": "加天花粉15g、石斛12g生津", "便结难解": "加火麻仁15g、郁李仁12g润肠"},
     "confidence_threshold": 0.65, "priority": 60, "is_active": 1},
    {"disease_type": "便秘", "syndrome_code": "BM_DCHJ", "syndrome_name": "大肠寒结",
     "treatment_principle": "温里散寒，通便止痛",
     "required_symptoms": {"stool_condition": ["秘结", "干结"], "tongue_coating": ["白", "白滑", "白厚"]},
     "optional_symptoms": {"pulse_deep": True, "pulse_slow": True, "abdomen": "腹胀"},
     "tongue_pulse": "舌淡苔白滑，脉沉迟", "recommended_formulas": ["大黄附子汤"],
     "modification_rules": {"腹冷痛明显": "加干姜6g、肉桂6g温中", "寒甚": "加附子6g（先煎）"},
     "confidence_threshold": 0.65, "priority": 58, "is_active": 1},
    {"disease_type": "便秘", "syndrome_code": "BM_WCRJ", "syndrome_name": "胃肠热结",
     "treatment_principle": "清热通腑，润肠导滞",
     "required_symptoms": {"stool_condition": ["干结", "秘结"], "tongue_coating": ["黄", "黄燥", "黄腻"]},
     "optional_symptoms": {"pulse_rapid": True, "pulse_slippery": True, "bitter_mouth": True, "urination": "短赤"},
     "tongue_pulse": "舌红苔黄燥，脉滑数", "recommended_formulas": ["麻子仁丸"],
     "modification_rules": {"腹胀满甚": "加枳实10g、厚朴10g行气", "热结重": "加大黄9g（后下）通腑"},
     "confidence_threshold": 0.65, "priority": 62, "is_active": 1},
    {"disease_type": "便秘", "syndrome_code": "BM_QXBJ", "syndrome_name": "气虚便结",
     "treatment_principle": "益气润肠，健脾通便",
     "required_symptoms": {"stool_condition": ["干结", "秘结"], "fatigue": True},
     "optional_symptoms": {"pulse_weak": True, "poor_appetite": True, "pale_complexion": True, "tongue_color": ["淡", "淡白"]},
     "tongue_pulse": "舌淡苔薄，脉虚", "recommended_formulas": ["黄芪汤", "补中益气汤"],
     "modification_rules": {"气虚明显": "重用黄芪至30g", "纳差": "加党参12g、白术12g健脾"},
     "confidence_threshold": 0.65, "priority": 59, "is_active": 1},
    {"disease_type": "便秘", "syndrome_code": "BM_QZBX", "syndrome_name": "气滞不行",
     "treatment_principle": "行气导滞，通便除胀",
     "required_symptoms": {"stool_condition": ["干结", "秘结"], "abdomen": "腹胀"},
     "optional_symptoms": {"pulse_wiry": True, "insomnia": True, "poor_appetite": True},
     "tongue_pulse": "舌淡红苔薄，脉弦", "recommended_formulas": ["六磨汤"],
     "modification_rules": {"嗳气频作": "加陈皮10g、半夏9g和胃", "胸胁胀满": "加柴胡10g、香附10g疏肝"},
     "confidence_threshold": 0.65, "priority": 57, "is_active": 1},
    {"disease_type": "便秘", "syndrome_code": "BM_QXLK", "syndrome_name": "气血两亏",
     "treatment_principle": "补气养血，润肠通便",
     "required_symptoms": {"stool_condition": ["干结", "秘结"], "pale_complexion": True, "fatigue": True},
     "optional_symptoms": {"pulse_fine": True, "pulse_weak": True, "insomnia": True, "tongue_color": "淡白"},
     "tongue_pulse": "舌淡苔薄，脉细弱", "recommended_formulas": ["八珍汤", "当归连翘汤"],
     "modification_rules": {"血虚明显": "加熟地15g、何首乌15g养血", "便秘重": "加火麻仁15g、肉苁蓉15g润肠"},
     "confidence_threshold": 0.65, "priority": 61, "is_active": 1},
    {"disease_type": "便秘", "syndrome_code": "BM_YXBJ", "syndrome_name": "阴虚便结",
     "treatment_principle": "滋阴润肠，增水行舟",
     "required_symptoms": {"stool_condition": ["干结", "秘结"], "tongue_color": "红", "tongue_coating": ["少苔", "无苔"]},
     "optional_symptoms": {"pulse_fine": True, "pulse_rapid": True, "insomnia": True, "fever": "潮热"},
     "tongue_pulse": "舌红少苔，脉细数", "recommended_formulas": ["增液汤", "麻仁滋脾丸"],
     "modification_rules": {"五心烦热": "加地骨皮10g、银柴胡10g退虚热", "便如羊屎": "加火麻仁15g、郁李仁12g润肠"},
     "confidence_threshold": 0.65, "priority": 60, "is_active": 1},

    # ============ 肛门湿疹/瘙痒三型 ============
    {"disease_type": "肛门湿疹", "syndrome_code": "SZ_SRXZ", "syndrome_name": "湿热下注",
     "treatment_principle": "清热利湿，祛风止痒",
     "required_symptoms": {"itching": {"present": True}, "tongue_coating": ["黄腻", "黄"]},
     "optional_symptoms": {"tongue_color": "红", "pulse_slippery": True, "pulse_wiry": True, "urination": "短赤", "bitter_mouth": True},
     "tongue_pulse": "舌红苔黄腻，脉弦滑", "recommended_formulas": ["萆薢渗湿汤", "三妙丸"],
     "modification_rules": {"渗出糜烂重": "加薏苡仁15g、土茯苓15g利湿", "瘙痒剧烈": "加白鲜皮15g、地肤子10g止痒"},
     "confidence_threshold": 0.65, "priority": 60, "is_active": 1},
    {"disease_type": "肛门湿疹", "syndrome_code": "SZ_XSFZ", "syndrome_name": "血虚风燥",
     "treatment_principle": "养血润燥，祛风止痒",
     "required_symptoms": {"itching": {"present": True}, "pale_complexion": True},
     "optional_symptoms": {"pulse_fine": True, "tongue_color": ["淡", "淡白"], "fatigue": True, "insomnia": True},
     "tongue_pulse": "舌淡苔薄，脉细", "recommended_formulas": ["当归饮子"],
     "modification_rules": {"皮肤干燥肥厚": "加玄参15g、天花粉15g润燥", "入夜痒甚": "加酸枣仁15g、夜交藤15g安神"},
     "confidence_threshold": 0.65, "priority": 58, "is_active": 1},
    {"disease_type": "肛门湿疹", "syndrome_code": "SZ_ZQXJ", "syndrome_name": "中气下陷（脾虚湿蕴）",
     "treatment_principle": "补中益气，升阳举陷，兼清湿热",
     "required_symptoms": {"itching": {"present": True}, "fatigue": True, "poor_appetite": True},
     "optional_symptoms": {"pulse_weak": True, "tongue_color": ["淡", "淡白"], "stool_condition": "溏泄", "pale_complexion": True},
     "tongue_pulse": "舌淡苔薄，脉弱", "recommended_formulas": ["补中益气汤", "三妙丸"],
     "modification_rules": {"下坠明显": "加升麻6g、柴胡6g升阳", "兼湿热": "合三妙丸清利湿热"},
     "confidence_threshold": 0.65, "priority": 59, "is_active": 1},
]


async def main():
    async with AsyncSessionLocal() as session:
        print("=" * 64)
        print("「便秘七型 + 肛门湿疹」辨证补全")
        print("=" * 64)
        for data in FORMULAS:
            r = await session.execute(select(AnorectalFormula).where(AnorectalFormula.name == data["name"]))
            f = r.scalar_one_or_none()
            if f:
                for k, v in data.items():
                    setattr(f, k, v)
                print(f"更新方剂 {data['name']}")
            else:
                session.add(AnorectalFormula(**data))
                print(f"新增方剂 {data['name']}")
        for data in SYNDROMES:
            r = await session.execute(select(SyndromeRule).where(SyndromeRule.syndrome_code == data["syndrome_code"]))
            s = r.scalar_one_or_none()
            if s:
                for k, v in data.items():
                    setattr(s, k, v)
                print(f"更新证型 {data['syndrome_code']} {data['syndrome_name']}")
            else:
                session.add(SyndromeRule(**data))
                print(f"新增证型 {data['syndrome_code']} {data['syndrome_name']}")
        await session.commit()
        print("\n✅ 便秘七型与肛门湿疹辨证补全完成。")


if __name__ == "__main__":
    asyncio.run(main())
