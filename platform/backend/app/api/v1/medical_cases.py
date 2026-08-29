"""
医案库API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, cast, String
from typing import List, Optional
from app.database import get_db
from app.models.medical_case import MedicalCase
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/medical-cases", tags=["医案库"])


@router.get("/", summary="医案列表")
async def get_medical_cases(
    disease_type: Optional[str] = Query(None, description="病种筛选"),
    syndrome_type: Optional[str] = Query(None, description="证型筛选"),
    is_classic: Optional[bool] = Query(None, description="仅经典案例"),
    difficulty_level: Optional[int] = Query(None, description="难度等级：1-3"),
    tags: Optional[str] = Query(None, description="标签筛选，逗号分隔"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取医案列表

    支持多维度筛选：
    - 病种（痔疮/直肠脱垂/肛裂/肛周脓肿/肛瘘）
    - 证型（湿热瘀滞型/气血两虚型等）
    - 是否经典案例
    - 难度等级（1简单/2中等/3困难）
    - 标签
    """
    # 构建查询
    query = select(MedicalCase).where(MedicalCase.tenant_id == None)  # 公共医案

    # 应用筛选条件
    if disease_type:
        query = query.where(MedicalCase.disease_type == disease_type)

    if syndrome_type:
        query = query.where(MedicalCase.syndrome_type == syndrome_type)

    if is_classic is not None:
        query = query.where(MedicalCase.is_classic == is_classic)

    if difficulty_level:
        query = query.where(MedicalCase.difficulty_level == difficulty_level)

    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        # JSONB数组包含任一标签
        for tag in tag_list:
            query = query.where(
                func.jsonb_exists(MedicalCase.tags, tag)
            )

    # 按日期降序排序
    query = query.order_by(MedicalCase.case_date.desc())

    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    cases = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "items": [case.to_summary() for case in cases]
    }


@router.get("/classic", summary="经典案例列表")
async def get_classic_cases(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取所有经典案例（is_classic=true）
    按难度升序排列
    """
    query = select(MedicalCase).where(
        and_(
            MedicalCase.is_classic == True,
            MedicalCase.tenant_id == None
        )
    ).order_by(MedicalCase.difficulty_level.asc())

    result = await db.execute(query)
    cases = result.scalars().all()

    return {
        "total": len(cases),
        "items": [case.to_summary() for case in cases]
    }


@router.get("/disease/{disease}", summary="按病种查询医案")
async def get_cases_by_disease(
    disease: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    按病种查询医案

    disease: 痔疮/直肠脱垂/肛裂/肛周脓肿/肛瘘
    """
    query = select(MedicalCase).where(
        and_(
            MedicalCase.disease_type == disease,
            MedicalCase.tenant_id == None
        )
    ).order_by(MedicalCase.case_date.desc())

    result = await db.execute(query)
    cases = result.scalars().all()

    if not cases:
        raise HTTPException(status_code=404, detail=f"未找到病种为 {disease} 的医案")

    return {
        "disease_type": disease,
        "total": len(cases),
        "items": [case.to_summary() for case in cases]
    }


@router.get("/syndrome/{syndrome}", summary="按证型查询医案")
async def get_cases_by_syndrome(
    syndrome: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    按证型查询医案

    syndrome: 湿热瘀滞型/气血两虚型/虚热内蕴等
    """
    query = select(MedicalCase).where(
        and_(
            MedicalCase.syndrome_type == syndrome,
            MedicalCase.tenant_id == None
        )
    ).order_by(MedicalCase.case_date.desc())

    result = await db.execute(query)
    cases = result.scalars().all()

    if not cases:
        raise HTTPException(status_code=404, detail=f"未找到证型为 {syndrome} 的医案")

    return {
        "syndrome_type": syndrome,
        "total": len(cases),
        "items": [case.to_summary() for case in cases]
    }


@router.get("/{case_id}", summary="医案详情")
async def get_medical_case_detail(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取医案完整详情

    包含：
    - 基本信息
    - 四诊数据
    - 辨证分析
    - 完整治疗方案
    - 疗效追踪
    - 教学要点
    """
    result = await db.execute(
        select(MedicalCase).where(MedicalCase.id == case_id)
    )
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail="医案不存在")

    # 增加浏览次数
    case.view_count += 1
    data = case.to_dict()  # 在 commit 前序列化，避免异步会话对象过期后触发同步加载
    await db.commit()

    return data


@router.get("/stats/overview", summary="医案库统计")
async def get_medical_cases_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    医案库统计数据

    返回：
    - 总案例数
    - 按病种分布
    - 按证型分布
    - 按疗效分布
    - 经典案例数
    """
    # 总案例数
    total_result = await db.execute(
        select(func.count()).select_from(MedicalCase).where(MedicalCase.tenant_id == None)
    )
    total = total_result.scalar()

    # 按病种分布
    disease_result = await db.execute(
        select(
            MedicalCase.disease_type,
            func.count(MedicalCase.id).label("count")
        ).where(MedicalCase.tenant_id == None)
        .group_by(MedicalCase.disease_type)
    )
    by_disease = {row[0]: row[1] for row in disease_result.all()}

    # 按证型分布
    syndrome_result = await db.execute(
        select(
            MedicalCase.syndrome_type,
            func.count(MedicalCase.id).label("count")
        ).where(MedicalCase.tenant_id == None)
        .group_by(MedicalCase.syndrome_type)
    )
    by_syndrome = {row[0]: row[1] for row in syndrome_result.all()}

    # 按疗效分布
    outcome_result = await db.execute(
        select(
            MedicalCase.outcome,
            func.count(MedicalCase.id).label("count")
        ).where(MedicalCase.tenant_id == None)
        .group_by(MedicalCase.outcome)
    )
    by_outcome = {row[0]: row[1] for row in outcome_result.all()}

    # 经典案例数
    classic_result = await db.execute(
        select(func.count()).select_from(MedicalCase).where(
            and_(
                MedicalCase.is_classic == True,
                MedicalCase.tenant_id == None
            )
        )
    )
    classic_count = classic_result.scalar()

    return {
        "total": total,
        "classic_count": classic_count,
        "by_disease": by_disease,
        "by_syndrome": by_syndrome,
        "by_outcome": by_outcome
    }


@router.post("/similar", summary="相似案例推荐")
async def find_similar_cases(
    payload: dict,
    limit: int = Query(5, ge=1, le=10, description="返回数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    基于症状相似度推荐医案

    请求体：
    {
      "disease_type": "痔疮",
      "symptoms": {
        "pain": {"present": true, "degree": "剧烈"},
        "bleeding": {"present": true, "color": "鲜红"},
        ...
      }
    }

    返回相似度最高的案例列表
    """
    disease_type = payload.get("disease_type")
    symptoms = payload.get("symptoms", {})

    if not disease_type:
        raise HTTPException(status_code=400, detail="disease_type 不能为空")

    # 基础查询：同病种
    query = select(MedicalCase).where(
        and_(
            MedicalCase.disease_type == disease_type,
            MedicalCase.tenant_id == None
        )
    )

    result = await db.execute(query)
    cases = result.scalars().all()

    if not cases:
        return {"total": 0, "items": []}

    # 计算相似度
    scored_cases = []
    for case in cases:
        score = _calculate_similarity(symptoms, case.inquiry, case.inspection, case.palpation)
        scored_cases.append((case, score))

    # 按相似度降序排序
    scored_cases.sort(key=lambda x: x[1], reverse=True)

    # 返回Top N
    top_cases = scored_cases[:limit]

    return {
        "total": len(top_cases),
        "items": [
            {
                **case.to_summary(),
                "similarity_score": round(score, 2)
            }
            for case, score in top_cases
        ]
    }


def _calculate_similarity(symptoms: dict, inquiry: dict, inspection: dict, palpation: dict) -> float:
    """
    计算症状相似度

    权重分配：
    - 主诉症状（inquiry）：40%
    - 局部表现（inspection）：30%
    - 舌脉（palpation）：30%
    """
    score = 0.0
    max_score = 0.0

    # 1. 问诊症状匹配（40%权重）
    inquiry_weight = 0.4
    for key, value in symptoms.items():
        max_score += inquiry_weight
        if key in inquiry:
            if isinstance(value, dict) and isinstance(inquiry[key], dict):
                # 复杂症状比较
                if value.get("present") == inquiry[key].get("present"):
                    score += inquiry_weight * 0.5
                    # 细节匹配
                    if value.get("color") == inquiry[key].get("color"):
                        score += inquiry_weight * 0.3
                    if value.get("degree") == inquiry[key].get("degree"):
                        score += inquiry_weight * 0.2
            elif value == inquiry[key]:
                score += inquiry_weight

    # 2. 望诊匹配（30%权重）
    inspection_weight = 0.3
    if "tongue" in symptoms and "tongue" in inspection:
        max_score += inspection_weight
        if symptoms["tongue"] in str(inspection.get("tongue", "")):
            score += inspection_weight

    # 3. 切诊匹配（30%权重）
    palpation_weight = 0.3
    if "pulse" in symptoms and "pulse" in palpation:
        max_score += palpation_weight
        if symptoms["pulse"] in str(palpation.get("pulse", "")):
            score += palpation_weight

    # 归一化到0-100
    return (score / max_score * 100) if max_score > 0 else 0
