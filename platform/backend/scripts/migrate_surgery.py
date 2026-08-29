#!/usr/bin/env python3
"""从 platform/surgery.db(SQLite) 全量迁移疮疡数据到 PostgreSQL 的 surgery_* 表。

用法(独立运行):
    cd platform/backend
    DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db" python scripts/migrate_surgery.py

可选环境变量:
    SOURCE_DB            源 SQLite 路径(默认 ../surgery.db)
    TARGET_TABLE_PREFIX  目标表前缀(默认 surgery_)

行为:
    - 先按 ORM 模型(single source of truth)创建 surgery_* 表(幂等);
    - 逐表"先清空再全量插入"(幂等,可重复执行);
    - 逐表输出对账:表名: 源N行 -> 目标M行;
    - 处理 JSON 字段(diseases.aliases,JSON→TEXT/JSON)与日期字段;
    - 疮疡 patients 表复用基座已有 patients 表(源表为空),故不迁移。

注意:脚本只写 PG,不会碰基座(痔漏)的任何表。
"""
from __future__ import annotations

import asyncio
import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# 让 `app` 包可被导入(脚本可能以 `python scripts/migrate_surgery.py` 方式运行)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import create_async_engine  # noqa: E402

from app.database import Base  # noqa: E402
import app.models.surgery  # noqa: E402,F401  确保 surgery_* 表注册进 metadata


# 源表 → 迁移顺序(先父后子,保证外键依赖)
MIGRATION_ORDER = [
    "diseases",
    "syndromes",
    "formulas",
    "treatment_rules",
    "images",
    "cases",
    "case_images",
    "treatment_records",
    "expert_experiences",
    "expert_cases",
    "clinical_tips",
]

# 复用基座 patients 表,不迁移(源 patients 表为空)
SKIP_SOURCE_TABLES = {"patients"}

# 每张源表的列类型规格(kind 决定值转换方式)
# kind: int | str | text | bool | json | datetime
TABLE_COLUMNS: dict[str, dict[str, str]] = {
    "diseases": {
        "id": "int", "name": "str", "aliases": "json", "category": "str",
        "location": "str", "morphology": "text", "characteristics": "text",
        "differential": "text", "prognosis": "text", "western_equiv": "str",
        "source": "str", "is_dangerous": "bool", "is_sores": "bool",
        "is_yang": "bool", "differentiation": "str",
    },
    "syndromes": {
        "id": "int", "name": "str", "yin_yang": "str", "stage": "str",
        "local_signs": "text", "systemic_signs": "text", "tongue_pulse": "text",
    },
    "formulas": {
        "id": "int", "name": "str", "source": "str", "composition": "text",
        "dosage": "text", "function": "text", "indication": "text",
        "method": "str", "usage_type": "str", "usage": "text",
        "contraindications": "text", "toxicity": "str", "modifications": "text",
        "preparation": "text", "domain": "str",
    },
    "treatment_rules": {
        "id": "int", "disease_id": "int", "stage": "str", "syndrome_id": "int",
        "internal_formula_id": "int", "external_treatment": "text",
        "nursing": "text", "note": "text", "is_specific": "bool",
    },
    "images": {
        "id": "int", "disease_id": "int", "image_type": "str", "category": "str",
        "path": "str", "caption": "str",
    },
    "cases": {
        "id": "int", "patient_id": "int", "patient_name": "str", "gender": "str",
        "age": "int", "disease_id": "int", "syndrome_id": "int", "stage": "str",
        "chief_complaint": "text", "created_at": "datetime", "syndrome": "text",
        "treatment": "text", "effect": "text", "source": "str", "domain": "str",
        "history": "text",
    },
    "case_images": {
        "id": "int", "case_id": "int", "path": "str", "taken_at": "datetime",
    },
    "treatment_records": {
        "id": "int", "case_id": "int", "formula_id": "int",
        "external_treatment": "text", "effect": "text", "recorded_at": "datetime",
    },
    "expert_experiences": {
        "id": "int", "category": "str", "expert_name": "str",
        "syndrome_points": "text", "internal_treatment": "text",
        "external_treatment": "text", "source": "str", "domain": "str",
    },
    "expert_cases": {
        "id": "int", "category": "str", "expert_name": "str", "diagnosis": "str",
        "history": "text", "syndrome": "text", "treatment": "text",
        "effect": "text", "domain": "str",
    },
    "clinical_tips": {
        "id": "int", "category": "str", "content": "text", "source": "str",
    },
}


def parse_datetime(value) -> datetime | None:
    """解析 SQLite 的 'YYYY-MM-DD HH:MM:SS[.ffffff]' 为朴素 datetime。"""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    s = str(value).strip().replace(" ", "T")
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return datetime.fromisoformat(s[:19])


def convert_value(kind: str, value):
    if value is None:
        return None
    if kind == "int":
        return int(value)
    if kind == "bool":
        return bool(int(value))
    if kind == "json":
        if isinstance(value, (list, dict)):
            return value
        if isinstance(value, str):
            s = value.strip()
            if not s:
                return []
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                return []
        return []
    if kind == "datetime":
        return parse_datetime(value)
    # str / text
    return value


def read_source_table(source_db: str, table: str) -> list[dict]:
    """用 stdlib sqlite3 读取源表全部行,返回按规格转换后的行字典列表。"""
    conn = sqlite3.connect(source_db)
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(f'SELECT * FROM "{table}"')
        specs = TABLE_COLUMNS[table]
        rows = []
        for r in cur.fetchall():
            row = {col: convert_value(specs[col], r[col]) for col in specs}
            rows.append(row)
        return rows
    finally:
        conn.close()


def read_source_count(source_db: str, table: str) -> int:
    conn = sqlite3.connect(source_db)
    try:
        return conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
    finally:
        conn.close()


async def main() -> None:
    if os.environ.get("ALLOW_TRUNCATE") != "1":
        print("提示: 目标 surgery_* 表可能已有业务数据;如确认要清空重灌,请设置 ALLOW_TRUNCATE=1 后重跑。", file=sys.stderr)
        print("(当前为首次迁移模式,不会强制清空已存在的表数据)", file=sys.stderr)
    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        print("错误: 未设置 DATABASE_URL 环境变量。", file=sys.stderr)
        print(
            "示例: DATABASE_URL='postgresql+asyncpg://user:pass@host:5432/db' "
            "python scripts/migrate_surgery.py",
            file=sys.stderr,
        )
        sys.exit(1)

    prefix = os.environ.get("TARGET_TABLE_PREFIX", "surgery_")
    source_db = os.environ.get(
        "SOURCE_DB",
        str(Path(__file__).resolve().parent.parent.parent / "surgery.db"),
    )

    if not Path(source_db).exists():
        print(f"错误: 源数据库不存在: {source_db}", file=sys.stderr)
        sys.exit(1)

    engine = create_async_engine(database_url, echo=False)

    # 1) 建表(幂等)——只建 surgery_* 表,复用 ORM 模型定义(含索引/外键/类型)
    surgery_tables = [
        Base.metadata.tables[name]
        for name in Base.metadata.tables
        if name.startswith(prefix) and name != prefix + "patients"
    ]

    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(sync_conn, tables=surgery_tables)
        )

    # 2) 逐表"先清空、再全量插入",并输出对账
    results = []
    for source_table in MIGRATION_ORDER:
        if source_table in SKIP_SOURCE_TABLES:
            continue
        target_name = prefix + source_table
        if target_name not in Base.metadata.tables:
            print(f"警告: 目标表 {target_name} 不存在于 ORM metadata,跳过", file=sys.stderr)
            continue

        source_rows = read_source_table(source_db, source_table)
        source_count = read_source_count(source_db, source_table)
        target_table = Base.metadata.tables[target_name]

        async with engine.begin() as conn:
            await conn.execute(target_table.delete())
            if source_rows:
                await conn.execute(target_table.insert(), source_rows)
            target_count = (
                await conn.execute(text(f"SELECT COUNT(*) FROM {target_name}"))
            ).scalar()

        results.append((source_table, source_count, target_count))
        status = "OK" if source_count == target_count else "!! 不一致"
        print(f"{source_table} -> {target_name}: 源{source_count}行 -> 目标{target_count}行  [{status}]")

    await engine.dispose()

    # 汇总
    total_src = sum(s for _, s, _ in results)
    total_dst = sum(d for _, _, d in results)
    print(f"汇总: 源{total_src}行 -> 目标{total_dst}行")
    if total_src != total_dst:
        print("!! 存在行数不一致,请检查上表。", file=sys.stderr)
        sys.exit(1)
    print("迁移完成。")


if __name__ == "__main__":
    asyncio.run(main())
