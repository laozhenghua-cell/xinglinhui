"""
医案库数据模型
"""
from sqlalchemy import Column, String, Integer, Boolean, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.database import Base
import uuid


class MedicalCase(Base):
    """经典医案模型"""
    __tablename__ = "medical_cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)

    # 基本信息
    case_number = Column(String(50), unique=True, nullable=False, index=True)
    case_title = Column(String(200), nullable=False)
    source = Column(String(100), default="临床经验")
    case_date = Column(Date)

    # 患者信息
    patient_info = Column(JSONB, default={})

    # 四诊信息
    inspection = Column(JSONB, default={})
    auscultation = Column(JSONB, default={})
    inquiry = Column(JSONB, default={})
    palpation = Column(JSONB, default={})

    # 辨证过程
    disease_type = Column(String(50), nullable=False, index=True)
    syndrome_analysis = Column(Text)
    syndrome_type = Column(String(100), index=True)
    treatment_principle = Column(String(200))

    # 治疗方案
    internal_formula = Column(JSONB, default={})
    external_treatment = Column(JSONB, default=[])
    other_treatments = Column(Text)

    # 疗效追踪
    follow_ups = Column(JSONB, default=[])
    outcome = Column(String(50))
    outcome_notes = Column(Text)

    # 教学要点
    key_points = Column(Text)
    teaching_notes = Column(Text)
    tags = Column(JSONB, default=[])

    # 元数据
    is_classic = Column(Boolean, default=False, index=True)
    difficulty_level = Column(Integer, default=2)
    view_count = Column(Integer, default=0)
    reference_count = Column(Integer, default=0)

    created_at = Column(
        "created_at",
        type_=lambda: __import__("sqlalchemy").types.TIMESTAMP(timezone=True),
        server_default=func.now()
    )
    updated_at = Column(
        "updated_at",
        type_=lambda: __import__("sqlalchemy").types.TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": str(self.id),
            "case_number": self.case_number,
            "case_title": self.case_title,
            "source": self.source,
            "case_date": self.case_date.isoformat() if self.case_date else None,
            "patient_info": self.patient_info,
            "inspection": self.inspection,
            "auscultation": self.auscultation,
            "inquiry": self.inquiry,
            "palpation": self.palpation,
            "disease_type": self.disease_type,
            "syndrome_analysis": self.syndrome_analysis,
            "syndrome_type": self.syndrome_type,
            "treatment_principle": self.treatment_principle,
            "internal_formula": self.internal_formula,
            "external_treatment": self.external_treatment,
            "other_treatments": self.other_treatments,
            "follow_ups": self.follow_ups,
            "outcome": self.outcome,
            "outcome_notes": self.outcome_notes,
            "key_points": self.key_points,
            "teaching_notes": self.teaching_notes,
            "tags": self.tags,
            "is_classic": self.is_classic,
            "difficulty_level": self.difficulty_level,
            "view_count": self.view_count,
            "reference_count": self.reference_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def to_summary(self):
        """转换为摘要（列表显示）"""
        return {
            "id": str(self.id),
            "case_number": self.case_number,
            "case_title": self.case_title,
            "disease_type": self.disease_type,
            "syndrome_type": self.syndrome_type,
            "patient_info": {
                "age": self.patient_info.get("age"),
                "gender": self.patient_info.get("gender"),
                "chief_complaint": self.patient_info.get("chief_complaint")
            },
            "outcome": self.outcome,
            "is_classic": self.is_classic,
            "difficulty_level": self.difficulty_level,
            "tags": self.tags,
            "case_date": self.case_date.isoformat() if self.case_date else None
        }
