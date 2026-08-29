import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base


class ExpertResponse(Base):
    """专家会诊回复"""
    __tablename__ = "expert_responses"
    __table_args__ = (
        Index("ix_expert_responses_request_id", "request_id"),
        Index("ix_expert_responses_expert_id", "expert_id"),
        Index("ix_expert_responses_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id: Mapped[str] = mapped_column(String(36), ForeignKey("consultation_requests.id"), nullable=False, unique=True)
    expert_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)

    # 专家诊断
    expert_diagnosis: Mapped[str] = mapped_column(Text, nullable=False, comment="专家诊断")
    syndrome_differentiation: Mapped[str] = mapped_column(Text, nullable=False, comment="辨证分析")

    # 治疗方案
    treatment_principle: Mapped[str | None] = mapped_column(Text, comment="治则治法")

    internal_prescription: Mapped[dict | None] = mapped_column(JSON, comment="内服处方")
    # internal_prescription格式: {
    #   "formula_name": "五味消毒饮加减",
    #   "herbs": [
    #     {"name": "金银花", "dosage": "15g", "note": "清热解毒"},
    #     {"name": "野菊花", "dosage": "15g"}
    #   ],
    #   "usage": "水煎服，日一剂",
    #   "course": "3-5日"
    # }

    external_treatment: Mapped[dict | None] = mapped_column(JSON, comment="外治方案")
    # external_treatment格式: {
    #   "topical": "油调膏外敷",
    #   "frequency": "每日2-3次",
    #   "wash": "黄连解毒汤熏洗",
    #   "other": "如出脓可用九一丹提脓"
    # }

    # 图像标注（关键特征标注）
    image_annotations: Mapped[dict | None] = mapped_column(JSON, comment="图像标注数据")
    # image_annotations格式: {
    #   "image_id": "xxx",
    #   "annotations": [
    #     {
    #       "type": "circle",
    #       "x": 100, "y": 200, "radius": 30,
    #       "label": "脓头位置",
    #       "color": "red"
    #     },
    #     {
    #       "type": "arrow",
    #       "points": [[50, 50], [80, 80]],
    #       "label": "注意此处红肿",
    #       "color": "yellow"
    #     }
    #   ]
    # }

    # 指导建议
    clinical_advice: Mapped[str | None] = mapped_column(Text, comment="临床指导")
    follow_up_plan: Mapped[str | None] = mapped_column(Text, comment="随访计划")
    precautions: Mapped[str | None] = mapped_column(Text, comment="注意事项")
    diet_advice: Mapped[str | None] = mapped_column(Text, comment="饮食建议")

    # 转诊建议
    need_referral: Mapped[bool] = mapped_column(default=False, comment="是否建议转诊")
    referral_reason: Mapped[str | None] = mapped_column(Text, comment="转诊原因")

    # 多媒体指导
    voice_guidance_url: Mapped[str | None] = mapped_column(String(512), comment="语音指导URL")
    video_consultation_url: Mapped[str | None] = mapped_column(String(512), comment="视频会诊URL")

    # 质量评估
    response_quality: Mapped[int | None] = mapped_column(Integer, comment="基层医生评分1-5")
    response_feedback: Mapped[str | None] = mapped_column(Text, comment="反馈意见")

    # 时间统计
    response_time_minutes: Mapped[int | None] = mapped_column(Integer, comment="响应时长（分钟）")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    request: Mapped["ConsultationRequest"] = relationship("ConsultationRequest", back_populates="expert_response")
    expert: Mapped["User"] = relationship("User", back_populates="expert_responses")
