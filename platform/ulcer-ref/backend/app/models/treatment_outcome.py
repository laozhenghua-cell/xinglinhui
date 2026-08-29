import uuid
from datetime import date, datetime
from sqlalchemy import String, Date, DateTime, ForeignKey, Integer, Float, Boolean, JSON, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base


class TreatmentOutcome(Base):
    """治疗结果追踪"""
    __tablename__ = "treatment_outcomes"
    __table_args__ = (
        Index("ix_treatment_outcomes_consultation_id", "consultation_id"),
        Index("ix_treatment_outcomes_followup_date", "followup_date"),
        Index("ix_treatment_outcomes_cured", "cured"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    consultation_id: Mapped[str] = mapped_column(String(36), ForeignKey("ulcer_consultations.id"), nullable=False)

    # 随访信息
    followup_date: Mapped[date] = mapped_column(Date, nullable=False, comment="随访日期")
    days_since_treatment: Mapped[int] = mapped_column(Integer, comment="治疗天数")
    followup_type: Mapped[str] = mapped_column(String(20), comment="线上/线下/电话")

    # 症状改善
    symptom_improvement: Mapped[int | None] = mapped_column(Integer, comment="症状改善评分1-10")
    pain_level: Mapped[int | None] = mapped_column(Integer, comment="疼痛评分1-10")
    size_change: Mapped[str | None] = mapped_column(String(50), comment="大小变化：缩小/无变化/增大")

    # 客观指标
    objective_assessment: Mapped[dict | None] = mapped_column(JSON, comment="客观评估")
    # objective_assessment格式: {
    #   "redness": "减轻",  # 红肿程度
    #   "swelling": "消退",
    #   "pus": "已排出",
    #   "healing": "结痂",
    #   "measurements": {"diameter_mm": 8}  # 初诊12mm
    # }

    # 图像对比
    image_comparison: Mapped[dict | None] = mapped_column(JSON, comment="图像对比分析")
    # image_comparison格式: {
    #   "initial_image_id": "xxx",
    #   "current_image_id": "yyy",
    #   "ai_comparison": {
    #     "redness_reduction": 0.6,  # 红肿减少60%
    #     "size_reduction": 0.33,    # 尺寸缩小33%
    #     "improvement_score": 7.5
    #   }
    # }

    # 治疗效果评估
    treatment_effectiveness: Mapped[str | None] = mapped_column(String(20), comment="显效/有效/无效/加重")
    cured: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否治愈")
    cure_date: Mapped[date | None] = mapped_column(Date, comment="治愈日期")

    # 并发症
    has_complications: Mapped[bool] = mapped_column(Boolean, default=False)
    complications: Mapped[str | None] = mapped_column(Text, comment="并发症描述")

    # 方案调整
    treatment_adjusted: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否调整方案")
    adjustment_reason: Mapped[str | None] = mapped_column(Text, comment="调整原因")
    new_treatment: Mapped[dict | None] = mapped_column(JSON, comment="新治疗方案")

    # 患者满意度
    patient_satisfaction: Mapped[int | None] = mapped_column(Integer, comment="患者满意度1-5")
    patient_feedback: Mapped[str | None] = mapped_column(Text, comment="患者反馈")

    # 备注
    notes: Mapped[str | None] = mapped_column(Text, comment="随访备注")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    consultation: Mapped["UlcerConsultation"] = relationship("UlcerConsultation", back_populates="treatment_outcomes")
