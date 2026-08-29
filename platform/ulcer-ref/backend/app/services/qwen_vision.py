"""
千问视觉服务 - 用于疮疡图像分析
"""
import base64
import os
import httpx
from typing import Optional, Dict, Any
from pathlib import Path

from ..core.config import settings


class QwenVisionService:
    """千问视觉API服务"""

    def __init__(self):
        self.api_key = os.environ.get("QWEN_API_KEY", "")
        self.api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.model = "qwen-vl-max-latest"  # 千问3.8 VL Max

    def _encode_image(self, image_path: str) -> str:
        """将图片编码为base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    async def analyze_ulcer_image(
        self,
        image_url: str,
        patient_info: Optional[Dict[str, Any]] = None,
        symptoms: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        分析疮疡图像

        Args:
            image_url: 图片URL或本地路径
            patient_info: 患者信息（性别、年龄等）
            symptoms: 症状信息（疼痛、发热等）

        Returns:
            AI分析结果
        """
        # 构建分析提示词
        prompt = self._build_analysis_prompt(patient_info, symptoms)

        # 如果是本地文件，转换为base64
        if image_url.startswith('/') or image_url.startswith('file://'):
            image_path = image_url.replace('file://', '')
            image_base64 = self._encode_image(image_path)
            image_content = f"data:image/jpeg;base64,{image_base64}"
        else:
            image_content = image_url

        # 调用千问API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {"url": image_content}
                                },
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ]
                        }
                    ],
                    "temperature": 0.3,
                    "top_p": 0.8
                }
            )

            if response.status_code != 200:
                raise Exception(f"千问API调用失败: {response.text}")

            result = response.json()
            ai_text = result["choices"][0]["message"]["content"]

            # 解析AI返回结果
            return self._parse_analysis_result(ai_text)

    def _build_analysis_prompt(
        self,
        patient_info: Optional[Dict[str, Any]],
        symptoms: Optional[Dict[str, Any]]
    ) -> str:
        """构建分析提示词"""
        prompt = """你是一位中医外科专家，精通疮疡诊断。请根据图片分析这个疮疡病例。

【分析要点】
1. 发病部位：准确描述患处位置（头面部/上肢/下肢/躯干，具体部位）
2. 疮疡类型：判断最可能的疮疡类型（如：印堂疔、鼻疔、眼有疔、虎口疔、蛇头疔等）
3. 形态特征：
   - 颜色（鲜红/暗红/黄白/紫红等）
   - 大小（粟粒大/蚕豆大/栗子大等）
   - 形状（圆形/椭圆/不规则）
   - 质地（根深坚硬/柔软/有波动感）
   - 是否有脓头、麻栓
4. 疾病分期：初期/中期/后期/溃脓期/收口期
5. 证型判断：火毒炽盛/正虚邪恋/气血两虚等
6. 严重程度：轻度/中度/重度/危重（1-10分）
7. 是否需要专家会诊：判断基层医生是否需要上级专家指导
8. 治疗建议：
   - 内治法：推荐方剂（如五味消毒饮、仙方活命饮等）
   - 外治法：外敷药物（如油调膏、玉露散等）
   - 其他建议（切开排脓、熏洗等）

"""

        # 添加患者信息
        if patient_info:
            prompt += f"\n【患者信息】\n"
            if patient_info.get("gender"):
                prompt += f"- 性别：{patient_info['gender']}\n"
            if patient_info.get("age"):
                prompt += f"- 年龄：{patient_info['age']}岁\n"

        # 添加症状信息
        if symptoms:
            prompt += f"\n【主诉症状】\n"
            if symptoms.get("pain_level"):
                prompt += f"- 疼痛程度：{symptoms['pain_level']}/10\n"
            if symptoms.get("duration_days"):
                prompt += f"- 病程：{symptoms['duration_days']}天\n"
            if symptoms.get("fever"):
                prompt += f"- 发热：是\n"
            if symptoms.get("systemic"):
                prompt += f"- 全身症状：{symptoms['systemic']}\n"

        prompt += """
请以JSON格式返回分析结果（仅返回JSON，不要其他说明文字）：
{
  "location": "发病部位",
  "location_detail": "具体位置描述",
  "ulcer_type": "疮疡类型",
  "confidence": 0.85,
  "morphology": {
    "color": "颜色",
    "size": "大小",
    "shape": "形状",
    "texture": "质地",
    "has_pus": true/false
  },
  "stage": "疾病分期",
  "syndrome": "证型",
  "severity": 7,
  "severity_level": "中度",
  "needs_expert": true/false,
  "expert_reason": "需要专家原因",
  "treatment_suggestion": {
    "principle": "治则",
    "internal": {
      "formula": "方剂名称",
      "herbs": ["药物1", "药物2"],
      "usage": "用法"
    },
    "external": {
      "topical": "外敷药物",
      "frequency": "频次",
      "other": "其他外治法"
    }
  },
  "precautions": ["注意事项1", "注意事项2"],
  "differential_diagnosis": ["鉴别诊断1", "鉴别诊断2"]
}
"""
        return prompt

    def _parse_analysis_result(self, ai_text: str) -> Dict[str, Any]:
        """解析AI返回结果"""
        import json
        import re

        # 提取JSON部分（去除可能的markdown代码块标记）
        json_match = re.search(r'```json\s*(.*?)\s*```', ai_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 尝试直接解析
            json_str = ai_text.strip()

        try:
            result = json.loads(json_str)
            return result
        except json.JSONDecodeError:
            # 如果解析失败，返回原始文本
            return {
                "error": "AI返回结果解析失败",
                "raw_text": ai_text,
                "ulcer_type": "未知",
                "confidence": 0.0,
                "needs_expert": True,
                "expert_reason": "AI分析异常，建议人工审核"
            }

    async def compare_images(
        self,
        initial_image_url: str,
        current_image_url: str,
        days_since_treatment: int
    ) -> Dict[str, Any]:
        """
        对比治疗前后的疮疡图像

        Args:
            initial_image_url: 初诊图片
            current_image_url: 复诊图片
            days_since_treatment: 治疗天数

        Returns:
            对比分析结果
        """
        prompt = f"""你是一位中医外科专家。这是同一患者治疗前后的疮疡对比照片。

第一张图：初诊时的患处照片
第二张图：治疗{days_since_treatment}天后的复诊照片

请对比分析：
1. 红肿程度变化（消退/无变化/加重）
2. 疮口大小变化（缩小比例、愈合情况）
3. 颜色变化（鲜红→淡红→正常）
4. 分泌物变化（脓液减少/消失）
5. 周围肿胀变化
6. 整体改善评分（1-10分，10分为完全治愈）
7. 疗效评价（显效/有效/无效/加重）
8. 后续治疗建议

以JSON格式返回：
{{
  "redness_change": "减轻/无变化/加重",
  "redness_reduction": 0.6,
  "size_change": "缩小/无变化/增大",
  "size_reduction": 0.4,
  "color_improvement": "淡红",
  "discharge_change": "脓液减少",
  "swelling_change": "消退",
  "improvement_score": 7.5,
  "effectiveness": "有效",
  "detailed_analysis": "详细对比分析...",
  "next_treatment": "后续治疗建议...",
  "estimated_cure_days": 5
}}
"""

        # 处理图片URL
        images = []
        for img_url in [initial_image_url, current_image_url]:
            if img_url.startswith('/') or img_url.startswith('file://'):
                image_path = img_url.replace('file://', '')
                image_base64 = self._encode_image(image_path)
                images.append(f"data:image/jpeg;base64,{image_base64}")
            else:
                images.append(img_url)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "image_url", "image_url": {"url": images[0]}},
                                {"type": "image_url", "image_url": {"url": images[1]}},
                                {"type": "text", "text": prompt}
                            ]
                        }
                    ],
                    "temperature": 0.3
                }
            )

            if response.status_code != 200:
                raise Exception(f"千问API调用失败: {response.text}")

            result = response.json()
            ai_text = result["choices"][0]["message"]["content"]

            return self._parse_analysis_result(ai_text)


# 全局实例
qwen_vision_service = QwenVisionService()
