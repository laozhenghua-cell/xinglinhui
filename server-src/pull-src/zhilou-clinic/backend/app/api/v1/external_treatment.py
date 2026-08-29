"""
外治法推荐API
External Treatment Recommendation Routes
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.external_treatment import ExternalTreatment
from app.models.user import User
from app.core.security import get_current_user


router = APIRouter(prefix="/external-treatments", tags=["external_treatments"])

_HIGH_RISK_MARKERS = (
    "注射", "封闭", "枯痔", "红粉", "红升", "砒", "鸦胆", "亚甲兰", "布比卡因", "腐蚀"
)


def _is_high_risk(treatment: ExternalTreatment) -> bool:
    text = f"{treatment.name or ''}{treatment.source or ''}{treatment.treatment_type or ''}"
    return treatment.treatment_type == "injection" or any(marker in text for marker in _HIGH_RISK_MARKERS)


def _treatment_payload(treatment: ExternalTreatment, compact: bool = False) -> dict:
    high_risk = _is_high_risk(treatment)
    payload = {
        "id": str(treatment.id),
        "name": treatment.name,
        "treatment_type": treatment.treatment_type,
        "treatment_type_name": _get_treatment_type_name(treatment.treatment_type),
        "composition": treatment.composition,
        "preparation": treatment.preparation,
        "usage": treatment.usage,
        "frequency": treatment.frequency,
        "duration": treatment.duration,
        "function": treatment.function,
        "indications": treatment.indications,
        "syndrome_types": treatment.syndrome_types,
        "disease_types": treatment.disease_types,
        "contraindications": treatment.contraindications,
        "precautions": treatment.precautions,
        "source": treatment.source,
        "priority": treatment.priority,
        "notes": treatment.notes,
        "learning_only": high_risk,
        "self_execution_allowed": False if high_risk else None,
        "risk_label": "高风险·仅院内专科" if high_risk else "需医师审核",
        "clinical_governance": [
            "诊断和适应证由专科医师确认",
            "完成禁忌证核对、知情同意和必要检查",
            "具备无菌条件、急救药械和术后观察安排",
            "记录操作者、批号、患者反应、术后医嘱和复诊结果",
        ] if high_risk else [],
    }
    if high_risk:
        payload["composition"] = "高风险操作参数已隐藏"
        payload["preparation"] = "制备/配制参数仅在院内批准协议和资质培训中管理"
        payload["usage"] = "仅限资质人员按院内协议执行，不提供患者自行操作步骤"
        payload["frequency"] = None
        payload["duration"] = None
    if compact:
        return {key: payload[key] for key in ("id", "name", "function", "indications", "source", "priority", "learning_only", "risk_label")}
    return payload


def _require_clinician(current_user: User) -> User:
    if current_user.role not in {"admin", "doctor"}:
        raise HTTPException(status_code=403, detail="仅医生或管理员可访问院内学习资料")
    return current_user


@router.get("/recommend/{syndrome_type}")
async def recommend_by_syndrome(
    syndrome_type: str,
    disease_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    根据证型推荐外治法

    Args:
        syndrome_type: 证型（如：湿热下注型、气血两虚型）
        disease_type: 疾病类型（如：痔疮、肛裂）

    Returns:
        推荐的外治法列表，按优先级排序
    """

    # 构建查询条件
    conditions = []

    # 证型匹配：syndrome_types JSONB数组包含该证型
    if syndrome_type and syndrome_type != "通用":
        conditions.append(
            or_(
                ExternalTreatment.syndrome_types.contains([syndrome_type]),
                ExternalTreatment.syndrome_types.contains(["通用"])
            )
        )

    # 疾病类型匹配
    if disease_type:
        conditions.append(
            ExternalTreatment.disease_types.contains([disease_type])
        )

    # 执行查询
    if conditions:
        stmt = select(ExternalTreatment).where(
            and_(*conditions)
        ).order_by(ExternalTreatment.priority.desc())
    else:
        stmt = select(ExternalTreatment).order_by(
            ExternalTreatment.priority.desc()
        )

    result = await db.execute(stmt)
    treatments = result.scalars().all()

    if not treatments:
        # 如果没有精确匹配，返回通用外治法
        stmt = select(ExternalTreatment).where(
            ExternalTreatment.syndrome_types.contains(["通用"])
        ).order_by(ExternalTreatment.priority.desc())
        result = await db.execute(stmt)
        treatments = result.scalars().all()

    return {
        "syndrome_type": syndrome_type,
        "disease_type": disease_type,
        "count": len(treatments),
        "treatments": [_treatment_payload(t) for t in treatments]
    }


@router.get("/by-type/{treatment_type}")
async def get_by_type(
    treatment_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    按外治法类型查询

    Args:
        treatment_type: fumigation(熏洗), ointment(外敷), suppository(栓剂), injection(注射)
    """
    stmt = select(ExternalTreatment).where(
        ExternalTreatment.treatment_type == treatment_type
    ).order_by(ExternalTreatment.priority.desc())

    result = await db.execute(stmt)
    treatments = result.scalars().all()

    return {
        "treatment_type": treatment_type,
        "treatment_type_name": _get_treatment_type_name(treatment_type),
        "count": len(treatments),
        "treatments": [_treatment_payload(t) for t in treatments]
    }


@router.get("/detail/{treatment_id}")
async def get_treatment_detail(
    treatment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取外治法详情"""
    stmt = select(ExternalTreatment).where(
        ExternalTreatment.id == treatment_id
    )
    result = await db.execute(stmt)
    treatment = result.scalar_one_or_none()

    if not treatment:
        raise HTTPException(status_code=404, detail="外治法不存在")

    return _treatment_payload(treatment)


@router.get("/detail/{treatment_id}/clinical-learning")
async def get_treatment_clinical_learning(
    treatment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """医生学习摘要：保留专科背景和治理要求，不下发可执行操作参数。"""
    _require_clinician(current_user)
    result = await db.execute(select(ExternalTreatment).where(ExternalTreatment.id == treatment_id))
    treatment = result.scalar_one_or_none()
    if not treatment:
        raise HTTPException(status_code=404, detail="外治法不存在")
    data = _treatment_payload(treatment)
    return {
        "id": data["id"],
        "name": data["name"],
        "treatment_type": data["treatment_type"],
        "treatment_type_name": data["treatment_type_name"],
        "source": data.get("source"),
        "risk_label": data.get("risk_label"),
        "learning_only": data.get("learning_only"),
        "function": data.get("function"),
        "indications": data.get("indications"),
        "contraindications": data.get("contraindications"),
        "precautions": data.get("precautions"),
        "notes": "历史专科资料仅用于医生学习和院内评审；具体执行必须依据本院受控协议、资质培训和现行规范。",
        "clinical_governance": data.get("clinical_governance", []),
        "operational_parameters": "请查阅本院受控的专科操作协议，不通过通用接口下发。",
    }


@router.get("/all")
async def get_all_treatments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有外治法（按类型分组）"""
    stmt = select(ExternalTreatment).order_by(
        ExternalTreatment.treatment_type,
        ExternalTreatment.priority.desc()
    )
    result = await db.execute(stmt)
    treatments = result.scalars().all()

    # 按类型分组
    grouped = {
        "fumigation": [],
        "ointment": [],
        "suppository": [],
        "injection": []
    }

    for t in treatments:
        if t.treatment_type in grouped:
            grouped[t.treatment_type].append(_treatment_payload(t, compact=True))

    return {
        "fumigation": {
            "name": "熏洗方",
            "count": len(grouped["fumigation"]),
            "treatments": grouped["fumigation"]
        },
        "ointment": {
            "name": "外敷药膏",
            "count": len(grouped["ointment"]),
            "treatments": grouped["ointment"]
        },
        "suppository": {
            "name": "栓剂",
            "count": len(grouped["suppository"]),
            "treatments": grouped["suppository"]
        },
        "injection": {
            "name": "注射疗法",
            "count": len(grouped["injection"]),
            "treatments": grouped["injection"]
        }
    }


def _get_treatment_type_name(treatment_type: str) -> str:
    """获取外治法类型中文名"""
    type_map = {
        "fumigation": "熏洗方",
        "ointment": "外敷药膏",
        "suppository": "栓剂",
        "injection": "注射疗法"
    }
    return type_map.get(treatment_type, treatment_type)
