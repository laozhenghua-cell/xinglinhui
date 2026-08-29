"""拍照辨病 —— 上传疮疡照片,AI 识别 + 匹配图谱库病种"""
import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db
from ..models import Disease
from ..schemas import DiagnosisOut
from ..security import is_valid_image, limit_ai, read_limited
from ..services.deepseek import deepseek_service
from ..services.qwen_vision import qwen_vision_service

router = APIRouter(prefix="/api/v1/diagnosis", tags=["diagnosis"])

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def _match_diseases(name: str, diseases: list[Disease]) -> list[Disease]:
    """把 AI 给出的病名模糊匹配到图谱库病种"""
    if not name:
        return []
    n = name.strip()
    matched = []
    for d in diseases:
        aliases = d.aliases or []
        if n == d.name or n in aliases or d.name in n or any(n in a or a in n for a in aliases):
            matched.append(d)
    return matched


@router.post("/analyze", response_model=DiagnosisOut)
async def analyze_text(
    symptoms: str = Form(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """纯文本辨病:根据疮形特点描述,AI 辅助辨病 + 辨证"""
    limit_ai(request)
    try:
        ai = await deepseek_service.analyze_symptoms(symptoms)
    except Exception as e:
        ai = {"error": "AI 识别失败,请稍后重试", "disease_name": ""}

    diseases = (await db.execute(select(Disease).order_by(Disease.id))).scalars().all()
    matched = _match_diseases(ai.get("disease_name", ""), diseases)

    hint = ""
    if ai.get("dangerous"):
        hint = f"⚠️ 危险提示:{ai.get('danger_reason') or '本病易走黄/内陷,建议谨慎处理,必要时转诊。'}"
    elif not matched:
        hint = "AI 未能精确匹配图谱库病种,请结合疮形特点人工核对。"

    return DiagnosisOut(image_url="", ai=ai, matched_diseases=matched, hint=hint)


@router.post("/identify", response_model=DiagnosisOut)
async def identify(
    image: UploadFile = File(...),
    symptoms: Optional[str] = Form(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    limit_ai(request)
    ext = os.path.splitext(image.filename or "")[-1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail=f"不支持的图片格式: {ext or '未知'}")

    data = await read_limited(image)
    if not is_valid_image(data):
        raise HTTPException(status_code=400, detail="无效的图片文件")

    os.makedirs(settings.upload_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(settings.upload_dir, filename)
    with open(save_path, "wb") as f:
        f.write(data)

    # 调用 QWEN Vision 辨病(视觉 key 失效时,降级用 DeepSeek 文本分析症状描述)
    ai = {}
    try:
        ai = await qwen_vision_service.identify_disease(save_path, symptoms)
    except Exception as e:
        if symptoms:
            try:
                ai = await deepseek_service.analyze_symptoms(symptoms)
                ai["_fallback"] = "vision 不可用,已用症状文本分析"
            except Exception:
                ai = {"error": "AI 识别失败,请稍后重试", "disease_name": ""}
        else:
            ai = {"error": "AI 识别失败,请稍后重试", "disease_name": ""}

    # 匹配图谱库病种
    diseases = (await db.execute(select(Disease).order_by(Disease.id))).scalars().all()
    matched = _match_diseases(ai.get("disease_name", ""), diseases)

    hint = ""
    if ai.get("dangerous"):
        hint = f"⚠️ 危险提示:{ai.get('danger_reason') or '本病易走黄/内陷,建议谨慎处理,必要时转诊。'}"
    elif not matched:
        hint = "AI 未能精确匹配图谱库病种,请结合疮形特点人工核对。"

    return DiagnosisOut(
        image_url=f"/uploads/{filename}",
        ai=ai,
        matched_diseases=matched,
        hint=hint,
    )
