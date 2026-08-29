"""
用药安全检查服务 - 配伍禁忌、妊娠禁忌、剂量检查
"""
from typing import Dict, List, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.diagnosis import SafetyRule


# 十八反配伍禁忌（经典中医理论）
EIGHTEEN_INCOMPATIBILITIES = {
    "甘草": ["甘遂", "大戟", "海藻", "芫花"],
    "乌头": ["贝母", "瓜蒌", "半夏", "白蔹", "白及"],
    "藜芦": ["人参", "沙参", "丹参", "玄参", "细辛", "芍药"],
}

# 十九畏配伍禁忌
NINETEEN_FEARS = {
    "硫黄": ["朴硝"],
    "水银": ["砒霜"],
    "狼毒": ["密陀僧"],
    "巴豆": ["牵牛子"],
    "丁香": ["郁金"],
    "牙硝": ["三棱"],
    "川乌": ["犀角"],
    "草乌": ["犀角"],
    "人参": ["五灵脂"],
    "官桂": ["石脂"],
}

# 妊娠禁忌药物分级
PREGNANCY_CONTRAINDICATIONS = {
    "严格禁用": [
        "麝香", "斑蝥", "天雄", "巴豆", "牵牛子", "大戟", "芫花", "甘遂",
        "商陆", "蜈蚣", "水蛭", "虻虫", "三棱", "莪术", "水银", "砒霜",
        "雄黄", "轻粉"
    ],
    "慎用": [
        "桃仁", "红花", "牛膝", "大黄", "枳实", "附子", "肉桂", "干姜",
        "半夏", "南星", "通草", "瞿麦", "木通", "薏苡仁", "代赭石",
        "芒硝", "牡丹皮", "茜草", "苏木", "刘寄奴", "益母草", "茺蔚子"
    ],
    "孕后期慎用": ["桂枝", "附子", "肉桂", "干姜", "吴茱萸"]
}

# 剂量上限（克/日）
DOSAGE_LIMITS = {
    "附子": {"max": 15, "typical": 6, "warning": "大剂量需久煎60分钟以上，防乌头碱中毒"},
    "细辛": {"max": 3, "typical": 1, "warning": "细辛不过钱（3克），过量可致呼吸抑制"},
    "马钱子": {"max": 0.6, "typical": 0.3, "warning": "剧毒药，需炮制，过量致惊厥"},
    "川乌": {"max": 6, "typical": 3, "warning": "需先煎30-60分钟，生川乌禁用"},
    "草乌": {"max": 6, "typical": 3, "warning": "需先煎30-60分钟，生草乌禁用"},
    "大黄": {"max": 15, "typical": 6, "warning": "大剂量致泻，孕妇慎用"},
    "芒硝": {"max": 15, "typical": 10, "warning": "后下或冲服，孕妇禁用"},
    "巴豆": {"max": 0.3, "typical": 0.1, "warning": "峻下药，去油用，孕妇禁用"},
    "甘遂": {"max": 1.5, "typical": 0.5, "warning": "峻下逐水药，醋炙用"},
    "芫花": {"max": 6, "typical": 3, "warning": "峻下逐水药，醋炙用"},
    "商陆": {"max": 6, "typical": 3, "warning": "有毒，需炮制"},
    "雄黄": {"max": 1.5, "typical": 0.3, "warning": "外用为主，内服需微量"},
    "轻粉": {"max": 0.3, "typical": 0.1, "warning": "含汞，外用为主"},
    "朱砂": {"max": 1, "typical": 0.3, "warning": "含汞，不入煎剂，冲服"},
}

# 特殊人群用药调整
SPECIAL_POPULATIONS = {
    "儿童": {
        "禁用": ["朱砂", "轻粉", "雄黄", "砒霜"],
        "慎用": ["大黄", "芒硝", "附子", "细辛"],
        "剂量调整": "按体重计算，一般为成人量的1/4-1/2"
    },
    "老年人": {
        "慎用": ["大黄", "芒硝", "附子", "麻黄"],
        "剂量调整": "一般为成人量的2/3-3/4"
    },
    "肝功能不全": {
        "禁用": ["何首乌", "黄药子", "苍耳子", "雷公藤"],
        "慎用": ["大黄", "虎杖", "柴胡", "黄芩"]
    },
    "肾功能不全": {
        "禁用": ["马兜铃", "关木通", "广防己", "青木香"],
        "慎用": ["大黄", "芒硝", "车前子", "木通"]
    }
}


class SafetyCheckService:
    """用药安全检查服务"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_formula_safety(
        self,
        herbs: List[Dict[str, Any]],  # [{"name": "黄芪", "dosage": 30}, ...]
        patient_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        全面安全检查

        Args:
            herbs: 药物列表 [{"name": "黄芪", "dosage": 30}, ...]
            patient_info: 患者信息 {"is_pregnant": bool, "age": int, ...}

        Returns:
            {
                "errors": [...],      # 严重错误（必须修改）
                "warnings": [...],    # 警告（建议注意）
                "suggestions": [...]  # 优化建议
            }
        """
        result = {
            "errors": [],
            "warnings": [],
            "suggestions": []
        }

        if not herbs:
            return result

        patient_info = patient_info or {}
        herb_names = [h["name"] for h in herbs]

        # 1. 十八反检查
        eighteen_conflicts = self._check_eighteen_incompatibilities(herb_names)
        result["errors"].extend(eighteen_conflicts)

        # 2. 十九畏检查
        nineteen_conflicts = self._check_nineteen_fears(herb_names)
        result["warnings"].extend(nineteen_conflicts)

        # 3. 妊娠禁忌检查
        if patient_info.get("is_pregnant"):
            pregnancy_issues = self._check_pregnancy_contraindications(herb_names)
            result["errors"].extend([i for i in pregnancy_issues if i["severity"] == "critical"])
            result["warnings"].extend([i for i in pregnancy_issues if i["severity"] == "warning"])

        # 4. 剂量检查
        dosage_issues = self._check_dosage_limits(herbs)
        result["errors"].extend([i for i in dosage_issues if i["severity"] == "critical"])
        result["warnings"].extend([i for i in dosage_issues if i["severity"] == "warning"])

        # 5. 特殊人群检查
        if patient_info.get("age"):
            age = patient_info["age"]
            if age < 14:
                population_issues = self._check_special_population(herb_names, "儿童")
                result["warnings"].extend(population_issues)
            elif age > 65:
                population_issues = self._check_special_population(herb_names, "老年人")
                result["suggestions"].extend(population_issues)

        # 6. 肝肾功能检查
        if patient_info.get("liver_dysfunction"):
            liver_issues = self._check_special_population(herb_names, "肝功能不全")
            result["errors"].extend([i for i in liver_issues if "禁用" in i.get("message", "")])
            result["warnings"].extend([i for i in liver_issues if "慎用" in i.get("message", "")])

        if patient_info.get("kidney_dysfunction"):
            kidney_issues = self._check_special_population(herb_names, "肾功能不全")
            result["errors"].extend([i for i in kidney_issues if "禁用" in i.get("message", "")])
            result["warnings"].extend([i for i in kidney_issues if "慎用" in i.get("message", "")])

        # 7. 过敏史检查
        if patient_info.get("allergies"):
            allergy_list = patient_info["allergies"]
            if isinstance(allergy_list, str):
                allergy_list = [a.strip() for a in allergy_list.split(",")]
            allergy_issues = self._check_allergies(herb_names, allergy_list)
            result["errors"].extend(allergy_issues)

        return result

    def _check_eighteen_incompatibilities(self, herb_names: List[str]) -> List[Dict[str, Any]]:
        """检查十八反"""
        errors = []
        for herb in herb_names:
            if herb in EIGHTEEN_INCOMPATIBILITIES:
                conflicts = set(herb_names) & set(EIGHTEEN_INCOMPATIBILITIES[herb])
                if conflicts:
                    errors.append({
                        "type": "十八反配伍禁忌",
                        "severity": "critical",
                        "herb": herb,
                        "conflicts": list(conflicts),
                        "message": f"【严重】{herb} 与 {', '.join(conflicts)} 相反，属于十八反配伍禁忌，严禁同用！",
                        "suggestion": f"必须去除 {herb} 或 {', '.join(conflicts)} 之一"
                    })
        return errors

    def _check_nineteen_fears(self, herb_names: List[str]) -> List[Dict[str, Any]]:
        """检查十九畏"""
        warnings = []
        for herb, feared in NINETEEN_FEARS.items():
            if herb in herb_names and any(f in herb_names for f in feared):
                conflicts = [f for f in feared if f in herb_names]
                warnings.append({
                    "type": "十九畏配伍禁忌",
                    "severity": "warning",
                    "herb": herb,
                    "conflicts": conflicts,
                    "message": f"【警告】{herb} 畏 {', '.join(conflicts)}，不宜同用",
                    "suggestion": "建议分开使用或调整方剂"
                })
        return warnings

    def _check_pregnancy_contraindications(self, herb_names: List[str]) -> List[Dict[str, Any]]:
        """检查妊娠禁忌"""
        issues = []
        for level, forbidden_herbs in PREGNANCY_CONTRAINDICATIONS.items():
            for herb in herb_names:
                if herb in forbidden_herbs:
                    severity = "critical" if "严格" in level else "warning"
                    issues.append({
                        "type": "妊娠禁忌",
                        "severity": severity,
                        "herb": herb,
                        "level": level,
                        "message": f"【{'严重' if severity == 'critical' else '警告'}】孕妇{level}：{herb}",
                        "suggestion": "建议更换其他药物" if severity == "critical" else "请谨慎使用，密切观察"
                    })
        return issues

    def _check_dosage_limits(self, herbs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """检查剂量上限"""
        issues = []
        for herb_data in herbs:
            herb_name = herb_data.get("name")
            dosage = herb_data.get("dosage", 0)

            if herb_name in DOSAGE_LIMITS:
                limit_info = DOSAGE_LIMITS[herb_name]
                max_dosage = limit_info["max"]
                typical_dosage = limit_info["typical"]

                if dosage > max_dosage:
                    issues.append({
                        "type": "剂量超限",
                        "severity": "critical",
                        "herb": herb_name,
                        "current_dosage": dosage,
                        "max_dosage": max_dosage,
                        "message": f"【严重】{herb_name} 剂量 {dosage}克 超过最大安全剂量 {max_dosage}克",
                        "warning": limit_info["warning"],
                        "suggestion": f"建议调整至 {typical_dosage}-{max_dosage}克"
                    })
                elif dosage > typical_dosage * 1.5:
                    issues.append({
                        "type": "剂量偏大",
                        "severity": "warning",
                        "herb": herb_name,
                        "current_dosage": dosage,
                        "typical_dosage": typical_dosage,
                        "message": f"【提示】{herb_name} 剂量 {dosage}克 偏大（常用量 {typical_dosage}克）",
                        "warning": limit_info["warning"],
                        "suggestion": "请确认剂量合理性"
                    })
        return issues

    def _check_special_population(self, herb_names: List[str], population: str) -> List[Dict[str, Any]]:
        """检查特殊人群用药"""
        issues = []
        if population not in SPECIAL_POPULATIONS:
            return issues

        pop_rules = SPECIAL_POPULATIONS[population]

        # 检查禁用药物
        if "禁用" in pop_rules:
            for herb in herb_names:
                if herb in pop_rules["禁用"]:
                    issues.append({
                        "type": "特殊人群用药",
                        "severity": "critical",
                        "population": population,
                        "herb": herb,
                        "message": f"【严重】{population}禁用：{herb}",
                        "suggestion": "必须更换其他药物"
                    })

        # 检查慎用药物
        if "慎用" in pop_rules:
            for herb in herb_names:
                if herb in pop_rules["慎用"]:
                    issues.append({
                        "type": "特殊人群用药",
                        "severity": "warning",
                        "population": population,
                        "herb": herb,
                        "message": f"【警告】{population}慎用：{herb}",
                        "suggestion": pop_rules.get("剂量调整", "请谨慎使用")
                    })

        return issues

    def _check_allergies(self, herb_names: List[str], allergy_list: List[str]) -> List[Dict[str, Any]]:
        """检查过敏史"""
        issues = []
        for herb in herb_names:
            if herb in allergy_list:
                issues.append({
                    "type": "过敏史",
                    "severity": "critical",
                    "herb": herb,
                    "message": f"【严重】患者对 {herb} 过敏",
                    "suggestion": "必须去除该药物"
                })
        return issues

    async def get_herb_safety_info(self, herb_name: str) -> Optional[Dict[str, Any]]:
        """获取单个药物的安全信息"""
        info = {
            "name": herb_name,
            "incompatibilities": [],
            "fears": [],
            "pregnancy": None,
            "dosage_limit": None
        }

        # 十八反
        if herb_name in EIGHTEEN_INCOMPATIBILITIES:
            info["incompatibilities"] = EIGHTEEN_INCOMPATIBILITIES[herb_name]

        # 十九畏
        if herb_name in NINETEEN_FEARS:
            info["fears"] = NINETEEN_FEARS[herb_name]

        # 妊娠禁忌
        for level, herbs in PREGNANCY_CONTRAINDICATIONS.items():
            if herb_name in herbs:
                info["pregnancy"] = level
                break

        # 剂量上限
        if herb_name in DOSAGE_LIMITS:
            info["dosage_limit"] = DOSAGE_LIMITS[herb_name]

        return info
