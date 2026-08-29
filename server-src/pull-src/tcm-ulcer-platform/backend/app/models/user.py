import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base


class User(Base):
    """用户表（基层医生、专家、管理员）"""
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_role", "role"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    role: Mapped[str] = mapped_column(String(20), nullable=False, comment="doctor/expert/admin")
    hospital: Mapped[str | None] = mapped_column(String(100), comment="所在医院")
    department: Mapped[str | None] = mapped_column(String(50), comment="科室")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, comment="资质认证")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    expert_profile: Mapped["ExpertProfile | None"] = relationship("ExpertProfile", back_populates="user", uselist=False)
    consultations: Mapped[list["UlcerConsultation"]] = relationship("UlcerConsultation", back_populates="doctor", foreign_keys="UlcerConsultation.doctor_id")
    expert_requests: Mapped[list["ConsultationRequest"]] = relationship("ConsultationRequest", back_populates="expert", foreign_keys="ConsultationRequest.expert_id")
    expert_responses: Mapped[list["ExpertResponse"]] = relationship("ExpertResponse", back_populates="expert")
