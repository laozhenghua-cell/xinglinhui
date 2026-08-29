"""通义千问 QWEN Vision 服务 —— 疮疡图像辨病 + 辨证"""
import base64
import json
import re
from pathlib import Path
from typing import Any, Optional

import httpx

from ..config import settings


class QwenVisionService:
    def __init__(self) -> None:
        self.api_key = settings.qwen_api_key
        self.api_base = settings.qwen_api_base
        self.model = settings.qwen_vision_model

    def _encode(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _to_content(self, image_ref: str) -> str:
        if image_ref.startswith(("http://", "https://", "data:image")):
            return image_ref
        return f"data:image/jpeg;base64,{self._encode(image_ref)}"

    async def identify_disease(self, image_ref: str, symptoms: Optional[str] = None) -> dict[str, Any]:
        """拍照辨病:识别疮疡类型 + 形态 + 分期 + 证型 + 治疗建议"""
        prompt = """你是中医外科专家,精通疮疡(疖、痈、疽、疔、瘰疬、流注、臁疮、脱疽等)的辨病与辨证。
请仔细观察这张疮疡照片,结合中医外科疮疡的辨证方法分析。

【分析要点】
1. 发病部位(具体部位)
2. 疮形特点:颜色、大小、形状、质地、有无脓头/脓栓、根盘是否收束、有无头
3. 辨病:最可能的病种(如:印堂疔、鼻疔、蛇头疔、热疖、颈痈、脑疽、发背、附骨疽、臁疮、脱疽等)
4. 辨阴阳:阳证(红、肿、热、痛、发病急)或阴证(色白不热、漫肿、发病缓)
5. 分期:初起(未成脓)/ 成脓(按之应指)/ 溃后(脓出未敛)
6. 证型:火毒炽盛 / 热盛肉腐 / 余毒未清 / 正虚邪恋 / 气血两虚 / 湿热下注
7. 危险提示:是否位于颜面危险三角区、是否可能走黄/内陷、是否需要转诊
"""
        if symptoms:
            prompt += f"\n【主诉症状】{symptoms}\n"

        prompt += """
请只返回 JSON(不要任何其他文字):
{
  "location": "发病部位",
  "disease_name": "最可能病种",
  "confidence": 0.85,
  "morphology": {"color":"颜色","size":"大小","shape":"形状","texture":"质地","has_pus_head":true},
  "yin_yang": "阳",
  "stage": "初起",
  "syndrome_name": "火毒炽盛",
  "dangerous": false,
  "danger_reason": "危险原因或空字符串",
  "differential": ["鉴别诊断1","鉴别诊断2"],
  "treatment": {"principle":"治则","internal":"内治方","external":"外治法"},
  "note": "给医生的一句话提示"
}
"""

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.api_base}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": self._to_content(image_ref)}},
                            {"type": "text", "text": prompt},
                        ],
                    }],
                    "temperature": 0.3,
                },
            )
            if resp.status_code != 200:
                raise RuntimeError(f"QWEN Vision 调用失败({resp.status_code}): {resp.text[:200]}")

            ai_text = resp.json()["choices"][0]["message"]["content"]
            return self._parse(ai_text)

    def _parse(self, ai_text: str) -> dict[str, Any]:
        m = re.search(r"```(?:json)?\s*(.*?)\s*```", ai_text, re.DOTALL)
        raw = m.group(1) if m else ai_text.strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"raw_text": ai_text, "error": "AI 返回解析失败,请重试"}

    async def compare_images(self, initial_path: str, current_path: str, days: int = 0) -> dict[str, Any]:
        """复诊对比:对比治疗前后疮疡照片,评估疗效"""
        prompt = f"""你是中医外科专家。这是同一患者治疗前后的疮疡对比照片。
第一张:初诊(治疗前);第二张:复诊(治疗后,间隔约{days}天)。

请对比分析并只返回 JSON(不要其他文字):
{{
  "redness_change": "减轻/无变化/加重",
  "size_change": "缩小/无变化/增大",
  "discharge_change": "脓液减少/无变化/增多",
  "effectiveness": "显效/有效/无效/加重",
  "score": 7,
  "analysis": "红肿、疮口大小、颜色、分泌物等的变化描述",
  "suggestion": "后续治疗建议"
}}"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.api_base}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": self._to_content(initial_path)}},
                            {"type": "image_url", "image_url": {"url": self._to_content(current_path)}},
                            {"type": "text", "text": prompt},
                        ],
                    }],
                    "temperature": 0.3,
                },
            )
            if resp.status_code != 200:
                raise RuntimeError(f"QWEN Vision 调用失败({resp.status_code}): {resp.text[:200]}")
            return self._parse(resp.json()["choices"][0]["message"]["content"])


qwen_vision_service = QwenVisionService()
