"""
华夏痔瘘辅助诊疗系统 - 知识库种子数据
来源：华夏老中医临床经验整理
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import AsyncSessionLocal, engine, Base
from app.models import AnorectalHerb, AnorectalFormula, AnorectalCase, PreventionGuide

# ============ 肛肠科常用中药 ============
HERBS = [
    {"name": "槐花", "category": "止血药", "properties": "苦，微寒", "meridians": "肝、大肠经",
     "effects": "凉血止血，清肝泻火", "indications": "肠风便血，痔血", "contraindications": "脾胃虚寒者慎用"},
    {"name": "地榆", "category": "止血药", "properties": "苦酸，微寒", "meridians": "肝、大肠经",
     "effects": "凉血止血，解毒敛疮", "indications": "便血，痔血，血痢，疮疡", "contraindications": "大面积烧伤不宜外用"},
    {"name": "侧柏叶", "category": "止血药", "properties": "苦涩，微寒", "meridians": "肺、肝、大肠经",
     "effects": "凉血止血，化痰止咳", "indications": "各种出血证", "contraindications": "无"},
    {"name": "仙鹤草", "category": "止血药", "properties": "苦涩，平", "meridians": "肺、肝、脾经",
     "effects": "收敛止血，截疟，止痢", "indications": "各种出血证", "contraindications": "无明显禁忌"},
    {"name": "黄芪", "category": "补气药", "properties": "甘，微温", "meridians": "脾、肺经",
     "effects": "补气升阳，益卫固表，托毒生肌", "indications": "脾虚气陷，直肠脱垂，气虚便血",
     "contraindications": "实证、阳证疮疡不宜"},
    {"name": "当归", "category": "补血药", "properties": "甘辛，温", "meridians": "肝、心、脾经",
     "effects": "补血活血，调经止痛，润肠通便", "indications": "血虚便秘，痔疮出血",
     "contraindications": "湿盛中满、大便溏泄者慎用"},
    {"name": "黄连", "category": "清热药", "properties": "苦，寒", "meridians": "心、脾、胃、胆、大肠经",
     "effects": "清热燥湿，泻火解毒", "indications": "湿热痢疾，肛门肿痛", "contraindications": "脾胃虚寒者忌用"},
    {"name": "黄芩", "category": "清热药", "properties": "苦，寒", "meridians": "肺、胆、脾、大肠经",
     "effects": "清热燥湿，泻火解毒，止血安胎", "indications": "湿热泻痢，便血", "contraindications": "脾胃虚寒者不宜"},
    {"name": "金银花", "category": "清热药", "properties": "甘，寒", "meridians": "肺、心、胃经",
     "effects": "清热解毒，疏散风热", "indications": "肛周脓肿，疮疡肿毒", "contraindications": "脾胃虚寒者慎用"},
    {"name": "赤芍", "category": "活血药", "properties": "苦，微寒", "meridians": "肝经",
     "effects": "清热凉血，散瘀止痛", "indications": "血瘀肿痛，痈肿疮疡", "contraindications": "血虚无瘀者不宜"},
]

# PLACEHOLDER_MORE_HERBS

# ============ 经典方剂 ============
FORMULAS = [
    {
        "name": "槐花散加味",
        "composition": "槐花12克，侧柏叶10克，炒荆芥10克，枳壳10克，防风10克，生地10克，地榆10克，仙鹤草15克，麻仁9克，生甘草10克（原文第132行）",
        "usage": "水煎服，日服一剂",
        "function": "清热疏风，和血止血",
        "indications": "以便秘、出血、疼痛为主的各期内痔、混合痔、炎性外痔",
        "syndrome_type": "实热证"
    },
    {
        "name": "地榆散加味",
        "composition": "地榆12克，黄芩10克，黄连10克，山栀10克，槐花10克，当归12克，赤小豆15克，丹皮10克，甘草6克（原文第133行）",
        "usage": "水煎服，日服一剂",
        "function": "清热凉血，活血止血",
        "indications": "血热型痔疮出血",
        "syndrome_type": "实热证"
    },
    {
        "name": "五神汤加味",
        "composition": "茯苓10克，金银花20克，牛夕（牛膝）10克，车前子10克，地丁15克，黄芩10克，归尾10克，赤芍10克，甘草10克（原文第136行）",
        "usage": "水煎服，日服一剂",
        "function": "清热利湿，活血化瘀",
        "indications": "湿热瘀滞型痔疮、血栓外痔",
        "syndrome_type": "湿热瘀滞型"
    },
    {
        "name": "活血散瘀汤",
        "composition": "归尾10克，赤芍10克，桃仁10克，大黄10克，川芎10克，丹皮10克，枳壳10克，瓜蒌仁10克，槟榔10克（原文第137行）",
        "usage": "水煎服，日服一剂",
        "function": "活血化瘀，行气止痛",
        "indications": "气滞血瘀型痔疮",
        "syndrome_type": "气滞血瘀型"
    },
    {
        "name": "归脾汤加味",
        "composition": "人参10克，黄芪10克，白术10克，茯苓10克，枣仁10克，龙眼肉10克，远志10克，木香6克，甘草6克，灶心土80克，升麻10克（原文第140行）",
        "usage": "水煎服，日服一剂",
        "function": "益气健脾，补血止血",
        "indications": "脾虚不摄型痔疮出血",
        "syndrome_type": "虚寒证"
    },
    {
        "name": "八珍汤",
        "composition": "熟地15克，白芍10克，当归10克，川芎10克，党参15克，白术10克，甘草10克（原文第145行；医案加味方另行保存）",
        "usage": "水煎服，日服一剂",
        "function": "补气益血",
        "indications": "气血亏损型痔疮，便血日久",
        "syndrome_type": "气血亏损型"
    },
    {
        "name": "内疏黄连汤加减",
        "composition": "黄连10克，黄芩6克，大黄6克，栀子10克，桔梗6克，木香6克，槟榔6克，连翘10克，赤白芍各10克，全当归10克，甘草6克",
        "usage": "水煎服，日服一剂",
        "function": "清泻实热，宣散郁结",
        "indications": "肛周脓肿初起，实热壅盛",
        "syndrome_type": "热毒蕴结"
    },
    {
        "name": "止痛如神汤",
        "composition": "秦艽10克，桃仁10克，皂角子6克，苍术10克，防风10克，黄柏10克，当归10克，泽泻10克，大黄6克（后下），槟榔10克，甘草6克",
        "usage": "水煎服，日服一剂",
        "function": "活血祛风，清热利湿",
        "indications": "肛裂疼痛，湿热型痔疮疼痛",
        "syndrome_type": "湿热下注"
    },
    {
        "name": "补中益气汤",
        "composition": "黄芪15克，党参10克，白术10克，柴胡10克，陈皮10克，升麻12克，当归10克，甘草10克（原文第146行）",
        "usage": "水煎服，日服一剂",
        "function": "补中益气，升阳举陷",
        "indications": "直肠脱垂，脾虚气陷型痔疮",
        "syndrome_type": "脾虚气陷"
    },
    {
        "name": "凉血地黄汤",
        "composition": "生地15克，当归10克，地榆10克，槐花10克，黄芩10克，天花粉10克，升麻6克，赤芍10克，甘草6克",
        "usage": "水煎服，日服一剂",
        "function": "凉血止血，养阴润燥",
        "indications": "肛裂出血，血热肠燥",
        "syndrome_type": "血热肠燥"
    },
    {
        "name": "萆薢渗湿汤",
        "composition": "萆薢10克，苡仁15克，黄柏10克，赤茯苓10克，丹皮10克，泽泻10克，通草6克，滑石10克（包煎）",
        "usage": "水煎服，日服一剂",
        "function": "清热利湿",
        "indications": "肛门湿疹，湿热下注型",
        "syndrome_type": "湿热下注"
    },
    {
        "name": "托里消毒散加味",
        "composition": "黄芪20克，党参10克，当归10克，白芍10克，白术10克，茯苓10克，金银花15克，白芷6克，桔梗6克，皂角刺10克，甘草6克",
        "usage": "水煎服，日服一剂",
        "function": "益气补血，托里排脓",
        "indications": "肛周脓肿后期，正虚邪恋",
        "syndrome_type": "正虚邪恋"
    },
]

# ============ 典型医案 ============
CASES = [
    {
        "title": "实热内蕴痔疮出血",
        "disease_type": "痔疮",
        "patient_info": "男，40岁",
        "chief_complaint": "大便带血一月余",
        "symptoms": "便干难解，3~4日一次，小便短赤。舌红、苔黄，脉弦数",
        "syndrome": "实热内蕴，血热肠燥",
        "treatment": "清热止血，润肠通便",
        "formula": "槐花散加减",
        "prescription": "槐花12克，侧柏叶10克，炒荆芥10克，枳壳10克，防风10克，生地15克，地榆10克，仙鹤草15克，麻仁9克，生甘草10克",
        "outcome": "五日后复诊，便血已止。续用前方五剂而痊愈。"
    },
    {
        "title": "湿热下注血栓外痔",
        "disease_type": "痔疮",
        "patient_info": "男，24岁",
        "chief_complaint": "肛门肿痛三天",
        "symptoms": "便干，无血，口苦，纳食欠佳。舌质红，苔黄腻，脉弦滑数",
        "syndrome": "湿热下注，气滞血瘀",
        "treatment": "清热利湿，活血化瘀",
        "formula": "五神汤加减",
        "prescription": "茯苓10克，金银花20克，牛膝10克，车前子10克，地丁15克，黄芩10克，归尾10克，赤芍10克，甘草10克",
        "outcome": "三日后复诊，疼痛减轻。改用活血散瘀汤加减，五日后痊愈。"
    },
    {
        "title": "气血亏损产后痔疮",
        "disease_type": "痔疮",
        "patient_info": "女，28岁",
        "chief_complaint": "大便带血三个月（产后）",
        "symptoms": "面色无华，神疲乏力，少气懒言，纳食差。脉细弱，舌淡白",
        "syndrome": "气血亏损、气不摄血",
        "treatment": "补气益血",
        "formula": "八珍汤",
        "prescription": "熟地15克，白芍10克，当归15克，川芎10克，党参15克，白术12克，茯苓10克，炙黄芪30克，木香10克，炙甘草6克",
        "outcome": "七日后便血已止。续服前方半个月，诸症均消。嘱服人参养荣丸巩固。"
    },
    {
        "title": "实热肛周脓肿消散",
        "disease_type": "肛周脓肿",
        "patient_info": "男，32岁",
        "chief_complaint": "肛旁肿胀疼痛二天",
        "symptoms": "身热，口渴喜冷饮，大便秘结，小便短赤。舌质红，苔黄腻，脉弦滑数",
        "syndrome": "实热壅盛，下注肛门",
        "treatment": "清泻实热，宣散郁结",
        "formula": "内疏黄连汤加减",
        "prescription": "黄连10克，黄芩6克，大黄6克，栀子10克，桔梗6克，木香6克，槟榔6克，连翘10克，赤白芍各10克，全当归10克，甘草6克",
        "outcome": "五日后肛旁肿痛消失。继用前方三剂清余热，痊愈。"
    },
    {
        "title": "直肠脱垂气虚下陷（小儿）",
        "disease_type": "直肠脱垂",
        "patient_info": "男，3.5岁",
        "chief_complaint": "便后肛门有物脱出半年",
        "symptoms": "食少，睡眠不佳，面色恍白，目睛无彩。舌淡苔少，脉象虚弱",
        "syndrome": "脾肺气虚，中气下陷",
        "treatment": "补脾益肺，升提固涩",
        "formula": "补中益气汤加减",
        "prescription": "黄芪15克，党参10克，白术8克，当归6克，陈皮4克，升麻4克，柴胡4克，五味子5克，甘草4克",
        "outcome": "服药七剂后脱出明显减少。续服半月痊愈，随访一年未复发。"
    },
]

# ============ 预防保健 ============
PREVENTION_GUIDES = [
    {
        "disease_type": "痔疮",
        "prevention_points": "1.保持大便通畅，养成定时排便习惯；2.饮食清淡，忌辛辣刺激、酗酒；3.避免久坐久立久蹲；4.适当运动，提肛锻炼；5.保持肛门清洁；6.女性注意孕期保健",
        "postop_care": "化腐期（术后1-7天）：创面分泌物较多，以祛腐为主，使用九华膏纱条换药。生肌期（7-14天）：创面渐洁净，以生肌为主，改用生肌散。收口期（14天后）：创面缩小，促进愈合，使用珍珠散。",
        "acupuncture": "取穴：长强、承山、百会、足三里。脾虚加脾俞、气海；血热加血海、曲池。"
    },
    {
        "disease_type": "肛裂",
        "prevention_points": "1.保持大便软化通畅，多食蔬果纤维；2.便后温水坐浴；3.避免腹泻；4.及时治疗肛窦炎；5.避免过度用力排便",
        "postop_care": "术后每日温水坐浴2-3次，保持创面清洁。局部外用九华膏促进愈合。口服润肠通便之品（麻仁丸等）。",
        "acupuncture": "取穴：长强、承山、大肠俞、支沟。血热加血海；气滞加太冲。"
    },
    {
        "disease_type": "肛周脓肿",
        "prevention_points": "1.保持肛门清洁干燥；2.及时治疗肛窦炎和肛乳头炎；3.避免辛辣刺激食物；4.增强体质，避免过度疲劳；5.糖尿病患者控制血糖",
        "postop_care": "术后充分引流，每日换药，冲洗脓腔。内服清热解毒之品（五味消毒饮等）。注意观察有无肛瘘形成。",
        "acupuncture": "取穴：长强、会阴、大肠俞、曲池。热毒盛加合谷、血海。"
    },
    {
        "disease_type": "直肠脱垂",
        "prevention_points": "1.增强体质，适当锻炼；2.积极治疗慢性咳嗽、便秘、腹泻；3.避免蹲厕过久；4.坚持提肛运动；5.小儿注意营养，防止久泻",
        "postop_care": "术后卧床休息，控制排便3天。进食少渣饮食。口服补中益气丸巩固。坚持提肛运动。",
        "acupuncture": "取穴：百会、长强、大肠俞、足三里、气海。针用补法，可灸百会、气海。"
    },
]


async def seed():
    """执行种子数据导入"""
    async with AsyncSessionLocal() as session:
        # 清空旧数据
        await session.execute(text("DELETE FROM anorectal_herbs"))
        await session.execute(text("DELETE FROM anorectal_formulas"))
        await session.execute(text("DELETE FROM anorectal_cases"))
        await session.execute(text("DELETE FROM prevention_guides"))

        # 插入中药
        for h in HERBS:
            session.add(AnorectalHerb(**h))
        print(f"✅ 导入 {len(HERBS)} 味中药")

        # 插入方剂
        for f in FORMULAS:
            session.add(AnorectalFormula(**f))
        print(f"✅ 导入 {len(FORMULAS)} 首方剂")

        # 插入医案
        for c in CASES:
            # 字段映射：treatment -> treatment_principle, prescription -> treatment_process
            case_data = c.copy()
            if 'treatment' in case_data:
                case_data['treatment_principle'] = case_data.pop('treatment')
            if 'prescription' in case_data:
                case_data['treatment_process'] = case_data.pop('prescription')
            session.add(AnorectalCase(**case_data))
        print(f"✅ 导入 {len(CASES)} 例医案")

        # 插入预防保健
        for p in PREVENTION_GUIDES:
            # 字段映射和转换
            guide_data = p.copy()
            if 'acupuncture' in guide_data:
                guide_data['acupuncture_points'] = guide_data.pop('acupuncture')
            # 转换字符串为列表（如果是字符串）
            if 'prevention_points' in guide_data and isinstance(guide_data['prevention_points'], str):
                guide_data['prevention_points'] = [point.strip() for point in guide_data['prevention_points'].split('；') if point.strip()]
            # 生成标题（如果没有）
            if 'title' not in guide_data or not guide_data['title']:
                guide_data['title'] = f"{guide_data['disease_type']}预防与保健"
            session.add(PreventionGuide(**guide_data))
        print(f"✅ 导入 {len(PREVENTION_GUIDES)} 条预防保健指南")

        await session.commit()
        print("\n🎉 知识库种子数据导入完成！")


if __name__ == "__main__":
    asyncio.run(seed())
