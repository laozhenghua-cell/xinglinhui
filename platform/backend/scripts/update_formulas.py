"""
更新方剂数据 - 补充完整的组成、加减、注意事项
"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from app.database import AsyncSessionLocal
from app.models.knowledge import AnorectalFormula


# 完整方剂数据
FORMULAS_UPDATE = [
    {
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
        "usage": "水煎服，日1剂，分2-3次温服",
        "modifications": "便秘严重：加大黄10g、芒硝6g（后下）；疼痛剧烈：加延胡索10g、川楝子10g；出血量大：加仙鹤草15g、茜草10g",
        "notes": "强调：湿邪为患，必重用利湿之品，故茯苓、车前子、泽泻三药并用"
    },
    {
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
        "usage": "水煎服，日1剂，分2次温服",
        "modifications": "疼痛剧烈：加延胡索10g、乳香6g、没药6g；肿块坚硬：重用三棱、莪术各12g；大便不畅：加大黄6g、厚朴9g",
        "notes": "经验：血栓外痔必用此方，一般3-5剂可见消肿。孕妇禁用（含桃仁、红花、三棱、莪术）"
    },
    {
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
        "usage": "水煎服，日1剂，分2次温服，连服10-15剂",
        "modifications": "便血不止：加仙鹤草20g、血余炭9g；脱肛：加升麻6g、柴胡6g；失眠严重：加夜交藤15g、合欢皮10g",
        "notes": "强调：气血亏损型患者切忌攻伐，必以补益为主，止血为辅"
    },
    {
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
        "usage": "水煎服，日1剂，分2次温服，连服15-20剂",
        "modifications": "脱垂严重：加黄精15g、肉苁蓉12g；失血过多：加阿胶10g（烊化）、龙眼肉12g；便秘：加火麻仁12g、郁李仁10g",
        "notes": "强调：III度脱垂患者必用此方打底，不可单纯升提"
    },
    {
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
        "usage": "水煎服，饴糖烊化兑入，日1剂，分2次温服",
        "modifications": "脱垂严重：加党参15g、黄精12g；腹痛：加白术12g、炙甘草6g；腹泻：加炮姜6g、诃子10g",
        "notes": "经验：脱垂患者必升阳举陷，重用黄芪，配合升麻、柴胡"
    }
]


async def update_formulas():
    print("=" * 60)
    print("更新方剂详细数据")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        updated_count = 0

        for formula_data in FORMULAS_UPDATE:
            # 查找现有方剂
            result = await db.execute(
                select(AnorectalFormula).where(
                    AnorectalFormula.name == formula_data["name"]
                )
            )
            formula = result.scalar_one_or_none()

            if formula:
                # 更新数据
                formula.source = formula_data.get("source", formula.source)
                formula.composition = formula_data["composition"]
                formula.function = formula_data.get("function", formula.function)
                formula.indications = formula_data.get("indications", formula.indications)
                formula.usage = formula_data.get("usage", formula.usage)
                formula.modifications = formula_data.get("modifications")
                formula.notes = formula_data.get("notes")

                updated_count += 1
                print(f"✅ 已更新：{formula_data['name']}")
            else:
                print(f"⚠️  方剂不存在：{formula_data['name']}")

        await db.commit()
        print(f"\n🎉 更新完成！共更新 {updated_count} 个方剂")


if __name__ == "__main__":
    asyncio.run(update_formulas())
