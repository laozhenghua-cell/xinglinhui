"""
经典医案数据导入
第一批：3个典型案例
"""
import asyncio
import uuid
import json
from datetime import date
from app.database import AsyncSessionLocal
from sqlalchemy import text


# 第一批：3个经典医案
CLASSIC_CASES = [
    {
        "id": str(uuid.uuid4()),
        "case_number": "ZJM-ZC-001",
        "case_title": "湿热瘀滞型痔疮典型案例",
        "source": "临床经验",
        "case_date": date(1985, 3, 15),
        "patient_info": {
            "age": 42,
            "gender": "男",
            "occupation": "办公室职员",
            "chief_complaint": "痔核肿痛3天，便血1周",
            "duration": "1周"
        },
        "inspection": {
            "local": "肛门周围可见3个暗紫色痔核，肿胀明显，触之疼痛",
            "tongue": "舌质红",
            "tongue_coating": "黄腻"
        },
        "auscultation": {},
        "inquiry": {
            "pain": {"present": True, "degree": "剧烈", "nature": "胀痛"},
            "bleeding": {"present": True, "color": "鲜红", "volume": "中量"},
            "stool_condition": "干结",
            "bitter_mouth": True,
            "dry_throat": True,
            "urination": "短赤",
            "appetite": "纳差",
            "sleep": "难寐"
        },
        "palpation": {
            "pulse": "弦滑数"
        },
        "disease_type": "痔疮",
        "syndrome_analysis": """
辨证分析：
1. 症状特点：痔核肿痛剧烈、便血鲜红、大便干结，属实证、热证
2. 全身症状：口苦咽干、小便短赤，提示湿热内蕴
3. 舌脉：舌质红、苔黄腻、脉弦滑数，确证湿热下注
4. 病机：湿热下注肛门，气滞血瘀，瘀热互结

指出："痔之临证所见，实证者多，虚证者少。此患者正值壮年，体质尚实，
加之饮食不节、嗜食辛辣，致湿热下注，气血瘀滞于肛门。治当清热除湿，活血化瘀。"
        """,
        "syndrome_type": "湿热瘀滞型",
        "treatment_principle": "清热除湿，活血化瘀",
        "internal_formula": {
            "name": "五神汤加味",
            "composition": [
                {"herb": "茯苓", "dosage": "10g"},
                {"herb": "金银花", "dosage": "20g"},
                {"herb": "牛膝", "dosage": "10g"},
                {"herb": "车前子", "dosage": "10g"},
                {"herb": "地丁", "dosage": "15g"},
                {"herb": "黄芩", "dosage": "10g"},
                {"herb": "归尾", "dosage": "10g"},
                {"herb": "赤芍", "dosage": "10g"},
                {"herb": "大黄", "dosage": "6g"},
                {"herb": "甘草", "dosage": "10g"}
            ],
            "usage": "水煎服，每日1剂，分2次温服",
            "modifications": "便秘严重加芒硝6g；疼痛剧烈加延胡索10g"
        },
        "external_treatment": [
            {
                "name": "朴硝马齿苋熏洗方",
                "usage": "先熏后洗，每次20-30分钟",
                "frequency": "每日2次"
            },
            {
                "name": "四黄膏",
                "usage": "外敷患处，厚度2-3mm",
                "frequency": "每日3次"
            }
        ],
        "other_treatments": "卧床休息，避免久坐；忌食辛辣刺激食物",
        "follow_ups": [
            {
                "date": "1985-03-18",
                "days": 3,
                "symptoms_change": "肿痛明显减轻，便血减少，大便转软",
                "adjustment": "守方继续，大黄减至3g",
                "notes": "疗效显著"
            },
            {
                "date": "1985-03-22",
                "days": 7,
                "symptoms_change": "肿痛基本消失，便血停止，大便正常",
                "adjustment": "停用内服药，继续外洗3天巩固",
                "notes": "临床治愈"
            }
        ],
        "outcome": "痊愈",
        "outcome_notes": "7天临床治愈，随访3个月未复发",
        "key_points": """
点评要点：
1. 辨证准确：抓住"湿热"和"瘀滞"两个关键
2. 内外兼治：内服清热活血，外用熏洗消肿，疗效倍增
3. 用药精当：五神汤清利湿热，加大黄、归尾增强活血化瘀
4. 及时调整：见效后及时减轻攻伐药物剂量，防止伤正
5. 预防复发：强调饮食起居调护，从根本上防止复发

教学意义：本案例典型体现"注重湿邪为患"和"内外兼治"学术思想，
是学习痔疮实证治疗的经典案例。
        """,
        "teaching_notes": """
适合教学场景：
- 中医外科临床带教
- 肛肠病辨证施治培训
- 学术思想学习
- 实证型痔疮典型案例参考
        """,
        "tags": ["典型案例", "内外兼治", "湿热证", "疗效显著"],
        "is_classic": True,
        "difficulty_level": 2,
        "view_count": 0,
        "reference_count": 0
    },
    {
        "id": str(uuid.uuid4()),
        "case_number": "ZJM-TC-001",
        "case_title": "气血两虚型直肠脱垂 - 明矾注射疗法",
        "source": "临床经验",
        "case_date": date(1981, 6, 20),
        "patient_info": {
            "age": 65,
            "gender": "女",
            "occupation": "退休工人",
            "chief_complaint": "直肠脱出3年，加重半年",
            "duration": "3年"
        },
        "inspection": {
            "local": "直肠黏膜脱出约5cm，色淡红，表面光滑",
            "tongue": "舌质淡",
            "tongue_coating": "薄白"
        },
        "auscultation": {},
        "inquiry": {
            "prolapse": True,
            "prolapse_trigger": "咳嗽、用力时脱出",
            "fatigue": True,
            "shortness_of_breath": True,
            "poor_appetite": True,
            "pale_complexion": True,
            "dizziness": True
        },
        "palpation": {
            "pulse": "细弱"
        },
        "disease_type": "直肠脱垂",
        "syndrome_analysis": """
辨证分析：
1. 病史特点：老年女性，脱垂3年，反复发作
2. 局部表现：直肠黏膜脱出，色淡红而非暗紫，提示虚证
3. 全身症状：神疲乏力、气短懒言、面色萎黄，典型气血两虚
4. 舌脉：舌淡苔薄白、脉细弱，确证气血不足

指出："直肠脱垂虽属虚证，但病因很多。此患者年老体弱，气血两虚，
中气下陷，不能固摄，致直肠脱出。单纯补益气血，疗程长、疗效慢。
根据'酸可收敛、涩可固脱'理论，宜采用明矾注射疗法，配合内服补益气血方剂。"
        """,
        "syndrome_type": "气血两虚型",
        "treatment_principle": "补益气血，升举固脱",
        "internal_formula": {
            "name": "八珍汤加味",
            "composition": [
                {"herb": "人参", "dosage": "10g"},
                {"herb": "白术", "dosage": "10g"},
                {"herb": "茯苓", "dosage": "10g"},
                {"herb": "炙甘草", "dosage": "6g"},
                {"herb": "当归", "dosage": "12g"},
                {"herb": "川芎", "dosage": "10g"},
                {"herb": "白芍", "dosage": "10g"},
                {"herb": "熟地黄", "dosage": "15g"},
                {"herb": "黄芪", "dosage": "30g"},
                {"herb": "升麻", "dosage": "6g"},
                {"herb": "柴胡", "dosage": "6g"}
            ],
            "usage": "水煎服，每日1剂，分2次温服",
            "modifications": "加黄芪、升麻、柴胡增强升举固脱之力"
        },
        "external_treatment": [
            {
                "name": "6%明矾液注射疗法",
                "usage": "直肠黏膜下多点注射，每点2-3ml",
                "frequency": "首次治疗",
                "notes": "1959年首创，1981年治疗成人完全性直肠脱垂全愈率99.5%"
            }
        ],
        "other_treatments": "提肛运动：每日3次，每次50下；避免久站、便时勿过度用力",
        "follow_ups": [
            {
                "date": "1981-06-27",
                "days": 7,
                "symptoms_change": "脱垂明显减轻，仅用力时轻度脱出",
                "adjustment": "继续内服方剂，暂不追加注射",
                "notes": "注射疗效显著"
            },
            {
                "date": "1981-07-11",
                "days": 21,
                "symptoms_change": "脱垂基本控制，日常活动不脱出",
                "adjustment": "二次明矾注射，剂量减半",
                "notes": "巩固疗效"
            },
            {
                "date": "1981-08-20",
                "days": 60,
                "symptoms_change": "直肠脱垂完全治愈，无复发",
                "adjustment": "停药，嘱继续提肛锻炼",
                "notes": "临床痊愈"
            }
        ],
        "outcome": "痊愈",
        "outcome_notes": "2个月治愈，随访1年无复发，疗效巩固",
        "key_points": """
点评要点：
1. 创新疗法：明矾注射疗法是1959年首创，理论依据"酸可收敛、涩可固脱"
2. 内外结合：注射疗法解决局部脱垂，内服方剂调理气血，标本兼治
3. 分次治疗：首次注射观察疗效，酌情追加第二次，避免过度治疗
4. 疗效确切：1981年鉴定数据显示全愈率99.5%，且无直肠狭窄等后遗症
5. 预防复发：强调功能锻炼（提肛运动），从根本上恢复肛门功能

历史意义：本案例是明矾注射疗法的经典应用，为成人完全性直肠脱垂
的非手术治疗开辟了新路，具有重要学术价值和临床价值。
        """,
        "teaching_notes": """
适合教学场景：
- 中医外科创新疗法学习
- 学术思想传承
- 直肠脱垂非手术治疗培训
- 虚证型肛肠病治疗参考

重点教学内容：
1. 明矾注射疗法的理论依据
2. 注射技术要点（层次、剂量、部位）
3. 内外兼治的临床应用
4. 疗效评价与随访管理
        """,
        "tags": ["经典案例", "创新疗法", "明矾注射", "内外兼治", "虚证"],
        "is_classic": True,
        "difficulty_level": 3,
        "view_count": 0,
        "reference_count": 0
    },
    {
        "id": str(uuid.uuid4()),
        "case_number": "ZJM-GL-001",
        "case_title": "虚热内蕴型肛瘘 - 术后换药经验",
        "source": "临床经验",
        "case_date": date(1978, 9, 10),
        "patient_info": {
            "age": 48,
            "gender": "男",
            "occupation": "教师",
            "chief_complaint": "肛瘘术后创面不愈3个月",
            "duration": "3个月"
        },
        "inspection": {
            "local": "肛门旁见手术创面，肉芽组织苍白，脓汁清稀，愈合缓慢",
            "tongue": "舌质红",
            "tongue_coating": "少苔"
        },
        "auscultation": {},
        "inquiry": {
            "chronic_fistula": True,
            "discharge": {"present": True, "color": "清稀"},
            "delayed_healing": True,
            "night_sweats": True,
            "low_fever": True,
            "fatigue": True,
            "poor_appetite": True
        },
        "palpation": {
            "pulse": "细数"
        },
        "disease_type": "肛瘘",
        "syndrome_analysis": """
辨证分析：
1. 病史特点：术后3个月创面不愈，脓汁清稀，属虚证
2. 局部表现：肉芽苍白、生长不良，提示气血不足
3. 全身症状：潮热盗汗、低热、懒言乏力，典型虚热内蕴
4. 舌脉：舌红少苔、脉细数，确证阴虚内热

指出："此乃久病失治，寒邪循络内侵，入里化热灼伤肺金，肺燥失润，
气机不得宣发，气血不达，肌肤失于濡养而致。治以滋阴养血通络之法，
使气血畅通，每获良效。同时换药方法至关重要：初时宜重化腐，
待腐脱管化改用玉红膏生肌。"
        """,
        "syndrome_type": "虚热内蕴",
        "treatment_principle": "滋阴养血，清热通络",
        "internal_formula": {
            "name": "当归连翘汤",
            "composition": [
                {"herb": "当归", "dosage": "12g"},
                {"herb": "连翘", "dosage": "12g"},
                {"herb": "生地", "dosage": "12g"},
                {"herb": "白芍", "dosage": "10g"},
                {"herb": "白芷", "dosage": "6g"},
                {"herb": "党参", "dosage": "15g"},
                {"herb": "白术", "dosage": "10g"},
                {"herb": "阿胶", "dosage": "12g"},
                {"herb": "甘草", "dosage": "6g"},
                {"herb": "地榆", "dosage": "10g"},
                {"herb": "乌梅", "dosage": "10g"}
            ],
            "usage": "水煎服，每日1剂，分2次温服",
            "modifications": "加鸡血藤15g、丹参12g活血通络，促进肉芽生长"
        },
        "external_treatment": [
            {
                "name": "玉红膏",
                "usage": "清洁创面后涂抹，或用药纱覆盖",
                "frequency": "每日换药1次",
                "notes": "强调：待腐脱管化后使用，促进创面愈合，防止假愈合"
            }
        ],
        "other_treatments": """
换药规律：
1. 初时宜重化腐：用红粉纱条蚀管祛腐
2. 待腐脱管化：改用生肌玉红膏换药
3. 接近愈合时：防止桥形粘连，避免假愈合
4. 肉芽水肿时：用盐水纱条消肿
5. 中心小创面：外用珍珠散收口
        """,
        "follow_ups": [
            {
                "date": "1978-09-20",
                "days": 10,
                "symptoms_change": "脓汁转为黄色粘稠，肉芽颜色转红，开始生长",
                "adjustment": "内服方守方，外用继续玉红膏",
                "notes": "开始见效"
            },
            {
                "date": "1978-10-05",
                "days": 25,
                "symptoms_change": "创面明显缩小，肉芽新鲜，脓汁基本消失",
                "adjustment": "内服方减轻剂量，外用继续",
                "notes": "疗效显著"
            },
            {
                "date": "1978-10-25",
                "days": 45,
                "symptoms_change": "创面基本愈合，仅中心留针尖大小",
                "adjustment": "外用珍珠散收口",
                "notes": "接近痊愈"
            },
            {
                "date": "1978-11-05",
                "days": 56,
                "symptoms_change": "创面完全愈合，无窦道残留",
                "adjustment": "停药",
                "notes": "临床治愈"
            }
        ],
        "outcome": "痊愈",
        "outcome_notes": "56天创面完全愈合，随访半年无复发",
        "key_points": """
点评要点：
1. 辨虚实：术后久不愈合，属虚证而非实证，不可一味清热解毒
2. 析病机：虚热内蕴，阴虚内热，治以滋阴养血为主，佐以清热通络
3. 重外治：换药方法至关重要，把握"化腐-生肌"转换时机
4. 察肉芽：根据肉芽颜色、质地调整用药，是特色经验
5. 防假愈：接近愈合时注意桥形粘连，防止表面愈合、深部残留

换药规律总结（经验）：
"初时宜重化腐，待腐脱管化改用玉红膏生肌，接近愈合时防止假愈合"
这是肛瘘术后处理的核心经验，值得深入学习。
        """,
        "teaching_notes": """
适合教学场景：
- 肛瘘术后处理培训
- 虚证型肛肠病辨治
- 创面换药技术教学
- 学术思想学习

重点教学内容：
1. 虚实辨证在术后管理中的应用
2. 换药时机的把握（化腐→生肌→收口）
3. 肉芽组织观察技巧
4. 假愈合的预防方法
5. 内外兼治的临床应用
        """,
        "tags": ["疑难病例", "术后处理", "虚证", "换药经验", "内外兼治"],
        "is_classic": True,
        "difficulty_level": 3,
        "view_count": 0,
        "reference_count": 0
    }
]


async def seed_medical_cases():
    """导入经典医案"""
    async with AsyncSessionLocal() as db:
        print("=" * 70)
        print("开始导入经典医案（第一批：3个典型案例）")
        print("=" * 70)

        imported_count = 0
        skipped_count = 0

        for case in CLASSIC_CASES:
            # 检查是否已存在
            result = await db.execute(
                text("SELECT id FROM medical_cases WHERE case_number = :case_number"),
                {"case_number": case["case_number"]}
            )
            existing = result.fetchone()

            if existing:
                print(f"\n⚠️  案例已存在，跳过：{case['case_title']} ({case['case_number']})")
                skipped_count += 1
                continue

            # 插入医案（使用CAST代替::语法）
            await db.execute(
                text("""
                    INSERT INTO medical_cases (
                        id, case_number, case_title, source, case_date,
                        patient_info, inspection, auscultation, inquiry, palpation,
                        disease_type, syndrome_analysis, syndrome_type, treatment_principle,
                        internal_formula, external_treatment, other_treatments,
                        follow_ups, outcome, outcome_notes,
                        key_points, teaching_notes, tags,
                        is_classic, difficulty_level, view_count, reference_count
                    ) VALUES (
                        CAST(:id AS UUID), :case_number, :case_title, :source, CAST(:case_date AS DATE),
                        CAST(:patient_info AS JSONB), CAST(:inspection AS JSONB), CAST(:auscultation AS JSONB),
                        CAST(:inquiry AS JSONB), CAST(:palpation AS JSONB),
                        :disease_type, :syndrome_analysis, :syndrome_type, :treatment_principle,
                        CAST(:internal_formula AS JSONB), CAST(:external_treatment AS JSONB), :other_treatments,
                        CAST(:follow_ups AS JSONB), :outcome, :outcome_notes,
                        :key_points, :teaching_notes, CAST(:tags AS JSONB),
                        :is_classic, :difficulty_level, :view_count, :reference_count
                    )
                """),
                {
                    "id": case["id"],
                    "case_number": case["case_number"],
                    "case_title": case["case_title"],
                    "source": case["source"],
                    "case_date": case["case_date"],
                    "patient_info": json.dumps(case["patient_info"], ensure_ascii=False),
                    "inspection": json.dumps(case["inspection"], ensure_ascii=False),
                    "auscultation": json.dumps(case["auscultation"], ensure_ascii=False),
                    "inquiry": json.dumps(case["inquiry"], ensure_ascii=False),
                    "palpation": json.dumps(case["palpation"], ensure_ascii=False),
                    "disease_type": case["disease_type"],
                    "syndrome_analysis": case["syndrome_analysis"],
                    "syndrome_type": case["syndrome_type"],
                    "treatment_principle": case["treatment_principle"],
                    "internal_formula": json.dumps(case["internal_formula"], ensure_ascii=False),
                    "external_treatment": json.dumps(case["external_treatment"], ensure_ascii=False),
                    "other_treatments": case["other_treatments"],
                    "follow_ups": json.dumps(case["follow_ups"], ensure_ascii=False),
                    "outcome": case["outcome"],
                    "outcome_notes": case["outcome_notes"],
                    "key_points": case["key_points"],
                    "teaching_notes": case["teaching_notes"],
                    "tags": json.dumps(case["tags"], ensure_ascii=False),
                    "is_classic": case["is_classic"],
                    "difficulty_level": case["difficulty_level"],
                    "view_count": case["view_count"],
                    "reference_count": case["reference_count"]
                }
            )

            print(f"\n✅ 导入成功：{case['case_title']}")
            print(f"   编号：{case['case_number']}")
            print(f"   病种：{case['disease_type']}")
            print(f"   证型：{case['syndrome_type']}")
            print(f"   难度：{'⭐' * case['difficulty_level']}")
            imported_count += 1

        await db.commit()

        print("\n" + "=" * 70)
        print(f"✅ 医案导入完成")
        print(f"   新增：{imported_count} 个")
        print(f"   跳过：{skipped_count} 个")
        print("=" * 70)

        # 统计医案库
        result = await db.execute(text("SELECT COUNT(*) FROM medical_cases"))
        total = result.scalar()
        print(f"\n📊 医案库统计：")
        print(f"   总案例数：{total} 个")
        print(f"   经典案例：{imported_count} 个")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(seed_medical_cases())
