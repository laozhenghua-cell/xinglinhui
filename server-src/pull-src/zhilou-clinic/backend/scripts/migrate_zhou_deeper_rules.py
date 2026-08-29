"""补充《临床经验原文》后续缺失的病因分型与肛瘘创面阶段规则。

规则均标注原文来源；没有足够资料时，辨证引擎只返回候选，不生成方剂。
脚本可重复执行，按 syndrome_code 更新已有记录。
"""
import asyncio
import sys
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import AsyncSessionLocal
from app.models.diagnosis import SyndromeRule


RULES = [
    {
        "disease_type": "直肠脱垂", "syndrome_code": "ZCTH_SG",
        "syndrome_name": "肾虚不固型", "treatment_principle": "补肾纳气，温阳固脱",
        "required_symptoms": {"prolapse_symptom": {"present": True}, "lumbar_soreness": True, "urination": ["频数", "清长"]},
        "optional_symptoms": {"fatigue": True, "pale_complexion": True, "stool_condition": ["溏泄", "先干后溏"], "pulse_deep": True},
        "tongue_pulse": "舌淡或淡胖，脉沉细/弱", "recommended_formulas": [],
        "modification_rules": {}, "confidence_threshold": 0.65, "priority": 72, "is_active": 1,
    },
    {
        "disease_type": "直肠脱垂", "syndrome_code": "ZCTH_XE",
        "syndrome_name": "小儿气血未壮型", "treatment_principle": "补中益气，升阳举陷；结合原发腹泻调治",
        "required_symptoms": {"prolapse_symptom": {"present": True}, "age_group": "小儿", "stool_condition": ["溏泄", "腹泻"]},
        "optional_symptoms": {"poor_appetite": True, "pale_complexion": True, "fatigue": True, "tongue_color": ["淡", "淡白"]},
        "tongue_pulse": "舌淡，脉虚弱", "recommended_formulas": ["补中益气汤"],
        "modification_rules": {}, "confidence_threshold": 0.65, "priority": 71, "is_active": 1,
    },
    {
        "disease_type": "直肠脱垂", "syndrome_code": "ZCTH_SR",
        "syndrome_name": "湿热下注努挣型", "treatment_principle": "清利湿热，通便降浊，兼顾升提",
        "required_symptoms": {"prolapse_symptom": {"present": True}, "bitter_mouth": True, "stool_condition": ["干结", "秘结"]},
        "optional_symptoms": {"urination": "短赤", "tongue_coating": "黄腻", "pulse_slippery": True, "anal_swelling": ["中度", "重度"]},
        "tongue_pulse": "舌红苔黄腻，脉滑数", "recommended_formulas": [],
        "modification_rules": {}, "confidence_threshold": 0.65, "priority": 69, "is_active": 1,
    },
    {
        "disease_type": "肛瘘", "syndrome_code": "GL_HFQ",
        "syndrome_name": "化腐期", "treatment_principle": "保持引流，清除腐败组织；严禁自行探查或腐蚀",
        "required_symptoms": {"wound_phase": "腐肉"}, "optional_symptoms": {"secretion": ["脓性", "血性"]},
        "tongue_pulse": "局部创面阶段字段", "recommended_formulas": [], "modification_rules": {}, "confidence_threshold": 0.65, "priority": 80, "is_active": 1,
    },
    {
        "disease_type": "肛瘘", "syndrome_code": "GL_TDQ",
        "syndrome_name": "托毒期", "treatment_principle": "评估主管、支管和死腔，保证脓毒外泄，防止假愈合",
        "required_symptoms": {"wound_phase": "脓液"}, "optional_symptoms": {"secretion": "脓性"},
        "tongue_pulse": "局部创面阶段字段", "recommended_formulas": [], "modification_rules": {}, "confidence_threshold": 0.65, "priority": 79, "is_active": 1,
    },
    {
        "disease_type": "肛瘘", "syndrome_code": "GL_SJQ",
        "syndrome_name": "生肌期", "treatment_principle": "腐脱管化后促进新鲜肉芽生长，由专业人员换药",
        "required_symptoms": {"wound_phase": "肉芽"}, "optional_symptoms": {"secretion": ["无", "血性"]},
        "tongue_pulse": "局部创面阶段字段", "recommended_formulas": [], "modification_rules": {}, "confidence_threshold": 0.65, "priority": 78, "is_active": 1,
    },
    {
        "disease_type": "肛瘘", "syndrome_code": "GL_SQK",
        "syndrome_name": "收口期", "treatment_principle": "检查桥形粘连、残余窦道和假愈合，审慎促进收口",
        "required_symptoms": {"wound_phase": "收口"}, "optional_symptoms": {"bridge_adhesion": True},
        "tongue_pulse": "局部创面阶段字段", "recommended_formulas": [], "modification_rules": {}, "confidence_threshold": 0.65, "priority": 77, "is_active": 1,
    },
]


async def main():
    async with AsyncSessionLocal() as session:
        for data in RULES:
            result = await session.execute(select(SyndromeRule).where(SyndromeRule.syndrome_code == data["syndrome_code"]))
            rule = result.scalar_one_or_none()
            if rule:
                for key, value in data.items():
                    setattr(rule, key, value)
                print(f"更新 {data['syndrome_code']} {data['syndrome_name']}")
            else:
                session.add(SyndromeRule(**data))
                print(f"新增 {data['syndrome_code']} {data['syndrome_name']}")
        await session.commit()
        print(f"完成：{len(RULES)} 条补充规则")


if __name__ == "__main__":
    asyncio.run(main())
