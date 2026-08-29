"""访问统计埋点表(visits)。IP / UA 只存加盐哈希，不存明文。"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
    module: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    ip_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    ua_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    referrer: Mapped[str] = mapped_column(String(500), nullable=True)
