import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base


class ConsultationRequest(Base):
    """专家会诊请求"""
    __tablename__ = "consultation_requests"
    __table_args__ = (
        Index("ix_consultation_requests_consultation_id", "consultation_id"),
        Index("ix_consultation_requests_requesting_doctor_id", "requesting_doctor_id"),
        Index("ix_consultation_requests_expert_id", "expert_id"),
        Index("ix_consultation_requests_status", "status"),
        Index("ix_consultation_requests_priority", "priority"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    consultation_id: Mapped[str] = mapped_column(String(36), ForeignKey("ulcer_consultations.id"), nullable=False, unique=True)
    requesting_doctor_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    expert_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), comment="指定专家，空则自动匹配")

    # 请求信息
    request_reason: Mapped[str | None] = mapped_column(Text, comment="请求原因")
    specific_questions: Mapped[str | None] = mapped_column(Text, comment="具体问题")
    ai_suggestion: Mapped[str | None] = mapped_column(Text, comment="AI推荐专家理由")

    # 状态
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        comment="pending/matched/accepted/completed/rejected/cancelled"
    )
    priority: Mapped[int] = mapped_column(Integer, default=3, comment="优先级1-5，5最高")

    # 时间追踪
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    matched_at: Mapped[datetime | None] = mapped_column(DateTime, comment="匹配专家时间")
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, comment="专家接受时间")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, comment="完成时间")

    # 响应时间（分钟）
    response_time_minutes: Mapped[int | None] = mapped_column(Integer, comment="响应时长")

    # 费用
    consultation_fee: Mapped[int | None] = mapped_column(Integer, comment="会诊费用（分）")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    consultation: Mapped["UlcerConsultation"] = relationship("UlcerConsultation", back_populates="consultation_request")
    requesting_doctor: Mapped["User"] = relationship("User", foreign_keys=[requesting_doctor_id])
    expert: Mapped["User | None"] = relationship("User", back_populates="expert_requests", foreign_keys=[expert_id])
    expert_response: Mapped["ExpertResponse | None"] = relationship("ExpertResponse", back_populates="request", uselist=False)
