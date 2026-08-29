"""
更新所有痔疮辨证方剂为完整的结构化数据
包含：组成（JSONB数组）、加减化裁、临床经验
"""
import asyncio
from sqlalchemy import select, update
from app.database import AsyncSessionLocal
from app.models.knowledge import AnorectalFormula


# 完整的8个痔疮方剂数据
FORMULAS_DATA = [
    {
        "name": "槐花散加味",
        "source": "经验方",
        "composition": [
            {"name": "槐花", "dosage": 12, "unit": "g"},
            {"name": "侧柏叶", "dosage": 10, "unit": "g"},
            {"name": "炒荆芥", "dosage": 10, "unit": "g"},
            {"name": "枳壳", "dosage": 10, "unit": "g"},
            {"name": "防风", "dosage": 10, "unit": "g"},
            {"name": "生地", "dosage": 15, "unit": "g"},
            {"name": "地榆", "dosage": 10, "unit": "g"},
            {"name": "仙鹤草", "dosage": 15, "unit": "g"},
            {"name": "麻仁", "dosage": 9, "unit": "g"},
            {"name": "生甘草", "dosage": 10, "unit": "g"}
        ],
        "function": "清热疏风，和血止血",
        "indications": "以便秘、出血、疼痛为主的各期内痔、混合痔、炎性外痔",
        "usage": "水煎服，日服一剂，分2-3次温服",
        "modifications": "便秘重：加生大黄6-10g（后下）；疼痛甚：加延胡索10g、川楝子10g；出血多：加茜草10g、三七粉3g（冲服）",
        "notes": "强调：槐花清肠止血，为治痔要药，但单用力薄，需配地榆、仙鹤草增强止血之功"
    },
    {
        "name": "地榆散加味",
        "source": "经验方",
        "composition": [
            {"name": "地榆", "dosage": 12, "unit": "g"},
            {"name": "黄芩", "dosage": 10, "unit": "g"},
            {"name": "黄连", "dosage": 10, "unit": "g"},
            {"name": "山栀", "dosage": 10, "unit": "g"},
            {"name": "槐花", "dosage": 10, "unit": "g"},
            {"name": "当归", "dosage": 12, "unit": "g"},
            {"name": "赤芍", "dosage": 10, "unit": "g"},
            {"name": "川芎", "dosage": 6, "unit": "g"},
            {"name": "甘草", "dosage": 6, "unit": "g"}
        ],
        "function": "清热凉血，活血止血",
        "indications": "血热型痔疮出血，血色鲜红或紫暗，肛门灼热，大便干结",
        "usage": "水煎服，日服一剂，分2-3次温服",
        "modifications": "出血量大：加仙鹤草15g、槐花炭12g；大便干结：加生大黄6g（后下）、芒硝6g（冲服）；肛门坠胀：加枳壳10g、木香6g",
        "notes": "临床经验：血热出血必用苦寒清热，但不可过用，恐伤脾胃，故配当归、川芎养血活血"
    },
    {
        "name": "活血散瘀汤",
        "source": "经验方",
        "composition": [
            {"name": "当归", "dosage": 15, "unit": "g"},
            {"name": "川芎", "dosage": 10, "unit": "g"},
            {"name": "赤芍", "dosage": 12, "unit": "g"},
            {"name": "桃仁", "dosage": 10, "unit": "g"},
            {"name": "红花", "dosage": 6, "unit": "g"},
            {"name": "延胡索", "dosage": 10, "unit": "g"},
            {"name": "枳壳", "dosage": 10, "unit": "g"},
            {"name": "木香", "dosage": 6, "unit": "g"},
            {"name": "地榆", "dosage": 15, "unit": "g"},
            {"name": "槐花", "dosage": 12, "unit": "g"}
        ],
        "function": "活血化瘀，行气止痛，凉血止血",
        "indications": "气滞血瘀型痔疮，血栓外痔，嵌顿性内痔，症见疼痛剧烈，肛门肿胀，便血色暗",
        "usage": "水煎服，日服一剂，分2-3次温服",
        "modifications": "疼痛剧烈：加乳香6g、没药6g；肿胀明显：加牛膝12g、泽兰10g；便秘：加生大黄6-10g（后下）",
        "notes": "强调：痔疮疼痛多因瘀血阻滞，活血化瘀为第一要务，但须配凉血止血之品，防止活血太过致出血不止"
    },
    {
        "name": "归脾汤加味",
        "source": "《济生方》加减",
        "composition": [
            {"name": "黄芪", "dosage": 15, "unit": "g"},
            {"name": "党参", "dosage": 12, "unit": "g"},
            {"name": "白术", "dosage": 10, "unit": "g"},
            {"name": "茯苓", "dosage": 12, "unit": "g"},
            {"name": "当归", "dosage": 10, "unit": "g"},
            {"name": "龙眼肉", "dosage": 10, "unit": "g"},
            {"name": "酸枣仁", "dosage": 10, "unit": "g"},
            {"name": "远志", "dosage": 6, "unit": "g"},
            {"name": "木香", "dosage": 6, "unit": "g"},
            {"name": "炙甘草", "dosage": 6, "unit": "g"},
            {"name": "地榆", "dosage": 15, "unit": "g"},
            {"name": "槐花", "dosage": 12, "unit": "g"}
        ],
        "function": "健脾养心，益气摄血",
        "indications": "气血亏损型痔疮出血，症见便血日久，血色淡红，面色萎黄，气短乏力，心悸失眠",
        "usage": "水煎服，日服一剂，分2-3次温服",
        "modifications": "气虚明显：加黄芪至20-30g；血虚明显：加熟地12g、白芍10g；脾虚泄泻：加山药15g、芡实12g",
        "notes": "经验：久病体虚，出血不止者，重在补气摄血，黄芪用量可增至30g，配地榆、槐花止血而不留瘀"
    },
    {
        "name": "八珍汤",
        "source": "《正体类要》",
        "composition": [
            {"name": "人参", "dosage": 10, "unit": "g", "note": "可用党参代"},
            {"name": "白术", "dosage": 10, "unit": "g"},
            {"name": "茯苓", "dosage": 10, "unit": "g"},
            {"name": "炙甘草", "dosage": 6, "unit": "g"},
            {"name": "当归", "dosage": 10, "unit": "g"},
            {"name": "川芎", "dosage": 6, "unit": "g"},
            {"name": "白芍", "dosage": 10, "unit": "g"},
            {"name": "熟地黄", "dosage": 12, "unit": "g"},
            {"name": "地榆", "dosage": 15, "unit": "g"},
            {"name": "槐花", "dosage": 12, "unit": "g"}
        ],
        "function": "益气补血",
        "indications": "气血两虚型痔疮，久病体弱，便血日久，面色苍白，头晕心悸，气短乏力",
        "usage": "水煎服，日服一剂，分2-3次温服",
        "modifications": "气虚重：加黄芪15g；血虚重：加阿胶10g（烊化）、桑葚10g；脾虚纳差：加山药15g、砂仁6g（后下）",
        "notes": "强调：气血两虚者，补气生血为主，止血为辅，切忌单纯止血，否则血止而气血更虚"
    },
    {
        "name": "补中益气汤",
        "source": "《脾胃论》",
        "composition": [
            {"name": "黄芪", "dosage": 20, "unit": "g"},
            {"name": "党参", "dosage": 15, "unit": "g"},
            {"name": "白术", "dosage": 10, "unit": "g"},
            {"name": "炙甘草", "dosage": 6, "unit": "g"},
            {"name": "当归", "dosage": 10, "unit": "g"},
            {"name": "陈皮", "dosage": 6, "unit": "g"},
            {"name": "升麻", "dosage": 6, "unit": "g"},
            {"name": "柴胡", "dosage": 6, "unit": "g"},
            {"name": "地榆", "dosage": 15, "unit": "g"},
            {"name": "槐花", "dosage": 12, "unit": "g"}
        ],
        "function": "补中益气，升阳举陷",
        "indications": "脾虚气陷型痔疮脱出，症见内痔脱出，肛门坠胀，神疲乏力，食少便溏，舌淡苔白",
        "usage": "水煎服，日服一剂，分2-3次温服，饭前服",
        "modifications": "脱垂严重：加炙黄芪至30g、升麻增至10g；便溏：加山药15g、芡实12g；气虚下陷：加枳壳10g",
        "notes": "经验：脾虚气陷，中气不足，升举无力则痔核脱出，重用黄芪、党参补气，配升麻、柴胡升提，多能奏效"
    },
    {
        "name": "黄芪建中汤加减",
        "source": "《金匮要略》加减",
        "composition": [
            {"name": "黄芪", "dosage": 20, "unit": "g"},
            {"name": "桂枝", "dosage": 10, "unit": "g"},
            {"name": "白芍", "dosage": 15, "unit": "g"},
            {"name": "炙甘草", "dosage": 6, "unit": "g"},
            {"name": "生姜", "dosage": 3, "unit": "片"},
            {"name": "大枣", "dosage": 6, "unit": "枚"},
            {"name": "饴糖", "dosage": 30, "unit": "g", "note": "烊化"},
            {"name": "当归", "dosage": 10, "unit": "g"},
            {"name": "地榆", "dosage": 15, "unit": "g"}
        ],
        "function": "温中补虚，缓急止痛",
        "indications": "虚寒型痔疮，症见便血色淡，肛门隐痛，喜温喜按，面色苍白，畏寒肢冷，舌淡苔白",
        "usage": "水煎服，饴糖烊化冲入，日服一剂，分2-3次温服",
        "modifications": "寒重：加干姜6g、附子6g（先煎）；腹痛：加白芍至20g、木香6g；便溏：去饴糖，加山药15g、芡实12g",
        "notes": "强调：虚寒证者，温补脾阳为主，配地榆凉血止血，寒热并用，标本兼治"
    }
]


async def main():
    async with AsyncSessionLocal() as db:
        updated_count = 0

        for formula_data in FORMULAS_DATA:
            name = formula_data["name"]

            # 检查方剂是否存在
            result = await db.execute(
                select(AnorectalFormula).where(AnorectalFormula.name == name)
            )
            formula = result.scalar_one_or_none()

            if formula:
                # 更新现有方剂
                await db.execute(
                    update(AnorectalFormula)
                    .where(AnorectalFormula.name == name)
                    .values(
                        composition=formula_data["composition"],
                        function=formula_data["function"],
                        indications=formula_data["indications"],
                        usage=formula_data["usage"],
                        modifications=formula_data["modifications"],
                        notes=formula_data["notes"],
                        source=formula_data["source"]
                    )
                )
                print(f"✓ 已更新: {name}")
                updated_count += 1
            else:
                print(f"✗ 未找到方剂: {name}")

        await db.commit()
        print(f"\n完成！共更新 {updated_count} 个方剂")


if __name__ == "__main__":
    asyncio.run(main())
