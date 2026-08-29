"""
原著「辨证用药」精准化补全脚本

目的：把《临床经验原文.txt》中一切治疗方法精准对齐到
「病种 → 证型 → 治则 → 方剂 → 药物组成与剂量」。

本脚本幂等，按 syndrome_code / formula.name upsert，可重复执行。

完成内容：
1. 修正与原文剂量不符的 3 首方剂（凉血地黄汤 / 止痛如神汤 / 萆薢渗湿汤）
2. 补充原文已引用但数据库缺失的 4 首方剂（升阳除湿汤 / 参蚧散 / 补肾固脱散 / 定喘固脱汤）
3. 补充 2 首临床扩展方以消除悬空引用（润肠汤 / 仙方活命饮）
4. 补充肛门疣赘 - 肝肾阴虚证 辨证规则（杞菊地黄汤）
5. 补全直肠脱垂 肾虚不固 / 湿热下注 两型的推荐方剂
6. 修正痔疮气血亏损型的推荐方剂为原文所述（八珍汤 / 补中益气汤 / 当归连翘汤）
7. 为罂粟壳补充受控药品安全警示
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.diagnosis import SyndromeRule, SafetyRule
from app.models.knowledge import AnorectalFormula


def _comp(items):
    """构造结构化组成：[{"name","unit","dosage"}, ...]"""
    return [{"name": n, "unit": u, "dosage": d} for n, u, d in items]


# 与原文严格一致的方剂（含剂量）
FORMULAS_FIX = [
    {
        "name": "凉血地黄汤",
        "source": "原文·证治方（原文第282行）",
        "formula_type": "internal",
        "syndrome_type": "血热肠燥",
        "disease_types": ["肛裂"],
        "function": "凉血润燥，止血止痛",
        "indications": "肛裂火燥证/血热肠燥：大便秘结、便时出血、便后疼痛、口苦咽干、心烦。",
        "usage": "水煎服，日服一剂。",
        "composition": _comp([
            ("细生地", "g", 20), ("归尾", "g", 10), ("地榆", "g", 15),
            ("槐角", "g", 10), ("黄连", "g", 6), ("天花粉", "g", 15),
            ("生甘草", "g", 10), ("升麻", "g", 10), ("赤芍", "g", 10),
            ("枳壳", "g", 6), ("黄芩", "g", 10), ("荆芥", "g", 6),
        ]),
    },
    {
        "name": "止痛如神汤",
        "source": "原文·证治方（原文第284行）",
        "formula_type": "internal",
        "syndrome_type": "湿热下注",
        "disease_types": ["肛裂"],
        "function": "清热利湿，润燥止痛",
        "indications": "肛裂湿热证：大便秘结、肛门坠胀、便后持续疼痛、偶有脓汁或黏液。",
        "usage": "水煎服，日服一剂。",
        "composition": _comp([
            ("秦艽", "g", 10), ("桃仁", "g", 10), ("皂角子", "g", 6),
            ("苍术", "g", 10), ("防风", "g", 10), ("黄柏", "g", 10),
            ("归尾", "g", 10), ("泽泻", "g", 10), ("槟榔", "g", 6),
            ("大黄", "g", 15),
        ]),
    },
    {
        "name": "萆薢渗湿汤",
        "source": "原文·证治方（原文第317行）",
        "formula_type": "internal",
        "syndrome_type": "湿热下注",
        "disease_types": ["肛门疣赘"],
        "function": "清热解毒，利湿散结",
        "indications": "肛门疣赘湿热下注证：肛门潮湿瘙痒、疣面糜烂渗出、基底潮红、便干溲赤。",
        "usage": "水煎服，每日一剂。",
        "composition": _comp([
            ("萆薢", "g", 12), ("薏苡仁", "g", 15), ("黄柏", "g", 10),
            ("赤茯苓", "g", 12), ("丹皮", "g", 12), ("泽泻", "g", 12),
            ("滑石", "g", 15), ("通草", "g", 6),
        ]),
    },
]

FORMULAS_ADD = [
    {
        "name": "升阳除湿汤",
        "source": "原文·处方（原文第385行）",
        "formula_type": "internal",
        "syndrome_type": "湿热下注",
        "disease_types": ["直肠脱垂"],
        "function": "清利湿热，通便降浊，兼顾升提",
        "indications": "直肠脱垂湿热努挣型：肛门下坠肿痛、小便淋漓、胸闷口苦口腻、脉滑数。",
        "usage": "每日一剂，水煎服。",
        "composition": _comp([
            ("升麻", "g", 3), ("柴胡", "g", 6), ("防风", "g", 9),
            ("麦芽", "g", 10), ("泽泻", "g", 6), ("苍术", "g", 9),
            ("神曲", "g", 9), ("茯苓", "g", 12), ("甘草", "g", 6),
            ("木香", "g", 6),
        ]),
    },
    {
        "name": "参蚧散",
        "source": "原文·处方（原文第384行）",
        "formula_type": "internal",
        "syndrome_type": "肾虚不固",
        "disease_types": ["直肠脱垂"],
        "function": "补肾纳气，温阳固脱",
        "indications": "直肠脱垂肾虚不固型：腰膝酸软、消化不良、身寒肢冷、尿频、体倦无力。",
        "usage": "人参、蛤蚧各3克，分2次冲服。",
        "composition": _comp([("人参", "g", 3), ("蛤蚧", "g", 3)]),
    },
    {
        "name": "补肾固脱散",
        "source": "原文·处方（原文第384-385行）",
        "formula_type": "internal",
        "syndrome_type": "肾虚不固",
        "disease_types": ["直肠脱垂"],
        "function": "补肾纳气，温阳固脱",
        "indications": "直肠脱垂肾虚不固型的收涩固脱备用方。",
        "usage": "研细末冲服，每次15克，每日2次。",
        "notes": "含罂粟壳，属麻醉药品管制品种：须医师严格掌握、中病即止、不宜久服，避免依赖与成瘾。",
        "composition": _comp([
            ("龙骨", "g", 9), ("牡蛎", "g", 9), ("诃子", "g", 6),
            ("赤石脂", "g", 6), ("熟地", "g", 12), ("五味子", "g", 6),
            ("菟丝子", "g", 6), ("罂粟壳", "g", 6),
        ]),
    },
    {
        "name": "定喘固脱汤",
        "source": "原文·处方（原文第383行）",
        "formula_type": "internal",
        "syndrome_type": "肺虚咳喘",
        "disease_types": ["直肠脱垂"],
        "function": "温肺益气，定喘固脱",
        "indications": "直肠脱垂肺虚咳喘、肠寒脱垂型：慢性咳喘、动则气短、舌淡苔白滑、脉沉细略滑。",
        "usage": "每日一剂，水煎服；巩固可三倍量研末炼蜜为丸，丸重9克，每日2次、每服2丸。",
        "composition": _comp([
            ("太子参", "g", 20), ("黄芪", "g", 20), ("全当归", "g", 8),
            ("杭白芍", "g", 9), ("炒白术", "g", 10), ("炙甘草", "g", 6),
            ("桑白皮", "g", 8), ("贝母", "g", 8), ("羌活", "g", 6),
            ("肉桂", "g", 6), ("五味子", "g", 16),
        ]),
    },
    # 补中益气汤的两处原文精确变体（剂量不同，不可混用）
    {
        "name": "补中益气汤·痔疮气血亏损",
        "source": "原文·证治方（原文第146行）",
        "formula_type": "internal",
        "syndrome_type": "气血两虚",
        "disease_types": ["痔疮"],
        "function": "补气益血，升提中气",
        "indications": "痔疮气血亏损型：便血日久、面色无华、气短心悸、少气懒言、肛门坠重、痔脱难收。",
        "usage": "水煎服，日服一剂。",
        "composition": _comp([
            ("黄芪", "g", 15), ("党参", "g", 10), ("白术", "g", 10),
            ("柴胡", "g", 10), ("陈皮", "g", 10), ("升麻", "g", 12),
            ("当归", "g", 10), ("甘草", "g", 10),
        ]),
    },
    {
        "name": "补中益气汤·脱垂中气下陷",
        "source": "原文·验案处方（原文第377行）",
        "formula_type": "internal",
        "syndrome_type": "中气下陷",
        "disease_types": ["直肠脱垂"],
        "function": "补中益气，升阳举陷",
        "indications": "直肠脱垂中气下陷/小儿气血未壮型：便时脱出、面色晄白、食少便溏、脉虚弱。",
        "usage": "水煎服；小儿剂量须按体重与年龄由医师酌定，不可照搬成人。",
        "composition": _comp([
            ("蜜炙黄芪", "g", 20), ("太子参", "g", 20), ("全当归", "g", 6),
            ("升麻", "g", 6), ("炒白术", "g", 3), ("陈皮", "g", 6),
            ("炙甘草", "g", 6), ("柴胡", "g", 3), ("生姜", "片", 3),
            ("大枣", "枚", 2),
        ]),
    },
    # 临床扩展方：仅用于消除辨证规则的悬空引用，非原文
    {
        "name": "润肠汤",
        "source": "临床扩展（非原文）",
        "formula_type": "internal",
        "syndrome_type": "阴虚津亏",
        "disease_types": ["肛裂"],
        "function": "养阴润燥，润肠通便",
        "indications": "肛裂阴虚津亏证（系统扩展证型）：大便干燥、数日一行、裂口久不愈、口干咽燥。",
        "usage": "水煎服，日服一剂。",
        "composition": _comp([
            ("当归", "g", 12), ("生地", "g", 15), ("火麻仁", "g", 15),
            ("桃仁", "g", 10), ("枳壳", "g", 10),
        ]),
    },
    {
        "name": "仙方活命饮",
        "source": "临床扩展·经典方（非原文）",
        "formula_type": "internal",
        "syndrome_type": "热毒蕴结",
        "disease_types": ["肛周脓肿"],
        "function": "清热解毒，消肿溃坚，活血止痛",
        "indications": "肛周脓肿热毒蕴结未成脓期的经典备用方（原文首选内疏黄连汤）。",
        "usage": "水煎服，日服一剂。",
        "composition": _comp([
            ("金银花", "g", 20), ("白芷", "g", 6), ("贝母", "g", 6),
            ("防风", "g", 6), ("赤芍", "g", 10), ("当归尾", "g", 10),
            ("甘草节", "g", 6), ("皂角刺", "g", 10), ("天花粉", "g", 10),
            ("乳香", "g", 6), ("没药", "g", 6), ("陈皮", "g", 6),
        ]),
    },
]

# 补充/修正的证型规则
SYNDROME_UPSERTS = [
    {
        # 新增：肛门疣赘 - 肝肾阴虚证（原文第318-319行）
        "disease_type": "肛门疣赘", "syndrome_code": "YZ_GSYX",
        "syndrome_name": "肝肾阴虚",
        "treatment_principle": "滋补肝肾",
        "required_symptoms": {"tongue_color": "红", "tongue_coating": ["少苔", "无苔"]},
        "optional_symptoms": {"pulse_fine": True, "pulse_rapid": True, "insomnia": True,
                              "pale_complexion": True, "fatigue": True},
        "tongue_pulse": "舌红苔少，脉细数",
        "recommended_formulas": ["杞菊地黄汤"],
        "modification_rules": {
            "阴虚明显": "加麦冬12g、玄参12g养阴",
            "失眠重": "加酸枣仁15g、远志10g安神",
            "潮热盗汗": "加地骨皮10g、银柴胡10g退虚热",
        },
        "confidence_threshold": 0.6, "priority": 60, "is_active": 1,
    },
    {
        # 修正：直肠脱垂 - 肾虚不固，补全推荐方剂
        "disease_type": "直肠脱垂", "syndrome_code": "ZCTH_SG",
        "syndrome_name": "肾虚不固型",
        "treatment_principle": "补肾纳气，温阳固脱",
        "required_symptoms": {"prolapse_symptom": {"present": True}, "lumbar_soreness": True, "urination": ["频数", "清长"]},
        "optional_symptoms": {"fatigue": True, "pale_complexion": True, "stool_condition": ["溏泄", "先干后溏"], "pulse_deep": True},
        "tongue_pulse": "舌淡或淡胖，脉沉细/弱",
        "recommended_formulas": ["参蚧散", "补肾固脱散"],
        "modification_rules": {
            "腰膝酸软明显": "加杜仲10g、续断10g补肾强腰",
            "阳虚肢冷": "加肉桂6g、制附片6g（先煎）温阳",
            "久泻不止": "加肉豆蔻6g、补骨脂10g温脾固涩",
        },
        "confidence_threshold": 0.65, "priority": 72, "is_active": 1,
    },
    {
        # 修正：直肠脱垂 - 湿热下注努挣，补全推荐方剂
        "disease_type": "直肠脱垂", "syndrome_code": "ZCTH_SR",
        "syndrome_name": "湿热下注努挣型",
        "treatment_principle": "清利湿热，通便降浊，兼顾升提",
        "required_symptoms": {"prolapse_symptom": {"present": True}, "bitter_mouth": True, "stool_condition": ["干结", "秘结"]},
        "optional_symptoms": {"urination": "短赤", "tongue_coating": "黄腻", "pulse_slippery": True, "anal_swelling": ["中度", "重度"]},
        "tongue_pulse": "舌红苔黄腻，脉滑数",
        "recommended_formulas": ["升阳除湿汤"],
        "modification_rules": {
            "湿热重": "加黄柏10g、苍术10g清利湿热",
            "下坠明显": "加升麻3g、柴胡6g升阳举陷",
            "便溏": "加茯苓12g、泽泻10g分利水湿",
            "小便不畅": "加车前子10g、木通6g通淋",
        },
        "confidence_threshold": 0.65, "priority": 69, "is_active": 1,
    },
    {
        # 修正：痔疮 - 气血亏损型，推荐方剂对齐原文（第144-147行）
        "disease_type": "痔疮", "syndrome_code": "ZC_QXKS",
        "syndrome_name": "气血亏损，气不摄血",
        "treatment_principle": "补气益血",
        "required_symptoms": {"bleeding": {"present": True, "color": "淡红"}, "fatigue": True, "pale_complexion": True},
        "optional_symptoms": {"poor_appetite": True, "prolapse_symptom": {"present": True},
                              "pulse_weak": True, "pulse_fine": True, "tongue_color": "淡白", "stool_condition": "干结"},
        "tongue_pulse": "舌质淡，苔薄白，脉细弱",
        "recommended_formulas": ["八珍汤", "补中益气汤·痔疮气血亏损", "当归连翘汤"],
        "modification_rules": {
            "出血日久不止": "加阿胶12g、艾叶炭10g止血",
            "脱垂严重": "加升麻12g、柴胡10g升提",
            "气虚明显": "重用黄芪至30g",
            "虚中兼湿热": "选当归连翘汤，补虚中兼清湿热和血疏风",
        },
        "confidence_threshold": 0.70, "priority": 80, "is_active": 1,
    },
    {
        # 修正：直肠脱垂 - 中气下陷，指向原文精确变体
        "disease_type": "直肠脱垂", "syndrome_code": "ZC_ZQXX",
        "syndrome_name": "中气下陷",
        "treatment_principle": "补中益气，升阳举陷",
        "required_symptoms": {"prolapse_symptom": {"present": True}},
        "optional_symptoms": {"fatigue": True, "poor_appetite": True, "stool_condition": ["溏泄", "腹泻"],
                              "pale_complexion": True, "pulse_weak": True},
        "tongue_pulse": "舌淡或胖大齿痕，脉虚弱",
        "recommended_formulas": ["补中益气汤·脱垂中气下陷"],
        "modification_rules": {
            "久泻不止": "加肉豆蔻6g、补骨脂10g温脾固涩",
            "脱垂严重": "加升麻6g、乌梅10g、五味子10g收敛升提",
            "纳差明显": "加鸡内金10g、麦芽10g健胃消食",
        },
        "confidence_threshold": 0.65, "priority": 74, "is_active": 1,
    },
]

SAFETY_RULES = [
    {
        "rule_type": "dosage", "severity": "critical", "herb_name": "罂粟壳",
        "warning_message": "罂粟壳为麻醉药品管制品种，须医师严格掌握适应症与剂量，中病即止、不宜久服，避免依赖与成瘾。",
        "suggestion": "成方中含罂粟壳（如补肾固脱散）时，应核对患者身份、记录用药并限制疗程。",
        "is_active": 1,
    },
]


async def upsert_formula(session, data):
    result = await session.execute(
        select(AnorectalFormula).where(AnorectalFormula.name == data["name"])
    )
    formula = result.scalar_one_or_none()
    if formula:
        for key, value in data.items():
            setattr(formula, key, value)
        return f"更新方剂 {data['name']}"
    session.add(AnorectalFormula(**data))
    return f"新增方剂 {data['name']}"


async def upsert_syndrome(session, data):
    result = await session.execute(
        select(SyndromeRule).where(SyndromeRule.syndrome_code == data["syndrome_code"])
    )
    rule = result.scalar_one_or_none()
    if rule:
        for key, value in data.items():
            setattr(rule, key, value)
        return f"更新证型 {data['syndrome_code']} {data['syndrome_name']}"
    session.add(SyndromeRule(**data))
    return f"新增证型 {data['syndrome_code']} {data['syndrome_name']}"


async def main():
    async with AsyncSessionLocal() as session:
        print("=" * 64)
        print("原著「辨证用药」精准化补全")
        print("=" * 64)

        for data in FORMULAS_FIX:
            print(await upsert_formula(session, data))

        for data in FORMULAS_ADD:
            print(await upsert_formula(session, data))

        for data in SYNDROME_UPSERTS:
            print(await upsert_syndrome(session, data))

        for data in SAFETY_RULES:
            result = await session.execute(
                select(SafetyRule).where(
                    SafetyRule.herb_name == data["herb_name"],
                    SafetyRule.rule_type == data["rule_type"],
                )
            )
            rule = result.scalar_one_or_none()
            if rule:
                for key, value in data.items():
                    setattr(rule, key, value)
                print(f"更新安全规则 {data['herb_name']}")
            else:
                session.add(SafetyRule(**data))
                print(f"新增安全规则 {data['herb_name']}")

        await session.commit()
        print("\n✅ 全部补全完成。")


if __name__ == "__main__":
    asyncio.run(main())
