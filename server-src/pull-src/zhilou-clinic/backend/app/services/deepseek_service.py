"""
DeepSeek text-based syndrome differentiation service for anorectal conditions.
Uses DeepSeek chat API (OpenAI-compatible) for TCM diagnostic reasoning.
"""
import json
import logging
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

SYNDROME_DIFFERENTIATION_PROMPT = """你是一位资深肛肠科中医专家，精通中医辨证论治体系，尤其擅长肛肠疾病的辨证分型与治疗。

请根据患者提供的症状信息，进行全面的中医辨证分析，给出诊断和治疗方案。

辨证框架：
1. 八纲辨证：表里、寒热、虚实、阴阳
2. 脏腑辨证：重点关注大肠、脾、肝、肾
3. 气血津液辨证：气虚、血瘀、湿热、阴虚
4. 六经辨证（如有外感）

肛肠科常见证型：
- 湿热下注证：便血色鲜，肛门灼热坠胀，大便黏滞不爽，口苦口干，小便黄赤，舌红苔黄腻，脉滑数
- 气滞血瘀证：肛门肿物暗紫，疼痛如刺，久坐加重，舌暗或有瘀斑，脉弦涩
- 脾虚气陷证：脱出物色淡，便后难回纳，面色萎黄，神疲乏力，食少便溏，舌淡苔白，脉弱
- 血热肠燥证：便血色鲜红量多，大便干结难解，口干咽燥，心烦易怒，舌红少津，脉细数
- 阴虚肠燥证：大便干结如羊粪，努挣难下，口干少津，五心烦热，舌红少苔，脉细
- 风伤肠络证：便血色鲜，量或多或少，肛门瘙痒，舌红苔薄，脉浮数
- 热毒蕴结证：肛周红肿热痛，触痛明显，发热恶寒，口渴喜饮，大便秘结，舌红苔黄，脉数有力
- 正虚邪恋证：病程日久，时发时止，肛门潮湿，神疲乏力，舌淡苔薄，脉细弱

治疗方案要求完整包含：
- 内服方药（方名、组成、用量、用法、加减化裁）
- 外治法（坐浴熏洗方、外敷药、栓剂）
- 针灸方案（取穴、手法）
- 饮食起居调护
- 疗程建议

请按以下JSON格式返回：
{
  "diagnosis": "中医诊断（病名）",
  "diseaseType": "具体分类",
  "syndrome": "证型名称",
  "syndromeAnalysis": "辨证分析过程",
  "pathogenesis": "病因病机",
  "eightPrinciples": {
    "exterior_interior": "表/里",
    "cold_heat": "寒/热",
    "deficiency_excess": "虚/实",
    "yin_yang": "阴/阳"
  },
  "treatmentPrinciple": "治则治法",
  "prescription": {
    "name": "方剂名称",
    "composition": [
      {"herb": "药名", "dosage": "用量", "role": "君/臣/佐/使"}
    ],
    "usage": "煎服法",
    "duration": "疗程",
    "modifications": "随症加减"
  },
  "externalTreatment": {
    "sitzBath": {"formula": "坐浴方", "method": "使用方法", "frequency": "频次"},
    "topical": "外敷/涂药方案",
    "suppository": "栓剂使用"
  },
  "acupuncture": {
    "mainPoints": ["主穴"],
    "supplementaryPoints": ["配穴"],
    "method": "手法及留针时间",
    "frequency": "治疗频次"
  },
  "dietaryAdvice": ["饮食建议"],
  "lifestyleAdvice": ["生活调护"],
  "prognosis": "预后判断",
  "followUpPlan": "复诊计划",
  "warnings": ["注意事项"]
}
"""


async def diagnose_syndrome(
    symptoms: str,
    disease_type: Optional[str] = None,
    tongue: Optional[str] = None,
    pulse: Optional[str] = None,
    medical_history: Optional[str] = None,
    physical_exam: Optional[str] = None,
) -> dict:
    """
    Perform TCM syndrome differentiation for anorectal conditions.

    Args:
        symptoms: Patient's symptom description
        disease_type: Suspected disease type (if any)
        tongue: Tongue diagnosis findings
        pulse: Pulse diagnosis findings
        medical_history: Relevant medical history
        physical_exam: Physical examination findings

    Returns:
        Structured diagnostic and treatment plan
    """
    if not settings.DEEPSEEK_API_KEY:
        return {
            "error": "DEEPSEEK_API_KEY未配置",
            "diagnosis": "无法分析",
            "syndrome": "AI服务未配置",
        }

    patient_description = f"主诉及症状：{symptoms}"
    if disease_type:
        patient_description += f"\n初步诊断/疑似：{disease_type}"
    if tongue:
        patient_description += f"\n舌诊：{tongue}"
    if pulse:
        patient_description += f"\n脉诊：{pulse}"
    if medical_history:
        patient_description += f"\n病史：{medical_history}"
    if physical_exam:
        patient_description += f"\n体格检查：{physical_exam}"

    messages = [
        {"role": "system", "content": SYNDROME_DIFFERENTIATION_PROMPT},
        {"role": "user", "content": patient_description},
    ]

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.DEEPSEEK_MODEL,
                    "messages": messages,
                    "temperature": 0.4,
                    "max_tokens": 4096,
                    "response_format": {"type": "json_object"},
                },
            )

            if response.status_code != 200:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return {
                    "error": f"AI服务请求失败: {response.status_code}",
                    "diagnosis": "分析失败",
                    "syndrome": "请稍后重试",
                }

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            try:
                analysis = json.loads(content)
            except json.JSONDecodeError:
                content_clean = content.strip()
                if content_clean.startswith("```json"):
                    content_clean = content_clean[7:]
                if content_clean.startswith("```"):
                    content_clean = content_clean[3:]
                if content_clean.endswith("```"):
                    content_clean = content_clean[:-3]
                try:
                    analysis = json.loads(content_clean.strip())
                except json.JSONDecodeError:
                    analysis = {
                        "diagnosis": "解析失败",
                        "syndrome": "返回结果格式异常",
                        "rawResponse": content[:1000],
                    }

            analysis["modelUsed"] = settings.DEEPSEEK_MODEL
            return analysis

    except httpx.TimeoutException:
        logger.error("DeepSeek API timeout")
        return {
            "error": "AI服务请求超时",
            "diagnosis": "分析超时",
            "syndrome": "请稍后重试",
        }
    except Exception as e:
        logger.error(f"DeepSeek syndrome differentiation error: {str(e)}")
        return {
            "error": f"分析异常: {str(e)}",
            "diagnosis": "分析异常",
            "syndrome": str(e),
        }


async def generate_treatment_plan(
    diagnosis: str,
    syndrome: str,
    patient_info: Optional[str] = None,
) -> dict:
    """
    Generate a detailed treatment plan based on established diagnosis and syndrome.
    """
    if not settings.DEEPSEEK_API_KEY:
        return {"error": "DEEPSEEK_API_KEY未配置"}

    plan_prompt = """基于以下诊断和辨证结果，请生成详细的治疗方案。
要求包含：内服方药、外治方案、针灸取穴、饮食禁忌、生活调护、疗程规划。

请按JSON格式返回治疗方案。"""

    user_msg = f"诊断：{diagnosis}\n证型：{syndrome}"
    if patient_info:
        user_msg += f"\n患者信息：{patient_info}"

    messages = [
        {"role": "system", "content": plan_prompt},
        {"role": "user", "content": user_msg},
    ]

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.DEEPSEEK_MODEL,
                    "messages": messages,
                    "temperature": 0.4,
                    "max_tokens": 3000,
                    "response_format": {"type": "json_object"},
                },
            )

            if response.status_code != 200:
                return {"error": f"API错误: {response.status_code}"}

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"rawResponse": content}

    except Exception as e:
        logger.error(f"Treatment plan generation error: {str(e)}")
        return {"error": str(e)}
