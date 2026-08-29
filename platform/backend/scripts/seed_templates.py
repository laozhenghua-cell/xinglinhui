"""
症状模板数据种子 - 9种常见证型的典型症状模板
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models import SymptomTemplate
import uuid
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://zhilou_user:Zhilou2024!@db:5432/zhilou_clinic")
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


SYSTEM_TEMPLATES = [
    {
        "disease_type": "痔疮",
        "syndrome_code": "ZC_SHINY",
        "template_name": "实热内蕴型（典型）",
        "description": "便血鲜红、大便干结、口苦、舌红苔黄、脉数",
        "symptoms_data": {
            "bleeding": {"present": True, "color": "鲜红", "volume": "中量", "timing": "便后"},
            "pain": {"present": True, "degree": "中度", "nature": "胀痛"},
            "stool_condition": "干结",
            "urination": "短赤",
            "bitter_mouth": True,
            "tongue_color": "红",
            "tongue_coating": "黄",
            "pulse_rapid": True,
            "pulse_wiry": True
        }
    },
    {
        "disease_type": "痔疮",
        "syndrome_code": "ZC_SRXZ",
        "template_name": "湿热下注型（典型）",
        "description": "肛门肿胀疼痛、分泌物多、舌红苔黄腻、脉滑数",
        "symptoms_data": {
            "pain": {"present": True, "degree": "中度", "nature": "胀痛"},
            "swelling_symptom": {"present": True, "location": "肛周"},
            "anal_swelling": "中度",
            "anal_secretion": "粘液性",
            "urination": "短赤",
            "bitter_mouth": True,
            "poor_appetite": True,
            "tongue_color": "红",
            "tongue_coating": "黄腻",
            "pulse_wiry": True,
            "pulse_slippery": True
        }
    },
    {
        "disease_type": "痔疮",
        "syndrome_code": "ZC_QXKS",
        "template_name": "气血亏损型（典型）",
        "description": "便血色淡、神疲乏力、面色无华、舌淡脉细",
        "symptoms_data": {
            "bleeding": {"present": True, "color": "淡红", "volume": "点滴"},
            "fatigue": True,
            "pale_complexion": True,
            "poor_appetite": True,
            "tongue_color": "淡红",
            "tongue_coating": "薄白",
            "pulse_fine": True,
            "pulse_weak": True
        }
    },
    {
        "disease_type": "痔疮",
        "syndrome_code": "ZC_PXQX",
        "template_name": "脾虚气陷型（典型）",
        "description": "痔核脱出、神疲乏力、食欲不振、舌淡胖齿痕",
        "symptoms_data": {
            "prolapse_symptom": {"present": True, "degree": "III度"},
            "fatigue": True,
            "poor_appetite": True,
            "stool_condition": "溏泄",
            "pale_complexion": True,
            "tongue_color": "淡红",
            "tongue_shape": "胖大齿痕",
            "tongue_coating": "薄白",
            "pulse_weak": True
        }
    },
    {
        "disease_type": "痔疮",
        "syndrome_code": "ZC_QZXY",
        "template_name": "气滞血瘀型（典型）",
        "description": "肛门刺痛、痔核暗紫、舌紫暗有瘀斑、脉弦或涩",
        "symptoms_data": {
            "pain": {"present": True, "degree": "重度", "nature": "刺痛"},
            "anal_color": "紫暗",
            "swelling_symptom": {"present": True},
            "tongue_color": "紫暗",
            "pulse_wiry": True
        }
    },
    {
        "disease_type": "肛裂",
        "syndrome_code": "GL_XRCZ",
        "template_name": "血热肠燥型（典型）",
        "description": "便后剧痛、便血鲜红、大便干结、舌红苔黄",
        "symptoms_data": {
            "pain": {"present": True, "degree": "剧烈", "nature": "刺痛", "timing": "便后持续"},
            "bleeding": {"present": True, "color": "鲜红", "timing": "便时"},
            "stool_condition": "干结",
            "urination": "短赤",
            "thirst": "口渴喜冷饮",
            "tongue_color": "红",
            "tongue_coating": "黄",
            "pulse_rapid": True,
            "sphincter": "痉挛"
        }
    },
    {
        "disease_type": "肛裂",
        "syndrome_code": "GL_YXJK",
        "template_name": "阴虚津亏型（典型）",
        "description": "便后灼痛、大便干结、口干、舌红少苔、脉细数",
        "symptoms_data": {
            "pain": {"present": True, "degree": "中度", "nature": "灼痛"},
            "stool_condition": "干结",
            "thirst": "口干不欲饮",
            "lumbar_soreness": True,
            "tongue_color": "红",
            "tongue_coating": "少苔",
            "pulse_fine": True,
            "pulse_rapid": True
        }
    },
    {
        "disease_type": "肛周脓肿",
        "syndrome_code": "GZ_RTYJ",
        "template_name": "热毒蕴结型（典型）",
        "description": "肛周红肿热痛、高热、舌红苔黄腻、脉洪数",
        "symptoms_data": {
            "pain": {"present": True, "degree": "剧烈", "nature": "跳痛"},
            "anal_swelling": "重度",
            "anal_color": "鲜红",
            "fever": "高热",
            "odor": "恶臭",
            "thirst": "口渴喜冷饮",
            "urination": "短赤",
            "tongue_color": "红",
            "tongue_coating": "黄腻",
            "pulse_rapid": True,
            "pulse_surging": True
        }
    },
    {
        "disease_type": "直肠脱垂",
        "syndrome_code": "ZC_ZQXX",
        "template_name": "中气下陷型（典型）",
        "description": "直肠脱出、神疲乏力、食欲不振、舌淡脉虚",
        "symptoms_data": {
            "prolapse_symptom": {"present": True, "degree": "III度"},
            "fatigue": True,
            "poor_appetite": True,
            "stool_condition": "溏泄",
            "pale_complexion": True,
            "lumbar_soreness": True,
            "tongue_color": "淡红",
            "tongue_coating": "薄白",
            "pulse_weak": True
        }
    }
]


async def seed_templates():
    """导入症状模板数据"""
    async with async_session_maker() as session:
        print("开始导入症状模板...")

        # 清除旧数据
        from sqlalchemy import delete
        await session.execute(delete(SymptomTemplate).where(SymptomTemplate.template_type == "system"))
        await session.commit()
        print("✅ 旧模板数据清理完成")

        # 导入新模板
        template_count = 0
        for tpl_data in SYSTEM_TEMPLATES:
            template = SymptomTemplate(
                id=uuid.uuid4(),
                tenant_id=None,  # 系统模板
                created_by=None,
                disease_type=tpl_data["disease_type"],
                syndrome_code=tpl_data["syndrome_code"],
                template_name=tpl_data["template_name"],
                description=tpl_data["description"],
                symptoms_data=tpl_data["symptoms_data"],
                template_type="system",
                usage_count=0,
                is_active=1
            )
            session.add(template)
            template_count += 1

        await session.commit()
        print(f"✅ 成功导入 {template_count} 个症状模板")

        # 按病种统计
        by_disease = {}
        for tpl in SYSTEM_TEMPLATES:
            disease = tpl["disease_type"]
            by_disease[disease] = by_disease.get(disease, 0) + 1

        for disease, count in by_disease.items():
            print(f"  - {disease}: {count}个模板")

        print("\n🎉 症状模板导入完成！")


if __name__ == "__main__":
    asyncio.run(seed_templates())
