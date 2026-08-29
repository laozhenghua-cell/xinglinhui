import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.consultation import Consultation, Prescription
from app.models.patient import Patient
from app.models.user import User
from app.services.deepseek_service import diagnose_syndrome

router = APIRouter(prefix="/consultations", tags=["诊疗记录"])


class ConsultationCreate(BaseModel):
    patient_id: uuid.UUID
    disease_type: Optional[str] = None
    chief_complaint: Optional[str] = None
    symptoms: Optional[dict] = {}
    tongue: Optional[str] = None
    pulse: Optional[str] = None
    physical_exam: Optional[dict] = {}
    inspection: Optional[str] = None
    inquiry: Optional[str] = None
    images: Optional[list] = []
    syndrome: Optional[str] = None
    treatment_principle: Optional[str] = None
    syndrome_result: Optional[dict] = None
    prescription_text: Optional[str] = None
    treatment: Optional[str] = None


class ConsultationUpdate(BaseModel):
    disease_type: Optional[str] = None
    chief_complaint: Optional[str] = None
    symptoms: Optional[dict] = None
    tongue: Optional[str] = None
    pulse: Optional[str] = None
    diagnosis: Optional[str] = None
    syndrome: Optional[str] = None
    treatment_principle: Optional[str] = None
    treatment: Optional[str] = None
    prescription_text: Optional[str] = None
    symptom_score: Optional[int] = None
    status: Optional[str] = None
    physical_exam: Optional[dict] = None
    inspection: Optional[str] = None
    inquiry: Optional[str] = None
    images: Optional[list] = None
    syndrome_result: Optional[dict] = None
    formula_modifications: Optional[str] = None


class AIDiagnosisRequest(BaseModel):
    consultation_id: uuid.UUID


class ConsultationResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    patient_id: uuid.UUID
    doctor_id: uuid.UUID
    disease_type: Optional[str] = None
    chief_complaint: Optional[str] = None
    symptoms: Optional[dict] = None
    tongue: Optional[str] = None
    pulse: Optional[str] = None
    diagnosis: Optional[str] = None
    syndrome: Optional[str] = None
    treatment_principle: Optional[str] = None
    treatment: Optional[str] = None
    prescription_text: Optional[str] = None
    symptom_score: Optional[int] = None
    status: str
    ai_analysis: Optional[dict] = None
    physical_exam: Optional[dict] = None
    created_at: str

    class Config:
        from_attributes = True


@router.get("")
async def list_consultations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    patient_id: Optional[uuid.UUID] = None,
    disease_type: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Consultation).where(Consultation.tenant_id == current_user.tenant_id)

    if patient_id:
        query = query.where(Consultation.patient_id == patient_id)
    if disease_type:
        query = query.where(Consultation.disease_type == disease_type)
    if status_filter:
        query = query.where(Consultation.status == status_filter)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(Consultation.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    consultations = result.scalars().all()

    return {"total": total, "items": [c.__dict__ for c in consultations]}


@router.get("/{consultation_id}")
async def get_consultation(
    consultation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Consultation).where(
            Consultation.id == consultation_id,
            Consultation.tenant_id == current_user.tenant_id,
        )
    )
    consultation = result.scalar_one_or_none()
    if not consultation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="诊疗记录不存在")

    # 附带患者姓名/电话，便于前端展示
    data = {k: v for k, v in consultation.__dict__.items() if not k.startswith("_")}
    if consultation.patient_id:
        p_res = await db.execute(select(Patient).where(Patient.id == consultation.patient_id))
        patient = p_res.scalar_one_or_none()
        if patient:
            data["patient_name"] = patient.name
            data["patient_phone"] = patient.phone
    return data


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_consultation(
    data: ConsultationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    consultation = Consultation(
        tenant_id=current_user.tenant_id,
        doctor_id=current_user.id,
        patient_id=data.patient_id,
        disease_type=data.disease_type,
        chief_complaint=data.chief_complaint,
        symptoms=data.symptoms or {},
        tongue=data.tongue,
        pulse=data.pulse,
        physical_exam=data.physical_exam or {},
        four_examinations={"inspection": data.inspection, "inquiry": data.inquiry},
        images=data.images or [],
        syndrome=data.syndrome,
        treatment_principle=data.treatment_principle,
        syndrome_result=data.syndrome_result or {},
        prescription_text=data.prescription_text,
        treatment=data.treatment,
        status="pending",
    )
    db.add(consultation)
    await db.flush()
    await db.refresh(consultation)
    return consultation


@router.put("/{consultation_id}")
async def update_consultation(
    consultation_id: uuid.UUID,
    data: ConsultationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Consultation).where(
            Consultation.id == consultation_id,
            Consultation.tenant_id == current_user.tenant_id,
        )
    )
    consultation = result.scalar_one_or_none()
    if not consultation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="诊疗记录不存在")

    update_data = data.model_dump(exclude_none=True)
    if "inspection" in update_data or "inquiry" in update_data:
        exams = dict(consultation.four_examinations or {})
        for key in ("inspection", "inquiry"):
            if key in update_data:
                exams[key] = update_data.pop(key)
        consultation.four_examinations = exams
    for key, value in update_data.items():
        setattr(consultation, key, value)

    db.add(consultation)
    await db.flush()
    await db.refresh(consultation)
    return consultation


@router.post("/{consultation_id}/ai-diagnosis")
async def trigger_ai_diagnosis(
    consultation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger AI-based syndrome differentiation for a consultation."""
    result = await db.execute(
        select(Consultation).where(
            Consultation.id == consultation_id,
            Consultation.tenant_id == current_user.tenant_id,
        )
    )
    consultation = result.scalar_one_or_none()
    if not consultation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="诊疗记录不存在")

    symptoms_text = consultation.chief_complaint or ""
    if consultation.symptoms:
        if isinstance(consultation.symptoms, dict):
            for key, val in consultation.symptoms.items():
                symptoms_text += f"\n{key}: {val}"

    physical_text = None
    if consultation.physical_exam and isinstance(consultation.physical_exam, dict):
        physical_text = "; ".join(f"{k}: {v}" for k, v in consultation.physical_exam.items())

    ai_result = await diagnose_syndrome(
        symptoms=symptoms_text,
        disease_type=consultation.disease_type,
        tongue=consultation.tongue,
        pulse=consultation.pulse,
        physical_exam=physical_text,
    )

    consultation.ai_analysis = ai_result
    if ai_result.get("diagnosis") and not ai_result.get("error"):
        consultation.diagnosis = ai_result.get("diagnosis")
        consultation.syndrome = ai_result.get("syndrome")
        consultation.treatment_principle = ai_result.get("treatmentPrinciple")
        consultation.status = "in_progress"

        prescription_data = ai_result.get("prescription")
        if prescription_data and isinstance(prescription_data, dict):
            prescription = Prescription(
                tenant_id=current_user.tenant_id,
                consultation_id=consultation.id,
                patient_id=consultation.patient_id,
                doctor_id=current_user.id,
                formula_name=prescription_data.get("name"),
                medicines=prescription_data.get("composition", []),
                dosage_instructions=prescription_data.get("usage"),
                notes=prescription_data.get("modifications"),
            )
            db.add(prescription)

    db.add(consultation)
    await db.flush()
    await db.refresh(consultation)

    return {"consultation": consultation, "ai_analysis": ai_result}


@router.post("/{consultation_id}/diagnose")
async def trigger_rule_based_diagnosis(
    consultation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    触发基于规则的辨证（不使用AI）

    根据临床经验的规则库进行辨证
    """
    from app.services.syndrome_engine import SyndromeEngine
    from app.services.treatment_plan import build_treatment_plan
    from app.services.external_treatment_recommender import recommend_external_treatments

    # 获取就诊记录
    result = await db.execute(
        select(Consultation).where(
            Consultation.id == consultation_id,
            Consultation.tenant_id == current_user.tenant_id,
        )
    )
    consultation = result.scalar_one_or_none()
    if not consultation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="诊疗记录不存在")

    # 检查必需字段
    if not consultation.disease_type:
        raise HTTPException(status_code=400, detail="请先选择病种")
    if not consultation.symptoms:
        raise HTTPException(status_code=400, detail="请先选择症状")

    # 调用规则辨证引擎
    engine = SyndromeEngine(db)
    syndromes = await engine.analyze(
        disease_type=consultation.disease_type,
        selected_symptoms=consultation.symptoms
    )

    if not syndromes:
        raise HTTPException(
            status_code=404,
            detail="未找到匹配的证型，请检查症状选择是否完整"
        )

    # 主证型
    primary_syndrome = syndromes[0]
    primary_syndrome["treatment_plan"] = build_treatment_plan(
        consultation.disease_type, primary_syndrome, consultation.symptoms
    )

    # 查询外治法
    syndrome_name = primary_syndrome.get("syndrome_name", "")
    external_treatments = await recommend_external_treatments(
        db, consultation.disease_type, syndrome_name
    )

    if external_treatments:
        primary_syndrome["external_treatments"] = [
            {
                "id": str(t.id),
                "name": t.name,
                "treatment_type": t.treatment_type,
                "treatment_type_name": {
                    "fumigation": "熏洗方", "ointment": "外敷药膏",
                    "suppository": "栓剂",
                }.get(t.treatment_type, t.treatment_type),
                "composition": t.composition,
                "preparation": t.preparation,
                "usage": t.usage,
                "frequency": t.frequency,
                "duration": t.duration,
                "function": t.function,
                "indications": t.indications,
                "contraindications": t.contraindications,
                "precautions": t.precautions,
                "source": t.source,
                "priority": t.priority,
                "notes": t.notes
            }
            for t in external_treatments
        ]

    if primary_syndrome.get("insufficient_data"):
        primary_syndrome["external_treatments"] = []

    # 更新就诊记录
    consultation.syndrome = primary_syndrome.get("syndrome_name")
    consultation.treatment_principle = primary_syndrome.get("treatment_principle")
    consultation.syndrome_result = {
        "syndromes": syndromes,
        "primary_syndrome": primary_syndrome,
    }
    consultation.selected_symptoms = consultation.symptoms
    consultation.status = "in_progress"

    # 构建处方文本（从第一个推荐方剂）
    formulas = primary_syndrome.get("recommended_formulas", [])
    if formulas:
        first_formula = formulas[0]
        prescription_text = f"{first_formula.get('name')}\n"

        # 组成
        composition = first_formula.get("composition", [])
        if composition:
            prescription_text += "\n【组成】\n"
            for herb in composition:
                note = f"（{herb.get('note')}）" if herb.get('note') else ""
                prescription_text += f"  {herb.get('name')} {herb.get('dosage')}{herb.get('unit')}{note}\n"

        # 用法
        if first_formula.get("usage"):
            prescription_text += f"\n【用法】{first_formula.get('usage')}\n"

        # 加减
        if first_formula.get("modifications"):
            prescription_text += f"\n【加减】{first_formula.get('modifications')}\n"

        consultation.prescription_text = prescription_text

    db.add(consultation)
    await db.commit()
    await db.refresh(consultation)

    # 返回完整辨证结果
    return {
        "syndromes": syndromes,
        "primary_syndrome": primary_syndrome,
        "consultation": consultation
    }


@router.delete("/{consultation_id}")
async def delete_consultation(
    consultation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Consultation).where(
            Consultation.id == consultation_id,
            Consultation.tenant_id == current_user.tenant_id,
        )
    )
    consultation = result.scalar_one_or_none()
    if not consultation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="诊疗记录不存在")

    await db.delete(consultation)
    await db.flush()
    return {"message": "诊疗记录已删除"}
