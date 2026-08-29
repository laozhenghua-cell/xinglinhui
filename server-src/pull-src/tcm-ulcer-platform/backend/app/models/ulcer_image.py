import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, Float, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..core.database import Base


class UlcerImage(Base):
    """疮疡图像"""
    __tablename__ = "ulcer_images"
    __table_args__ = (
        Index("ix_ulcer_images_consultation_id", "consultation_id"),
        Index("ix_ulcer_images_image_type", "image_type"),
        Index("ix_ulcer_images_capture_date", "capture_date"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    consultation_id: Mapped[str] = mapped_column(String(36), ForeignKey("ulcer_consultations.id"), nullable=False)

    # 图片信息
    image_url: Mapped[str] = mapped_column(String(512), nullable=False, comment="图片URL")
    image_type: Mapped[str] = mapped_column(String(20), comment="initial/followup/closeup/comparison")
    capture_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="拍摄时间")
    view_angle: Mapped[str | None] = mapped_column(String(50), comment="拍摄角度：正面/侧面/特写")

    # 图片质量
    quality_score: Mapped[float | None] = mapped_column(Float, comment="图片质量评分0-1")
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    file_size: Mapped[int | None] = mapped_column(Integer, comment="文件大小(bytes)")

    # AI分析结果
    ai_analysis: Mapped[dict | None] = mapped_column(JSON, comment="AI图像分析")
    # ai_analysis格式: {
    #   "detected_features": {
    #     "redness_area": 0.15,  # 红肿面积占比
    #     "color_rgb": [200, 80, 80],
    #     "texture": "smooth",
    #     "has_pus": false,
    #     "has_swelling": true
    #   },
    #   "measurements": {
    #     "estimated_diameter_mm": 12,
    #     "estimated_depth": "shallow"
    #   },
    #   "matched_cases": ["case_id_1", "case_id_2"],  # 相似病例
    #   "confidence": 0.82
    # }

    # 专家标注
    annotations: Mapped[dict | None] = mapped_column(JSON, comment="专家标注数据")
    # annotations格式: {
    #   "markers": [
    #     {"x": 100, "y": 200, "label": "脓头", "type": "point"},
    #     {"x": 50, "y": 50, "width": 80, "height": 80, "label": "红肿范围", "type": "rect"}
    #   ],
    #   "notes": "注意观察此处...",
    #   "annotated_by": "expert_id",
    #   "annotated_at": "2026-08-12T10:30:00Z"
    # }

    # 元数据
    image_metadata: Mapped[dict | None] = mapped_column(JSON, comment="其他元数据")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relations
    consultation: Mapped["UlcerConsultation"] = relationship("UlcerConsultation", back_populates="images")
