import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column
from ..core.database import Base


class UlcerKnowledge(Base):
    """疮疡知识库（从疮疡图谱提取）"""
    __tablename__ = "ulcer_knowledge"
    __table_args__ = (
        Index("ix_ulcer_knowledge_ulcer_type", "ulcer_type"),
        Index("ix_ulcer_knowledge_location", "location"),
        Index("ix_ulcer_knowledge_category", "category"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 基本信息
    ulcer_type: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="疮疡类型")
    chinese_name: Mapped[str] = mapped_column(String(100), nullable=False, comment="中文名称")
    english_name: Mapped[str | None] = mapped_column(String(100), comment="英文名称")
    aliases: Mapped[list | None] = mapped_column(JSON, comment="别名列表")

    # 分类
    category: Mapped[str] = mapped_column(String(20), comment="分类：痈/疽/疖/疔/疮")
    location: Mapped[str] = mapped_column(String(50), comment="好发部位")
    location_detail: Mapped[str | None] = mapped_column(Text, comment="部位详细描述")

    # 病因病机
    etiology: Mapped[str | None] = mapped_column(Text, comment="病因")
    pathogenesis: Mapped[str | None] = mapped_column(Text, comment="病机")

    # 临床表现
    morphology: Mapped[dict | None] = mapped_column(JSON, comment="形态特征")
    # morphology格式: {
    #   "color": "鲜红",
    #   "size": "蚕豆至栗子大",
    #   "shape": "圆形",
    #   "texture": "根深坚硬",
    #   "pain": "灼热疼痛",
    #   "progression": "3-5日成脓"
    # }

    clinical_features: Mapped[str | None] = mapped_column(Text, comment="临床特征")
    systemic_symptoms: Mapped[str | None] = mapped_column(Text, comment="全身症状")

    # 辨证论治
    syndrome_types: Mapped[list | None] = mapped_column(JSON, comment="证型列表")
    # syndrome_types格式: [
    #   {
    #     "syndrome": "火毒炽盛证",
    #     "symptoms": "局部红肿灼痛...",
    #     "tongue_pulse": "舌红苔黄，脉数有力"
    #   }
    # ]

    # 治疗方案
    treatment_principle: Mapped[str | None] = mapped_column(Text, comment="治则")

    internal_treatment: Mapped[dict | None] = mapped_column(JSON, comment="内治法")
    # internal_treatment格式: {
    #   "formulas": [
    #     {
    #       "name": "五味消毒饮",
    #       "composition": "金银花、野菊花、蒲公英...",
    #       "dosage": "各15g",
    #       "modifications": "热甚加黄连..."
    #     }
    #   ],
    #   "methods": ["消法", "托法"]
    # }

    external_treatment: Mapped[dict | None] = mapped_column(JSON, comment="外治法")
    # external_treatment格式: {
    #   "topical": [
    #     {"name": "油调膏", "usage": "外敷患处"},
    #     {"name": "玉露散", "usage": "外敷"}
    #   ],
    #   "wash": "黄连解毒汤熏洗",
    #   "other": ["切开排脓", "九一丹提脓"]
    # }

    # 预防与护理
    prevention: Mapped[str | None] = mapped_column(Text, comment="预防")
    nursing: Mapped[str | None] = mapped_column(Text, comment="护理要点")
    diet_advice: Mapped[str | None] = mapped_column(Text, comment="饮食宜忌")

    # 预后
    prognosis: Mapped[str | None] = mapped_column(Text, comment="预后")
    complications: Mapped[str | None] = mapped_column(Text, comment="并发症")

    # 鉴别诊断
    differential_diagnosis: Mapped[list | None] = mapped_column(JSON, comment="鉴别诊断")

    # 参考资料
    reference_images: Mapped[list | None] = mapped_column(JSON, comment="参考图谱URL列表")
    source: Mapped[str | None] = mapped_column(String(200), comment="数据来源")
    page_number: Mapped[int | None] = mapped_column(comment="图谱页码")

    # 统计数据
    case_count: Mapped[int] = mapped_column(default=0, comment="病例数")
    cure_rate: Mapped[float | None] = mapped_column(comment="治愈率")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
