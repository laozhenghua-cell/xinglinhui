"""
中医辨证引擎 - 基于规则的证型匹配系统
"""
from typing import Dict, List, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.diagnosis import SyndromeRule, SymptomDictionary
from app.models.knowledge import AnorectalFormula
from app.services.zhou_knowledge import build_original_knowledge


class SyndromeEngine:
    """辨证引擎"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def analyze(
        self,
        disease_type: str,
        selected_symptoms: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        分析症状，返回匹配的证型及置信度

        Args:
            disease_type: 病种
            selected_symptoms: 用户选择的症状数据

        Returns:
            List of syndrome results with confidence scores
        """
        # 获取该病种的所有辨证规则
        result = await self.session.execute(
            select(SyndromeRule)
            .where(SyndromeRule.disease_type == disease_type)
            .where(SyndromeRule.is_active == 1)
            .order_by(SyndromeRule.priority.desc())
        )
        rules = result.scalars().all()

        if not rules:
            return []

        # 对每个规则计算匹配度
        syndrome_matches = []
        print(f"\n🔍 开始辨证，共 {len(rules)} 个证型规则")
        for rule in rules:
            print(f"\n📋 检查证型: {rule.syndrome_name}")
            print(f"   必需症状: {rule.required_symptoms}")
            confidence = self._calculate_confidence(
                selected_symptoms,
                rule.required_symptoms,
                rule.optional_symptoms
            )
            print(f"   置信度: {confidence}")

            if confidence >= rule.confidence_threshold:
                # 生成加减化裁建议
                modifications = self._generate_modifications(
                    selected_symptoms,
                    rule.modification_rules
                )
                evidence = self._build_evidence(
                    selected_symptoms, rule.required_symptoms, rule.optional_symptoms
                )
                original_knowledge = build_original_knowledge(
                    disease_type, {
                        "syndrome_code": rule.syndrome_code,
                        "syndrome_name": rule.syndrome_name,
                        "treatment_principle": rule.treatment_principle,
                    }, selected_symptoms
                )

                # 查询完整方剂详情
                # rule.recommended_formulas 是字典列表，提取出方剂名称
                formula_names = self._extract_formula_names(rule.recommended_formulas)
                formula_details = await self._get_formula_details(formula_names)

                syndrome_matches.append({
                    "syndrome_name": rule.syndrome_name,
                    "syndrome_code": rule.syndrome_code,
                    "confidence": round(confidence, 2),
                    "treatment_principle": rule.treatment_principle,
                    "recommended_formulas": formula_details,
                    "tongue_pulse": rule.tongue_pulse,
                    "modifications": modifications,
                    "evidence": evidence,
                    "original_knowledge": original_knowledge,
                })

        # 部分症状资料也必须返回可解释的候选结果，避免临床流程因缺一项直接 404。
        if not syndrome_matches:
            scored = []
            for rule in rules:
                confidence = self._calculate_confidence(
                    selected_symptoms, rule.required_symptoms, rule.optional_symptoms,
                    allow_partial=True
                )
                scored.append((confidence, rule))
            scored.sort(key=lambda item: item[0], reverse=True)
            for confidence, rule in scored[:3]:
                syndrome_matches.append({
                    "syndrome_name": rule.syndrome_name,
                    "syndrome_code": rule.syndrome_code,
                    "confidence": round(confidence, 2),
                    "treatment_principle": rule.treatment_principle,
                    # 候选证型不能下发可执行方药，待四诊资料补全后再生成。
                    "recommended_formulas": [],
                    "tongue_pulse": rule.tongue_pulse,
                    "modifications": [],
                    "evidence": self._build_evidence(
                        selected_symptoms, rule.required_symptoms, rule.optional_symptoms
                    ),
                    "original_knowledge": build_original_knowledge(
                        disease_type, {
                            "syndrome_code": rule.syndrome_code,
                            "syndrome_name": rule.syndrome_name,
                            "treatment_principle": rule.treatment_principle,
                        }, selected_symptoms
                    ),
                    "insufficient_data": True,
                })

        # 按置信度排序
        syndrome_matches.sort(key=lambda x: x["confidence"], reverse=True)

        return syndrome_matches

    @staticmethod
    def _extract_formula_names(recommended: Any) -> List[str]:
        """兼容规则库中字符串和 {name: ...} 两种方剂格式。"""
        names = []
        for item in recommended or []:
            if isinstance(item, str) and item:
                names.append(item)
            elif isinstance(item, dict) and item.get("name"):
                names.append(item["name"])
        return names

    def _build_evidence(
        self,
        selected: Dict[str, Any],
        required: Optional[Dict[str, Any]],
        optional: Optional[Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """返回面向临床复核的命中依据，不暴露规则引擎调试信息。"""
        normalized = self._normalize_selected(selected)

        def compare(rule_items: Optional[Dict[str, Any]]):
            matched, missing = [], []
            for key, expected in (rule_items or {}).items():
                actual = normalized.get(key)
                item = {
                    "key": key,
                    "label": self._symptom_label(key),
                    "expected": self._display_value(expected),
                    "actual": self._display_value(actual),
                }
                (matched if self._match_symptom(actual, expected) else missing).append(item)
            return matched, missing

        matched_required, missing_required = compare(required)
        matched_optional, _ = compare(optional)
        return {
            "matched_required": matched_required,
            "matched_optional": matched_optional,
            "missing_required": missing_required,
        }

    @staticmethod
    def _symptom_label(key: str) -> str:
        labels = {
            "bleeding": "便血", "pain": "疼痛", "stool_condition": "大便",
            "tongue_color": "舌质", "tongue_coating": "舌苔",
            "pulse_rapid": "数脉", "pulse_wiry": "弦脉", "pulse_slippery": "滑脉",
            "pulse_weak": "弱脉", "pulse_thready": "细脉", "pulse_deep": "沉脉",
            "swelling_symptom": "肿胀", "prolapse_symptom": "脱出",
            "anal_swelling": "肛门肿胀", "bitter_mouth": "口苦",
            "urination": "小便", "fatigue": "乏力", "poor_appetite": "纳差",
        }
        return labels.get(key, key.replace("_", " "))

    @classmethod
    def _display_value(cls, value: Any) -> str:
        if value is None:
            return "未采集"
        if isinstance(value, bool):
            return "有" if value else "无"
        if isinstance(value, list):
            return "、".join(cls._display_value(item) for item in value)
        if isinstance(value, dict):
            field_labels = {
                "present": "有无", "color": "颜色", "volume": "量",
                "degree": "程度", "nature": "性质", "timing": "时间",
            }
            return "；".join(
                f"{field_labels.get(key, key)}：{cls._display_value(item)}"
                for key, item in value.items()
                if item not in (None, "", [], {})
            )
        return str(value)

    def _calculate_confidence(
        self,
        selected: Dict[str, Any],
        required: Dict[str, Any],
        optional: Dict[str, Any],
        allow_partial: bool = False,
    ) -> float:
        """
        计算症状匹配置信度

        匹配算法：
        - 必需症状：每项占60%权重，必须全部匹配
        - 可选症状：每项占40%权重，匹配越多得分越高
        """
        if not required:
            return 0.0

        selected = self._normalize_selected(selected)

        # 1. 检查必需症状
        required_score = 0
        required_total = len(required)
        required_matched = 0

        for symptom_name, required_value in required.items():
            selected_value = selected.get(symptom_name)

            if self._match_symptom(selected_value, required_value):
                required_matched += 1
            else:
                print(f"❌ 症状不匹配: {symptom_name}")
                print(f"   要求: {required_value}")
                print(f"   实际: {selected_value}")

        # 正常规则要求全部命中；降级评分用于返回候选证型。
        if required_matched < required_total and not allow_partial:
            print(f"❌ 必需症状未全部匹配: {required_matched}/{required_total}")
            return 0.0

        required_score = 0.7 * (required_matched / required_total)

        # 2. 检查可选症状
        optional_score = 0
        if optional:
            optional_total = len(optional)
            optional_matched = 0

            for symptom_name, optional_value in optional.items():
                selected_value = selected.get(symptom_name)

                if self._match_symptom(selected_value, optional_value):
                    optional_matched += 1

            # 可选症状按匹配比例计算
            optional_score = 0.3 * (optional_matched / optional_total)
        else:
            optional_score = 0.3

        return required_score + optional_score

    @staticmethod
    def _normalize_selected(selected: Dict[str, Any]) -> Dict[str, Any]:
        """兼容前端四诊组件的数组字段和脉象/全身症状复选框。"""
        normalized = dict(selected or {})
        for key in normalized.get("pulse_types", []) or []:
            normalized[key] = True
        for key in normalized.get("general", []) or []:
            normalized[key] = True
        for key in ("pain", "bleeding", "swelling_symptom", "prolapse_symptom"):
            value = normalized.get(key)
            if isinstance(value, dict):
                normalized[key] = dict(value)
        return normalized

    def _match_symptom(self, selected_value: Any, required_value: Any) -> bool:
        """
        匹配单个症状

        支持多种匹配模式：
        - 布尔值匹配
        - 字符串精确匹配
        - 列表包含匹配
        - 复合对象匹配
        """
        if selected_value is None:
            return False

        # 复选框可能传入数组，规则通常以单个布尔值表达。
        if isinstance(selected_value, list) and isinstance(required_value, bool):
            return required_value is (len(selected_value) > 0)

        # 布尔值匹配
        if isinstance(required_value, bool):
            if isinstance(selected_value, dict) and "present" in selected_value:
                selected_value = selected_value.get("present")
            return bool(selected_value) == required_value

        # 字符串匹配
        if isinstance(required_value, str):
            if isinstance(selected_value, list):
                return required_value in selected_value
            return selected_value == required_value

        # 列表匹配（selected必须在required列表中）
        if isinstance(required_value, list):
            if isinstance(selected_value, list):
                # 两个列表有交集即可
                return bool(set(selected_value) & set(required_value))
            else:
                return selected_value in required_value

        # 字典匹配（复合症状）
        if isinstance(required_value, dict) and isinstance(selected_value, dict):
            for key, req_val in required_value.items():
                sel_val = selected_value.get(key)
                if not self._match_symptom(sel_val, req_val):
                    return False
            return True

        return False

    async def _get_formula_details(self, formula_names: List[str]) -> List[Dict[str, Any]]:
        """
        查询方剂完整详情

        Args:
            formula_names: 方剂名称列表

        Returns:
            方剂详情列表（包含组成、用法、功效等）
        """
        if not formula_names:
            return []

        # 查询数据库获取方剂详情
        result = await self.session.execute(
            select(AnorectalFormula)
            .where(AnorectalFormula.name.in_(formula_names))
        )
        formulas = result.scalars().all()

        # 构建方剂详情列表，保持原有顺序
        formula_dict = {f.name: f for f in formulas}
        formula_details = []

        for i, name in enumerate(formula_names):
            formula = formula_dict.get(name)
            if formula:
                # 计算匹配度（第一个方剂优先级最高）
                priority = 1 if i == 0 else i + 1
                match_rate = 0.95 if i == 0 else max(0.7, 0.95 - i * 0.1)

                formula_details.append({
                    "name": formula.name,
                    "source": formula.source,
                    "composition": formula.composition,
                    "function": formula.function,
                    "indications": formula.indications,
                    "usage": formula.usage,
                    "modifications": formula.modifications,
                    "notes": formula.notes,
                    "contraindications": formula.contraindications if hasattr(formula, 'contraindications') else None,
                    "priority": priority,
                    "match_rate": match_rate
                })
            else:
                # 方剂未找到，返回基本信息
                formula_details.append({
                    "name": name,
                    "priority": i + 1,
                    "match_rate": 0.8
                })

        return formula_details

    def _generate_modifications(
        self,
        selected_symptoms: Dict[str, Any],
        modification_rules: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        根据兼症生成加减化裁建议

        Args:
            selected_symptoms: 选择的症状
            modification_rules: 加减规则库

        Returns:
            List of modification suggestions
        """
        if not modification_rules:
            return []

        modifications = []

        for condition, action in modification_rules.items():
            # 检查条件是否满足
            if self._check_modification_condition(condition, selected_symptoms):
                modifications.append({
                    "condition": condition,
                    "action": action
                })

        return modifications

    def _check_modification_condition(
        self,
        condition: str,
        selected_symptoms: Dict[str, Any]
    ) -> bool:
        """
        检查加减条件是否满足

        简化版：基于条件字符串中的关键词匹配
        """
        condition_lower = condition.lower()

        # 便秘相关
        if "便秘" in condition:
            stool = selected_symptoms.get("stool_condition")
            if stool in ["干结", "秘结"]:
                return True
            if "便秘严重" in condition:
                return stool == "秘结"

        # 疼痛相关
        if "疼痛" in condition:
            pain = selected_symptoms.get("pain", {})
            if isinstance(pain, dict) and pain.get("present"):
                if "剧烈" in condition:
                    return pain.get("degree") in ["重度", "剧烈"]
                return True

        # 出血相关
        if "出血" in condition:
            bleeding = selected_symptoms.get("bleeding", {})
            if isinstance(bleeding, dict) and bleeding.get("present"):
                if "量大" in condition or "出血多" in condition:
                    return bleeding.get("volume") in ["中量", "大量", "射血"]
                return True

        # 湿热相关
        if "湿热" in condition:
            tongue_coating = selected_symptoms.get("tongue_coating")
            if tongue_coating in ["黄腻", "白厚"]:
                return True
            bitter_mouth = selected_symptoms.get("bitter_mouth")
            urination = selected_symptoms.get("urination")
            return bitter_mouth or urination == "短赤"

        # 肿胀相关
        if "肿胀" in condition:
            swelling = selected_symptoms.get("swelling_symptom", {})
            if isinstance(swelling, dict) and swelling.get("present"):
                return True
            anal_swelling = selected_symptoms.get("anal_swelling")
            return anal_swelling in ["中度", "重度"]

        # 脱垂相关
        if "脱垂" in condition or "脱肛" in condition:
            prolapse = selected_symptoms.get("prolapse_symptom", {})
            if isinstance(prolapse, dict) and prolapse.get("present"):
                if "严重" in condition:
                    return prolapse.get("degree") in ["III度", "IV度"]
                return True

        # 气虚相关
        if "气虚" in condition:
            return (
                selected_symptoms.get("fatigue") or
                selected_symptoms.get("poor_appetite") or
                selected_symptoms.get("pulse_weak")
            )

        # 血虚相关
        if "血虚" in condition:
            return (
                selected_symptoms.get("pale_complexion") or
                selected_symptoms.get("pulse_fine") or
                selected_symptoms.get("tongue_color") == "淡白"
            )

        # 阴虚相关
        if "阴虚" in condition:
            tongue_coating = selected_symptoms.get("tongue_coating")
            return tongue_coating in ["少苔", "无苔"]

        # 高热相关
        if "高热" in condition:
            fever = selected_symptoms.get("fever")
            return fever in ["高热", "恶寒发热"]

        # 久泻相关
        if "久泻" in condition:
            stool = selected_symptoms.get("stool_condition")
            return stool == "溏泄"

        # 失眠相关
        if "失眠" in condition:
            return selected_symptoms.get("insomnia")

        # 腰酸相关
        if "腰酸" in condition or "腰膝酸软" in condition:
            return selected_symptoms.get("lumbar_soreness")

        # 小儿相关
        if "小儿" in condition:
            # 需要从患者信息中获取年龄，暂时返回False
            return False

        # 括约肌痉挛
        if "括约肌" in condition or "痉挛" in condition:
            return selected_symptoms.get("sphincter") == "痉挛"

        # 脓肿未溃
        if "未溃" in condition:
            secretion = selected_symptoms.get("secretion")
            return secretion != "脓性"

        # 便血不止
        if "便血不止" in condition:
            bleeding = selected_symptoms.get("bleeding", {})
            if isinstance(bleeding, dict) and bleeding.get("present"):
                return bleeding.get("volume") in ["中量", "大量", "射血"]

        # 血瘀重
        if "血瘀" in condition:
            tongue_color = selected_symptoms.get("tongue_color")
            anal_color = selected_symptoms.get("anal_color")
            return tongue_color == "紫暗" or anal_color == "紫暗"

        # 嵌顿
        if "嵌顿" in condition:
            prolapse = selected_symptoms.get("prolapse_symptom", {})
            pain = selected_symptoms.get("pain", {})
            return (
                isinstance(prolapse, dict) and prolapse.get("present") and
                isinstance(pain, dict) and pain.get("present")
            )

        return False


async def get_symptom_dictionary(
    session: AsyncSession,
    category: Optional[str] = None
) -> List[SymptomDictionary]:
    """获取症状字典"""
    query = select(SymptomDictionary)
    if category:
        query = query.where(SymptomDictionary.category == category)

    query = query.order_by(
        SymptomDictionary.category,
        SymptomDictionary.subcategory,
        SymptomDictionary.weight.desc()
    )

    result = await session.execute(query)
    return result.scalars().all()
