"""临床经验原文的可追溯知识层。

这里保存的是从仓库内《临床经验原文.txt》逐段整理出的临床要点，
用于解释规则命中和阶段性处置；它不是新的诊断模型，也不替代专科检查。
"""
from typing import Any, Dict, List

from app.services.zhou_coverage import build_clinical_assessment
from app.services.differential_diagnosis import get_differentials
from app.services.procedures import get_acupuncture, get_surgical_techniques


SOURCE = "《临床经验原文.txt》（中医临床经验总结）"

GENERAL_PRINCIPLES = [
    "四诊合参，先辨阴阳，再分表里、虚实、寒热，并结合局部肿痛脓痒辨病辨证。",
    "痔病多见湿、热、风、燥与瘀滞；实证祛邪，虚证扶正但不可忘记局部清热、和血。",
    "强调整体防病与内外合治：急则治标，缓则治本；有诸内必形诸外。",
    "创面处理遵循“脓毒宜泄，新肉宜生，腐肉宜除”，按阶段换药。",
]


SYNDROME_NOTES: Dict[str, Dict[str, Any]] = {
    "ZC_SHINY": {
        "source_status": "original_explicit",
        "basis": "口渴、唇燥咽干、小便短赤、大便秘结，便时疼痛出血，肛门灼热红肿，舌红苔黄燥，脉洪大或弦数。",
        "principle": "清热润燥，止血通便；槐花散加味与地榆散加味可交替、互相化裁。",
        "stage": "以便秘、出血、疼痛为主的各期内痔、混合痔、炎性外痔。",
        "source_sections": ["原文第130-134行", "原文第181-186行"],
    },
    "ZC_SRXZ": {
        "source_status": "original_explicit",
        "basis": "腹胀纳呆、便秘溲赤、肛门坠胀疼痛、肛门凸突红肿、结节宿滞不散，舌苔腻、脉弦。",
        "principle": "清热除湿，活血化瘀；热象退而瘀滞存时转用活血散瘀汤思路。",
        "stage": "血栓外痔、静脉曲张性外痔、嵌顿性内痔。",
        "source_sections": ["原文第135-138行", "原文第187-193行"],
    },
    "ZC_VHAN": {
        "source_status": "original_explicit",
        "basis": "身倦神疲、面色晄白、大便稀软、小便清长、食少腹胀，内痔脱出、便血晦暗，舌淡苔白，脉沉迟或细弱。",
        "principle": "健脾温中，固脱止血；归脾汤加减与黄芪建中汤加减可交替。",
        "stage": "内痔脱出严重、长期便血、消化不良或腹泻。",
        "source_sections": ["原文第139-142行"],
    },
    "ZC_QXKS": {
        "source_status": "original_explicit",
        "basis": "便血日久、面色无华、气短心悸、少气懒言、食少，肛门坠重、痔脱难收，脉细弱、舌淡。",
        "principle": "补气益血；强调“有形之血不能速生，无形之气所当急固”。",
        "stage": "产后、久病或长期失血所致气血双亏；虚中兼湿热时佐以清热和血。",
        "source_sections": ["原文第143-147行", "原文第194-198行"],
    },
    "GL_XRCZ": {
        "source_status": "original_explicit",
        "basis": "便秘、便时出血、便后疼痛，口苦咽干、心烦，舌苔黄燥、脉滑数。",
        "principle": "凉血润燥，止血止痛；肛裂治疗不可脱离通便。",
        "stage": "火燥证/血热肠燥，适用于新鲜裂伤的内治方向。",
        "source_sections": ["原文第286-304行"],
    },
    "GL_SR": {
        "source_status": "original_explicit",
        "basis": "大便秘结、肛门坠胀，便后持续疼痛，偶有脓汁或黏液，苔腻、脉数。",
        "principle": "清热利湿，润燥止痛，方宗止痛如神汤加减。",
        "stage": "湿热证；出现溃疡、皮赘、隐瘘或括约肌痉挛时需专科评估陈旧性肛裂。",
        "source_sections": ["原文第286-304行"],
    },
    "GZ_RTYJ": {
        "source_status": "original_explicit",
        "basis": "起病急、进展快、肿块高突红热、疼痛剧烈，可伴发热寒战、便秘，舌红苔黄燥，脉浮数洪大。",
        "principle": "初起未成脓可审证消之；成脓则因势逐之，不能以口服方替代引流。",
        "stage": "实热型肛痈；触及波动、脓已成或深部脓肿时当日专科评估。",
        "source_sections": ["原文第199-215行", "原文第229-248行"],
    },
    "GZ_XR": {
        "source_status": "original_explicit",
        "basis": "起病缓、病程长、肿块平塌或暗红、疼痛不剧、低热不著，神疲或五心烦热，脉细弱。",
        "principle": "清虚热，散毒气；正气渐复、毒邪外出后可酌加活血消散。",
        "stage": "虚热型/阴精亏虚肛痈，仍需排除深部脓腔和混合感染。",
        "source_sections": ["原文第229-248行", "原文第408-425行"],
    },
    "ZC_ZQXX": {
        "source_status": "original_explicit",
        "basis": "脱垂伴气短乏力、食少便溏、舌淡或胖大齿痕，脉虚弱。",
        "principle": "补中益气，升阳举陷；根据病因区分气虚、气血两虚、肺虚咳喘、肾虚失摄。",
        "stage": "中气下陷型脱垂；儿童、老人、久泻患者尤其要询问病因。",
        "source_sections": ["原文第372-407行", "原文第503-505行"],
    },
    "ZC_QXLX": {
        "source_status": "original_explicit",
        "basis": "产后或长期失血后脱垂，面色萎黄、头晕、寐少，舌淡红苔薄白。",
        "principle": "调荣养血，益气固脱；内服与局部收敛、提肛训练并用。",
        "stage": "气血两虚型脱垂，需记录脱出长度、能否还纳及黏膜损伤。",
        "source_sections": ["原文第372-407行"],
    },
    "ZC_FXKC": {
        "source_status": "original_explicit",
        "basis": "慢性咳喘、动则气短，舌淡苔白滑，脉沉细略滑并有脱垂。",
        "principle": "温肺益气，定喘固脱；肺与大肠相表里。",
        "stage": "肺虚咳喘、肠寒脱垂型。",
        "source_sections": ["原文第372-407行"],
    },
    "ZCTH_SG": {
        "source_status": "original_explicit",
        "basis": "腰膝酸软、身寒肢冷、尿频、体倦无力等肾虚不固表现，兼见脱垂。",
        "principle": "补肾纳气，温阳固脱。",
        "stage": "原著指出肾虚患者亦可发生直肠脱垂，需审证求因。",
        "source_sections": ["原文第374行", "原文第384-385行"],
    },
    "ZCTH_XE": {
        "source_status": "original_explicit",
        "basis": "小儿先天不足、气血未壮，常因腹泻后便时脱出，面色淡、食少便溏。",
        "principle": "补中益气，升阳举陷；同时调治原发腹泻。",
        "stage": "儿童脱垂需记录年龄、腹泻频次、脱出长度和黏膜损伤，不能照搬成人剂量。",
        "source_sections": ["原文第374-377行"],
    },
    "ZCTH_SR": {
        "source_status": "original_explicit",
        "basis": "脱垂伴肛门下坠肿痛、小便淋漓、胸闷口苦口腻、脉滑数等湿热努挣表现。",
        "principle": "清利湿热，通便降浊，兼顾升提。",
        "stage": "湿热便秘努挣所致者不能一味补益，应先审查便秘和湿热。",
        "source_sections": ["原文第385行", "原文第407行"],
    },
    "GL_HFQ": {
        "source_status": "original_explicit",
        "basis": "肛瘘术后创面腐败组织未尽，原著强调初时宜重化腐、保持引流。",
        "principle": "化腐祛腐，保持引流；具体换药仅限受控专科操作。",
        "stage": "化腐期，不提供红粉等腐蚀性制剂的自行操作参数。",
        "source_sections": ["原文第91-92行", "原文第460-463行"],
    },
    "GL_TDQ": {
        "source_status": "original_explicit",
        "basis": "肛瘘中期脓液未尽，需托里透脓、清化湿热，防止支管和死腔残留。",
        "principle": "托毒外出，评估主管、支管和死腔，防止假愈合。",
        "stage": "托毒期，换药和引流由专科人员实施。",
        "source_sections": ["原文第91-92行", "原文第463-465行", "原文第472行"],
    },
    "GL_SJQ": {
        "source_status": "original_explicit",
        "basis": "腐脱管化、脓出渐尽后进入新肉芽生长阶段。",
        "principle": "生肌长肉，促进创面修复。",
        "stage": "生肌期，需先确认腐肉已脱、管道已化，防止过早封口。",
        "source_sections": ["原文第91-92行", "原文第465-471行"],
    },
    "GL_SQK": {
        "source_status": "original_explicit",
        "basis": "创面接近愈合时，原著特别要求检查桥形粘连和假愈合。",
        "principle": "审查残余窦道和桥形粘连，审慎收口。",
        "stage": "收口期，需确认无支管残留、无假愈合后再结束换药。",
        "source_sections": ["原文第92行", "原文第465-471行"],
    },
    "GL_XRNY": {
        "source_status": "original_case",
        "basis": "反复外口流脓，病程久，面色无华、神疲乏力、脉细弱，见内口和瘘道。",
        "principle": "初期轻剂解散，中期托里透脓、清化湿热，邪尽后补气养血、生肌敛口。",
        "stage": "肛瘘必须明确内口、主管、支管和死腔；挂线、探查及换药均属专科操作。",
        "source_sections": ["原文第447-472行"],
    },
    "YZ_SRXZ": {
        "source_status": "original_explicit",
        "basis": "肛门潮湿瘙痒、疣表面糜烂渗出较多、味臭、基底潮红，大便干结、小便赤黄，舌红苔黄腻、脉弦。",
        "principle": "清热解毒，利湿散结，方宗萆薢渗湿汤。",
        "stage": "尖锐湿疣、扁平湿疣等属湿热下注者；需结合病原学/病理与现行性病防治规范。",
        "source_sections": ["原文第316-317行", "原文第332-337行"],
    },
    "YZ_GSYX": {
        "source_status": "original_explicit",
        "basis": "肛门周围干涩不适、面色无华、虚烦失眠、耳鸣目涩、头晕健忘、口干咽燥、五心烦热，舌红苔少、脉细数。",
        "principle": "滋补肝肾，方宗杞菊地黄汤。",
        "stage": "肝肾阴虚型疣赘；需结合专科检查排除性病与免疫因素。",
        "source_sections": ["原文第318-319行"],
    },
    "YZ_QXZH": {
        "source_status": "original_explicit",
        "basis": "肛周疣赘丛生、时疼时痒、烦躁易怒、胸胁胀满，妇女月经不调、痛经或经色紫暗有块，舌暗红苔少、脉涩。",
        "principle": "行气活血，方宗丹栀逍遥散。",
        "stage": "气滞血瘀型疣赘；情志与月经情况是辨证要点。",
        "source_sections": ["原文第320-321行", "原文第338-342行"],
    },
    "JZ_RDYJ": {
        "source_status": "original_explicit",
        "basis": "皮肤圆形小结逐渐增大、根硬而痛、表面焮热，可伴恶寒发热、口干，舌苔黄腻、脉滑数。",
        "principle": "清热解毒，方宗五味消毒饮；外用以化腐散点顶、玉露膏或四黄膏围敷。",
        "stage": "热毒疖肿；脓栓未脱或引流不畅时疼痛明显，不可挤压。",
        "source_sections": ["原文第350-355行", "原文第362-367行"],
    },
    "JZ_SRJB": {
        "source_status": "original_explicit",
        "basis": "病程日久、皮下走窜、此愈彼发、脓水不断，食少纳呆、夜寐不安、头昏脑胀，苔白腻、脉弦滑。",
        "principle": "清热利湿，方宗黄芩滑石汤加减。",
        "stage": "湿热疖肿；需排查糖尿病等原发病，防止反复发作。",
        "source_sections": ["原文第353-354行", "原文第368-371行"],
    },
}


DISEASE_DECISION_POINTS: Dict[str, List[str]] = {
    "痔疮": [
        "先分内痔、外痔、混合痔及内痔分期；早期内痔以保持大便通畅为主。",
        "便后脱出应记录能否自行还纳、需否手托以及是否出现紫暗、糜烂、嵌顿。",
        "出血、晚期脱出、嵌顿或贫血表现需要肛肠专科检查，不以方药替代肛门镜。",
    ],
    "肛周脓肿": [
        "先判断实热/虚热，再判断脓肿深浅：骨盆直肠窝、直肠后、黏膜下、坐骨直肠窝及皮下位置不同。",
        "波动感、进行性红肿热痛、发热或尿潴留提示脓已成/深部感染，需及时引流评估。",
        "高位脓肿处理要保护括约肌和肛提肌；炎症消退、瘘管固定后再评估二次处理。",
    ],
    "肛裂": [
        "新鲜裂口表浅鲜红；陈旧裂口可见溃疡、皮赘、肛窦/肛乳头肥大、隐瘘或括约肌痉挛。",
        "便秘、疼痛、出血互为因果，首要目标是软化大便并打破恶性循环。",
        "侧方、多发、久不愈或伴肿块流脓的裂口要鉴别炎症性肠病、肿瘤及其他肛周病变。",
    ],
    "肛瘘": [
        "评估外口数量、分泌物、内口、主管/支管和死腔；反复流脓不等于单纯皮肤病。",
        "术后创面按化腐期、生肌期、收口期分阶段换药，防止支管残留和桥形假愈合。",
        "高位、复杂、复发性肛瘘需影像和有经验团队处理，保护括约肌功能。",
    ],
    "直肠脱垂": [
        "记录脱出长度、黏膜/全层、能否自行还纳及水肿糜烂出血；并追问久泻、咳喘、产后和肾虚表现。",
        "虚证虽多，但要审证求因；湿热便秘努挣所致者不能一味补益。",
        "不能回纳、紫黑剧痛、黏膜坏死或大量出血属于急症，注射/手术只能由专科实施。",
    ],
}


def build_original_knowledge(
    disease_type: str, syndrome: Dict[str, Any], symptoms: Dict[str, Any]
) -> Dict[str, Any]:
    """将证型、病种和当前资料组合成可追溯的原著依据。"""
    code = syndrome.get("syndrome_code")
    note = SYNDROME_NOTES.get(code)
    knowledge: Dict[str, Any] = {
        "source": SOURCE,
        "source_status": note.get("source_status", "system_extension") if note else "system_extension",
        "general_principles": GENERAL_PRINCIPLES,
        "disease_decision_points": DISEASE_DECISION_POINTS.get(disease_type, []),
        "source_sections": note.get("source_sections", []) if note else [],
        "basis": note.get("basis") if note else "本证型未在当前原文摘录中找到逐字对应条目，属于系统扩展规则，需人工复核。",
        "principle": note.get("principle") if note else syndrome.get("treatment_principle"),
        "stage_guidance": note.get("stage") if note else "请补充病程、局部检查和舌脉后由医师判断阶段。",
        "clinical_assessment": build_clinical_assessment(disease_type, symptoms),
        "differential_diagnosis": get_differentials(disease_type),
        "acupuncture": get_acupuncture(disease_type),
        "surgical_techniques": get_surgical_techniques(disease_type),
    }

    # 原著的阶段信息需要由当前四诊资料触发，防止把“未成脓”和“成脓”混为一谈。
    if disease_type == "肛周脓肿":
        abscess = symptoms.get("abscess") or {}
        fluctuant = abscess.get("fluctuant") if isinstance(abscess, dict) else symptoms.get("fluctuant")
        if fluctuant is True or symptoms.get("pus_formed") is True:
            knowledge["current_stage"] = "疑似成脓/已有波动：原著主张早期引流，立即专科评估。"
        elif fluctuant is False or symptoms.get("pus_formed") is False:
            knowledge["current_stage"] = "目前资料偏向未成脓：可在专科观察下内外合治，并密切复评。"
        else:
            knowledge["current_stage"] = "尚未记录波动感/成脓状态：不能据此决定消散还是引流。"
    elif disease_type == "肛裂":
        duration = symptoms.get("duration_days") or symptoms.get("fissure_duration_days")
        chronic = symptoms.get("chronic_fissure") or symptoms.get("ulcer") or symptoms.get("skin_tag")
        if chronic or (isinstance(duration, (int, float)) and duration >= 42):
            knowledge["current_stage"] = "资料提示陈旧/迁延可能：需检查溃疡、皮赘、隐瘘、肛管狭窄和括约肌痉挛。"
        else:
            knowledge["current_stage"] = "资料偏向新鲜裂伤或病程未明：先以通便、止痛、局部护理为核心。"
    elif disease_type == "肛瘘":
        phase = symptoms.get("wound_phase")
        phase_map = {
            "腐肉": "化腐期：专科换药，目标是清除腐败组织、保持引流。",
            "脓液": "托毒期：评估支管和死腔，避免假愈合。",
            "肉芽": "生肌期：腐脱管化后再促进肉芽生长。",
            "收口": "收口期：检查桥形粘连和残余窦道。",
        }
        knowledge["current_stage"] = phase_map.get(phase, "需记录创面腐肉、脓液、肉芽及收口状态后决定换药阶段。")
    elif disease_type == "痔疮":
        prolapse = symptoms.get("prolapse_symptom") or {}
        if isinstance(prolapse, dict) and prolapse.get("present"):
            knowledge["current_stage"] = "请明确脱出后能否自行还纳、是否需手托及有无紫暗糜烂，以排除嵌顿。"
        else:
            knowledge["current_stage"] = "先按便血、便秘、疼痛和局部炎症判断证候；早期内痔以通便调护为先。"
    elif disease_type == "直肠脱垂":
        knowledge["current_stage"] = "请记录脱出长度、黏膜损伤和回纳情况，并追问久泻、咳喘、产后及肾虚病因。"
    return knowledge
