import uuid
from datetime import date, datetime
from sqlalchemy import String, Date, DateTime, ForeignKey, Text, JSON, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base


class UlcerConsultation(Base):
    """疮疡会诊记录"""
    __tablename__ = "ulcer_consultations"
    __table_args__ = (
        Index("ix_ulcer_consultations_patient_id", "patient_id"),
        Index("ix_ulcer_consultations_doctor_id", "doctor_id"),
        Index("ix_ulcer_consultations_status", "status"),
        Index("ix_ulcer_consultations_ulcer_type", "ulcer_type"),
        Index("ix_ulcer_consultations_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id: Mapped[str] = mapped_column(String(36), ForeignKey("patients.id"), nullable=False)
    doctor_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)

    # 疮疡基本信息
    ulcer_type: Mapped[str | None] = mapped_column(String(50), comment="疮疡类型：眼有疔/鼻疔/虎口疔...")
    location: Mapped[str | None] = mapped_column(String(50), comment="发病部位：头面部/上肢/下肢/躯干")
    location_detail: Mapped[str | None] = mapped_column(String(200), comment="具体位置描述")
    onset_date: Mapped[date | None] = mapped_column(Date, comment="发病日期")
    duration_days: Mapped[int | None] = mapped_column(Integer, comment="病程天数")

    # 主诉与症状
    chief_complaint: Mapped[str | None] = mapped_column(Text, comment="主诉")
    symptoms: Mapped[dict | None] = mapped_column(JSON, comment="症状详情")
    # symptoms格式: {
    #   "pain_level": 7,  # 疼痛程度1-10
    #   "redness": true,  # 红肿
    #   "heat": true,     # 灼热
    #   "swelling": true, # 肿胀
    #   "pus": false,     # 有脓
    #   "fever": false,   # 发热
    #   "systemic": "乏力、纳差"  # 全身症状
    # }

    # 望诊
    appearance: Mapped[dict | None] = mapped_column(JSON, comment="望诊所见")
    # appearance格式: {
    #   "color": "鲜红",
    #   "size": "蚕豆大小",
    #   "shape": "圆形",
    #   "texture": "根深坚硬",
    #   "discharge": "无",
    #   "surrounding": "周围肿胀"
    # }

    tongue_coating: Mapped[str | None] = mapped_column(String(100), comment="舌苔")
    tongue_body: Mapped[str | None] = mapped_column(String(100), comment="舌质")
    face_color: Mapped[str | None] = mapped_column(String(50), comment="面色")

    # 切诊
    pulse: Mapped[str | None] = mapped_column(String(200), comment="脉象")

    # 问诊（其他信息）
    inquiry_data: Mapped[dict | None] = mapped_column(JSON, comment="问诊数据")

    # AI初步诊断
    ai_analysis: Mapped[dict | None] = mapped_column(JSON, comment="AI分析结果")
    # ai_analysis格式: {
    #   "identified_type": "眼有疔",
    #   "confidence": 0.85,
    #   "syndrome": "火毒炽盛",
    #   "severity": "medium",  # low/medium/high/critical
    #   "needs_expert": true,
    #   "recommended_experts": ["expert_id_1", "expert_id_2"],
    #   "treatment_suggestion": {...}
    # }

    # 医生诊断
    doctor_diagnosis: Mapped[str | None] = mapped_column(Text, comment="医生最终诊断")
    syndrome_differentiation: Mapped[str | None] = mapped_column(Text, comment="辨证分析")

    # 治疗方案
    internal_treatment: Mapped[dict | None] = mapped_column(JSON, comment="内治方案")
    external_treatment: Mapped[dict | None] = mapped_column(JSON, comment="外治方案")

    # 状态流转
    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",
        comment="draft/ai_analyzing/pending_expert/expert_reviewing/in_treatment/completed/cancelled"
    )
    urgency_level: Mapped[str] = mapped_column(String(20), default="medium", comment="low/medium/high/critical")

    # 备注
    notes: Mapped[str | None] = mapped_column(Text, comment="备注")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    patient: Mapped["Patient"] = relationship("Patient", back_populates="consultations")
    doctor: Mapped["User"] = relationship("User", back_populates="consultations", foreign_keys=[doctor_id])
    images: Mapped[list["UlcerImage"]] = relationship("UlcerImage", back_populates="consultation", cascade="all, delete-orphan")
    consultation_request: Mapped["ConsultationRequest | None"] = relationship("ConsultationRequest", back_populates="consultation", uselist=False)
    treatment_outcomes: Mapped[list["TreatmentOutcome"]] = relationship("TreatmentOutcome", back_populates="consultation")
