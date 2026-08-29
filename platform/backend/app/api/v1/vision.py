import uuid
import base64
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.database import get_db
from app.models.image import Image
from app.models.user import User
from app.schemas.vision import ImageAnalysisRequest, ImageAnalysisResponse
from app.services.vision_ai import analyze_image, analyze_tongue_image

router = APIRouter(prefix="/vision", tags=["AI图像分析"])


@router.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_clinical_image(
    request: ImageAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze an anorectal clinical image using Qwen VL multimodal AI.
    Accepts base64-encoded image, returns structured diagnostic analysis.
    """
    # Validate base64 data
    try:
        decoded = base64.b64decode(request.image_base64)
        if len(decoded) < 100:
            raise ValueError("Image too small")
        if len(decoded) > 10 * 1024 * 1024:
            raise ValueError("Image exceeds 10MB limit")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的图片数据: {str(e)}",
        )

    # Call appropriate analysis service
    if request.image_type == "tongue":
        result = await analyze_tongue_image(
            image_base64=request.image_base64,
            symptoms=request.extra_symptoms,
        )
    else:
        result = await analyze_image(
            image_base64=request.image_base64,
            image_type=request.image_type,
            extra_symptoms=request.extra_symptoms,
            patient_info=request.patient_info,
        )

    # Save image record to database
    image_record = Image(
        tenant_id=current_user.tenant_id,
        consultation_id=request.consultation_id,
        patient_id=request.patient_id or uuid.uuid4(),  # placeholder if not provided
        file_path=f"base64_upload_{uuid.uuid4().hex[:8]}",
        file_name=f"analysis_{request.image_type}.jpg",
        file_size=len(decoded),
        image_type=request.image_type,
        stage=request.stage,
        ai_result=result,
    )

    if request.patient_id:
        image_record.patient_id = request.patient_id

    db.add(image_record)
    await db.flush()
    await db.refresh(image_record)

    response_data = {
        "image_id": image_record.id,
        **result,
    }

    return ImageAnalysisResponse(**response_data)


@router.get("/history/{patient_id}")
async def get_patient_image_history(
    patient_id: uuid.UUID,
    image_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all analyzed images for a patient, optionally filtered by type."""
    from sqlalchemy import select

    query = select(Image).where(
        Image.patient_id == patient_id,
        Image.tenant_id == current_user.tenant_id,
    )
    if image_type:
        query = query.where(Image.image_type == image_type)
    query = query.order_by(Image.created_at.desc())

    result = await db.execute(query)
    images = result.scalars().all()

    return {
        "total": len(images),
        "items": [
            {
                "id": img.id,
                "image_type": img.image_type,
                "stage": img.stage,
                "ai_result": img.ai_result,
                "created_at": img.created_at,
            }
            for img in images
        ],
    }


@router.post("/compare")
async def compare_images(
    before_image_id: uuid.UUID,
    after_image_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Compare before and after images to assess treatment progress."""
    from sqlalchemy import select

    before_result = await db.execute(
        select(Image).where(
            Image.id == before_image_id,
            Image.tenant_id == current_user.tenant_id,
        )
    )
    before_img = before_result.scalar_one_or_none()

    after_result = await db.execute(
        select(Image).where(
            Image.id == after_image_id,
            Image.tenant_id == current_user.tenant_id,
        )
    )
    after_img = after_result.scalar_one_or_none()

    if not before_img or not after_img:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图片记录不存在",
        )

    before_analysis = before_img.ai_result or {}
    after_analysis = after_img.ai_result or {}

    comparison = {
        "before": {
            "id": before_img.id,
            "stage": before_img.stage,
            "disease": before_analysis.get("disease"),
            "severity": before_analysis.get("severity"),
            "confidence": before_analysis.get("confidence"),
            "created_at": before_img.created_at,
        },
        "after": {
            "id": after_img.id,
            "stage": after_img.stage,
            "disease": after_analysis.get("disease"),
            "severity": after_analysis.get("severity"),
            "confidence": after_analysis.get("confidence"),
            "created_at": after_img.created_at,
        },
        "improvement": _assess_improvement(before_analysis, after_analysis),
    }

    return comparison


def _assess_improvement(before: dict, after: dict) -> dict:
    """Simple heuristic to assess improvement between two analyses."""
    severity_scale = {"重度": 3, "中度": 2, "轻度": 1}
    before_severity = severity_scale.get(before.get("severity", ""), 0)
    after_severity = severity_scale.get(after.get("severity", ""), 0)

    if after_severity < before_severity:
        status = "improved"
        description = "病情有所好转"
    elif after_severity > before_severity:
        status = "worsened"
        description = "病情有所加重"
    else:
        status = "stable"
        description = "病情基本稳定"

    return {
        "status": status,
        "description": description,
        "severity_change": before_severity - after_severity,
    }
