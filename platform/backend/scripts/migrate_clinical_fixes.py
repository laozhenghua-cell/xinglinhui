"""
临床可用性修复：让「手工辨证」能命中所有证型。

体检发现的问题：部分证型规则的 required/optional 症状值，前端四诊组件根本选不到
或类型不匹配，导致这些证型手工辨证永远无法命中（只有一键模板能塞入规则值）。

本脚本修正这些字段不匹配：
1. 虚寒证(ZC_VHAN)：fatigue 应为布尔、脱出用 prolapse_symptom、舌淡白是舌质、腹胀用 abdomen
2. 虚热脓肿(GZ_XR)：脓肿存在用可选到的 anal_swelling 表达
3. 肛瘘虚热内蕴(GL_XRNY)：分泌物/慢性瘘管/愈合延迟改为可选的乏力+面色无华
4. 大肠津亏(BM_DCJJ)：口渴为字符串选项
5. 大肠寒结(BM_DCHJ)：舌苔白滑/白厚/薄白

幂等：按 syndrome_code 更新。
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.diagnosis import SyndromeRule


FIXES = {
    "ZC_VHAN": {
        "required_symptoms": {
            "fatigue": True,
            "bleeding": {"color": "晦暗", "present": True},
            "pale_complexion": True,
            "stool_condition": "稀软",
        },
        "optional_symptoms": {
            "prolapse_symptom": {"present": True},
            "urination": "清长",
            "pulse_weak": True,
            "poor_appetite": True,
            "tongue_color": "淡白",
            "abdomen": "腹胀",
        },
    },
    "GZ_XR": {
        "required_symptoms": {
            "fever": "低热",
            "anal_swelling": ["轻度", "中度", "重度"],
            "fatigue": True,
        },
        "optional_symptoms": {
            "pain": {"degree": "轻度"},
            "pulse_fine": True,
            "pulse_weak": True,
            "night_sweats": True,
            "tongue_color": "淡",
            "pale_complexion": True,
        },
    },
    "GL_XRNY": {
        "required_symptoms": {
            "fatigue": True,
            "pale_complexion": True,
        },
        "optional_symptoms": {
            "pulse_weak": True,
            "pulse_fine": True,
            "poor_appetite": True,
            "tongue_color": "红",
            "tongue_coating": ["少苔", "无苔"],
            "night_sweats": True,
        },
    },
    "BM_DCJJ": {
        "optional_symptoms": {
            "thirst": ["口干不欲饮", "口渴喜热饮"],
            "pulse_fine": True,
            "tongue_color": "红",
        },
    },
    "BM_DCHJ": {
        "required_symptoms": {
            "stool_condition": ["秘结", "干结"],
            "tongue_coating": ["白滑", "白厚", "薄白"],
        },
    },
}


async def main():
    async with AsyncSessionLocal() as session:
        print("=" * 64)
        print("临床可用性修复：辨证规则字段对齐前端")
        print("=" * 64)
        for code, patch in FIXES.items():
            r = await session.execute(select(SyndromeRule).where(SyndromeRule.syndrome_code == code))
            rule = r.scalar_one_or_none()
            if not rule:
                print(f"⚠️ 未找到 {code}")
                continue
            for field, value in patch.items():
                setattr(rule, field, value)
            print(f"✅ 修正 {code} {rule.syndrome_name}")
        await session.commit()
        print("\n✅ 临床可用性修复完成。")


if __name__ == "__main__":
    asyncio.run(main())
