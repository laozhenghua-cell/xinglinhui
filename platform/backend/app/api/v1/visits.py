"""访问统计埋点(免鉴权)。

POST /api/v1/visits
    body: {module, path, referrer?}
    记录 client IP + User-Agent，IP 用加盐 SHA256 哈希后存储(不存明文)。
"""
import hashlib
from typing import Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.visit import Visit

router = APIRouter(prefix="/visits", tags=["访问统计"])


class VisitCreate(BaseModel):
    module: str
    path: str
    referrer: Optional[str] = None


def _real_ip(request: Request) -> str:
    """nginx 反代下 client.host 恒为网关地址;真实客户端 IP 取自 nginx 覆盖注入的 X-Real-IP。"""
    return (request.headers.get("x-real-ip") or "").strip() or (
        request.client.host if request.client else "unknown"
    )

def hash_ip(client_ip: str) -> str:
    salt = settings.visit_salt
    return hashlib.sha256(f"{salt}:{client_ip}".encode("utf-8")).hexdigest()


def hash_ua(user_agent: str) -> str:
    salt = settings.visit_salt
    return hashlib.sha256(f"{salt}:ua:{user_agent}".encode("utf-8")).hexdigest()


@router.post("")
async def record_visit(
    body: VisitCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    client_ip = _real_ip(request)
    user_agent = request.headers.get("user-agent", "") or ""

    visit = Visit(
        module=body.module,
        path=body.path,
        ip_hash=hash_ip(client_ip),
        ua_hash=hash_ua(user_agent),
        referrer=body.referrer,
    )
    db.add(visit)
    await db.commit()
    return {"status": "ok"}
