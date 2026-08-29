from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from typing import List, Optional
from datetime import datetime, date
import uuid
import os
import json
from pathlib import Path

from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User
from ...models.patient import Patient
from ...models.ulcer_consultation import UlcerConsultation
from ...models.ulcer_image import UlcerImage
from ...models.consultation_request import ConsultationRequest
from ...models.ulcer_knowledge import UlcerKnowledge
from ...services.qwen_vision import qwen_vision_service
from ...services.expert_matching import expert_matching_service
from ...core.config import settings

router = APIRouter()


@router.post("/consultations")
async def create_consultation(
    patient_id: str = Form(...),
    chief_complaint: str = Form(...),
    onset_date: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    location_detail: Optional[str] = Form(None),
    symptoms: Optional[str] = Form(None),  # JSON string
    appearance: Optional[str] = Form(None),  # JSON string
    tongue_coating: Optional[str] = Form(None),
    tongue_body: Optional[str] = Form(None),
    pulse: Optional[str] = Form(None),
    inquiry_data: Optional[str] = Form(None),  # JSON string
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建疮疡会诊记录"""

    # 验证患者存在
    patient_result = await db.execute(
        select(Patient).where(Patient.id == patient_id)
    )
    patient = patient_result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # 解析JSON字段
    symptoms_dict = json.loads(symptoms) if symptoms else None
    appearance_dict = json.loads(appearance) if appearance else None
    inquiry_dict = json.loads(inquiry_data) if inquiry_data else None

    # 计算病程天数
    duration_days = None
    if onset_date:
        onset = datetime.strptime(onset_date, "%Y-%m-%d").date()
        duration_days = (date.today() - onset).days

    # 创建会诊记录
    consultation = UlcerConsultation(
        patient_id=patient_id,
        doctor_id=current_user.id,
        chief_complaint=chief_complaint,
        onset_date=datetime.strptime(onset_date, "%Y-%m-%d").date() if onset_date else None,
        duration_days=duration_days,
        location=location,
        location_detail=location_detail,
        symptoms=symptoms_dict,
        appearance=appearance_dict,
        tongue_coating=tongue_coating,
        tongue_body=tongue_body,
        pulse=pulse,
        inquiry_data=inquiry_dict,
        status="draft",
        urgency_level="medium"
    )

    db.add(consultation)
    await db.commit()
    await db.refresh(consultation)

    return {
        "id": consultation.id,
        "patient_id": consultation.patient_id,
        "status": consultation.status,
        "created_at": consultation.created_at
    }


@router.post("/consultations/{consultation_id}/images")
async def upload_consultation_image(
    consultation_id: str,
    image: UploadFile = File(...),
    image_type: str = Form("initial"),  # initial/followup/closeup
    view_angle: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传疮疡图片"""

    # 验证会诊记录
    consultation_result = await db.execute(
        select(UlcerConsultation).where(
            and_(
                UlcerConsultation.id == consultation_id,
                UlcerConsultation.doctor_id == current_user.id
            )
        )
    )
    consultation = consultation_result.scalar_one_or_none()
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    # 保存图片
    upload_dir = Path(settings.UPLOAD_DIR) / "ulcer_images" / consultation_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_ext = os.path.splitext(image.filename)[1]
    file_name = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / file_name

    with open(file_path, "wb") as f:
        content = await image.read()
        f.write(content)

    # 图片URL
    image_url = f"/uploads/ulcer_images/{consultation_id}/{file_name}"

    # 创建图片记录
    ulcer_image = UlcerImage(
        consultation_id=consultation_id,
        image_url=image_url,
        image_type=image_type,
        view_angle=view_angle,
        capture_date=datetime.utcnow()
    )

    db.add(ulcer_image)
    await db.commit()
    await db.refresh(ulcer_image)

    return {
        "id": ulcer_image.id,
        "image_url": image_url,
        "image_type": image_type,
        "capture_date": ulcer_image.capture_date
    }


@router.post("/consultations/{consultation_id}/analyze")
async def analyze_consultation(
    consultation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI分析疮疡会诊（调用千问视觉）"""

    # 获取会诊记录和图片
    consultation_result = await db.execute(
        select(UlcerConsultation).where(
            and_(
                UlcerConsultation.id == consultation_id,
                UlcerConsultation.doctor_id == current_user.id
            )
        )
    )
    consultation = consultation_result.scalar_one_or_none()
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    # 获取图片
    images_result = await db.execute(
        select(UlcerImage).where(
            and_(
                UlcerImage.consultation_id == consultation_id,
                UlcerImage.image_type == "initial"
            )
        ).order_by(UlcerImage.capture_date.desc())
    )
    images = images_result.scalars().all()

    if not images:
        raise HTTPException(status_code=400, detail="No images found for analysis")

    # 使用第一张图片进行分析
    primary_image = images[0]
    image_path = str(Path(settings.UPLOAD_DIR).parent / primary_image.image_url.lstrip('/'))

    # 准备患者信息
    patient_result = await db.execute(
        select(Patient).where(Patient.id == consultation.patient_id)
    )
    patient = patient_result.scalar_one()

    patient_info = {
        "gender": patient.gender,
        "age": patient.age
    }

    # 调用千问视觉API分析
    consultation.status = "ai_analyzing"
    await db.commit()

    try:
        ai_result = await qwen_vision_service.analyze_ulcer_image(
            image_url=image_path,
            patient_info=patient_info,
            symptoms=consultation.symptoms
        )

        # 更新会诊记录
        consultation.ai_analysis = ai_result
        consultation.ulcer_type = ai_result.get("ulcer_type")
        consultation.location = ai_result.get("location") or consultation.location
        consultation.urgency_level = ai_result.get("severity_level", "medium").lower()

        # 如果AI建议需要专家，更新状态
        if ai_result.get("needs_expert"):
            consultation.status = "pending_expert"
        else:
            consultation.status = "ai_done"

        # 更新图片的AI分析结果
        primary_image.ai_analysis = ai_result.get("morphology")

        await db.commit()
        await db.refresh(consultation)

        # 如果需要专家，自动匹配专家
        matched_experts = []
        if ai_result.get("needs_expert"):
            matched_experts = await expert_matching_service.match_experts(
                db=db,
                ulcer_type=consultation.ulcer_type or "unknown",
                location=consultation.location or "unknown",
                urgency_level=consultation.urgency_level
            )

        return {
            "consultation_id": consultation.id,
            "ai_analysis": ai_result,
            "status": consultation.status,
            "ulcer_type": consultation.ulcer_type,
            "needs_expert": ai_result.get("needs_expert"),
            "recommended_experts": matched_experts[:3] if matched_experts else []
        }

    except Exception as e:
        consultation.status = "draft"
        await db.commit()
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@router.get("/consultations")
async def list_consultations(
    status: Optional[str] = None,
    patient_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取会诊列表"""

    query = select(UlcerConsultation).where(
        UlcerConsultation.doctor_id == current_user.id
    )

    if status:
        query = query.where(UlcerConsultation.status == status)

    if patient_id:
        query = query.where(UlcerConsultation.patient_id == patient_id)

    query = query.order_by(desc(UlcerConsultation.created_at)).offset(skip).limit(limit)

    result = await db.execute(query)
    consultations = result.scalars().all()

    return [
        {
            "id": c.id,
            "patient_id": c.patient_id,
            "ulcer_type": c.ulcer_type,
            "location": c.location,
            "status": c.status,
            "urgency_level": c.urgency_level,
            "created_at": c.created_at,
            "chief_complaint": c.chief_complaint[:50] + "..." if c.chief_complaint and len(c.chief_complaint) > 50 else c.chief_complaint
        }
        for c in consultations
    ]


@router.get("/consultations/{consultation_id}")
async def get_consultation_detail(
    consultation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取会诊详情"""

    # 获取会诊记录
    consultation_result = await db.execute(
        select(UlcerConsultation).where(UlcerConsultation.id == consultation_id)
    )
    consultation = consultation_result.scalar_one_or_none()
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    # 获取患者信息
    patient_result = await db.execute(
        select(Patient).where(Patient.id == consultation.patient_id)
    )
    patient = patient_result.scalar_one()

    # 获取图片
    images_result = await db.execute(
        select(UlcerImage).where(
            UlcerImage.consultation_id == consultation_id
        ).order_by(UlcerImage.capture_date)
    )
    images = images_result.scalars().all()

    # 获取会诊请求（如果有）
    request_result = await db.execute(
        select(ConsultationRequest).where(
            ConsultationRequest.consultation_id == consultation_id
        )
    )
    consultation_request = request_result.scalar_one_or_none()

    return {
        "id": consultation.id,
        "patient": {
            "id": patient.id,
            "name": patient.name,
            "gender": patient.gender,
            "age": patient.age
        },
        "chief_complaint": consultation.chief_complaint,
        "onset_date": consultation.onset_date,
        "duration_days": consultation.duration_days,
        "location": consultation.location,
        "location_detail": consultation.location_detail,
        "ulcer_type": consultation.ulcer_type,
        "symptoms": consultation.symptoms,
        "appearance": consultation.appearance,
        "tongue_coating": consultation.tongue_coating,
        "tongue_body": consultation.tongue_body,
        "pulse": consultation.pulse,
        "inquiry_data": consultation.inquiry_data,
        "ai_analysis": consultation.ai_analysis,
        "doctor_diagnosis": consultation.doctor_diagnosis,
        "syndrome_differentiation": consultation.syndrome_differentiation,
        "internal_treatment": consultation.internal_treatment,
        "external_treatment": consultation.external_treatment,
        "status": consultation.status,
        "urgency_level": consultation.urgency_level,
        "images": [
            {
                "id": img.id,
                "image_url": img.image_url,
                "image_type": img.image_type,
                "view_angle": img.view_angle,
                "capture_date": img.capture_date,
                "ai_analysis": img.ai_analysis
            }
            for img in images
        ],
        "consultation_request": {
            "id": consultation_request.id,
            "status": consultation_request.status,
            "expert_id": consultation_request.expert_id,
            "requested_at": consultation_request.requested_at
        } if consultation_request else None,
        "created_at": consultation.created_at,
        "updated_at": consultation.updated_at
    }


@router.post("/consultations/{consultation_id}/request-expert")
async def request_expert_consultation(
    consultation_id: str,
    expert_id: Optional[str] = None,
    request_reason: Optional[str] = None,
    specific_questions: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """发起专家会诊请求"""

    # 验证会诊记录
    consultation_result = await db.execute(
        select(UlcerConsultation).where(
            and_(
                UlcerConsultation.id == consultation_id,
                UlcerConsultation.doctor_id == current_user.id
            )
        )
    )
    consultation = consultation_result.scalar_one_or_none()
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")

    # 检查是否已有会诊请求
    existing_request = await db.execute(
        select(ConsultationRequest).where(
            ConsultationRequest.consultation_id == consultation_id
        )
    )
    if existing_request.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Consultation request already exists")

    # 如果没有指定专家，自动匹配
    ai_suggestion = None
    if not expert_id:
        matched_experts = await expert_matching_service.match_experts(
            db=db,
            ulcer_type=consultation.ulcer_type or "unknown",
            location=consultation.location or "unknown",
            urgency_level=consultation.urgency_level
        )
        if matched_experts:
            expert_id = matched_experts[0]["expert_id"]
            ai_suggestion = matched_experts[0]["match_reason"]

    # 创建会诊请求
    consultation_request = ConsultationRequest(
        consultation_id=consultation_id,
        requesting_doctor_id=current_user.id,
        expert_id=expert_id,
        request_reason=request_reason,
        specific_questions=specific_questions,
        ai_suggestion=ai_suggestion,
        status="pending" if expert_id else "pending",
        priority=3 if consultation.urgency_level == "medium" else (4 if consultation.urgency_level == "high" else 2)
    )

    db.add(consultation_request)

    # 更新会诊状态
    consultation.status = "pending_expert"

    await db.commit()
    await db.refresh(consultation_request)

    return {
        "request_id": consultation_request.id,
        "consultation_id": consultation_id,
        "expert_id": expert_id,
        "status": consultation_request.status,
        "ai_suggestion": ai_suggestion
    }


@router.get("/knowledge/ulcers")
async def list_ulcer_knowledge(
    category: Optional[str] = None,
    location: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """查询疮疡知识库"""

    query = select(UlcerKnowledge)

    if category:
        query = query.where(UlcerKnowledge.category == category)

    if location:
        query = query.where(UlcerKnowledge.location == location)

    if search:
        query = query.where(
            UlcerKnowledge.chinese_name.contains(search)
        )

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    knowledge_items = result.scalars().all()

    return [
        {
            "id": item.id,
            "ulcer_type": item.ulcer_type,
            "chinese_name": item.chinese_name,
            "category": item.category,
            "location": item.location,
            "morphology": item.morphology,
            "treatment_principle": item.treatment_principle,
            "page_number": item.page_number
        }
        for item in knowledge_items
    ]


@router.get("/knowledge/ulcers/{ulcer_type}")
async def get_ulcer_knowledge_detail(
    ulcer_type: str,
    db: AsyncSession = Depends(get_db)
):
    """获取疮疡知识详情"""

    result = await db.execute(
        select(UlcerKnowledge).where(UlcerKnowledge.ulcer_type == ulcer_type)
    )
    knowledge = result.scalar_one_or_none()

    if not knowledge:
        raise HTTPException(status_code=404, detail="Knowledge not found")

    return {
        "id": knowledge.id,
        "ulcer_type": knowledge.ulcer_type,
        "chinese_name": knowledge.chinese_name,
        "english_name": knowledge.english_name,
        "aliases": knowledge.aliases,
        "category": knowledge.category,
        "location": knowledge.location,
        "location_detail": knowledge.location_detail,
        "etiology": knowledge.etiology,
        "pathogenesis": knowledge.pathogenesis,
        "morphology": knowledge.morphology,
        "clinical_features": knowledge.clinical_features,
        "systemic_symptoms": knowledge.systemic_symptoms,
        "syndrome_types": knowledge.syndrome_types,
        "treatment_principle": knowledge.treatment_principle,
        "internal_treatment": knowledge.internal_treatment,
        "external_treatment": knowledge.external_treatment,
        "prevention": knowledge.prevention,
        "nursing": knowledge.nursing,
        "diet_advice": knowledge.diet_advice,
        "prognosis": knowledge.prognosis,
        "complications": knowledge.complications,
        "differential_diagnosis": knowledge.differential_diagnosis,
        "reference_images": knowledge.reference_images,
        "case_count": knowledge.case_count,
        "cure_rate": knowledge.cure_rate
    }
