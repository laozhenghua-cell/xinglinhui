"""
用药安全规则数据种子 - 十八反、十九畏、妊娠禁忌、剂量上限
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models import SafetyRule
import uuid

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://zhilou_user:Zhilou2024!@db:5432/zhilou_clinic")
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


SAFETY_RULES_DATA = []

# 十八反规则
EIGHTEEN_INCOMPATIBILITIES = {
    "甘草": ["甘遂", "大戟", "海藻", "芫花"],
    "乌头": ["贝母", "瓜蒌", "半夏", "白蔹", "白及"],
    "藜芦": ["人参", "沙参", "丹参", "玄参", "细辛", "芍药"],
}

for herb, conflicts in EIGHTEEN_INCOMPATIBILITIES.items():
    SAFETY_RULES_DATA.append({
        "rule_type": "incompatibility",
        "severity": "critical",
        "herb_name": herb,
        "conflicting_herbs": conflicts,
        "contraindication_info": {"type": "十八反", "description": "中药配伍大忌"},
        "warning_message": f"{herb} 与 {', '.join(conflicts)} 相反，属于十八反配伍禁忌，严禁同用！",
        "suggestion": f"必须去除 {herb} 或 {', '.join(conflicts)} 之一"
    })

# 十九畏规则
NINETEEN_FEARS = {
    "硫黄": ["朴硝"],
    "水银": ["砒霜"],
    "狼毒": ["密陀僧"],
    "巴豆": ["牵牛子"],
    "丁香": ["郁金"],
    "牙硝": ["三棱"],
    "川乌": ["犀角"],
    "草乌": ["犀角"],
    "人参": ["五灵脂"],
    "官桂": ["石脂"],
}

for herb, fears in NINETEEN_FEARS.items():
    SAFETY_RULES_DATA.append({
        "rule_type": "incompatibility",
        "severity": "warning",
        "herb_name": herb,
        "conflicting_herbs": fears,
        "contraindication_info": {"type": "十九畏", "description": "中药配伍警戒"},
        "warning_message": f"{herb} 畏 {', '.join(fears)}，不宜同用",
        "suggestion": "建议分开使用或调整方剂"
    })

# 妊娠禁忌规则
PREGNANCY_STRICT = [
    "麝香", "斑蝥", "天雄", "巴豆", "牵牛子", "大戟", "芫花", "甘遂",
    "商陆", "蜈蚣", "水蛭", "虻虫", "三棱", "莪术", "水银", "砒霜",
    "雄黄", "轻粉"
]

for herb in PREGNANCY_STRICT:
    SAFETY_RULES_DATA.append({
        "rule_type": "pregnancy",
        "severity": "critical",
        "herb_name": herb,
        "conflicting_herbs": None,
        "contraindication_info": {"level": "严格禁用", "population": "孕妇"},
        "warning_message": f"孕妇严格禁用：{herb}",
        "suggestion": "必须更换其他药物"
    })

PREGNANCY_CAUTION = [
    "桃仁", "红花", "牛膝", "大黄", "枳实", "附子", "肉桂", "干姜",
    "半夏", "南星", "通草", "瞿麦", "木通", "薏苡仁", "代赭石",
    "芒硝", "牡丹皮", "茜草", "苏木", "刘寄奴", "益母草", "茺蔚子"
]

for herb in PREGNANCY_CAUTION:
    SAFETY_RULES_DATA.append({
        "rule_type": "pregnancy",
        "severity": "warning",
        "herb_name": herb,
        "conflicting_herbs": None,
        "contraindication_info": {"level": "慎用", "population": "孕妇"},
        "warning_message": f"孕妇慎用：{herb}",
        "suggestion": "请谨慎使用，密切观察"
    })

# 剂量上限规则
DOSAGE_LIMITS = [
    {"herb": "附子", "max": 15, "typical": 6, "warning": "大剂量需久煎60分钟以上，防乌头碱中毒"},
    {"herb": "细辛", "max": 3, "typical": 1, "warning": "细辛不过钱（3克），过量可致呼吸抑制"},
    {"herb": "马钱子", "max": 0.6, "typical": 0.3, "warning": "剧毒药，需炮制，过量致惊厥"},
    {"herb": "川乌", "max": 6, "typical": 3, "warning": "需先煎30-60分钟，生川乌禁用"},
    {"herb": "草乌", "max": 6, "typical": 3, "warning": "需先煎30-60分钟，生草乌禁用"},
    {"herb": "大黄", "max": 15, "typical": 6, "warning": "大剂量致泻，孕妇慎用"},
    {"herb": "芒硝", "max": 15, "typical": 10, "warning": "后下或冲服，孕妇禁用"},
    {"herb": "巴豆", "max": 0.3, "typical": 0.1, "warning": "峻下药，去油用，孕妇禁用"},
    {"herb": "甘遂", "max": 1.5, "typical": 0.5, "warning": "峻下逐水药，醋炙用"},
    {"herb": "芫花", "max": 6, "typical": 3, "warning": "峻下逐水药，醋炙用"},
    {"herb": "商陆", "max": 6, "typical": 3, "warning": "有毒，需炮制"},
    {"herb": "雄黄", "max": 1.5, "typical": 0.3, "warning": "外用为主，内服需微量"},
    {"herb": "轻粉", "max": 0.3, "typical": 0.1, "warning": "含汞，外用为主"},
    {"herb": "朱砂", "max": 1, "typical": 0.3, "warning": "含汞，不入煎剂，冲服"},
]

for dosage_data in DOSAGE_LIMITS:
    SAFETY_RULES_DATA.append({
        "rule_type": "dosage",
        "severity": "critical",
        "herb_name": dosage_data["herb"],
        "conflicting_herbs": None,
        "contraindication_info": {
            "max_dosage": dosage_data["max"],
            "typical_dosage": dosage_data["typical"],
            "unit": "克/日"
        },
        "max_dosage": dosage_data["max"],
        "warning_message": f"{dosage_data['herb']} 最大安全剂量 {dosage_data['max']}克/日（常用量 {dosage_data['typical']}克）",
        "suggestion": dosage_data["warning"]
    })


async def seed_safety_rules():
    """导入用药安全规则数据"""
    async with async_session_maker() as session:
        print("开始导入用药安全规则...")

        # 清除旧数据
        from sqlalchemy import delete
        await session.execute(delete(SafetyRule))
        await session.commit()
        print("✅ 旧安全规则数据清理完成")

        # 导入新规则
        rule_count = 0
        for rule_data in SAFETY_RULES_DATA:
            rule = SafetyRule(
                id=uuid.uuid4(),
                rule_type=rule_data["rule_type"],
                severity=rule_data["severity"],
                herb_name=rule_data["herb_name"],
                conflicting_herbs=rule_data["conflicting_herbs"],
                contraindication_info=rule_data["contraindication_info"],
                max_dosage=rule_data.get("max_dosage"),
                warning_message=rule_data["warning_message"],
                suggestion=rule_data["suggestion"],
                is_active=1
            )
            session.add(rule)
            rule_count += 1

        await session.commit()
        print(f"✅ 成功导入 {rule_count} 条安全规则")

        # 按类型统计
        by_type = {}
        for rule in SAFETY_RULES_DATA:
            rule_type = rule["rule_type"]
            by_type[rule_type] = by_type.get(rule_type, 0) + 1

        type_names = {
            "incompatibility": "配伍禁忌",
            "pregnancy": "妊娠禁忌",
            "dosage": "剂量限制"
        }

        for rule_type, count in by_type.items():
            print(f"  - {type_names.get(rule_type, rule_type)}: {count}条")

        print("\n🎉 用药安全规则导入完成！")


if __name__ == "__main__":
    asyncio.run(seed_safety_rules())
