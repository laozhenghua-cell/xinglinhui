"""可观测性:结构化请求日志 + Prometheus /metrics(零第三方依赖,自产文本格式)。"""
from __future__ import annotations

import logging
import time
import uuid
from collections import defaultdict
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("http")

METRICS: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
_DURATION_SUM: dict[str, float] = defaultdict(float)
_DURATION_COUNT: dict[str, int] = defaultdict(int)
_BUCKETS = (0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
_DURATION_BUCKETS: dict[str, dict[float, int]] = defaultdict(lambda: defaultdict(int))


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """记录 request-id、状态码、耗时;聚合 Prometheus 指标。"""

    async def dispatch(self, request: Request, call_next: Callable):
        rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            METRICS["http_requests_total"][(request.url.path, request.method, "500")] += 1
            raise
        elapsed = time.perf_counter() - start
        status = str(response.status_code)
        path = request.url.path
        method = request.method
        METRICS["http_requests_total"][(path, method, status)] += 1
        _DURATION_SUM[path] += elapsed
        _DURATION_COUNT[path] += 1
        for b in _BUCKETS:
            if elapsed <= b:
                _DURATION_BUCKETS[path][b] += 1
        logger.info(
            'http request_id=%s method=%s path=%s status=%s dur=%.3f',
            rid, method, path, status, elapsed,
        )
        response.headers["X-Request-Id"] = rid
        return response


def metrics_text() -> str:
    """Prometheus 文本格式。"""
    from app.core.ai_gateway import gateway_stats

    lines = []
    lines.append("# HELP http_requests_total HTTP 请求总数(按 path/method/status)")
    lines.append("# TYPE http_requests_total counter")
    for (path, method, status), n in METRICS["http_requests_total"].items():
        labels = f'path="{path}",method="{method}",status="{status}"'
        lines.append(f"http_requests_total{{{labels}}} {n}")

    lines.append("# HELP http_request_duration_seconds 请求耗时")
    lines.append("# TYPE http_request_duration_seconds histogram")
    for path in _DURATION_COUNT:
        lines.append(f'http_request_duration_seconds_sum{{path="{path}"}} {_DURATION_SUM[path]:.6f}')
        lines.append(f'http_request_duration_seconds_count{{path="{path}"}} {_DURATION_COUNT[path]}')
        for b in _BUCKETS:
            lines.append(
                f'http_request_duration_seconds_bucket{{path="{path}",le="{b}"}} {_DURATION_BUCKETS[path].get(b, 0)}'
            )
        lines.append(f'http_request_duration_seconds_bucket{{path="{path}",le="+Inf"}} {_DURATION_COUNT[path]}')

    gs = gateway_stats()
    lines.append("# HELP ai_gateway_calls_total AI 网关调用次数")
    lines.append("# TYPE ai_gateway_calls_total counter")
    lines.append(f"ai_gateway_calls_total {gs.get('calls', 0)}")
    lines.append("# HELP ai_gateway_failures_total AI 网关失败次数")
    lines.append("# TYPE ai_gateway_failures_total counter")
    lines.append(f"ai_gateway_failures_total {gs.get('failures', 0)}")
    lines.append("# HELP ai_gateway_tokens_in_total AI 输入 tokens")
    lines.append("# TYPE ai_gateway_tokens_in_total counter")
    lines.append(f"ai_gateway_tokens_in_total {gs.get('tokens_in', 0)}")
    lines.append("# HELP ai_gateway_tokens_out_total AI 输出 tokens")
    lines.append("# TYPE ai_gateway_tokens_out_total counter")
    lines.append(f"ai_gateway_tokens_out_total {gs.get('tokens_out', 0)}")
    lines.append("# HELP ai_gateway_cost_milli_total AI 成本(分/千)")
    lines.append("# TYPE ai_gateway_cost_milli_total counter")
    lines.append(f"ai_gateway_cost_milli_total {gs.get('cost_milli', 0)}")
    return "\n".join(lines) + "\n"
