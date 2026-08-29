"""
外治法数据导入脚本
补充经验外治方（熏洗方、外敷方、栓剂）
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.external_treatment import ExternalTreatment
import uuid


# 外治法方剂
ZHOU_EXTERNAL_TREATMENTS = [
    # 1. 消肿止痛洗剂（经验熏洗方）
    {
        "id": str(uuid.uuid4()),
        "name": "消肿止痛洗剂",
        "treatment_type": "fumigation",
        "composition": [
            {"name": "瓦松", "dosage": 30, "unit": "g"},
            {"name": "五倍子", "dosage": 30, "unit": "g"},
            {"name": "马齿苋", "dosage": 30, "unit": "g"},
            {"name": "艾叶", "dosage": 30, "unit": "g"},
            {"name": "川椒", "dosage": 30, "unit": "g"}
        ],
        "preparation": "上药加水2000ml，煎煮20分钟，滤取药液约1000ml",
        "usage": "先熏后洗：趁热熏蒸肛门10分钟，待温度适宜后坐浴20分钟",
        "frequency": "每日1-2次",
        "duration": "7-14天为1疗程",
        "function": "清热解毒，活血祛瘀，利湿软坚，消肿止痛",
        "indications": "外痔发炎、血栓外痔、内痔脱出嵌顿、术后水肿疼痛、肛周脓肿术后",
        "syndrome_types": ["湿热下注型", "湿热瘀滞型", "气滞血瘀型"],
        "disease_types": ["痔疮", "血栓外痔", "肛周脓肿", "术后恢复"],
        "contraindications": "孕妇慎用；开放性创面较大者慎用",
        "precautions": "1. 水温以40-45℃为宜，避免烫伤；2. 熏洗后保持肛周清洁干燥；3. 每次用药液不重复使用",
        "source": "经验方",
        "priority": 100,
        "notes": "强调：此方为外痔、术后必用熏洗方，消肿止痛效果显著"
    },

    # 2. 朴硝马齿苋熏洗方（常用熏洗方）
    {
        "id": str(uuid.uuid4()),
        "name": "朴硝马齿苋熏洗方",
        "treatment_type": "fumigation",
        "composition": [
            {"name": "朴硝", "dosage": 30, "unit": "g"},
            {"name": "马齿苋", "dosage": 20, "unit": "g"},
            {"name": "瓦松", "dosage": 15, "unit": "g"},
            {"name": "归尾", "dosage": 15, "unit": "g"},
            {"name": "赤芍", "dosage": 15, "unit": "g"},
            {"name": "黄柏", "dosage": 15, "unit": "g"},
            {"name": "苍术", "dosage": 15, "unit": "g"}
        ],
        "preparation": "上药加水2000ml，煎煮20分钟，滤取药液，加入朴硝溶化",
        "usage": "先熏后洗，每次20-30分钟",
        "frequency": "每日2次",
        "duration": "连续使用至症状缓解",
        "function": "清热解毒，活血祛瘀，利湿软坚，消肿止痛",
        "indications": "混合痔急性发作、血栓外痔、内痔嵌顿、术后早期",
        "syndrome_types": ["湿热下注型", "湿热瘀滞型"],
        "disease_types": ["混合痔", "血栓外痔", "内痔嵌顿"],
        "contraindications": "术后大出血者禁用",
        "precautions": "朴硝易吸潮，应密封保存；熏洗水温适宜",
        "source": "临床经验",
        "priority": 95,
        "notes": "常用此方治疗急性期痔疮发作"
    },

    # 3. 四黄膏（外敷方）
    {
        "id": str(uuid.uuid4()),
        "name": "四黄膏",
        "treatment_type": "ointment",
        "composition": [
            {"name": "黄连", "dosage": 30, "unit": "g"},
            {"name": "黄芩", "dosage": 30, "unit": "g"},
            {"name": "黄柏", "dosage": 30, "unit": "g"},
            {"name": "栀子", "dosage": 30, "unit": "g"},
            {"name": "凡士林", "dosage": 500, "unit": "g", "note": "基质"}
        ],
        "preparation": "1. 四黄药材研成细粉；2. 与凡士林充分混合调匀成膏状；3. 装入容器密封备用",
        "usage": "清洁患处后，取适量药膏均匀涂抹于患处，厚度约2-3mm，用纱布覆盖固定",
        "frequency": "每日2-3次",
        "duration": "连续使用至症状缓解",
        "function": "清热消肿，凉血止痛，解毒敛疮",
        "indications": "内痔外痔发炎、水肿、术后疼痛、肛周湿疹",
        "syndrome_types": ["实热内蕴型", "湿热下注型"],
        "disease_types": ["痔疮", "肛周湿疹", "术后水肿"],
        "contraindications": "皮肤破损渗液较多者慎用",
        "precautions": "1. 涂药前清洁患处；2. 避免沾染内裤；3. 过敏者停用",
        "source": "传统方",
        "priority": 90,
        "notes": "经典外敷方，清热消肿效果好"
    },

    # 4. 玉红膏（生肌膏）
    {
        "id": str(uuid.uuid4()),
        "name": "玉红膏",
        "treatment_type": "ointment",
        "composition": [
            {"name": "白芷", "dosage": 15, "unit": "g"},
            {"name": "甘草", "dosage": 12, "unit": "g"},
            {"name": "归身", "dosage": 6, "unit": "g"},
            {"name": "白蜡", "dosage": 12, "unit": "g"},
            {"name": "轻粉", "dosage": 12, "unit": "g"},
            {"name": "血竭", "dosage": 12, "unit": "g"},
            {"name": "紫草", "dosage": 6, "unit": "g"},
            {"name": "麻油", "dosage": 500, "unit": "ml", "note": "基质"}
        ],
        "preparation": "传统炼制法：白芷等药入麻油炸枯去渣，下白蜡，离火后入轻粉、血竭等细粉，搅匀成膏",
        "usage": "清洁创面后，取适量药膏涂抹，或用药纱覆盖",
        "frequency": "每日1-2次",
        "duration": "使用至创面愈合",
        "function": "活血化瘀，解毒生肌，消肿止痛",
        "indications": "肛瘘术后、痔疮术后、创面肉芽生长期",
        "syndrome_types": ["气血两虚型", "瘀血阻滞型"],
        "disease_types": ["肛瘘", "痔疮术后", "慢性溃疡"],
        "contraindications": "感染化脓期不宜用",
        "precautions": "经验：待腐脱管化后使用，促进创面愈合，防止假愈合",
        "source": "《外科正宗》",
        "priority": 85,
        "notes": "术后换药规律：初时宜重化腐，待腐脱管化改用玉红膏生肌"
    },

    # 5. 地槐止血丸（经验方）
    {
        "id": str(uuid.uuid4()),
        "name": "地槐止血丸",
        "treatment_type": "suppository",
        "composition": [
            {"name": "地榆炭", "dosage": 60, "unit": "g"},
            {"name": "槐角", "dosage": 120, "unit": "g"},
            {"name": "防风", "dosage": 60, "unit": "g"},
            {"name": "黄柏", "dosage": 60, "unit": "g"}
        ],
        "preparation": "上药共研细末，炼蜜为丸，每丸重9g",
        "usage": "口服，每次1丸，每日2-3次，温开水送服",
        "frequency": "每日2-3次",
        "duration": "连服7-14天",
        "function": "清利湿热，止血通便，消肿止痛",
        "indications": "各期内痔出血、混合痔出血、便血日久",
        "syndrome_types": ["湿热下注型", "实热内蕴型"],
        "disease_types": ["痔疮", "便血"],
        "contraindications": "孕妇禁用；脾胃虚寒便溏者慎用",
        "precautions": "服药期间忌食辛辣刺激食物",
        "source": "经验方",
        "priority": 88,
        "notes": "经验方，对痔疮出血效果显著"
    },

    # 6. 复方痔疮栓（经验方）
    {
        "id": str(uuid.uuid4()),
        "name": "复方痔疮栓",
        "treatment_type": "suppository",
        "composition": [
            {"name": "地榆粉", "dosage": 20, "unit": "g"},
            {"name": "黄柏粉", "dosage": 10, "unit": "g"},
            {"name": "次没食子酸铋", "dosage": 10, "unit": "g"},
            {"name": "仙鹤草素", "dosage": 6, "unit": "片"},
            {"name": "地卡因", "dosage": 0.7, "unit": "g"},
            {"name": "冰片", "dosage": 0.7, "unit": "g"}
        ],
        "preparation": "上药混合均匀，加入可可豆脂或半合成脂肪酸甘油酯为基质，制成栓剂，每粒约2g",
        "usage": "每晚临睡前排空大便后，将栓剂纳入肛内",
        "frequency": "每晚1-2枚",
        "duration": "连续使用7-14天",
        "function": "消炎止血，止痛收敛，清热解毒",
        "indications": "各期内痔出血、肛窦炎、肛裂出血疼痛、混合痔",
        "syndrome_types": ["湿热下注型", "实热内蕴型", "血热肠燥型"],
        "disease_types": ["内痔", "肛裂", "肛窦炎", "混合痔"],
        "contraindications": "肛门外部病变不宜用；孕妇慎用",
        "precautions": "1. 纳入后保持卧位10分钟；2. 次日可能有少量药渣排出属正常；3. 地卡因过敏者禁用",
        "source": "经验方",
        "priority": 92,
        "notes": "经验方，对内痔出血、肛裂疼痛效果显著"
    },

    # 7. 明矾液注射疗法（创新疗法）
    {
        "id": str(uuid.uuid4()),
        "name": "4%明矾液注射疗法",
        "treatment_type": "injection",
        "composition": [
            {"name": "明矾", "dosage": 4, "unit": "g"},
            {"name": "注射用水", "dosage": 100, "unit": "ml"}
        ],
        "preparation": "明矾4g溶于100ml注射用水中，煮沸消毒，冷却后备用",
        "usage": "I-II期内痔：痔核基底部注射2-5ml；完全性直肠脱垂：6%明矾液于直肠黏膜下多点注射",
        "frequency": "每个痔核或脱垂注射点1次，间隔7-14天可重复",
        "duration": "根据病情决定，一般1-3次",
        "function": "酸可收敛，涩可固脱，使痔核萎缩硬化",
        "indications": "I-II期内痔、完全性直肠脱垂",
        "syndrome_types": ["脾虚气陷型", "气血亏损型"],
        "disease_types": ["I-II期内痔", "直肠脱垂"],
        "contraindications": "III-IV期内痔、血栓外痔、肛周脓肿、孕妇禁用",
        "precautions": "1. 严格无菌操作；2. 注射层次准确（黏膜下层）；3. 避免注射过浅或过深；4. 术后观察有无出血、感染",
        "source": "1959年创新疗法",
        "priority": 75,
        "notes": "首创明矾注射疗法，1981年治疗成人完全性直肠脱垂全愈率99.5%"
    },

    # 8. 高锰酸钾坐浴液
    {
        "id": str(uuid.uuid4()),
        "name": "高锰酸钾坐浴液",
        "treatment_type": "fumigation",
        "composition": [
            {"name": "高锰酸钾", "dosage": 0.1, "unit": "g"},
            {"name": "温开水", "dosage": 1000, "unit": "ml"}
        ],
        "preparation": "取高锰酸钾0.1g溶于1000ml温开水中，配成1:10000溶液（淡紫红色）",
        "usage": "坐浴，每次15-20分钟",
        "frequency": "每日1-2次",
        "duration": "连续使用至症状缓解",
        "function": "消毒杀菌，清洁创面，促进愈合",
        "indications": "痔疮术后、肛瘘术后、肛周感染、保持肛周清洁",
        "syndrome_types": ["通用"],
        "disease_types": ["术后护理", "肛周感染", "痔疮", "肛瘘"],
        "contraindications": "浓度过高会灼伤皮肤",
        "precautions": "1. 浓度不宜过高，以淡紫红色为宜；2. 现配现用，久置失效；3. 水温40℃左右",
        "source": "现代常规疗法",
        "priority": 70,
        "notes": "术后常规坐浴方法，简便有效"
    }
]


async def seed_external_treatments():
    """导入外治法"""
    async with AsyncSessionLocal() as session:
        print("="*60)
        print("外治法补充脚本")
        print("="*60)

        count = 0
        for treatment in ZHOU_EXTERNAL_TREATMENTS:
            # 检查是否已存在
            stmt = select(ExternalTreatment).where(
                ExternalTreatment.name == treatment["name"]
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                print(f"⚠️  外治法已存在，跳过：{treatment['name']}")
                continue

            # 创建新外治法
            new_treatment = ExternalTreatment(**treatment)
            session.add(new_treatment)
            count += 1
            print(f"✅ 新增外治法：{treatment['name']} ({treatment['treatment_type']})")

        await session.commit()
        print(f"\n🎉 外治法导入完成！")
        print(f"📊 新增外治法数量：{count}")

        # 统计总数
        stmt = select(ExternalTreatment)
        result = await session.execute(stmt)
        total = len(result.scalars().all())
        print(f"📊 系统总外治法数量：{total}")


if __name__ == "__main__":
    asyncio.run(seed_external_treatments())
