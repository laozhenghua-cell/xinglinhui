"""公开使用统计(免鉴权)。

GET /api/v1/stats/public
    {
      totals: {pv, uv, days},
      today: {pv, uv},
      by_module: [{module, pv, uv}],
      daily_30: [{date, pv, uv}]
    }
UV = 去重后的 ip_hash+ua_hash 组合(即"独立访客/设备")。
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from sqlalchemy import Date, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.visit import Visit

router = APIRouter(prefix="/stats", tags=["公开统计"])

# 独立访客表达式：ip_hash 与 ua_hash 均为 64 位十六进制，拼接后唯一
_UV = func.count(func.distinct(func.concat(Visit.ip_hash, ":", Visit.ua_hash)))
_PV = func.count()


@router.get("/public")
async def public_stats(db: AsyncSession = Depends(get_db)):
    today = datetime.now(ZoneInfo("Asia/Shanghai")).date()
    start_30 = today - timedelta(days=29)

    # 总量
    totals_row = (
        await db.execute(
            select(_PV, _UV, func.count(func.distinct(func.date(func.timezone('Asia/Shanghai', Visit.ts)))))
        )
    ).one()
    totals = {"pv": totals_row[0], "uv": totals_row[1], "days": totals_row[2]}

    # 今日
    today_row = (
        await db.execute(
            select(_PV, _UV).where(func.date(func.timezone('Asia/Shanghai', Visit.ts)) == today)
        )
    ).one()
    today_stats = {"pv": today_row[0], "uv": today_row[1]}

    # 按模块
    module_rows = (
        await db.execute(
            select(Visit.module, _PV, _UV)
            .group_by(Visit.module)
            .order_by(_PV.desc())
        )
    ).all()
    by_module = [{"module": m, "pv": pv, "uv": uv} for m, pv, uv in module_rows]

    # 近 30 天按天(子查询分组,规避表达式等价性差异)
    day_expr = func.cast(func.timezone("Asia/Shanghai", Visit.ts), Date)
    sub = (
        select(day_expr.label("day"), Visit.ip_hash, Visit.ua_hash)
        .where(day_expr >= start_30)
        .subquery()
    )
    daily_rows = (
        await db.execute(
            select(
                sub.c.day,
                func.count(),
                func.count(func.distinct(func.concat(sub.c.ip_hash, ":", sub.c.ua_hash))),
            )
            .group_by(sub.c.day)
            .order_by(sub.c.day)
        )
    ).all()
    daily_30 = [{"date": str(d), "pv": pv, "uv": uv} for d, pv, uv in daily_rows]

    return {
        "totals": totals,
        "today": today_stats,
        "by_module": by_module,
        "daily_30": daily_30,
    }
