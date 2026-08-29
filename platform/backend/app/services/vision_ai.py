"""
Qwen VL multimodal image analysis service for anorectal conditions.
Calls Qwen-VL-Max API with a detailed anorectal specialist prompt to analyze
clinical images and return structured diagnostic results.
"""
import json
import logging
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

ANORECTAL_VISION_PROMPT = """你是一位资深肛肠科中医专家，拥有30年临床经验，精通中西医结合肛肠病诊疗。
请仔细分析这张肛肠疾病临床图片，结合患者提供的症状信息，给出专业的诊断分析。

分析要求：
1. 视觉特征分析：详细描述图像中可见的病理特征（颜色、形态、大小、位置、数量等）
2. 疾病判断：根据视觉特征判断最可能的疾病类型
3. 分型分级：按照相关分类标准进行分型分级
4. 中医辨证：结合望诊所见，分析证型（湿热下注、气滞血瘀、脾虚气陷、血热肠燥等）
5. 病因病机：分析疾病的中医病因病机
6. 治疗方案：
   - 治则治法
   - 内服方药（方名、组成、用法）
   - 外用方案（坐浴/熏洗/外敷方药）
   - 针灸穴位建议
   - 必要时的手术建议
7. 生活调护建议

疾病类型参考：
- 痔疮（内痔I-IV度、外痔：结缔组织性/血栓性/静脉曲张性/炎性、混合痔）
- 肛裂（急性/慢性，前位/后位/侧位）
- 肛瘘（低位/高位，单纯性/复杂性）
- 肛周脓肿（皮下/坐骨直肠窝/骨盆直肠间隙/直肠后间隙）
- 直肠脱垂（I-III度，不完全/完全）
- 肛周湿疹（急性/亚急性/慢性）
- 尖锐湿疣
- 肛乳头肥大
- 肛门息肉

中医证型参考：
- 湿热下注证：红肿热痛，便秘溲赤，舌红苔黄腻
- 气滞血瘀证：肿物暗紫，刺痛明显，舌暗有瘀斑
- 脾虚气陷证：脱出难回，面色萎黄，气短乏力
- 血热肠燥证：出血鲜红，大便干结，口干咽燥
- 阴虚肠燥证：大便干结，口干少津，盗汗
- 风伤肠络证：便血色鲜，量多，肛门瘙痒

请按以下JSON格式返回分析结果：
{
  "disease": "疾病名称（中文）",
  "diseaseType": "具体分型",
  "classification": "分级/分期",
  "confidence": 0.85,
  "visualFindings": "视觉特征详细描述",
  "differentialDiagnosis": ["鉴别诊断1", "鉴别诊断2"],
  "syndrome": "中医证型",
  "pathogenesis": "病因病机分析",
  "treatmentPrinciple": "治则治法",
  "formula": {
    "name": "方剂名",
    "composition": "方药组成及用量",
    "usage": "用法",
    "modifications": "加减变化"
  },
  "externalTreatment": {
    "sitzBath": "坐浴/熏洗方",
    "topical": "外敷/外涂方案",
    "suppository": "栓剂/塞药建议"
  },
  "acupuncture": {
    "points": ["穴位1", "穴位2"],
    "method": "针灸手法说明"
  },
  "surgeryAdvice": "手术建议（如需要）",
  "severity": "轻度/中度/重度",
  "urgency": "常规/尽快/紧急",
  "prognosis": "预后评估",
  "lifestyle": ["生活建议1", "生活建议2", "生活建议3"],
  "followUp": "复诊建议",
  "warnings": ["注意事项1", "注意事项2"]
}

注意：
- 仅基于图像可见信息进行分析，不确定的内容标注置信度
- 如图片不清晰或非肛肠相关，请在结果中说明
- 建议仅供参考，最终诊断需结合完整四诊信息
"""


async def analyze_image(
    image_base64: str,
    image_type: str = "lesion",
    extra_symptoms: Optional[str] = None,
    patient_info: Optional[str] = None,
) -> dict:
    """
    Analyze an anorectal clinical image using Qwen VL multimodal model.

    Args:
        image_base64: Base64-encoded image data
        image_type: Type of image (hemorrhoid, fissure, abscess, fistula, prolapse, eczema, condyloma, lesion, tongue)
        extra_symptoms: Additional symptom description from the patient
        patient_info: Brief patient demographics (age, gender, duration)

    Returns:
        Structured diagnostic result as a dictionary
    """
    if not settings.QWEN_API_KEY:
        return {
            "error": "QWEN_API_KEY未配置",
            "disease": "无法分析",
            "confidence": 0,
            "visualFindings": "AI服务未配置，请联系管理员设置QWEN_API_KEY",
        }

    image_type_map = {
        "hemorrhoid": "痔疮",
        "fissure": "肛裂",
        "abscess": "肛周脓肿",
        "fistula": "肛瘘",
        "prolapse": "直肠脱垂",
        "eczema": "肛周湿疹",
        "condyloma": "尖锐湿疣",
        "lesion": "肛周病变",
        "tongue": "舌象",
    }

    disease_hint = image_type_map.get(image_type, "肛周病变")

    user_content_parts = []

    system_prompt = ANORECTAL_VISION_PROMPT

    supplementary_text = f"图片类型提示：{disease_hint}"
    if extra_symptoms:
        supplementary_text += f"\n患者主诉症状：{extra_symptoms}"
    if patient_info:
        supplementary_text += f"\n患者基本信息：{patient_info}"

    user_content_parts.append({"type": "text", "text": supplementary_text})
    user_content_parts.append({
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
    })
    user_content_parts.append({"type": "text", "text": "请分析这张图片并按指定JSON格式返回结果。"})

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content_parts},
    ]

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.QWEN_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.QWEN_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.QWEN_MODEL,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 4096,
                    "response_format": {"type": "json_object"},
                },
            )

            if response.status_code != 200:
                logger.error(f"Qwen API error: {response.status_code} - {response.text}")
                return {
                    "error": f"AI服务请求失败: {response.status_code}",
                    "disease": "分析失败",
                    "confidence": 0,
                    "visualFindings": "AI 服务返回异常,请稍后重试",
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
                        "disease": "解析失败",
                        "confidence": 0,
                        "visualFindings": content[:500],
                        "rawResponse": content,
                    }

            analysis["imageType"] = image_type
            analysis["modelUsed"] = settings.QWEN_MODEL
            return analysis

    except httpx.TimeoutException:
        logger.error("Qwen API timeout")
        return {
            "error": "AI服务请求超时",
            "disease": "分析超时",
            "confidence": 0,
            "visualFindings": "请求超时，请稍后重试",
        }
    except Exception as e:
        logger.error(f"Vision AI analysis error: {str(e)}")
        return {
            "error": f"分析异常: {str(e)}",
            "disease": "分析异常",
            "confidence": 0,
            "visualFindings": "AI 服务暂时不可用,请稍后重试",
        }


async def analyze_tongue_image(image_base64: str, symptoms: Optional[str] = None) -> dict:
    """
    Analyze a tongue image for TCM diagnosis support.
    """
    tongue_prompt = """你是一位资深中医舌诊专家。请分析这张舌象图片，给出详细的舌诊分析。

分析内容：
1. 舌体：大小、形态、动态（胖大/瘦薄/齿痕/裂纹/歪斜）
2. 舌色：淡白/淡红/红/绛/紫/青
3. 舌苔：薄白/薄黄/厚腻/黄腻/灰黑/剥苔/无苔
4. 舌下络脉：正常/怒张/紫暗

请按JSON格式返回：
{
  "tongueBody": {"size": "", "shape": "", "features": []},
  "tongueColor": "",
  "coating": {"color": "", "thickness": "", "moisture": "", "distribution": ""},
  "sublingualVeins": "",
  "tcmAnalysis": "中医辨证分析",
  "possibleSyndromes": ["可能证型1", "可能证型2"],
  "relevantToAnorectal": "与肛肠疾病的关联分析"
}"""

    if not settings.QWEN_API_KEY:
        return {"error": "QWEN_API_KEY未配置"}

    user_parts = [
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
        {"type": "text", "text": "请分析这张舌象图片。" + (f"患者症状：{symptoms}" if symptoms else "")},
    ]

    messages = [
        {"role": "system", "content": tongue_prompt},
        {"role": "user", "content": user_parts},
    ]

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.QWEN_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.QWEN_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.QWEN_MODEL,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 2048,
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
        logger.error(f"Tongue analysis error: {str(e)}")
        return {"error": str(e)}
