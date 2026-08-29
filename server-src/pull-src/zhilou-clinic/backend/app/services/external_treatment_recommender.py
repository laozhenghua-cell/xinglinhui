"""外治法推荐：兼容组合证名和同病种的临床分型名称。"""
import re
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.external_treatment import ExternalTreatment


DISEASE_FAMILIES = {
    "痔疮": {"痔疮", "内痔", "外痔", "混合痔", "血栓外痔", "内痔嵌顿", "便血", "I-II期内痔"},
    "肛周脓肿": {"肛周脓肿", "肛门直肠周围脓肿", "肛痈"},
    "肛裂": {"肛裂"},
    "肛瘘": {"肛瘘", "肛漏", "漏"},
    "直肠脱垂": {"直肠脱垂", "脱肛"},
    "肛门疣赘": {"肛门疣赘", "疣赘", "尖锐湿疣"},
    "肛门疖肿": {"肛门疖肿", "疖肿", "坐板疮"},
    "肛门湿疹": {"肛门湿疹", "湿疹", "肛门瘙痒"},
}


def _syndrome_tokens(name: str) -> set[str]:
    return {
        token.removesuffix("型").strip()
        for token in re.split(r"[，、,/；;]+", name or "")
        if token.strip()
    }


def _matches_syndrome(treatment: ExternalTreatment, syndrome_name: str) -> bool:
    result_tokens = _syndrome_tokens(syndrome_name)
    treatment_tokens = {
        normalized
        for item in (treatment.syndrome_types or [])
        for normalized in _syndrome_tokens(str(item))
    }
    return bool(result_tokens & treatment_tokens)


def _matches_disease(treatment: ExternalTreatment, disease_type: str) -> bool:
    accepted = DISEASE_FAMILIES.get(disease_type, {disease_type})
    return bool(accepted & set(treatment.disease_types or []))


async def recommend_external_treatments(
    session: AsyncSession,
    disease_type: str,
    syndrome_name: str,
    limit: int = 5,
) -> List[ExternalTreatment]:
    result = await session.execute(
        select(ExternalTreatment)
        .where(ExternalTreatment.treatment_type != "injection")
        .order_by(ExternalTreatment.priority.desc())
    )
    treatments = result.scalars().all()
    ranked = []
    for treatment in treatments:
        if not _matches_disease(treatment, disease_type):
            continue
        syndrome_match = _matches_syndrome(treatment, syndrome_name)
        is_general = "通用" in (treatment.syndrome_types or [])
        if syndrome_match or is_general:
            ranked.append((1 if syndrome_match else 0, treatment.priority, treatment))
    ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [item[2] for item in ranked[:limit]]
