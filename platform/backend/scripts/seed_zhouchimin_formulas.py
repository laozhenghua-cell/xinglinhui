"""
核心方剂补充脚本
补充10首常用经验方
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.knowledge import AnorectalFormula
import uuid


# 10首核心方剂
ZHOU_FORMULAS = [
    # 1. 五神汤加味（治疗湿热瘀滞型痔疮首选）
    {
        "id": str(uuid.uuid4()),
        "name": "五神汤加味",
        "source": "经验方",
        "composition": [
            {"name": "茯苓", "dosage": 15, "unit": "g"},
            {"name": "赤芍", "dosage": 12, "unit": "g"},
            {"name": "车前子", "dosage": 12, "unit": "g", "note": "包煎"},
            {"name": "泽泻", "dosage": 10, "unit": "g"},
            {"name": "牡丹皮", "dosage": 10, "unit": "g"},
            {"name": "黄柏", "dosage": 9, "unit": "g"},
            {"name": "地榆", "dosage": 15, "unit": "g"},
            {"name": "槐花", "dosage": 12, "unit": "g"}
        ],
        "function": "清热利湿，活血化瘀，凉血止血",
        "indications": "湿热瘀滞型痔疮、血栓外痔、嵌顿性内痔。证见：肿痛并重，便血鲜红，肛门坠胀，大便干结，舌红苔黄腻，脉滑数",
        "syndrome_type": "湿热瘀滞型",
        "disease_types": ["痔疮", "血栓外痔", "嵌顿痔"],
        "modifications": "便秘严重：加大黄10g、芒硝6g（后下）；疼痛剧烈：加延胡索10g、川楝子10g；出血量大：加仙鹤草15g、茜草10g",
        "usage": "水煎服，日1剂，分2-3次温服",
        "formula_type": "internal",
        "notes": "强调：湿邪为患，必重用利湿之品，故茯苓、车前子、泽泻三药并用"
    },

    # 2. 活血散瘀汤（治疗血瘀型痔疮）
    {
        "id": str(uuid.uuid4()),
        "name": "活血散瘀汤",
        "source": "经验方",
        "composition": [
            {"name": "当归", "dosage": 12, "unit": "g"},
            {"name": "赤芍", "dosage": 10, "unit": "g"},
            {"name": "桃仁", "dosage": 9, "unit": "g"},
            {"name": "红花", "dosage": 6, "unit": "g"},
            {"name": "川芎", "dosage": 6, "unit": "g"},
            {"name": "三棱", "dosage": 9, "unit": "g"},
            {"name": "莪术", "dosage": 9, "unit": "g"},
            {"name": "枳壳", "dosage": 10, "unit": "g"},
            {"name": "槐花", "dosage": 12, "unit": "g"}
        ],
        "function": "活血化瘀，行气止痛",
        "indications": "气滞血瘀型痔疮、血栓外痔、术后肿痛不消。证见：肛门肿块青紫，疼痛刺痛，大便干结，舌暗有瘀斑，脉涩",
        "syndrome_type": "气滞血瘀型",
        "disease_types": ["痔疮", "血栓外痔"],
        "modifications": "疼痛剧烈：加延胡索10g、乳香6g、没药6g；肿块坚硬：重用三棱、莪术各12g；大便不畅：加大黄6g、厚朴9g",
        "usage": "水煎服，日1剂，分2次温服",
        "formula_type": "internal",
        "notes": "经验：血栓外痔必用此方，一般3-5剂可见消肿。孕妇禁用（含桃仁、红花、三棱、莪术）"
    },

    # 3. 归脾汤加味（治疗气血亏损型）
    {
        "id": str(uuid.uuid4()),
        "name": "归脾汤加味",
        
        
        "source": "《济生方》加减",
        "composition": [
            {"name": "黄芪", "dosage": 30, "unit": "g"},
            {"name": "党参", "dosage": 15, "unit": "g"},
            {"name": "白术", "dosage": 12, "unit": "g"},
            {"name": "茯神", "dosage": 12, "unit": "g"},
            {"name": "当归", "dosage": 10, "unit": "g"},
            {"name": "龙眼肉", "dosage": 10, "unit": "g"},
            {"name": "酸枣仁", "dosage": 12, "unit": "g"},
            {"name": "远志", "dosage": 6, "unit": "g"},
            {"name": "木香", "dosage": 6, "unit": "g"},
            {"name": "地榆炭", "dosage": 15, "unit": "g"},
            {"name": "槐花", "dosage": 10, "unit": "g"}
        ],
        "function": "补气养血，健脾止血",
        "indications": "便血色淡，神疲乏力，面色苍白，头晕心悸，纳差便溏，舌淡苔薄，脉细弱",
        "modifications": "便血不止：加仙鹤草20g、血余炭9g；脱肛：加升麻6g、柴胡6g；失眠严重：加夜交藤15g、合欢皮10g",
        "usage": "水煎服，日1剂，分2次温服，连服10-15剂",
        "notes": "强调：气血亏损型患者切忌攻伐，必以补益为主，止血为辅"
    },

    # 4. 黄芪建中汤加味（治疗脾虚气陷型）
    {
        "id": str(uuid.uuid4()),
        "name": "黄芪建中汤加味",
        
        
        "source": "《金匮要略》加减",
        "composition": [
            {"name": "黄芪", "dosage": 30, "unit": "g"},
            {"name": "桂枝", "dosage": 9, "unit": "g"},
            {"name": "白芍", "dosage": 18, "unit": "g"},
            {"name": "生姜", "dosage": 9, "unit": "g"},
            {"name": "大枣", "dosage": 12, "unit": "g"},
            {"name": "饴糖", "dosage": 30, "unit": "g", "note": "烊化"},
            {"name": "升麻", "dosage": 6, "unit": "g"},
            {"name": "柴胡", "dosage": 6, "unit": "g"},
            {"name": "枳壳", "dosage": 10, "unit": "g"}
        ],
        "function": "温中补虚，升阳举陷",
        "indications": "脱肛，气短乏力，面色萎黄，纳差便溏，舌淡苔白，脉细弱",
        "modifications": "脱垂严重：加党参15g、黄精12g；腹痛：加白术12g、炙甘草6g；腹泻：加炮姜6g、诃子10g",
        "usage": "水煎服，饴糖烊化兑入，日1剂，分2次温服",
        "notes": "经验：脱垂患者必升阳举陷，重用黄芪，配合升麻、柴胡"
    },

    # 5. 八珍汤加味（治疗气血两虚型脱垂）
    {
        "id": str(uuid.uuid4()),
        "name": "八珍汤加味",
        
        
        "source": "《瑞竹堂经验方》加减",
        "composition": [
            {"name": "党参", "dosage": 15, "unit": "g"},
            {"name": "白术", "dosage": 12, "unit": "g"},
            {"name": "茯苓", "dosage": 12, "unit": "g"},
            {"name": "甘草", "dosage": 6, "unit": "g"},
            {"name": "当归", "dosage": 12, "unit": "g"},
            {"name": "川芎", "dosage": 9, "unit": "g"},
            {"name": "白芍", "dosage": 12, "unit": "g"},
            {"name": "熟地黄", "dosage": 15, "unit": "g"},
            {"name": "黄芪", "dosage": 30, "unit": "g"},
            {"name": "升麻", "dosage": 6, "unit": "g"},
            {"name": "柴胡", "dosage": 6, "unit": "g"}
        ],
        "function": "益气养血，升阳举陷",
        "indications": "脱垂严重，神疲乏力，面色苍白，心悸气短，舌淡脉细弱",
        "modifications": "脱垂严重：加黄精15g、肉苁蓉12g；失血过多：加阿胶10g（烊化）、龙眼肉12g；便秘：加火麻仁12g、郁李仁10g",
        "usage": "水煎服，日1剂，分2次温服，连服15-20剂",
        "notes": "强调：III度脱垂患者必用此方打底，不可单纯升提"
    },

    # 6. 当归连翘汤（治疗肛周脓肿初期）
    {
        "id": str(uuid.uuid4()),
        "name": "当归连翘汤",
        
        
        "source": "经验方",
        "composition": [
            {"name": "当归", "dosage": 15, "unit": "g"},
            {"name": "连翘", "dosage": 15, "unit": "g"},
            {"name": "金银花", "dosage": 20, "unit": "g"},
            {"name": "赤芍", "dosage": 12, "unit": "g"},
            {"name": "牡丹皮", "dosage": 10, "unit": "g"},
            {"name": "黄芩", "dosage": 10, "unit": "g"},
            {"name": "栀子", "dosage": 9, "unit": "g"},
            {"name": "大黄", "dosage": 6, "unit": "g", "note": "后下"},
            {"name": "皂角刺", "dosage": 12, "unit": "g"},
            {"name": "甘草", "dosage": 6, "unit": "g"}
        ],
        "function": "清热解毒，消肿散结，活血止痛",
        "indications": "肛周红肿热痛，发热恶寒，大便秘结，舌红苔黄，脉洪数",
        "modifications": "发热高：加生石膏30g（先煎）、知母10g；疼痛剧烈：加乳香6g、没药6g；便秘严重：重用大黄10g",
        "usage": "水煎服，日1剂，分3次温服",
        "notes": "经验：脓肿初期用此方可促进吸收消散，避免手术"
    },

    # 7. 凉血地黄汤（治疗血热肠燥型肛裂）
    {
        "id": str(uuid.uuid4()),
        "name": "凉血地黄汤",
        
        
        "source": "《医宗金鉴》加减",
        "composition": [
            {"name": "生地黄", "dosage": 20, "unit": "g"},
            {"name": "玄参", "dosage": 15, "unit": "g"},
            {"name": "麦冬", "dosage": 12, "unit": "g"},
            {"name": "丹皮", "dosage": 10, "unit": "g"},
            {"name": "赤芍", "dosage": 10, "unit": "g"},
            {"name": "黄芩", "dosage": 9, "unit": "g"},
            {"name": "栀子", "dosage": 9, "unit": "g"},
            {"name": "当归", "dosage": 10, "unit": "g"},
            {"name": "火麻仁", "dosage": 15, "unit": "g"},
            {"name": "甘草", "dosage": 6, "unit": "g"}
        ],
        "function": "凉血清热，养阴润燥",
        "indications": "肛裂疼痛剧烈，便血鲜红，大便干结如羊屎，口干咽燥，舌红少津，脉细数",
        "modifications": "疼痛剧烈：加白芍15g、甘草9g缓急止痛；便秘严重：加瓜蒌仁15g、郁李仁10g；阴虚明显：加石斛12g、天花粉10g",
        "usage": "水煎服，日1剂，分2次温服",
        "notes": "强调：肛裂必润，不可峻攻"
    },

    # 8. 止痛如神汤（治疗疼痛剧烈者）
    {
        "id": str(uuid.uuid4()),
        "name": "止痛如神汤",
        
        
        "source": "《兰室秘藏》加减",
        "composition": [
            {"name": "秦艽", "dosage": 15, "unit": "g"},
            {"name": "当归", "dosage": 12, "unit": "g"},
            {"name": "白芍", "dosage": 15, "unit": "g"},
            {"name": "川芎", "dosage": 9, "unit": "g"},
            {"name": "延胡索", "dosage": 10, "unit": "g"},
            {"name": "川楝子", "dosage": 10, "unit": "g"},
            {"name": "黄柏", "dosage": 9, "unit": "g"},
            {"name": "泽泻", "dosage": 12, "unit": "g"},
            {"name": "防风", "dosage": 6, "unit": "g"},
            {"name": "甘草", "dosage": 6, "unit": "g"}
        ],
        "function": "清热祛湿，活血止痛",
        "indications": "肛门剧痛，坐卧不安，大便时疼痛加剧",
        "modifications": "热象明显：加黄芩10g、栀子9g；血瘀明显：加桃仁9g、红花6g；便秘：加大黄6g（后下）",
        "usage": "水煎服，日1剂，分3次温服",
        "notes": "经验：疼痛剧烈者必用此方，止痛效果显著"
    },

    # 9. 内疏黄连汤（治疗湿热下注型）
    {
        "id": str(uuid.uuid4()),
        "name": "内疏黄连汤",
        
        
        "source": "《医宗金鉴》",
        "composition": [
            {"name": "黄连", "dosage": 6, "unit": "g"},
            {"name": "黄芩", "dosage": 10, "unit": "g"},
            {"name": "栀子", "dosage": 9, "unit": "g"},
            {"name": "连翘", "dosage": 15, "unit": "g"},
            {"name": "槐花", "dosage": 12, "unit": "g"},
            {"name": "当归", "dosage": 10, "unit": "g"},
            {"name": "赤芍", "dosage": 10, "unit": "g"},
            {"name": "木香", "dosage": 6, "unit": "g"},
            {"name": "枳壳", "dosage": 10, "unit": "g"},
            {"name": "大黄", "dosage": 6, "unit": "g", "note": "后下"},
            {"name": "甘草", "dosage": 6, "unit": "g"}
        ],
        "function": "清热除湿，活血消肿",
        "indications": "肛门肿痛，局部灼热，便血或脓血，口苦，舌红苔黄腻，脉滑数",
        "modifications": "脓肿：加金银花20g、蒲公英15g；便秘：重用大黄10g；肿痛剧烈：加延胡索10g、乳香6g",
        "usage": "水煎服，日1剂，分2-3次温服",
        "notes": "常用此方治疗急性期湿热证"
    },

    # 10. 青蒿鳖甲汤加减（治疗虚热型脓肿）
    {
        "id": str(uuid.uuid4()),
        "name": "青蒿鳖甲汤加减",
        
        
        "source": "《温病条辨》加减",
        "composition": [
            {"name": "青蒿", "dosage": 12, "unit": "g", "note": "后下"},
            {"name": "鳖甲", "dosage": 15, "unit": "g", "note": "先煎"},
            {"name": "生地黄", "dosage": 15, "unit": "g"},
            {"name": "知母", "dosage": 10, "unit": "g"},
            {"name": "丹皮", "dosage": 10, "unit": "g"},
            {"name": "黄芩", "dosage": 9, "unit": "g"},
            {"name": "金银花", "dosage": 15, "unit": "g"},
            {"name": "连翘", "dosage": 12, "unit": "g"},
            {"name": "当归", "dosage": 10, "unit": "g"},
            {"name": "黄芪", "dosage": 15, "unit": "g"}
        ],
        "function": "清虚热，散毒气，养阴扶正",
        "indications": "脓肿日久不愈，低热缠绵，神疲乏力，盗汗，舌淡苔薄，脉细数",
        "modifications": "阴虚明显：加麦冬12g、石斛12g；气虚明显：重用黄芪30g、加党参15g；盗汗：加浮小麦30g、煅牡蛎20g（先煎）",
        "usage": "水煎服，日1剂，分2次温服",
        "notes": "经验：脓肿日久正虚者必用此方，切忌苦寒攻伐"
    }
]


async def seed_zhou_formulas():
    """导入方剂"""
    async with AsyncSessionLocal() as session:
        print("="*60)
        print("核心方剂补充脚本")
        print("="*60)

        count = 0
        for formula in ZHOU_FORMULAS:
            # 检查是否已存在
            stmt = select(AnorectalFormula).where(AnorectalFormula.name == formula["name"])
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                print(f"⚠️  方剂已存在，跳过：{formula['name']}")
                continue

            # 创建新方剂
            new_formula = AnorectalFormula(**formula)
            session.add(new_formula)
            count += 1
            print(f"✅ 新增方剂：{formula['name']}")

        await session.commit()
        print(f"\n🎉 方剂导入完成！")
        print(f"📊 新增方剂数量：{count}")

        # 统计总数
        stmt = select(AnorectalFormula)
        result = await session.execute(stmt)
        total = len(result.scalars().all())
        print(f"📊 系统总方剂数量：{total}")


if __name__ == "__main__":
    asyncio.run(seed_zhou_formulas())
