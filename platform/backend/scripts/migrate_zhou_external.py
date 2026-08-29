"""
原著「外治法 / 外用药」完整补全与病症精准映射脚本

目标：把《临床经验原文》中全部外治方法（熏洗、外敷、栓剂、注射、
换药等）补齐到 external_treatments 表，并让每一味外用药精准对应到
「病种 → 证型」。

幂等：按 name upsert。高危操作（注射/封闭/枯痔/红粉/砒/鸦胆子等）沿用
现有安全治理逻辑，标记为 learning_only（仅院内专科学习，不下发操作参数）。
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select, delete
from app.database import AsyncSessionLocal
from app.models.external_treatment import ExternalTreatment
from app.models.knowledge import AnorectalFormula


def _c(items):
    return [{"name": n, "unit": u, "dosage": d} for n, u, d in items]


# 需补充/修正的外治法（覆盖全部病种）
TREATMENTS = [
    # 修正既有条目的病症映射（对齐原文）
    {
        "name": "朴硝马齿苋熏洗方",
        "treatment_type": "fumigation",
        "composition": _c([
            ("朴硝", "g", 30), ("马齿苋", "g", 20), ("瓦松", "g", 15),
            ("归尾", "g", 15), ("赤芍", "g", 15), ("黄柏", "g", 15),
            ("苍术", "g", 15),
        ]),
        "preparation": "上药加水煎煮去渣，药液约1000ml，趁热先熏后洗",
        "usage": "先熏后洗，或浸布湿敷患处；肛门红肿热痛者每日坐浴",
        "frequency": "每日2-3次",
        "duration": "连续使用至炎症缓解",
        "function": "清热解毒，活血祛瘀，利湿软坚，消肿止痛",
        "indications": "痔、瘘、肛痈之炎症期，肛裂便后疼痛，痈疽疔疖急性期炎症",
        "syndrome_types": ["湿热下注", "湿热瘀滞", "热毒蕴结"],
        "disease_types": ["痔疮", "肛周脓肿", "肛裂", "肛瘘", "肛门疖肿"],
        "contraindications": "术后大出血者禁用",
        "precautions": "朴硝易吸潮，密封保存；水温适宜",
        "source": "原文·辅助治疗（原文第150-153行）",
        "priority": 96,
        "notes": "治嵌顿痔、炎性外痔、血栓外痔重视外治，此方为通用熏洗方",
    },
    {
        "name": "四黄膏",
        "treatment_type": "ointment",
        "composition": "黄连、黄芩、黄柏、栀子各等份研末；凡士林70g + 四黄粉30g 调匀成膏",
        "preparation": "四黄各等份研细末，凡士林70g与四黄粉30g混合调匀成膏",
        "usage": "外敷患处",
        "frequency": "每日2-3次",
        "duration": "连续使用至红肿消退",
        "function": "清热消肿，凉血止痛",
        "indications": "内痔外痔发炎、水肿、术后疼痛，痈疽疔疖红肿",
        "syndrome_types": ["实热内蕴", "湿热下注", "热毒蕴结"],
        "disease_types": ["痔疮", "肛周脓肿", "肛门疖肿", "术后水肿"],
        "contraindications": "皮肤破损渗液较多者慎用",
        "precautions": "涂药前清洁患处；过敏者停用",
        "source": "原文·辅助治疗（原文第154-157行）",
        "priority": 90,
        "notes": "用于痔、痈、疽、疔、疖红肿的外敷要药",
    },
    {
        "name": "消肿止痛洗剂",
        "treatment_type": "fumigation",
        "composition": _c([
            ("瓦松", "g", 30), ("五倍子", "g", 30), ("马齿苋", "g", 30),
            ("艾叶", "g", 30), ("川椒", "g", 30),
        ]),
        "preparation": "上药煎水1000ml",
        "usage": "先熏后洗",
        "frequency": "每日1-2次",
        "duration": "连续使用至肿痛缓解",
        "function": "消肿止痛，收敛",
        "indications": "外痔发炎、血栓外痔、内痔脱出嵌顿、直肠脱垂及术后伤口水肿疼痛",
        "syndrome_types": ["湿热下注", "湿热瘀滞", "气滞血瘀"],
        "disease_types": ["痔疮", "血栓外痔", "直肠脱垂", "术后恢复"],
        "contraindications": "孕妇慎用；开放性创面较大者慎用",
        "precautions": "水温40-45℃，避免烫伤；药液不重复使用",
        "source": "经验方（原文第167-170行）",
        "priority": 100,
        "notes": "经验熏洗方，消肿止痛、收敛固脱",
    },

    # ============ 熏洗 fumigation ============
    {
        "name": "肛裂熏洗方",
        "treatment_type": "fumigation",
        "composition": _c([
            ("瓦松", "g", 30), ("苦参", "g", 30), ("马齿苋", "g", 30),
            ("川椒", "g", 15), ("防风", "g", 16), ("赤芍", "g", 16),
            ("黄柏", "g", 18),
        ]),
        "preparation": "上药加水煎煮，取药液约1000ml",
        "usage": "先熏后洗，每次20分钟",
        "frequency": "每日1-2次",
        "duration": "连续使用至疼痛出血缓解",
        "function": "清热利湿，消肿止痛",
        "indications": "肛裂便后疼痛、出血，括约肌痉挛",
        "syndrome_types": ["血热肠燥", "湿热"],
        "disease_types": ["肛裂"],
        "contraindications": "皮肤破损渗血较多者慎用",
        "precautions": "水温适宜，避免烫伤",
        "source": "原文·辅助治疗（原文第287行）",
        "priority": 88,
        "notes": "以熏洗缓解肛裂括约肌痉挛、消肿止痛",
    },
    {
        "name": "疣赘熏洗方",
        "treatment_type": "fumigation",
        "composition": _c([
            ("五倍子", "g", 20), ("马齿苋", "g", 30), ("土茯苓", "g", 30),
            ("板蓝根", "g", 30), ("赤芍", "g", 20), ("黄柏", "g", 20),
            ("白鲜皮", "g", 30),
        ]),
        "preparation": "上药加水煎煮，取药液外洗",
        "usage": "水煎外洗患处",
        "frequency": "每日1-2次",
        "duration": "连续使用至疣赘消退",
        "function": "清热解毒，利湿散结",
        "indications": "肛门疣赘（尖锐湿疣等）",
        "syndrome_types": ["湿热下注"],
        "disease_types": ["肛门疣赘"],
        "contraindications": "皮肤破溃感染者慎用",
        "precautions": "需配合专科病原学与病理检查，伴侣管理与随访按现行指南",
        "source": "原文·辅助治疗（原文第330行）",
        "priority": 80,
        "notes": "外洗配合内服与腐蚀疗法（如鸦胆子仁、枯痔散），须专科辨证",
    },
    {
        "name": "五味消毒饮熏洗",
        "treatment_type": "fumigation",
        "composition": _c([
            ("金银花", "g", 20), ("野菊花", "g", 15), ("蒲公英", "g", 15),
            ("紫花地丁", "g", 15), ("天葵子", "g", 10),
        ]),
        "preparation": "头二煎内服，第三煎加水煎煮后外洗",
        "usage": "取第三煎药液外洗疖肿患处",
        "frequency": "每日1-2次",
        "duration": "连续使用至疖肿消退",
        "function": "清热解毒，消肿排脓",
        "indications": "肛门疖肿（热毒型）",
        "syndrome_types": ["热毒蕴结"],
        "disease_types": ["肛门疖肿"],
        "contraindications": "虚寒型慎用",
        "precautions": "疖肿不可挤压，脓栓未脱时配合化腐散点顶",
        "source": "原文·辅助治疗（原文第355行）",
        "priority": 85,
        "notes": "以内服五味消毒饮、第三煎外洗同治热毒疖肿",
    },
    {
        "name": "直肠脱垂熏洗方",
        "treatment_type": "fumigation",
        "composition": _c([
            ("五倍子", "g", 10), ("白矾", "g", 15), ("朴硝", "g", 80),
            ("生甘草", "g", 10), ("薄荷", "g", 10),
        ]),
        "preparation": "上药加水煎汤",
        "usage": "每日熏洗两次",
        "frequency": "每日2次",
        "duration": "按疗程使用至脱垂缓解",
        "function": "收敛固脱，消肿利湿",
        "indications": "直肠脱垂、脱出肠段充血水肿糜烂",
        "syndrome_types": ["通用"],
        "disease_types": ["直肠脱垂"],
        "contraindications": "黏膜紫黑坏死者禁用",
        "precautions": "初诊方为乌梅10g、五倍子10g、草河车30g、生甘草10g；收敛后改本方",
        "source": "原文·验案处方（原文第400、405行）",
        "priority": 82,
        "notes": "外用熏洗收涩固脱，配合内服与收肛散外敷",
    },
    {
        "name": "湿疹洗剂",
        "treatment_type": "fumigation",
        "composition": _c([
            ("马齿苋", "g", 30), ("赤芍", "g", 15), ("地榆", "g", 20),
            ("苦参", "g", 30), ("白鲜皮", "g", 20), ("明矾", "g", 10),
            ("百部", "g", 80), ("川椒", "g", 10),
        ]),
        "preparation": "上药加水1500-2000ml煎煮，置温",
        "usage": "置温后坐浴，每次20分钟",
        "frequency": "每日2-3次",
        "duration": "连续使用至瘙痒渗出缓解",
        "function": "清热利湿，活血止痒",
        "indications": "肛门湿疹、肛门瘙痒",
        "syndrome_types": ["通用"],
        "disease_types": ["肛门湿疹"],
        "contraindications": "急性渗出伴感染重者需专科评估",
        "precautions": "忌热水烫洗、避免搔抓，忌辛辣刺激",
        "source": "原文·验方选论（原文第474-490行）",
        "priority": 78,
        "notes": "治疗顽固肛门湿疹瘙痒的验方，临证常获奇效",
    },

    # ============ 外敷 ointment ============
    {
        "name": "玉露膏",
        "treatment_type": "ointment",
        "composition": "芙蓉花叶晒干研末，用凡士林调匀成30%软膏",
        "preparation": "芙蓉花叶晒干研细末，与凡士林调匀成30%软膏",
        "usage": "外敷患处",
        "frequency": "每日2次",
        "duration": "连续使用至红肿消退",
        "function": "清热消肿，凉血解毒",
        "indications": "肛周脓肿急性期、疖肿红肿",
        "syndrome_types": ["热毒蕴结"],
        "disease_types": ["肛周脓肿", "肛门疖肿"],
        "contraindications": "成脓波动明显者应切开引流，不宜仅外敷",
        "precautions": "脓已成宜早期切开，不能以膏药替代引流",
        "source": "原文·辅助治疗（原文第239行）",
        "priority": 84,
        "notes": "用于肛痈、疖肿急性炎症期的外敷",
    },
    {
        "name": "金黄膏",
        "treatment_type": "ointment",
        "composition": _c([
            ("黄柏", "g", 60), ("大黄", "g", 60), ("姜黄", "g", 60),
            ("白芷", "g", 60), ("厚朴", "g", 25), ("陈皮", "g", 25),
            ("苍术", "g", 25), ("天南星", "g", 25), ("甘草", "g", 25),
            ("天花粉", "g", 30),
        ]),
        "preparation": "共研细末，以茶水调和外敷，或配成30%凡士林软膏",
        "usage": "外敷或贴敷患处",
        "frequency": "每日2次",
        "duration": "连续使用至肿消痛减",
        "function": "清热消肿，软坚散结",
        "indications": "肛周脓肿慢性/虚热型、肿块平塌者",
        "syndrome_types": ["虚热"],
        "disease_types": ["肛周脓肿"],
        "contraindications": "皮肤破溃处慎用",
        "precautions": "用于虚热型脓肿，配合内服青蒿鳖甲汤加减",
        "source": "原文·辅助治疗（原文第242行）",
        "priority": 76,
        "notes": "虚热型肛痈外敷首选，散瘀消肿",
    },
    {
        "name": "九华膏",
        "treatment_type": "ointment",
        "composition": "传统名方（黄连、黄柏、冰片、血竭、乳香、没药等，制为膏剂）",
        "preparation": "传统制膏法",
        "usage": "外敷裂口，每次2-3ml",
        "frequency": "每日1-2次",
        "duration": "连续使用至裂口愈合",
        "function": "消炎止痛，止血生肌",
        "indications": "新鲜肛裂",
        "syndrome_types": ["血热肠燥"],
        "disease_types": ["肛裂"],
        "contraindications": "感染化脓者慎用",
        "precautions": "配合通便、熏洗，打破便秘-疼痛恶性循环",
        "source": "传统名方（原文第288行）",
        "priority": 86,
        "notes": "以九华膏外敷治疗新鲜肛裂",
    },
    {
        "name": "利多卡因软膏（5%）",
        "treatment_type": "ointment",
        "composition": "5%利多卡因软膏",
        "preparation": "成品制剂",
        "usage": "外涂肛裂局部",
        "frequency": "按需",
        "duration": "疼痛缓解即止",
        "function": "局部止痛，缓解括约肌痉挛",
        "indications": "肛裂便后疼痛、括约肌痉挛",
        "syndrome_types": ["通用"],
        "disease_types": ["肛裂"],
        "contraindications": "对酰胺类局麻药过敏者禁用",
        "precautions": "避免大面积长期使用",
        "source": "现代药物（原文第290行）",
        "priority": 60,
        "notes": "辅助止痛，缓解肛裂括约肌痉挛",
    },
    {
        "name": "枯痔散",
        "treatment_type": "ointment",
        "composition": _c([
            ("白矾", "g", 60), ("白砒", "g", 6), ("硼砂", "g", 6),
            ("雄黄", "g", 6), ("硫黄", "g", 6),
        ]),
        "preparation": "分别研细，除硫黄外混匀入沙罐，纸封留孔，炭火煅制；药化声匀时自孔倾入硫黄，减低火力，声消取下冷却研末",
        "usage": "撒于疣赘表面（多发性疣每次用量<1g），周围涂凡士林保护；单发者以盐水调少许点于疣顶",
        "frequency": "每日换药1次",
        "duration": "至疣赘变黑变硬完全脱落，改敷生肌玉红膏",
        "function": "腐蚀疣赘，去腐生新",
        "indications": "肛门疣赘（尖锐湿疣、传染性软疣、扁平湿疣）",
        "syndrome_types": ["通用"],
        "disease_types": ["肛门疣赘"],
        "contraindications": "含白砒（砒霜），毒性反应明显者停用；孕妇禁用",
        "precautions": "密切观察砒霜毒性反应，如有及时停用；周围皮肤须涂凡士林保护",
        "source": "原文·辅助治疗（原文第323-327行）",
        "priority": 55,
        "notes": "历史腐蚀疗法，仅作院内专科学习；现代须按性病与皮肤专科规范评估",
    },
    {
        "name": "鸦胆子仁",
        "treatment_type": "ointment",
        "composition": "鸦胆子仁适量（捣烂）",
        "preparation": "取鸦胆子仁捣烂",
        "usage": "直接敷于疣赘顶端，保护周围健康皮肤",
        "frequency": "每日换药1次",
        "duration": "至疣赘完全脱落",
        "function": "腐蚀疣赘",
        "indications": "肛门疣赘（尖锐湿疣等）",
        "syndrome_types": ["湿热下注", "气滞血瘀"],
        "disease_types": ["肛门疣赘"],
        "contraindications": "周围皮肤须保护，避免灼伤",
        "precautions": "注意保护周围健康皮肤，避免腐蚀正常组织",
        "source": "原文·辅助治疗（原文第328-329行）",
        "priority": 58,
        "notes": "验案中配合内服萆薢渗湿汤/丹栀逍遥散治疗尖锐湿疣",
    },
    {
        "name": "化腐散",
        "treatment_type": "ointment",
        "composition": _c([
            ("红粉", "g", 5), ("朱砂", "g", 10), ("石膏", "g", 15),
            ("乳香", "g", 10), ("没药", "g", 10),
        ]),
        "preparation": "共研细末",
        "usage": "点于疖肿白头处促脓栓脱落；或调糊做成药条插入瘘道",
        "frequency": "每日1-2次",
        "duration": "至脓栓脱落/腐肉脱尽",
        "function": "化腐祛腐，排脓生新",
        "indications": "肛门疖肿脓栓、肛瘘换药化腐期",
        "syndrome_types": ["化腐期", "托毒期", "热毒蕴结"],
        "disease_types": ["肛门疖肿", "肛瘘"],
        "contraindications": "含红粉（氧化汞），汞过敏者禁用；孕妇禁用",
        "precautions": "红粉为含汞制剂，须专科掌握、严格限量",
        "source": "原文·处方（原文第460-462行）",
        "priority": 54,
        "notes": "即化腐生肌散，用于疖肿点顶与肛瘘药条换药",
    },
    {
        "name": "收肛散",
        "treatment_type": "ointment",
        "composition": "验方（收敛固脱之药，方从略）",
        "preparation": "制为散剂",
        "usage": "熏洗后将脱出直肠还纳，外敷收肛散，纱布垫加压固定于肛门两侧",
        "frequency": "每次便后及换药时",
        "duration": "脱垂回纳稳定后停用",
        "function": "收敛固脱，消肿利湿",
        "indications": "直肠脱垂脱出后回纳固定",
        "syndrome_types": ["中气下陷", "气血两虚"],
        "disease_types": ["直肠脱垂"],
        "contraindications": "黏膜紫黑坏死者禁用",
        "precautions": "需先还纳脱出肠段，配合内服升阳固脱",
        "source": "原文·验案处方（原文第402行）",
        "priority": 70,
        "notes": "以收肛散外敷并纱布加压固定，阻止再度脱出",
    },
    {
        "name": "红粉纱条",
        "treatment_type": "ointment",
        "composition": "红粉（升丹）药纱条",
        "preparation": "以红粉制剂浸制纱条",
        "usage": "置入创面/瘘道，蚀管祛腐",
        "frequency": "每日换药1次",
        "duration": "创面腐脱管化后停用",
        "function": "蚀管祛腐，保持引流",
        "indications": "肛瘘术后化腐期、腐败组织未尽",
        "syndrome_types": ["化腐期"],
        "disease_types": ["肛瘘"],
        "contraindications": "含汞制剂，汞过敏者禁用；孕妇禁用",
        "precautions": "红粉为含汞制剂，仅限专科换药、严格限量",
        "source": "原文·换药规律（原文第92行）",
        "priority": 52,
        "notes": "强调肛瘘术后初时宜重化腐，用红粉纱条蚀管祛腐",
    },
    {
        "name": "生肌玉红膏",
        "treatment_type": "ointment",
        "composition": _c([
            ("白芷", "g", 15), ("甘草", "g", 12), ("当归身", "g", 6),
            ("白蜡", "g", 12), ("轻粉", "g", 12), ("血竭", "g", 12),
            ("紫草", "g", 6), ("麻油", "ml", 500),
        ]),
        "preparation": "白芷等入麻油炸枯去渣，下白蜡，离火后入轻粉、血竭等细粉搅匀成膏",
        "usage": "清洁创面后涂抹或药纱覆盖",
        "frequency": "每日1-2次",
        "duration": "创面接近愈合时使用",
        "function": "活血化瘀，解毒生肌",
        "indications": "肛瘘术后生肌期、创面腐脱后肉芽生长",
        "syndrome_types": ["生肌期", "收口期"],
        "disease_types": ["肛瘘"],
        "contraindications": "感染化脓期不宜用",
        "precautions": "待腐脱管化后使用，防止过早封口形成假愈合",
        "source": "《外科正宗》（原文第92行）",
        "priority": 72,
        "notes": "术后换药规律：腐脱管化后改生肌玉红膏促进肉芽生长",
    },
    {
        "name": "盐水纱条",
        "treatment_type": "ointment",
        "composition": "生理盐水浸润纱条",
        "preparation": "以无菌生理盐水浸润无菌纱条",
        "usage": "换药时敷于创面",
        "frequency": "每日换药1次",
        "duration": "肉芽水肿消退后停用",
        "function": "消肿，促进肉芽新鲜",
        "indications": "肛瘘术后肉芽生长不良、水肿",
        "syndrome_types": ["生肌期"],
        "disease_types": ["肛瘘"],
        "contraindications": "无特殊",
        "precautions": "经验：肉芽水肿时用盐水纱条换药",
        "source": "原文·换药规律（原文第92行）",
        "priority": 60,
        "notes": "用于肉芽生长不良和水肿，促进肉芽新鲜消肿",
    },
    {
        "name": "珍珠散",
        "treatment_type": "ointment",
        "composition": "传统名方（珍珠、冰片、血竭等，制为散剂）",
        "preparation": "制为散剂",
        "usage": "撒敷于瘢痕中心不易愈合的小创面",
        "frequency": "每日换药1次",
        "duration": "至创面愈合",
        "function": "生肌敛口",
        "indications": "肛瘘术后瘢痕中心小创面久不愈合（排除假愈合后）",
        "syndrome_types": ["收口期"],
        "disease_types": ["肛瘘"],
        "contraindications": "未排除假愈合者禁用",
        "precautions": "须先排除假愈合，再以珍珠散收口",
        "source": "传统名方（原文第92行）",
        "priority": 58,
        "notes": "用于瘢痕中心小创面难愈，排除假愈合后外用常获良效",
    },

    # ============ 栓剂 suppository ============
    {
        "name": "消炎痛栓",
        "treatment_type": "suppository",
        "composition": "吲哚美辛栓（成品）",
        "preparation": "成品制剂",
        "usage": "纳入肛内，每次1粒",
        "frequency": "每日1-2次",
        "duration": "疼痛缓解即止",
        "function": "消炎止痛，止血",
        "indications": "肛裂疼痛、内痔出血",
        "syndrome_types": ["血热肠燥", "湿热"],
        "disease_types": ["肛裂"],
        "contraindications": "消化性溃疡、阿司匹林过敏者慎用",
        "precautions": "按说明书使用，注意胃肠道不良反应",
        "source": "现代药物（原文第288行）",
        "priority": 62,
        "notes": "用于肛裂消炎止痛止血",
    },

    # ============ 注射 injection（仅院内专科，不自动下发） ============
    {
        "name": "6%明矾液注射疗法",
        "treatment_type": "injection",
        "composition": _c([("明矾", "g", 6), ("注射用水", "ml", 100)]),
        "preparation": "明矾6g溶于100ml注射用水中，煮沸消毒，冷却备用",
        "usage": "成人完全性直肠脱垂：6%明矾液于直肠黏膜下多点注射",
        "frequency": "按疗程由专科执行",
        "duration": "按病情决定",
        "function": "酸可收敛，涩可固脱",
        "indications": "成人完全性直肠脱垂（1981年部级鉴定，全愈率99.5%）",
        "syndrome_types": ["中气下陷", "气血两虚", "肾虚不固"],
        "disease_types": ["直肠脱垂"],
        "contraindications": "黏膜坏死、感染、孕妇等",
        "precautions": "严格无菌、层次准确，仅限资质人员执行",
        "source": "经验方（原文第88-89行）",
        "priority": 50,
        "notes": "创新疗法，成人完全性直肠脱垂非手术治疗的里程碑",
    },
    {
        "name": "肛裂封闭疗法",
        "treatment_type": "injection",
        "composition": "0.25%布比卡因6ml（长强穴扇形注射）；或亚甲蓝0.26g+地卡因0.2g+蒸馏水加至100ml（局部封闭）",
        "preparation": "按无菌原则配制",
        "usage": "布比卡因于长强穴扇形注射；或亚甲蓝地卡因液局部封闭，每次5-10ml",
        "frequency": "布比卡因隔日一次，5次一疗程；亚甲蓝每周1-2次",
        "duration": "按疗程",
        "function": "止痛，缓解括约肌痉挛",
        "indications": "肛裂顽固疼痛、括约肌痉挛",
        "syndrome_types": ["通用"],
        "disease_types": ["肛裂"],
        "contraindications": "对局麻药过敏者禁用",
        "precautions": "仅限专科医师执行，注意无菌与过敏反应",
        "source": "原文·辅助治疗（原文第291行）",
        "priority": 48,
        "notes": "用于缓解肛裂疼痛与括约肌痉挛的封闭疗法",
    },
]

# 修正既有条目：玉红膏 → 生肌玉红膏（名称对齐原文）
RENAME_MAP = {"玉红膏": "生肌玉红膏"}


async def main():
    async with AsyncSessionLocal() as session:
        print("=" * 64)
        print("原著「外治法/外用药」完整补全")
        print("=" * 64)

        # 1. 地槐止血丸为内服丸，从外治法表移除，并在方剂表中标注 internal
        result = await session.execute(
            select(ExternalTreatment).where(ExternalTreatment.name == "地槐止血丸")
        )
        herb_pill = result.scalar_one_or_none()
        if herb_pill:
            await session.execute(delete(ExternalTreatment).where(ExternalTreatment.id == herb_pill.id))
            print("移除误归为外治的 地槐止血丸（内服丸）")
        fresult = await session.execute(
            select(AnorectalFormula).where(AnorectalFormula.name == "地槐止血丸")
        )
        fp = fresult.scalar_one_or_none()
        if fp and fp.formula_type != "internal":
            fp.formula_type = "internal"
            print("标注 地槐止血丸 为内服方（internal）")

        # 2. 修正既有条目的名称与映射
        for old, new in RENAME_MAP.items():
            r = await session.execute(select(ExternalTreatment).where(ExternalTreatment.name == old))
            t = r.scalar_one_or_none()
            if t:
                t.name = new
                print(f"重命名 {old} -> {new}")

        # 3. 补充缺失外治法
        for data in TREATMENTS:
            r = await session.execute(select(ExternalTreatment).where(ExternalTreatment.name == data["name"]))
            t = r.scalar_one_or_none()
            if t:
                for key, value in data.items():
                    setattr(t, key, value)
                print(f"更新外治法 {data['name']}")
            else:
                session.add(ExternalTreatment(**data))
                print(f"新增外治法 {data['name']}")

        await session.commit()
        print("\n✅ 外治法补全完成。")


if __name__ == "__main__":
    asyncio.run(main())
