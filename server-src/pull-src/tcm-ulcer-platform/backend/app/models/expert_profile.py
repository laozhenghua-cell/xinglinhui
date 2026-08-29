import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, Float, Boolean, JSON, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base


class ExpertProfile(Base):
    """专家资料"""
    __tablename__ = "expert_profiles"
    __table_args__ = (
        Index("ix_expert_profiles_user_id", "user_id"),
        Index("ix_expert_profiles_is_active", "is_active"),
        Index("ix_expert_profiles_average_rating", "average_rating"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, unique=True)

    # 专业信息
    title: Mapped[str | None] = mapped_column(String(50), comment="职称：主治医师/副主任医师/主任医师")
    specialty: Mapped[list | None] = mapped_column(JSON, comment="专长领域")
    # specialty格式: ["头面部疮疡", "手足疔疮", "乳痈", "肠痈"]

    certifications: Mapped[list | None] = mapped_column(JSON, comment="资质证书")
    # certifications格式: [
    #   {"name": "中医执业医师证", "number": "xxx", "issued_date": "2015-06-01"},
    #   {"name": "中医外科主任医师证", "number": "yyy", "issued_date": "2020-01-01"}
    # ]

    experience_years: Mapped[int | None] = mapped_column(Integer, comment="从业年限")
    bio: Mapped[str | None] = mapped_column(Text, comment="个人简介")
    achievements: Mapped[str | None] = mapped_column(Text, comment="主要成就")

    # 工作信息
    hospital: Mapped[str | None] = mapped_column(String(100), comment="所在医院")
    department: Mapped[str | None] = mapped_column(String(50), comment="科室")
    hospital_level: Mapped[str | None] = mapped_column(String(20), comment="医院级别：三甲/三乙/二甲...")

    # 会诊设置
    consultation_fee: Mapped[int] = mapped_column(Integer, default=10000, comment="会诊费用（分）")
    available_hours: Mapped[dict | None] = mapped_column(JSON, comment="可接诊时间")
    # available_hours格式: {
    #   "monday": ["09:00-12:00", "14:00-17:00"],
    #   "tuesday": ["09:00-12:00"],
    #   ...
    # }

    max_daily_consultations: Mapped[int] = mapped_column(Integer, default=10, comment="每日最大接诊量")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否接单")
    auto_accept: Mapped[bool] = mapped_column(Boolean, default=False, comment="自动接单")

    # 统计数据
    consultation_count: Mapped[int] = mapped_column(Integer, default=0, comment="累计会诊次数")
    completed_count: Mapped[int] = mapped_column(Integer, default=0, comment="完成会诊次数")
    average_rating: Mapped[float | None] = mapped_column(Float, comment="平均评分")
    total_earnings: Mapped[int] = mapped_column(Integer, default=0, comment="累计收益（分）")
    average_response_minutes: Mapped[int | None] = mapped_column(Integer, comment="平均响应时长")

    # 擅长病种（自动统计）
    expertise_ulcer_types: Mapped[list | None] = mapped_column(JSON, comment="擅长的疮疡类型")
    # 格式: [
    #   {"ulcer_type": "眼有疔", "count": 25, "cure_rate": 0.95},
    #   {"ulcer_type": "鼻疔", "count": 18, "cure_rate": 0.92}
    # ]

    # 认证状态
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否通过认证")
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, comment="认证时间")
    verified_by: Mapped[str | None] = mapped_column(String(36), comment="认证管理员ID")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    user: Mapped["User"] = relationship("User", back_populates="expert_profile")
