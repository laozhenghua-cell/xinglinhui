"""
辨证诊断相关模型
"""
from sqlalchemy import Column, String, Integer, Float, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class SymptomDictionary(Base):
    """症状字典表 - 四诊采集用"""
    __tablename__ = "symptom_dictionary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String(50), nullable=False, comment="望/闻/问/切")
    subcategory = Column(String(50), comment="主症/次症/舌诊/脉诊等")
    name = Column(String(100), nullable=False, comment="症状名称")
    display_name = Column(String(100), comment="显示名称")
    options = Column(JSONB, comment="选项配置：程度、性质、时机等")
    weight = Column(Integer, default=1, comment="辨证权重")
    description = Column(Text, comment="症状说明")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class SyndromeRule(Base):
    """辨证规则表"""
    __tablename__ = "syndrome_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    disease_type = Column(String(50), nullable=False, comment="病种：痔疮/肛裂/脱垂等")
    syndrome_name = Column(String(100), nullable=False, comment="证型名称")
    syndrome_code = Column(String(50), comment="证型代码")

    # 症状模式匹配
    required_symptoms = Column(JSONB, comment="必需症状")
    optional_symptoms = Column(JSONB, comment="可选症状")
    tongue_pulse = Column(JSONB, comment="舌脉特征")

    # 治疗原则
    treatment_principle = Column(Text, nullable=False, comment="治则")

    # 推荐方剂
    recommended_formulas = Column(JSONB, comment="推荐方剂列表")

    # 匹配阈值
    confidence_threshold = Column(Float, default=0.6, comment="置信度阈值")

    # 加减化裁规则
    modification_rules = Column(JSONB, comment="加减规则库")

    priority = Column(Integer, default=0, comment="优先级")
    is_active = Column(Integer, default=1, comment="是否启用")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class DiagnosisRecord(Base):
    """辨证记录表 - 用于复诊对比和疗效追踪"""
    __tablename__ = "diagnosis_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, comment="租户ID")
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, comment="患者ID")
    consultation_id = Column(UUID(as_uuid=True), ForeignKey("consultations.id"), comment="就诊记录ID")

    # 辨证数据
    disease_type = Column(String(50), nullable=False, comment="病种")
    selected_symptoms = Column(JSONB, nullable=False, comment="选择的症状（完整四诊数据）")
    syndrome_result = Column(JSONB, nullable=False, comment="辨证结果（完整返回数据）")
    primary_syndrome_code = Column(String(50), comment="主证型代码")
    primary_syndrome_name = Column(String(100), comment="主证型名称")
    confidence = Column(Float, comment="置信度")

    # 处方数据
    selected_formula = Column(String(200), comment="选用的方剂")
    formula_modifications = Column(Text, comment="加减化裁内容")

    # 疗效追踪
    efficacy_rating = Column(Integer, comment="疗效评分 1-5分")
    efficacy_notes = Column(Text, comment="疗效说明")
    follow_up_date = Column(TIMESTAMP(timezone=True), comment="复诊日期")

    # 医生备注
    doctor_notes = Column(Text, comment="医生备注")

    created_by = Column(UUID(as_uuid=True), comment="创建人（医生ID）")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    # 关系
    patient = relationship("Patient", back_populates="diagnosis_records")
    consultation = relationship("Consultation", back_populates="diagnosis_records")


class SymptomTemplate(Base):
    """症状模板表 - 快速填充常见证型"""
    __tablename__ = "symptom_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), comment="租户ID（null为系统模板）")
    created_by = Column(UUID(as_uuid=True), comment="创建人ID（个人模板）")

    disease_type = Column(String(50), nullable=False, comment="病种")
    syndrome_code = Column(String(50), comment="关联证型代码")
    template_name = Column(String(100), nullable=False, comment="模板名称")
    description = Column(String(200), comment="模板描述")

    # 模板内容
    symptoms_data = Column(JSONB, nullable=False, comment="症状数据（完整四诊）")

    # 类型与使用统计
    template_type = Column(String(20), default="system", comment="system/personal")
    usage_count = Column(Integer, default=0, comment="使用次数")
    is_active = Column(Integer, default=1, comment="是否启用")

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())


class SafetyRule(Base):
    """用药安全规则表 - 配伍禁忌、妊娠禁忌等"""
    __tablename__ = "safety_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    rule_type = Column(String(50), nullable=False, comment="规则类型：incompatibility/pregnancy/dosage/allergy")
    severity = Column(String(20), nullable=False, comment="严重程度：critical/warning/info")

    # 规则内容
    herb_name = Column(String(100), comment="中药名称")
    conflicting_herbs = Column(JSONB, comment="相冲突药物列表（十八反十九畏）")
    contraindication_info = Column(JSONB, comment="禁忌信息")
    max_dosage = Column(Float, comment="最大剂量（克/日）")
    warning_message = Column(Text, nullable=False, comment="警告信息")
    suggestion = Column(Text, comment="建议")

    is_active = Column(Integer, default=1, comment="是否启用")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
