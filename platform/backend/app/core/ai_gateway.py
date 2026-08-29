"""AI 模型网关 — 多模型路由 / 统一超时重试熔断 / 用量与成本计量 / JSON 校验。

设计目标:
- 全部 AI 调用收敛到本模块(DeepSeek 文本、Qwen 文本与视觉);
- 每提供商独立熔断(连续失败 N 次打开 60s);
- 每次调用记录 tokens 与估算成本(结构化日志 + 计数器);
- chat_json 强制 JSON 输出并自动剥代码围栏。
"""
from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Optional

import httpx

from app.config import settings

logger = logging.getLogger("ai_gateway")

# 成本估算(人民币/百万 token,2026 参考价,可调)
COST_PER_MTOK = {
    "deepseek-chat": (2.0, 8.0),   # 输入/输出
    "qwen-vl-max": (3.0, 12.0),
    "qwen-plus": (0.8, 2.0),
    "qwen-turbo": (0.3, 0.6),
}


class CircuitBreaker:
    """进程内熔断器:连续失败 >= threshold 则打开 open_seconds。"""

    def __init__(self, threshold: int = 5, open_seconds: float = 60.0):
        self.threshold = threshold
        self.open_seconds = open_seconds
        self._fails: dict[str, int] = {}
        self._open_until: dict[str, float] = {}

    def allow(self, name: str) -> bool:
        until = self._open_until.get(name, 0)
        if until and time.time() < until:
            return False
        if until:
            self._open_until.pop(name, None)
            self._fails[name] = 0
        return True

    def record(self, name: str, ok: bool) -> None:
        if ok:
            self._fails[name] = 0
            return
        self._fails[name] = self._fails.get(name, 0) + 1
        if self._fails[name] >= self.threshold:
            self._open_until[name] = time.time() + self.open_seconds
            logger.warning("ai_gateway 熔断器打开: provider=%s", name)


_breakers = CircuitBreaker()

# 简单计数器(供 /metrics 采集)
_gw_stats: dict[str, int] = {"calls": 0, "failures": 0, "tokens_in": 0, "tokens_out": 0, "cost_milli": 0}


def gateway_stats() -> dict[str, int]:
    return dict(_gw_stats)


class AIError(Exception):
    """网关统一异常(业务层可据此降级)。"""


def _provider(name: str) -> dict[str, str]:
    if name == "deepseek":
        if not settings.DEEPSEEK_API_KEY:
            raise AIError("DEEPSEEK_API_KEY 未配置")
        return {"base": settings.DEEPSEEK_BASE_URL, "key": settings.DEEPSEEK_API_KEY, "model": settings.DEEPSEEK_MODEL}
    if name == "qwen":
        if not settings.QWEN_API_KEY:
            raise AIError("QWEN_API_KEY 未配置")
        return {"base": settings.QWEN_BASE_URL, "key": settings.QWEN_API_KEY, "model": settings.QWEN_MODEL}
    raise AIError(f"未知提供商: {name}")


def _record_usage(model: str, usage: Optional[dict]) -> None:
    if not usage:
        return
    pin = int(usage.get("prompt_tokens") or 0)
    pout = int(usage.get("completion_tokens") or 0)
    _gw_stats["tokens_in"] += pin
    _gw_stats["tokens_out"] += pout
    price = COST_PER_MTOK.get(model, COST_PER_MTOK.get("deepseek-chat", (2.0, 8.0)))
    cost = pin / 1e6 * price[0] + pout / 1e6 * price[1]
    _gw_stats["cost_milli"] += int(cost * 1000)
    logger.info("ai_gateway usage model=%s in=%d out=%d cost=%.5f", model, pin, pout, cost)


async def chat(
    task: str,
    messages: list[dict],
    provider: str = "deepseek",
    timeout: float = 60.0,
    temperature: float = 0.3,
    max_retries: int = 2,
) -> dict:
    """通用对话调用。返回 {"text":..., "usage":...}。失败抛 AIError。"""
    if not _breakers.allow(provider):
        raise AIError(f"AI 提供商 {provider} 熔断中,请稍后重试")
    cfg = _provider(provider)
    _gw_stats["calls"] += 1
    last_err: Optional[Exception] = None
    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(
                    f"{cfg['base']}/chat/completions",
                    headers={"Authorization": f"Bearer {cfg['key']}"},
                    json={
                        "model": cfg["model"],
                        "messages": messages,
                        "temperature": temperature,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                choice = data["choices"][0]["message"]["content"]
                usage = data.get("usage")
                _record_usage(cfg["model"], usage)
                _breakers.record(provider, True)
                logger.info("ai_gateway call ok task=%s provider=%s attempt=%d", task, provider, attempt)
                return {"text": choice, "usage": usage, "model": cfg["model"]}
        except Exception as e:  # noqa: BLE001
            last_err = e
            _gw_stats["failures"] += 1
            logger.warning("ai_gateway call failed task=%s provider=%s attempt=%d err=%s", task, provider, attempt, repr(e))
            if attempt < max_retries:
                await _sleep(0.5 * (attempt + 1))
    _breakers.record(provider, False)
    raise AIError(f"AI 调用失败({provider}): {repr(last_err)}")


async def _sleep(seconds: float) -> None:
    import asyncio

    await asyncio.sleep(seconds)


async def chat_json(
    task: str,
    messages: list[dict],
    provider: str = "deepseek",
    timeout: float = 60.0,
    temperature: float = 0.3,
) -> dict:
    """强制 JSON 输出:剥离 ```json 围栏并解析;失败抛 AIError。"""
    result = await chat(task, messages, provider=provider, timeout=timeout, temperature=temperature)
    text = result["text"].strip()
    m = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    raw = m.group(1) if m else text
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise AIError(f"AI 输出非 JSON: {e}") from e
    return {**result, "json": parsed}


async def vision(
    image_b64: str,
    symptoms: Optional[str] = None,
    provider: str = "qwen",
    timeout: float = 90.0,
) -> dict:
    """视觉辨病(Qwen-VL 多模态)。返回 {"text", "json", "usage"}。"""
    if not _breakers.allow(provider):
        raise AIError(f"AI 提供商 {provider} 熔断中,请稍后重试")
    cfg = _provider(provider)
    _gw_stats["calls"] += 1
    prompt = (
        "你是中医专家,请对患处照片做辨病辨证:部位、疮形、辨病、辨阴阳、分期、证型、危险提示。"
        "只返回 JSON(字段:disease_name, confidence, yin_yang, stage, syndrome_name, dangerous, danger_reason, differential, treatment)。"
    )
    if symptoms:
        prompt += f"主诉:{symptoms}"
    content = [
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
        {"type": "text", "text": prompt},
    ]
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                f"{cfg['base']}/chat/completions",
                headers={"Authorization": f"Bearer {cfg['key']}"},
                json={"model": cfg["model"], "messages": [{"role": "user", "content": content}]},
            )
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            usage = data.get("usage")
            _record_usage(cfg["model"], usage)
            _breakers.record(provider, True)
            m = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
            raw = m.group(1) if m else text.strip()
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = {"raw_text": text[:2000]}
            return {"text": text, "json": parsed, "usage": usage}
    except Exception as e:  # noqa: BLE001
        _gw_stats["failures"] += 1
        _breakers.record(provider, False)
        raise AIError(f"视觉调用失败({provider}): {repr(e)}") from e


async def embed(texts: list[str], provider: str = "qwen", timeout: float = 30.0) -> list[list[float]]:
    """文本向量化(Qwen text-embedding)。空输入返回空列表。"""
    if not texts:
        return []
    cfg = _provider(provider)
    out: list[list[float]] = []
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Dashscope 批大小上限约 10+,分块请求(每批 10)
            for i in range(0, len(texts), 10):
                chunk = texts[i : i + 10]
                resp = await client.post(
                    f"{cfg['base']}/embeddings",
                    headers={"Authorization": f"Bearer {cfg['key']}"},
                    json={"model": "text-embedding-v3", "input": chunk},
                )
                resp.raise_for_status()
                data = resp.json()
                out.extend(item["embedding"] for item in sorted(data["data"], key=lambda x: x["index"]))
        return out
    except Exception as e:  # noqa: BLE001
        logger.warning("ai_gateway embed failed err=%s", repr(e))
        raise AIError(f"向量化失败: {repr(e)}") from e
