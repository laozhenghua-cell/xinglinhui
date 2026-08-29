"""
从辨证规则自动生成症状模板，覆盖全部证型。

每个模板的 symptoms_data 直接由对应证型规则的 required_symptoms + optional_symptoms
归一化而来，保证「一键填充 → 智能辨证」能命中该证型（高置信度）。

幂等：按 (disease_type, syndrome_code) upsert system 模板。
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.diagnosis import SyndromeRule, SymptomTemplate


def _normalize(value):
    """把规则匹配值转成前端单选框可接受的单值。"""
    if isinstance(value, list):
        return value[0] if value else None
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    return value


def build_template_symptoms(rule: SyndromeRule) -> dict:
    """合并必需+可选症状并归一化，作为模板症状数据。"""
    merged = {}
    for source in (rule.required_symptoms or {}, rule.optional_symptoms or {}):
        for key, value in source.items():
            normalized = _normalize(value)
            # 已有更精确的 required 值时，不被 optional 覆盖
            if key not in merged or isinstance(merged[key], bool) is False:
                if key not in merged:
                    merged[key] = normalized
    return merged


async def main():
    async with AsyncSessionLocal() as session:
        print("=" * 64)
        print("自动生成证型症状模板（覆盖全部证型）")
        print("=" * 64)
        result = await session.execute(
            select(SyndromeRule).where(SyndromeRule.is_active == 1).order_by(SyndromeRule.disease_type, SyndromeRule.priority.desc())
        )
        rules = result.scalars().all()

        created = updated = 0
        for rule in rules:
            symptoms_data = build_template_symptoms(rule)
            if not symptoms_data:
                continue

            stmt = select(SymptomTemplate).where(
                SymptomTemplate.disease_type == rule.disease_type,
                SymptomTemplate.syndrome_code == rule.syndrome_code,
                SymptomTemplate.template_type == "system",
            )
            existing = (await session.execute(stmt)).scalar_one_or_none()

            payload = {
                "disease_type": rule.disease_type,
                "syndrome_code": rule.syndrome_code,
                "template_name": f"{rule.syndrome_name}（一键辨证）",
                "description": f"治则：{rule.treatment_principle}；舌脉：{rule.tongue_pulse or ''}",
                "symptoms_data": symptoms_data,
                "template_type": "system",
                "usage_count": 0,
                "is_active": 1,
            }

            if existing:
                for k, v in payload.items():
                    setattr(existing, k, v)
                updated += 1
            else:
                session.add(SymptomTemplate(**payload))
                created += 1

        await session.commit()
        total = await session.execute(select(SymptomTemplate).where(SymptomTemplate.template_type == "system"))
        print(f"\n✅ 完成：新增 {created}，更新 {updated}")
        print(f"📊 系统模板总数：{len(total.scalars().all())}")


if __name__ == "__main__":
    asyncio.run(main())
