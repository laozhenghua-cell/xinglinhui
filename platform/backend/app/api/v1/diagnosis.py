"""
辨证诊断API路由
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.user import User
from app.models.patient import Patient
from app.core.security import get_current_user
from app.services.syndrome_engine import SyndromeEngine, get_symptom_dictionary
from app.services.safety_check import SafetyCheckService
from app.services.treatment_plan import build_treatment_plan
from app.services.external_treatment_recommender import recommend_external_treatments
from app.services.prescription_pdf import build_prescription_pdf
from app.api.v1.external_treatment import _treatment_payload
from app.models.diagnosis import DiagnosisRecord, SymptomTemplate, SafetyRule
from app.models.consultation import Followup, Prescription


router = APIRouter()


class SyndromeAnalysisRequest(BaseModel):
    """辨证分析请求"""
    disease_type: str
    selected_symptoms: Dict[str, Any]


class SyndromeAnalysisResponse(BaseModel):
    """辨证分析响应"""
    syndromes: List[Dict[str, Any]]
    primary_syndrome: Dict[str, Any] | None


class SymptomDictionaryResponse(BaseModel):
    """症状字典响应"""
    id: UUID
    category: str
    subcategory: str | None
    name: str
    display_name: str | None
    options: Dict[str, Any] | None
    weight: int
    description: str | None


@router.get("/symptoms", response_model=List[SymptomDictionaryResponse])
async def list_symptoms(
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取症状字典

    Query Parameters:
        - category: 症状类别（望诊/闻诊/问诊/切诊）
    """
    symptoms = await get_symptom_dictionary(db, category)
    return symptoms


@router.post("/analyze", response_model=SyndromeAnalysisResponse)
async def analyze_syndrome(
    request: SyndromeAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    辨证分析

    根据用户选择的症状，智能匹配证型并给出治疗建议

    Request Body:
        - disease_type: 病种（痔疮/肛裂/肛周脓肿/直肠脱垂）
        - selected_symptoms: 症状数据结构
          ```json
          {
            "bleeding": {"present": true, "color": "鲜红", "volume": "中量"},
            "pain": {"present": true, "degree": "中度", "nature": "胀痛"},
            "stool_condition": "干结",
            "tongue_color": "红",
            "tongue_coating": "黄",
            "pulse_rapid": true,
            "pulse_wiry": true,
            ...
          }
          ```

    Response:
        - syndromes: 所有匹配的证型列表（按置信度排序）
        - primary_syndrome: 主证型（置信度最高）
    """
    engine = SyndromeEngine(db)

    # 执行辨证分析
    syndromes = await engine.analyze(
        disease_type=request.disease_type,
        selected_symptoms=request.selected_symptoms
    )

    if not syndromes:
        raise HTTPException(
            status_code=404,
            detail="未找到匹配的证型，请检查症状选择是否完整"
        )

    # 为主证型推荐外治法
    primary_syndrome = syndromes[0] if syndromes else None
    if primary_syndrome:
        syndrome_name = primary_syndrome.get("syndrome_name", "")
        external_treatments = await recommend_external_treatments(
            db, request.disease_type, syndrome_name
        )

        # 将外治法添加到主证型结果中
        if external_treatments:
            primary_syndrome["external_treatments"] = [_treatment_payload(t) for t in external_treatments]

        if primary_syndrome.get("insufficient_data"):
            primary_syndrome["external_treatments"] = []

        primary_syndrome["treatment_plan"] = build_treatment_plan(
            request.disease_type, primary_syndrome, request.selected_symptoms
        )

    # 返回结果
    return {
        "syndromes": syndromes,
        "primary_syndrome": primary_syndrome
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


@router.get("/syndromes/{disease_type}")
async def get_syndromes_by_disease(
    disease_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取指定病种的所有证型列表

    Path Parameters:
        - disease_type: 病种名称
    """
    from sqlalchemy import select
    from app.models.diagnosis import SyndromeRule

    result = await db.execute(
        select(SyndromeRule)
        .where(SyndromeRule.disease_type == disease_type)
        .where(SyndromeRule.is_active == 1)
        .order_by(SyndromeRule.priority.desc())
    )
    rules = result.scalars().all()

    return [
        {
            "syndrome_name": r.syndrome_name,
            "syndrome_code": r.syndrome_code,
            "treatment_principle": r.treatment_principle,
            "tongue_pulse": r.tongue_pulse,
        }
        for r in rules
    ]


# ==================== Phase 4: 辨证记录与复诊对比 ====================

class SaveDiagnosisRecordRequest(BaseModel):
    """保存辨证记录请求"""
    patient_id: UUID
    consultation_id: Optional[UUID] = None
    disease_type: str
    selected_symptoms: Dict[str, Any]
    syndrome_result: Dict[str, Any]
    selected_formula: Optional[str] = None
    formula_modifications: Optional[str] = None
    doctor_notes: Optional[str] = None


class PrescriptionDraftRequest(BaseModel):
    formula_name: str
    medicines: Any = Field(default_factory=list)  # 结构化组成数组 或 组成文本字符串
    dosage_instructions: Optional[str] = None
    duration_days: int = Field(default=7, ge=1, le=90)
    notes: Optional[str] = None


@router.post("/records")
async def save_diagnosis_record(
    request: SaveDiagnosisRecordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    保存辨证记录（用于复诊对比）

    每次辨证完成后，保存完整记录供后续复诊参考
    """
    import uuid

    # 提取主证型信息
    primary = request.syndrome_result.get("primary_syndrome", {})

    record = DiagnosisRecord(
        id=uuid.uuid4(),
        tenant_id=current_user.tenant_id,
        patient_id=request.patient_id,
        consultation_id=request.consultation_id,
        disease_type=request.disease_type,
        selected_symptoms=request.selected_symptoms,
        syndrome_result=request.syndrome_result,
        primary_syndrome_code=primary.get("syndrome_code"),
        primary_syndrome_name=primary.get("syndrome_name"),
        confidence=primary.get("confidence"),
        selected_formula=request.selected_formula,
        formula_modifications=request.formula_modifications,
        doctor_notes=request.doctor_notes,
        created_by=current_user.id
    )

    db.add(record)
    await db.commit()
    await db.refresh(record)

    return {
        "id": record.id,
        "message": "辨证记录保存成功"
    }


@router.post("/records/{record_id}/prescription", status_code=201)
async def create_prescription_draft(
    record_id: UUID,
    request: PrescriptionDraftRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """从已保存辨证记录生成待审核处方草稿。"""
    result = await db.execute(
        select(DiagnosisRecord).where(
            DiagnosisRecord.id == record_id,
            DiagnosisRecord.tenant_id == current_user.tenant_id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="辨证记录未找到")
    if not request.formula_name.strip():
        raise HTTPException(status_code=422, detail="方剂名称不能为空")

    prescription = Prescription(
        tenant_id=current_user.tenant_id,
        consultation_id=record.consultation_id,
        patient_id=record.patient_id,
        doctor_id=current_user.id,
        formula_name=request.formula_name.strip(),
        medicines=request.medicines,
        dosage_instructions=request.dosage_instructions,
        duration_days=request.duration_days,
        notes=request.notes,
        status="draft",
    )
    db.add(prescription)
    await db.commit()
    await db.refresh(prescription)
    return {"id": prescription.id, "status": prescription.status, "formula_name": prescription.formula_name, "message": "处方草稿已生成，请审核后确认"}


class PrescriptionStatusRequest(BaseModel):
    status: str = Field(pattern="^(reviewed|confirmed|cancelled)$")


@router.put("/prescriptions/{prescription_id}/status")
async def update_prescription_status(
    prescription_id: UUID,
    request: PrescriptionStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Prescription).where(Prescription.id == prescription_id, Prescription.tenant_id == current_user.tenant_id)
    )
    prescription = result.scalar_one_or_none()
    if not prescription:
        raise HTTPException(status_code=404, detail="处方不存在")
    allowed = {"draft": {"reviewed", "cancelled"}, "reviewed": {"confirmed", "cancelled"}, "confirmed": {"cancelled"}, "cancelled": set()}
    if request.status not in allowed.get(prescription.status, set()):
        raise HTTPException(status_code=400, detail=f"处方不能从{prescription.status}变更为{request.status}")
    prescription.status = request.status
    db.add(prescription)
    await db.commit()
    await db.refresh(prescription)
    return {"id": prescription.id, "status": prescription.status, "message": "处方状态已更新"}


@router.get("/prescriptions/{prescription_id}/pdf")
async def get_prescription_pdf(
    prescription_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """生成中医处方笺 PDF（用于打印 / 下载）。"""
    result = await db.execute(
        select(Prescription).where(
            Prescription.id == prescription_id,
            Prescription.tenant_id == current_user.tenant_id,
        )
    )
    prescription = result.scalar_one_or_none()
    if not prescription:
        raise HTTPException(status_code=404, detail="处方不存在")

    # 患者信息
    patient = None
    if prescription.patient_id:
        pres = await db.execute(select(Patient).where(Patient.id == prescription.patient_id))
        patient = pres.scalar_one_or_none()

    # 证型 / 治则：优先从关联辨证记录取
    syndrome_name = ""
    treatment_principle = ""
    if prescription.consultation_id:
        rec_res = await db.execute(
            select(DiagnosisRecord).where(DiagnosisRecord.consultation_id == prescription.consultation_id)
        )
        record = rec_res.scalar_one_or_none()
        if record:
            syndrome_name = record.primary_syndrome_name or ""
            if record.syndrome_result:
                primary = record.syndrome_result.get("primary_syndrome", {})
                syndrome_name = primary.get("syndrome_name") or syndrome_name
                treatment_principle = primary.get("treatment_principle") or ""

    doctor_name = current_user.name or current_user.email or ""
    patient_info = {
        "name": patient.name if patient else "",
        "gender": patient.gender if patient else "",
        "age": patient.age if patient else None,
        "phone": patient.phone if patient else "",
    }

    pdf_bytes = build_prescription_pdf(
        patient=patient_info,
        doctor_name=doctor_name,
        formula_name=prescription.formula_name or "",
        composition=prescription.medicines,
        dosage_instructions=prescription.dosage_instructions or "",
        duration_days=prescription.duration_days or 7,
        syndrome_name=syndrome_name,
        treatment_principle=treatment_principle,
        notes=prescription.notes or "",
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="prescription-{prescription_id}.pdf"'},
    )


@router.get("/records/patient/{patient_id}")
async def get_patient_diagnosis_history(
    patient_id: UUID,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取患者的辨证历史记录（用于复诊对比）

    返回该患者的所有辨证记录，按时间倒序
    """
    result = await db.execute(
        select(DiagnosisRecord)
        .where(DiagnosisRecord.tenant_id == current_user.tenant_id)
        .where(DiagnosisRecord.patient_id == patient_id)
        .order_by(desc(DiagnosisRecord.created_at))
        .limit(limit)
    )
    records = result.scalars().all()

    return [
        {
            "id": r.id,
            "disease_type": r.disease_type,
            "primary_syndrome_name": r.primary_syndrome_name,
            "confidence": r.confidence,
            "selected_formula": r.selected_formula,
            "selected_symptoms": r.selected_symptoms,
            "syndrome_result": r.syndrome_result,
            "doctor_notes": r.doctor_notes,
            "efficacy_rating": r.efficacy_rating,
            "efficacy_notes": r.efficacy_notes,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in records
    ]


@router.get("/records/compare/{record_id_1}/{record_id_2}")
async def compare_diagnosis_records(
    record_id_1: UUID,
    record_id_2: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    对比两次辨证记录（复诊分析）

    对比症状变化、证型变化、用方调整
    """
    # 获取两条记录
    result = await db.execute(
        select(DiagnosisRecord)
        .where(DiagnosisRecord.tenant_id == current_user.tenant_id)
        .where(DiagnosisRecord.id.in_([record_id_1, record_id_2]))
    )
    records = {r.id: r for r in result.scalars().all()}

    if len(records) != 2:
        raise HTTPException(status_code=404, detail="辨证记录未找到")

    r1 = records[record_id_1]
    r2 = records[record_id_2]

    # 对比症状变化
    symptoms_comparison = _compare_symptoms(
        r1.selected_symptoms,
        r2.selected_symptoms
    )

    # 对比证型变化
    syndrome_changed = r1.primary_syndrome_code != r2.primary_syndrome_code

    return {
        "record_1": {
            "id": r1.id,
            "date": r1.created_at.isoformat() if r1.created_at else None,
            "syndrome": r1.primary_syndrome_name,
            "confidence": r1.confidence,
            "formula": r1.selected_formula
        },
        "record_2": {
            "id": r2.id,
            "date": r2.created_at.isoformat() if r2.created_at else None,
            "syndrome": r2.primary_syndrome_name,
            "confidence": r2.confidence,
            "formula": r2.selected_formula
        },
        "changes": {
            "syndrome_changed": syndrome_changed,
            "symptoms_added": symptoms_comparison["added"],
            "symptoms_removed": symptoms_comparison["removed"],
            "symptoms_modified": symptoms_comparison["modified"]
        },
        "suggestion": _generate_follow_up_suggestion(r1, r2, syndrome_changed)
    }


def _compare_symptoms(symptoms1: Dict, symptoms2: Dict) -> Dict:
    """对比症状变化"""
    added = []
    removed = []
    modified = []

    all_keys = set(symptoms1.keys()) | set(symptoms2.keys())

    for key in all_keys:
        val1 = symptoms1.get(key)
        val2 = symptoms2.get(key)

        if val1 is None and val2 is not None:
            added.append({"key": key, "value": val2})
        elif val1 is not None and val2 is None:
            removed.append({"key": key, "value": val1})
        elif val1 != val2:
            modified.append({"key": key, "from": val1, "to": val2})

    return {"added": added, "removed": removed, "modified": modified}


def _generate_follow_up_suggestion(r1: DiagnosisRecord, r2: DiagnosisRecord, syndrome_changed: bool) -> str:
    """生成复诊建议"""
    if syndrome_changed:
        return f"证型已从「{r1.primary_syndrome_name}」转为「{r2.primary_syndrome_name}」，建议调整治法，更换方剂。"
    else:
        if r2.confidence and r1.confidence and r2.confidence > r1.confidence:
            return "证型未变，症状符合度提高，建议守方继续治疗。"
        else:
            return "证型未变，但症状有变化，建议在原方基础上加减化裁。"


class UpdateEfficacyRequest(BaseModel):
    """更新疗效评价请求"""
    efficacy_rating: int = Field(ge=1, le=5)  # 1-5分
    efficacy_notes: Optional[str] = None


@router.put("/records/{record_id}/efficacy")
async def update_efficacy(
    record_id: UUID,
    request: UpdateEfficacyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    更新辨证记录的疗效评价（复诊时填写）
    """
    result = await db.execute(
        select(DiagnosisRecord)
        .where(DiagnosisRecord.id == record_id)
        .where(DiagnosisRecord.tenant_id == current_user.tenant_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="记录未找到")

    record.efficacy_rating = request.efficacy_rating
    record.efficacy_notes = request.efficacy_notes

    await db.commit()

    return {"message": "疗效评价更新成功"}


class ScheduleFollowupRequest(BaseModel):
    scheduled_date: datetime
    notes: Optional[str] = None


@router.post("/records/{record_id}/schedule-followup")
async def schedule_followup(
    record_id: UUID,
    request: ScheduleFollowupRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """从辨证记录直接安排复诊，并保留记录之间的关联。"""
    result = await db.execute(
        select(DiagnosisRecord).where(
            DiagnosisRecord.id == record_id,
            DiagnosisRecord.tenant_id == current_user.tenant_id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="记录未找到")
    if request.scheduled_date.tzinfo is None:
        raise HTTPException(status_code=422, detail="复诊时间必须包含时区")

    followup = Followup(
        tenant_id=current_user.tenant_id,
        patient_id=record.patient_id,
        consultation_id=record.consultation_id,
        doctor_id=current_user.id,
        scheduled_date=request.scheduled_date,
        notes=request.notes or f"针对辨证记录：{record.primary_syndrome_name or '未命名证型'}",
        status="scheduled",
    )
    record.follow_up_date = request.scheduled_date
    db.add(followup)
    await db.commit()
    await db.refresh(followup)
    return {"id": followup.id, "scheduled_date": followup.scheduled_date, "message": "复诊已安排"}


# ==================== Phase 4: 症状模板管理 ====================

@router.get("/templates")
async def list_symptom_templates(
    disease_type: Optional[str] = None,
    template_type: Optional[str] = Query(None, regex="^(system|personal)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取症状模板列表

    Query Parameters:
        - disease_type: 病种筛选
        - template_type: system（系统模板）/ personal（个人模板）
    """
    query = select(SymptomTemplate).where(SymptomTemplate.is_active == 1)

    if disease_type:
        query = query.where(SymptomTemplate.disease_type == disease_type)

    if template_type:
        query = query.where(SymptomTemplate.template_type == template_type)
    else:
        # 默认返回系统模板和当前用户的个人模板
        query = query.where(
            (SymptomTemplate.template_type == "system") |
            (SymptomTemplate.created_by == current_user.id)
        )

    query = query.order_by(desc(SymptomTemplate.usage_count))

    result = await db.execute(query)
    templates = result.scalars().all()

    return [
        {
            "id": t.id,
            "template_name": t.template_name,
            "description": t.description,
            "disease_type": t.disease_type,
            "syndrome_code": t.syndrome_code,
            "symptoms_data": t.symptoms_data,
            "template_type": t.template_type,
            "usage_count": t.usage_count
        }
        for t in templates
    ]


@router.get("/templates/{template_id}")
async def get_template_detail(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取模板详情（用于一键填充）
    """
    result = await db.execute(
        select(SymptomTemplate)
        .where(SymptomTemplate.id == template_id)
        .where(SymptomTemplate.is_active == 1)
    )
    template = result.scalar_one_or_none()

    if not template:
        raise HTTPException(status_code=404, detail="模板未找到")

    # 增加使用次数
    template.usage_count += 1
    await db.commit()

    return {
        "id": template.id,
        "template_name": template.template_name,
        "description": template.description,
        "symptoms_data": template.symptoms_data
    }


class CreateTemplateRequest(BaseModel):
    """创建个人模板请求"""
    disease_type: str
    syndrome_code: Optional[str] = None
    template_name: str
    description: Optional[str] = None
    symptoms_data: Dict[str, Any]


@router.post("/templates")
async def create_personal_template(
    request: CreateTemplateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    创建个人症状模板

    医生可以保存常用症状组合为个人模板
    """
    import uuid

    template = SymptomTemplate(
        id=uuid.uuid4(),
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        disease_type=request.disease_type,
        syndrome_code=request.syndrome_code,
        template_name=request.template_name,
        description=request.description,
        symptoms_data=request.symptoms_data,
        template_type="personal",
        usage_count=0,
        is_active=1
    )

    db.add(template)
    await db.commit()
    await db.refresh(template)

    return {
        "id": template.id,
        "message": "个人模板创建成功"
    }


# ==================== Phase 4: 用药安全检查 ====================

class SafetyCheckRequest(BaseModel):
    """用药安全检查请求"""
    herbs: List[Dict[str, Any]]  # [{"name": "黄芪", "dosage": 30}, ...]
    patient_info: Optional[Dict[str, Any]] = None  # {"is_pregnant": bool, "age": int, ...}


@router.post("/safety-check")
async def check_formula_safety(
    request: SafetyCheckRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    方剂用药安全检查

    检查项目：
    1. 十八反配伍禁忌
    2. 十九畏配伍警戒
    3. 妊娠禁忌
    4. 剂量上限
    5. 特殊人群（儿童、老人、肝肾功能不全）
    6. 过敏史

    Request Body:
    ```json
    {
      "herbs": [
        {"name": "黄芪", "dosage": 30},
        {"name": "当归", "dosage": 10}
      ],
      "patient_info": {
        "is_pregnant": false,
        "age": 45,
        "liver_dysfunction": false,
        "kidney_dysfunction": false,
        "allergies": "青霉素"
      }
    }
    ```

    Response:
    ```json
    {
      "errors": [...],      // 严重错误（必须修改）
      "warnings": [...],    // 警告（建议注意）
      "suggestions": [...]  // 优化建议
    }
    ```
    """
    service = SafetyCheckService(db)

    result = await service.check_formula_safety(
        herbs=request.herbs,
        patient_info=request.patient_info
    )

    return result


@router.get("/safety-info/{herb_name}")
async def get_herb_safety_info(
    herb_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取单个药物的安全信息

    返回该药物的配伍禁忌、妊娠禁忌、剂量限制等
    """
    service = SafetyCheckService(db)
    info = await service.get_herb_safety_info(herb_name)

    return info
