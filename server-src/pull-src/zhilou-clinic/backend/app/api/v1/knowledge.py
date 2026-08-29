import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.knowledge import AnorectalHerb, AnorectalFormula, AnorectalCase, PreventionGuide
from app.models.user import User
from app.services.zhou_coverage import coverage_report
from app.services.differential_diagnosis import get_differentials, list_disease_types
from app.services.procedures import get_acupuncture, get_surgical_techniques, list_procedure_diseases

router = APIRouter(prefix="/knowledge", tags=["知识库"])


@router.get("/zhou-coverage")
async def get_zhou_coverage(current_user: User = Depends(get_current_user)):
    """返回原文的结构化覆盖矩阵，供医生学习和质量核对。"""
    return coverage_report()


@router.get("/differentials")
async def list_differential_diseases(current_user: User = Depends(get_current_user)):
    """列出已建立鉴别诊断知识库的病种。"""
    return {"disease_types": list_disease_types()}


@router.get("/differentials/{disease_type}")
async def get_differential_by_disease(
    disease_type: str,
    current_user: User = Depends(get_current_user),
):
    """返回指定病种的鉴别诊断要点（用于防止误诊的临床提示）。"""
    return get_differentials(disease_type)


@router.get("/acupuncture/{disease_type}")
async def get_acupuncture_by_disease(
    disease_type: str,
    current_user: User = Depends(get_current_user),
):
    """返回指定病种的针刺方案（针灸属专业操作）。"""
    return get_acupuncture(disease_type)


@router.get("/surgical-techniques/{disease_type}")
async def get_surgical_techniques_by_disease(
    disease_type: str,
    current_user: User = Depends(get_current_user),
):
    """返回指定病种的手术技法（挂线、外剥内扎、注射等专科操作，仅供学习）。"""
    return get_surgical_techniques(disease_type)


@router.get("/procedures")
async def list_procedures(current_user: User = Depends(get_current_user)):
    """列出已建立针刺法与手术技法知识库的病种。"""
    return list_procedure_diseases()


_HIGH_RISK_FORMULA_MARKERS = (
    "注射", "封闭", "枯痔", "红粉", "红升", "砒", "鸦胆", "亚甲兰", "布比卡因",
    "挂线", "切开", "引流", "腐蚀",
)


def _formula_metadata(formula: AnorectalFormula) -> dict:
    """给知识库条目补充可筛选的出处和风险标签。"""
    source = formula.source or ""
    name = formula.name or ""
    is_high_risk = any(marker in f"{name}{source}" for marker in _HIGH_RISK_FORMULA_MARKERS)
    if is_high_risk:
        source_status = "historical_specialist"
        source_label = "历史专科疗法"
    elif source.startswith("原文·证治方"):
        source_status = "original_explicit"
        source_label = "原文证治方"
    elif "" in source and ("医案" in source or "扩展" in source or "经验" in source):
        source_status = "original_case"
        source_label = "医案/临床扩展"
    elif source:
        source_status = "traditional_classic"
        source_label = "传统经典/其他来源"
    else:
        source_status = "system_extension"
        source_label = "系统整理"

    if is_high_risk:
        risk_level = "high"
        risk_label = "高风险·仅专科"
    elif formula.formula_type in {"external", "fumigation", "sitz_bath"}:
        risk_level = "medium"
        risk_label = "需医师审核"
    else:
        risk_level = "low"
        risk_label = "资料参考"

    data = {key: value for key, value in formula.__dict__.items() if key != "_sa_instance_state"}
    data.update({
        "source_status": source_status,
        "source_label": source_label,
        "risk_level": risk_level,
        "risk_label": risk_label,
        "learning_only": is_high_risk,
        "self_execution_allowed": False if is_high_risk else None,
        "learning_topics": [
            "了解该疗法在原著或历史肛肠专科中的治疗目的和适应证背景",
            "比较历史疗法与现代规范治疗在有效性、可控性和并发症方面的差异",
            "识别组织坏死、感染、出血、中毒、过敏及神经血管损伤等风险",
            "掌握需要转诊、检查、无菌条件、急救条件和术后监测的原因",
        ] if is_high_risk else [],
        "modern_boundary": (
            "仅供医学史和专科决策学习。配制浓度、注射点位、进针方法、腐蚀性制剂制作及具体操作步骤不作为患者自学或居家实践内容。"
            if is_high_risk else None
        ),
        "clinical_governance": [
            "仅限具备相应资质和培训记录的肛肠专科人员，在院内批准的操作协议下执行",
            "执行前完成诊断确认、适应证/禁忌证核对、知情同意和必要检查",
            "必须具备无菌条件、止血与过敏反应处置能力及术后观察安排",
            "记录操作者、批号、核对结果、患者反应、术后医嘱和复诊结果",
        ] if is_high_risk else [],
    })
    if is_high_risk:
        data["composition"] = "高风险操作参数已隐藏；仅用于历史资料识别和院内审批，不作为患者自行配制依据"
        data["preparation"] = "高风险制备/配制参数不在患者端和通用知识库接口展示"
        data["usage"] = "仅限院内正式协议、资质人员和具备应急条件的专科执行；不提供患者自行操作步骤"
        data["frequency"] = None
        data["duration"] = None
        data["modifications"] = None
    return data


def _require_clinician(current_user: User) -> User:
    """院内学习资料只允许管理员或医生角色访问。"""
    if current_user.role not in {"admin", "doctor"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅医生或管理员可访问院内学习资料")
    return current_user


# Herbs
@router.get("/herbs")
async def list_herbs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    category: Optional[str] = None,
    common_only: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(AnorectalHerb).where(
        or_(
            AnorectalHerb.tenant_id == current_user.tenant_id,
            AnorectalHerb.tenant_id.is_(None),
        )
    )

    if search:
        query = query.where(
            or_(
                AnorectalHerb.name.ilike(f"%{search}%"),
                AnorectalHerb.pinyin.ilike(f"%{search}%"),
                AnorectalHerb.effects.ilike(f"%{search}%"),
            )
        )
    if category:
        query = query.where(AnorectalHerb.category == category)
    if common_only:
        query = query.where(AnorectalHerb.is_common == True)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(AnorectalHerb.name)
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    herbs = result.scalars().all()

    return {"total": total, "items": herbs}


@router.get("/herbs/{herb_id}")
async def get_herb(
    herb_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AnorectalHerb).where(AnorectalHerb.id == herb_id))
    herb = result.scalar_one_or_none()
    if not herb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="药材不存在")
    return herb


# Formulas
@router.get("/formulas")
async def list_formulas(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    syndrome_type: Optional[str] = None,
    disease_type: Optional[str] = None,
    formula_type: Optional[str] = None,
    source_status: Optional[str] = None,
    risk_level: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(AnorectalFormula).where(
        or_(
            AnorectalFormula.tenant_id == current_user.tenant_id,
            AnorectalFormula.tenant_id.is_(None),
        )
    )

    if search:
        query = query.where(
            or_(
                AnorectalFormula.name.ilike(f"%{search}%"),
                AnorectalFormula.indications.ilike(f"%{search}%"),
            )
        )
    if syndrome_type:
        query = query.where(AnorectalFormula.syndrome_type.ilike(f"%{syndrome_type}%"))
    if formula_type:
        query = query.where(AnorectalFormula.formula_type == formula_type)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(AnorectalFormula.name)
    if source_status or risk_level:
        # 出处/风险是由来源文字推导的标签，先取候选集再筛选和分页，避免只筛当前数据库页。
        result = await db.execute(query)
        candidates = result.scalars().all()
        formulas = [
            formula for formula in candidates
            if (not source_status or _formula_metadata(formula)["source_status"] == source_status)
            and (not risk_level or _formula_metadata(formula)["risk_level"] == risk_level)
        ]
        total = len(formulas)
        formulas = formulas[(page - 1) * page_size: page * page_size]
    else:
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        formulas = result.scalars().all()

    return {"total": total, "items": [_formula_metadata(formula) for formula in formulas]}


@router.get("/formulas/{formula_id}")
async def get_formula(
    formula_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AnorectalFormula).where(AnorectalFormula.id == formula_id)
    )
    formula = result.scalar_one_or_none()
    if not formula:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="方剂不存在")
    return _formula_metadata(formula)


@router.get("/formulas/{formula_id}/clinical-learning")
async def get_formula_clinical_learning(
    formula_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """返回医生学习用的历史/专科资料摘要，不提供可直接执行的操作步骤。"""
    _require_clinician(current_user)
    result = await db.execute(
        select(AnorectalFormula).where(
            AnorectalFormula.id == formula_id,
            or_(AnorectalFormula.tenant_id == current_user.tenant_id, AnorectalFormula.tenant_id.is_(None)),
        )
    )
    formula = result.scalar_one_or_none()
    if not formula:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="方剂不存在")
    data = _formula_metadata(formula)
    return {
        "id": data["id"],
        "name": data["name"],
        "source": data.get("source"),
        "source_label": data.get("source_label"),
        "risk_level": data.get("risk_level"),
        "risk_label": data.get("risk_label"),
        "learning_only": data.get("learning_only"),
        "function": data.get("function"),
        "indications": data.get("indications"),
        "contraindications": data.get("contraindications"),
        "notes": "历史资料原文保留在院内授权知识库；涉及注射、封闭、枯痔、红粉、腐蚀或有毒制剂的具体参数，必须以本院现行批准协议、药品说明书和专科培训为准。",
        "learning_topics": data.get("learning_topics", []),
        "clinical_governance": data.get("clinical_governance", []),
        "modern_boundary": data.get("modern_boundary"),
        "operational_parameters": "请查阅本院受控的专科操作协议，不通过通用接口下发。",
    }


@router.get("/formulas/recommend/{disease_type}")
async def recommend_formulas(
    disease_type: str,
    syndrome: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Recommend formulas based on disease type and syndrome."""
    query = select(AnorectalFormula).where(
        or_(
            AnorectalFormula.tenant_id == current_user.tenant_id,
            AnorectalFormula.tenant_id.is_(None),
        )
    )

    # Filter by disease type in the JSONB disease_types field
    query = query.where(
        or_(
            AnorectalFormula.indications.ilike(f"%{disease_type}%"),
            AnorectalFormula.name.ilike(f"%{disease_type}%"),
        )
    )

    if syndrome:
        query = query.where(AnorectalFormula.syndrome_type.ilike(f"%{syndrome}%"))

    result = await db.execute(query.limit(10))
    formulas = result.scalars().all()

    return {"disease_type": disease_type, "syndrome": syndrome, "recommendations": formulas}


# Cases
@router.get("/cases")
async def list_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    disease_type: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(AnorectalCase).where(
        or_(
            AnorectalCase.tenant_id == current_user.tenant_id,
            AnorectalCase.tenant_id.is_(None),
        )
    )

    if disease_type:
        query = query.where(AnorectalCase.disease_type == disease_type)
    if search:
        query = query.where(
            or_(
                AnorectalCase.title.ilike(f"%{search}%"),
                AnorectalCase.syndrome.ilike(f"%{search}%"),
                AnorectalCase.symptoms.ilike(f"%{search}%"),
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(AnorectalCase.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    cases = result.scalars().all()

    return {"total": total, "items": cases}


@router.get("/cases/{case_id}")
async def get_case(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AnorectalCase).where(AnorectalCase.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="病例不存在")
    return case


# Prevention Guides
@router.get("/prevention")
async def list_prevention_guides(
    disease_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(PreventionGuide).where(
        or_(
            PreventionGuide.tenant_id == current_user.tenant_id,
            PreventionGuide.tenant_id.is_(None),
        )
    )

    if disease_type:
        query = query.where(PreventionGuide.disease_type == disease_type)

    query = query.order_by(PreventionGuide.disease_type)
    result = await db.execute(query)
    guides = result.scalars().all()

    return {"items": guides}


@router.get("/prevention/{guide_id}")
async def get_prevention_guide(
    guide_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PreventionGuide).where(PreventionGuide.id == guide_id)
    )
    guide = result.scalar_one_or_none()
    if not guide:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="预防指南不存在")
    return guide
