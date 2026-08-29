"""DeepSeek 文本服务 —— 根据疮形特点描述辨病 + 辨证(视觉 key 失效时的可靠降级)"""
import json
import re
from typing import Any, Optional

import httpx

from ..config import settings


class DeepSeekService:
    def __init__(self) -> None:
        self.api_key = settings.deepseek_api_key
        self.api_base = settings.deepseek_base_url
        self.model = settings.deepseek_model

    async def analyze_symptoms(self, text: str) -> dict[str, Any]:
        """根据医生对疮形特点的文字描述,辅助辨病 + 辨证"""
        prompt = f"""你是中医外科专家。请根据医生对疮疡的描述,辅助辨病辨证。
疮疡病种参考:印堂疔、鼻疔、人中疔、蛇头疔、托盘疔、热疖、暑疖、蝼蛄疖、坐板疖、颈痈、结喉痈、脑疽、发背、附骨疽、臁疮、脱疽等。

【医生描述】
{text}

请只返回 JSON(不要其他文字):
{{
  "disease_name": "最可能病种",
  "confidence": 0.8,
  "yin_yang": "阳",
  "stage": "初起",
  "syndrome_name": "火毒炽盛",
  "dangerous": false,
  "danger_reason": "",
  "differential": ["鉴别1","鉴别2"],
  "treatment": {{"principle":"治则","internal":"内治方","external":"外治法"}},
  "note": "给医生的一句话提示"
}}"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.api_base}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                },
            )
            if resp.status_code != 200:
                raise RuntimeError(f"DeepSeek 调用失败({resp.status_code}): {resp.text[:200]}")
            ai_text = resp.json()["choices"][0]["message"]["content"]
            return self._parse(ai_text)

    def _parse(self, ai_text: str) -> dict[str, Any]:
        m = re.search(r"```(?:json)?\s*(.*?)\s*```", ai_text, re.DOTALL)
        raw = m.group(1) if m else ai_text.strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"raw_text": ai_text, "error": "AI 返回解析失败"}


deepseek_service = DeepSeekService()
