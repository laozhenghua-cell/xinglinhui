"""轻量级进程内滑动窗口限流，用于登录/注册接口的暴力破解防护。

说明：本实现基于单进程内存，适合单 worker 演示环境。
多 worker / 多实例生产部署应改用 Redis 或网关层（如 Nginx limit_req）做共享限流。
"""
import time
from collections import defaultdict, deque
from typing import Deque, Dict


class SlidingWindowLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)

    def is_allowed(self, key: str) -> bool:
        now = time.monotonic()
        q = self._hits[key]
        while q and now - q[0] > self.window_seconds:
            q.popleft()
        if len(q) >= self.max_requests:
            return False
        q.append(now)
        return True

    def reset(self, key: str) -> None:
        self._hits.pop(key, None)


# 登录：每个来源（IP+邮箱）60 秒内最多 10 次
login_limiter = SlidingWindowLimiter(max_requests=10, window_seconds=60)
# 注册：每个来源（IP+邮箱）10 分钟内最多 5 次
register_limiter = SlidingWindowLimiter(max_requests=5, window_seconds=600)
