"""《临床经验原文》的结构化覆盖与专科核对层。"""
from typing import Any, Dict, List


SOURCE_TOTAL_LINES = 518


COVERAGE_MATRIX: List[Dict[str, Any]] = [
    {
        "section": "学术思想与辨证总则",
        "lines": "72-93",
        "status": "structured",
        "integrations": ["辨证依据", "阶段判断", "治疗路径", "便秘七型辨证", "肛门湿疹/瘙痒辨证"],
        "included": ["四诊合参", "八纲辨证", "内外合治", "创面分期", "手术与换药原则", "便秘七型", "肛门瘙痒（补中益气丸合三妙丸）"],
        "remaining": [],
    },
    {
        "section": "痔疮证治",
        "lines": "95-198",
        "status": "structured",
        "integrations": ["辨证规则", "形态分型", "内痔分期", "鉴别提示", "方剂", "医案", "手术技法"],
        "included": ["外痔四型", "内痔三期", "混合痔", "四类证候", "主要鉴别", "原文证治方", "外剥内扎/保留皮桥/枯痔/明矾注射"],
        "remaining": [],
    },
    {
        "section": "肛周脓肿证治",
        "lines": "199-261",
        "status": "structured",
        "integrations": ["辨证规则", "部位判断", "成脓分期", "鉴别提示", "治疗路径", "手术技法"],
        "included": ["深浅部位六类", "实热/虚热", "未成脓/成脓", "六类鉴别", "早期切开/粘膜下切开/高位处理/遗留瘘管"],
        "remaining": ["解剖影像不能由规则替代"],
    },
    {
        "section": "肛裂证治",
        "lines": "262-304",
        "status": "structured",
        "integrations": ["辨证规则", "新鲜/陈旧分期", "局部检查", "鉴别提示", "方剂"],
        "included": ["火燥证", "湿热证", "皮赘/隐瘘/乳头肥大/狭窄", "肛缘皲裂鉴别"],
        "remaining": ["封闭疗法仅作院内受控学习资料"],
    },
    {
        "section": "肛门疣赘证治",
        "lines": "305-342",
        "status": "partial",
        "integrations": ["辨证规则", "形态鉴别", "治疗边界"],
        "included": ["尖锐湿疣", "传染性软疣", "扁平湿疣形态", "病理/病原学核对"],
        "remaining": ["现代性病筛查与伴侣管理需按现行指南完善", "腐蚀性历史疗法不进入通用执行方案"],
    },
    {
        "section": "肛门疖肿证治",
        "lines": "343-371",
        "status": "structured",
        "integrations": ["辨证规则", "病程分流", "鉴别提示", "治疗路径"],
        "included": ["热毒型", "湿热型", "单发/多发", "脓栓/窦道", "基础病核对"],
        "remaining": ["化脓性汗腺炎仍需专科确诊"],
    },
    {
        "section": "直肠脱垂证治",
        "lines": "372-407",
        "status": "structured",
        "integrations": ["辨证规则", "脱垂检查", "治疗路径", "医案"],
        "included": ["中气下陷", "气血两虚", "肺虚咳喘", "肾虚失摄", "小儿气虚", "湿热下注"],
        "remaining": ["明矾注射仅作院内受控学习资料"],
    },
    {
        "section": "医案述评",
        "lines": "386-472",
        "status": "structured",
        "integrations": ["医案库", "原文证候依据", "复诊阶段", "方意按语"],
        "included": ["脱垂案", "虚热肛痈案", "嵌顿痔案", "复杂肛瘘案", "复诊加减与方意"],
        "remaining": ["历史腐蚀性外治不进入通用执行方案"],
    },
    {
        "section": "验方选论",
        "lines": "473-505",
        "status": "structured",
        "integrations": ["方剂库", "外治法", "医案库", "针刺法模块"],
        "included": ["湿疹洗剂", "复方痔疮栓", "针灸治疗脱肛（虚实分型选穴）"],
        "remaining": ["针灸操作须由专业资质人员执行，系统仅提供选穴方案"],
    },
    {
        "section": "生平、成果与继承人资料",
        "lines": "1-71、506-518",
        "status": "reference_only",
        "integrations": ["原文资料"],
        "included": ["学术生平", "科研成果", "论文专著目录"],
        "remaining": ["属于学术史资料，不参与患者辨证"],
    },
]


def coverage_report() -> Dict[str, Any]:
    counts = {"structured": 0, "partial": 0, "reference_only": 0}
    for item in COVERAGE_MATRIX:
        counts[item["status"]] += 1
    return {
        "source": "《临床经验原文.txt》",
        "source_total_lines": SOURCE_TOTAL_LINES,
        "summary": counts,
        "definition": {
            "structured": "已形成系统字段、规则或可追溯治疗路径",
            "partial": "已有知识条目，但仍有内容未形成完整决策流程",
            "reference_only": "保留原文用于查阅，不参与临床规则",
        },
        "honesty_notice": "覆盖状态表示结构化程度，不表示系统可替代面诊、专科检查或医师处方审核。",
        "sections": COVERAGE_MATRIX,
    }


def _present(value: Any) -> bool:
    if isinstance(value, dict):
        return bool(value.get("present"))
    return bool(value) and value not in {"无", "未见", "未查"}


def build_clinical_assessment(disease_type: str, symptoms: Dict[str, Any]) -> Dict[str, Any]:
    """根据原文的病种形态与检查要点生成核对结果，不替代确诊。"""
    result: Dict[str, Any] = {
        "classification": [],
        "differential_alerts": [],
        "missing_checks": [],
        "source_sections": [],
    }

    if disease_type == "痔疮":
        subtype = symptoms.get("hemorrhoid_subtype")
        degree = (symptoms.get("prolapse_symptom") or {}).get("degree")
        if subtype:
            result["classification"].append(f"当前记录形态：{subtype}。需结合齿线关系和肛门镜确认。")
        if degree == "I度":
            result["classification"].append("对应原著初期内痔线索：便血而无脱出。")
        elif degree == "II度":
            result["classification"].append("对应原著中期内痔线索：便时脱出、便后自行回纳。")
        elif degree in {"III度", "IV度"}:
            result["classification"].append("对应原著晚期内痔/嵌顿风险线索：需手托或不能回纳。")
        if symptoms.get("mass_surface") in {"粗糙菜花样", "质硬固定"} or symptoms.get("blood_mixed_in_stool"):
            result["differential_alerts"].append("不能按痔疮处理：需排除直肠肿瘤并完成指检、内镜及必要病理检查。")
        if symptoms.get("purulent_opening"):
            result["differential_alerts"].append("肿块伴流脓小孔更符合肛瘘外口线索，需检查内口和瘘管。")
        for key, label in (("hemorrhoid_subtype", "内痔/外痔/混合痔及外痔亚型"), ("dentate_relation", "齿线关系"), ("anoscopy_finding", "肛门镜所见")):
            if not symptoms.get(key):
                result["missing_checks"].append(label)
        result["source_sections"] = ["原文第99-128行"]

    elif disease_type == "肛周脓肿":
        location = symptoms.get("abscess_location")
        if location:
            depth = "深部" if location in {"骨盆直肠窝", "直肠后", "黏膜下"} else "浅部"
            result["classification"].append(f"记录部位为{location}，原著归为{depth}脓肿；必须结合指检和影像确认范围。")
        if symptoms.get("fluctuant") is True or symptoms.get("pus_formed") is True:
            result["classification"].append("已有波动/成脓线索，进入及时引流评估阶段。")
        if symptoms.get("rapid_spread") or symptoms.get("crepitus"):
            result["differential_alerts"].append("迅速扩散或捻发感属于严重感染警讯，应立即急诊评估，不等待辨证用药。")
        if not location:
            result["missing_checks"].append("脓肿解剖部位与深浅")
        if symptoms.get("fluctuant") is None:
            result["missing_checks"].append("波动感/是否成脓")
        result["source_sections"] = ["原文第199-248行"]

    elif disease_type == "肛裂":
        chronic_signs = [key for key in ("ulcer", "skin_tag", "hypertrophied_papilla", "hidden_fistula", "anal_stenosis") if symptoms.get(key)]
        duration = symptoms.get("duration_days")
        if chronic_signs or isinstance(duration, (int, float)) and duration >= 42:
            result["classification"].append("存在陈旧性肛裂线索，需评估溃疡、皮赘、隐瘘、乳头肥大和狭窄。")
        elif duration:
            result["classification"].append("病程和局部资料偏向新鲜肛裂。")
        if symptoms.get("fissure_location") in {"左侧", "右侧", "多发"}:
            result["differential_alerts"].append("侧方或多发裂口不符合常见原著形态，需排查炎症性肠病、感染和肿瘤。")
        for key, label in (("fissure_location", "裂口位置"), ("duration_days", "病程天数"), ("sphincter", "括约肌状态")):
            if symptoms.get(key) in (None, ""):
                result["missing_checks"].append(label)
        result["source_sections"] = ["原文第265-290行"]

    elif disease_type == "直肠脱垂":
        layer = symptoms.get("prolapse_layer")
        length = symptoms.get("prolapse_length_cm")
        if layer or length:
            result["classification"].append(f"脱垂记录：{layer or '层次未明'}，长度{length if length not in (None, '') else '未测'}厘米。")
        if symptoms.get("reducibility") == "不能回纳" or symptoms.get("mucosal_injury") in {"紫黑", "坏死"}:
            result["differential_alerts"].append("不能回纳或黏膜紫黑/坏死属于急症，应立即专科处置。")
        for key, label in (("prolapse_layer", "黏膜或全层脱垂"), ("prolapse_length_cm", "脱出长度"), ("reducibility", "回纳情况"), ("mucosal_injury", "黏膜充血/水肿/糜烂")):
            if symptoms.get(key) in (None, ""):
                result["missing_checks"].append(label)
        result["source_sections"] = ["原文第372-407行"]

    elif disease_type == "肛瘘":
        phase = symptoms.get("wound_phase")
        if phase:
            result["classification"].append(f"当前创面阶段：{phase}。换药目标应随腐肉、脓液、肉芽和收口状态调整。")
        if symptoms.get("bridge_adhesion"):
            result["differential_alerts"].append("发现桥形粘连/表面先合线索，需排除残腔和假愈合。")
        for key, label in (("external_opening_count", "外口数量"), ("internal_opening", "内口"), ("main_tract", "主管走向"), ("branch_tract", "支管"), ("dead_space", "死腔"), ("fistula_level", "高位/低位"), ("fistula_complexity", "单纯/复杂/复发")):
            if symptoms.get(key) in (None, ""):
                result["missing_checks"].append(label)
        result["source_sections"] = ["原文第90-93行", "原文第447-472行"]

    return result
