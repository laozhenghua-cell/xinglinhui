import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel


class ImageAnalysisRequest(BaseModel):
    image_base64: str
    image_type: str = "lesion"  # hemorrhoid, fissure, abscess, fistula, prolapse, eczema, condyloma, lesion, tongue
    stage: str = "before"  # before, during, after
    patient_id: Optional[uuid.UUID] = None
    consultation_id: Optional[uuid.UUID] = None
    extra_symptoms: Optional[str] = None
    patient_info: Optional[str] = None


class FormulaDetail(BaseModel):
    name: Optional[str] = None
    composition: Optional[str] = None
    usage: Optional[str] = None
    modifications: Optional[str] = None


class ExternalTreatment(BaseModel):
    sitzBath: Optional[str] = None
    topical: Optional[str] = None
    suppository: Optional[str] = None


class AcupunctureAdvice(BaseModel):
    points: Optional[List[str]] = None
    method: Optional[str] = None


class ImageAnalysisResponse(BaseModel):
    image_id: Optional[uuid.UUID] = None
    disease: Optional[str] = None
    diseaseType: Optional[str] = None
    classification: Optional[str] = None
    confidence: Optional[float] = None
    visualFindings: Optional[str] = None
    differentialDiagnosis: Optional[List[str]] = None
    syndrome: Optional[str] = None
    pathogenesis: Optional[str] = None
    treatmentPrinciple: Optional[str] = None
    formula: Optional[Dict[str, Any]] = None
    externalTreatment: Optional[Dict[str, Any]] = None
    acupuncture: Optional[Dict[str, Any]] = None
    surgeryAdvice: Optional[str] = None
    severity: Optional[str] = None
    urgency: Optional[str] = None
    prognosis: Optional[str] = None
    lifestyle: Optional[List[str]] = None
    followUp: Optional[str] = None
    warnings: Optional[List[str]] = None
    imageType: Optional[str] = None
    modelUsed: Optional[str] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True
