"""把《临床经验原文.txt》的证治方与后续扩展方分开保存。

原有方剂中有部分剂量、药味来自医案加减或后续整理。本迁移不删除它们，
而是将原有记录标为“医案/临床扩展方”，再把原文证治方写回同名主记录，
让规则命中的方剂可以逐味追溯到原文行号。
"""
import asyncio
import sys
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import AsyncSessionLocal
from app.models.knowledge import AnorectalFormula


ORIGINAL_FORMULAS = [
    {
        "name": "槐花散加味",
        "source": "原文·证治方（原文第132行）",
        "composition": [("槐花", 12), ("侧柏叶", 10), ("炒荆芥", 10), ("枳壳", 10), ("防风", 10), ("生地", 10), ("地榆", 10), ("仙鹤草", 15), ("麻仁", 9), ("生甘草", 10)],
        "function": "清热润燥，止血通便；兼能清热疏风、和血止血",
        "indications": "湿热内蕴、血热肠燥所致痔疮，见便秘、出血、肛门灼热疼痛；适用于内痔、混合痔、炎性外痔相应证候",
        "usage": "水煎服，日服一剂（具体分服、疗程由医师审核）",
        "modifications": "原文说明可与地榆散加味交替、互相化裁；具体加减须结合复诊四诊资料",
        "notes": "原文证治方；与原文第185行医案方相比，生地剂量不同（证治方10克，医案方15克）。",
    },
    {
        "name": "地榆散加味",
        "source": "原文·证治方（原文第133行）",
        "composition": [("地榆", 12), ("黄芩", 10), ("黄连", 10), ("山栀", 10), ("槐花", 10), ("当归", 12), ("赤小豆", 15), ("丹皮", 10), ("甘草", 6)],
        "function": "清热凉血，止血和血",
        "indications": "实热证、湿热内蕴、血热肠燥所致痔疮便血、肛门灼热疼痛",
        "usage": "水煎服，日服一剂（具体分服、疗程由医师审核）",
        "modifications": "原文说明可与槐花散加味交替、互相化裁；具体加减须结合复诊四诊资料",
        "notes": "原文证治方。数据库中的赤芍、川芎版本另标为医案/临床扩展方，不冒充原文组成。",
    },
    {
        "name": "五神汤加味",
        "source": "原文·证治方（原文第136行）",
        "composition": [("茯苓", 10), ("金银花", 20), ("牛膝", 10), ("车前子", 10), ("地丁", 15), ("黄芩", 10), ("归尾", 10), ("赤芍", 10), ("甘草", 10)],
        "function": "清热除湿，活血化瘀",
        "indications": "湿热瘀滞型痔疮，见腹胀纳呆、便秘溲赤、肛门坠胀疼痛、红肿结节不散；包括血栓外痔、静脉曲张性外痔、嵌顿性内痔相应证候",
        "usage": "水煎服，日服一剂（具体分服、疗程由医师审核）",
        "modifications": "原文说明可与活血散瘀汤交替、互相加减；热象退而瘀滞存时由医师复诊决定转方",
        "notes": "原文证治方；牛夕按现代药名规范记为牛膝，归尾即当归尾。",
    },
    {
        "name": "活血散瘀汤",
        "source": "原文·证治方（原文第137行）",
        "composition": [("归尾", 10), ("赤芍", 10), ("桃仁", 10), ("大黄", 10), ("川芎", 10), ("丹皮", 10), ("枳壳", 10), ("瓜蒌仁", 10), ("槟榔", 10)],
        "function": "清利湿热，消除瘀滞，活血行气",
        "indications": "湿热瘀滞型痔疮，尤其血栓外痔、静脉曲张性外痔、嵌顿性内痔；常用于热象减轻而瘀滞未消的复诊阶段",
        "usage": "水煎服，日服一剂（大黄后下等炮制方法由医师审核）",
        "modifications": "原文说明可与五神汤加味交替、互相加减；原文医案第193行为复诊加减方，须单独复核",
        "notes": "原文证治方；与数据库原有活血化瘀扩展版药味不同，扩展版另存为临床扩展方。",
    },
    {
        "name": "归脾汤加味",
        "source": "原文·证治方（原文第140行）",
        "composition": [("人参", 10), ("黄芪", 10), ("白术", 10), ("茯苓", 10), ("枣仁", 10), ("龙眼肉", 10), ("远志", 10), ("木香", 6), ("甘草", 6), ("灶心土", 80), ("升麻", 10)],
        "function": "健脾温中，固脱止血",
        "indications": "虚寒证痔疮，见身倦神疲、面色晄白、便稀、小便清长、食少腹胀、内痔脱出及晦暗便血",
        "usage": "水煎服，日服一剂；灶心土按医师要求煎汤代水",
        "modifications": "原文说明可与黄芪建中汤加减交替；长期便血、脱出或腹泻需复诊调整",
        "notes": "原文证治方。数据库中的党参、地榆、槐花等版本另标为临床扩展方。",
    },
    {
        "name": "黄芪建中汤加减",
        "source": "原文·证治方（原文第141行）",
        "composition": [("黄芪", 15), ("桂枝", 10), ("白芍", 10), ("白术", 10), ("生姜", 3, "片"), ("大枣", 7, "枚"), ("陈棕炭", 10), ("侧柏叶", 10), ("陈皮", 10), ("甘草", 6)],
        "function": "健脾温中，固气升提，止血止泻",
        "indications": "虚寒证痔疮，内痔脱出严重、长期便血、消化不良或腹泻",
        "usage": "水煎服，日服一剂（具体分服、疗程由医师审核）",
        "modifications": "原文说明可与归脾汤加味交替；白芍、生姜、大枣及陈棕炭等用量须按原文和患者情况审核",
        "notes": "原文写作“黄芪健中汤加减”，系统统一名称为“黄芪建中汤加减”；不与后续温补扩展方混同。",
    },
    {
        "name": "八珍汤",
        "source": "原文·证治方（原文第145行）",
        "composition": [("熟地", 15), ("白芍", 10), ("当归", 10), ("川芎", 10), ("党参", 15), ("白术", 10), ("甘草", 10)],
        "function": "补气益血",
        "indications": "气血亏损型痔疮，便血日久、面色无华、气短心悸、肛门坠重、痔脱难收或血燥便秘",
        "usage": "水煎服，日服一剂（具体分服、疗程由医师审核）",
        "modifications": "原文气血亏损型可与补中益气汤互参；原文医案第197行另为八珍汤加味，须单独复核",
        "notes": "原文证治方；与原文第197行医案加味方药味、剂量不同。",
    },
]


def as_composition(items):
    return [
        {"name": item[0], "dosage": item[1], "unit": item[2] if len(item) > 2 else "g"}
        for item in items
    ]


async def main():
    async with AsyncSessionLocal() as db:
        changed = 0
        for item in ORIGINAL_FORMULAS:
            result = await db.execute(select(AnorectalFormula).where(AnorectalFormula.name == item["name"]))
            rows = result.scalars().all()
            original = next((row for row in rows if (row.source or "").startswith("原文·证治方")), None)
            legacy = next((row for row in rows if row is not original), None)

            # 先保留旧版本，避免历史医案/扩展内容因校正而丢失。
            if legacy and not (legacy.name or "").endswith("（临床扩展方）"):
                legacy.name = f"{item['name']}（临床扩展方）"
                legacy.source = f"{legacy.source or '系统整理'}；非原文证治方，保留供医师复核"
                changed += 1

            if original is None:
                original = AnorectalFormula(name=item["name"])
                db.add(original)
            original.source = item["source"]
            original.composition = as_composition(item["composition"])
            original.function = item["function"]
            original.indications = item["indications"]
            original.usage = item["usage"]
            original.modifications = item["modifications"]
            original.notes = item["notes"]
            original.syndrome_type = "原著证治方"
            original.formula_type = "internal"
            changed += 1
        await db.commit()
        print(f"已校正/新增原文主方 {len(ORIGINAL_FORMULAS)} 首，保留旧扩展版本，变更记录 {changed} 条")


if __name__ == "__main__":
    asyncio.run(main())
