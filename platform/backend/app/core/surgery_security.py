"""疮疡模块安全工具：上传文件校验 + AI 接口限流。

由 cy-backend-ref/app/security.py 移植而来（去除 SQLite 依赖，逻辑不变）。
"""
import time
from collections import defaultdict, deque
from typing import Any, Optional

from fastapi import HTTPException, UploadFile

from app.config import settings


def is_valid_image(data: bytes) -> bool:
    """按文件头(magic bytes)校验图片，防止伪装扩展名上传恶意文件。"""
    if not data:
        return False
    if data[:3] == b"\xff\xd8\xff":  # JPEG
        return True
    if data[:8] == b"\x89PNG\r\n\x1a\n":  # PNG
        return True
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":  # WebP
        return True
    if data[:2] == b"BM":  # BMP
        return True
    return False


async def read_limited(file: UploadFile, max_size: Optional[int] = None) -> bytes:
    """分块读取上传文件，超过大小上限即拒绝（防内存/磁盘 DoS）。"""
    limit = max_size or settings.MAX_UPLOAD_SIZE
    data = bytearray()
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        data += chunk
        if len(data) > limit:
            raise HTTPException(status_code=413, detail="文件过大(超过 10MB 限制)")
    return bytes(data)


class RateLimiter:
    """简单的内存限流器(按 key 统计固定时间窗口内的请求次数)。"""

    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window = window_seconds
        self._hits: dict[str, deque] = defaultdict(deque)

    def check(self, key: str) -> bool:
        now = time.time()
        dq = self._hits[key]
        while dq and now - dq[0] > self.window:
            dq.popleft()
        if len(dq) >= self.max_requests:
            return False
        dq.append(now)
        return True


# AI 接口限流：同一 IP 每分钟最多 10 次(防刷爆付费 API)
ai_limiter = RateLimiter(max_requests=10, window_seconds=60.0)
write_limiter = RateLimiter(max_requests=30, window_seconds=60.0)


def limit_write(request: Any) -> None:
    """写接口限流:同一 IP 每分钟最多 30 次(全开放平台的滥用防护)。"""
    client_ip = (
        (request.headers.get("x-real-ip") or "").strip()
        if request is not None
        else ""
    ) or (request.client.host if request and request.client else "unknown")
    if not write_limiter.check(client_ip):
        raise HTTPException(status_code=429, detail="操作过于频繁,请稍后再试")


def limit_ai(request: Any) -> None:
    client_ip = (
        (request.headers.get("x-real-ip") or "").strip()
        if request is not None
        else ""
    ) or (request.client.host if request and request.client else "unknown")
    if not ai_limiter.check(client_ip):
        raise HTTPException(status_code=429, detail="请求过于频繁,请稍后再试")
