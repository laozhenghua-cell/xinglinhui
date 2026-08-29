# 合并工程改动说明(MERGE_NOTES)

本文件记录把「华夏痔瘘辅助诊疗系统(基座) + 外科疮疡 + 访问统计」合并为统一后端的改动清单、
新增配置、迁移脚本用法,以及服务器部署注意事项。

## 一、改动清单

### 1. 全开放模式(OPEN_ACCESS)

| 文件 | 改动 |
| --- | --- |
| `app/config.py` | 新增 `OPEN_ACCESS: bool = False`、`VISIT_SALT: str = ""` 及 `visit_salt` property(为空回退 `SECRET_KEY`) |
| `app/core/open_access.py` | **新增**。公开租户/公开用户的常量与 `ensure_public_user(db)`(固定 UUID 主键,幂等、并发安全) |
| `app/core/security.py` | `HTTPBearer(auto_error=False)`;`get_current_user` 在"无凭证 + OPEN_ACCESS=true"时落到公开用户;有 token 仍走原逻辑;无凭证且未开启时返回 401 |
| `app/database.py` | `init_db` 建表后调用 `ensure_public_user` 提前建好公开租户/用户 |

公开账号:租户 `公开诊所`(id `00000000-0000-0000-0000-000000000001`),
用户 `open@tcm-platform.local` / `访客`(id `00000000-0000-0000-0000-000000000002`,不可登录,密码为随机占位哈希)。

### 2. 疮疡(外科)模块 `/api/v1/surgery`

| 文件 | 说明 |
| --- | --- |
| `app/models/surgery.py` | **新增**。11 个 `surgery_*` 模型(整数自增主键、JSON 用通用 `JSON`、日期用朴素 `DateTime`),与旧版字段/响应一致 |
| `app/schemas/surgery.py` | **新增**。由 cy-backend-ref `schemas.py` 移植,字段保持旧版 |
| `app/core/surgery_security.py` | **新增**。`is_valid_image` / `read_limited` / `RateLimiter` / `ai_limiter` / `limit_ai`(沿用基座 `MAX_UPLOAD_SIZE`) |
| `app/services/surgery_ai.py` | **新增**。`SurgeryDeepSeekService` + `SurgeryQwenVisionService`,API key 读取 `settings.DEEPSEEK_API_KEY` / `settings.QWEN_API_KEY`(及对应 BASE_URL/MODEL) |
| `app/api/v1/surgery/*.py` | **新增**。12 个路由:cases、diagnosis、diseases、expert、formulas、images、patients、search、stats、syndromes、tips、treatment。各路由 prefix 已写全 `/api/v1/surgery/...` |
| `app/main.py` | include 以上 12 个疮疡路由(不动既有痔漏路由) |

路由映射(旧 → 新):
- `/api/v1/diseases` → `/api/v1/surgery/diseases`
- `/api/v1/syndromes` → `/api/v1/surgery/syndromes`
- `/api/v1/formulas` → `/api/v1/surgery/formulas`
- `/api/v1/treatment/*` → `/api/v1/surgery/treatment/*`(recommend / differentiate / match-options / match-syndrome / match-formula)
- `/api/v1/diagnosis/*` → `/api/v1/surgery/diagnosis/*`(analyze / identify)
- `/api/v1/cases` → `/api/v1/surgery/cases`
- `/api/v1/patients` → `/api/v1/surgery/patients`
- `/api/v1/stats` → `/api/v1/surgery/stats`
- `/api/v1/expert/*` → `/api/v1/surgery/expert/*`
- `/api/v1/images` → `/api/v1/surgery/images`
- `/api/v1/tips` → `/api/v1/surgery/tips`
- `/api/v1/search` → `/api/v1/surgery/search`

> ⚠️ 差异说明(重要):
> - 疮疡 **患者复用基座 `patients` 表**(UUID 主键、`tenant_id` 必填、`notes` 字段)。
>   因此 `/api/v1/surgery/patients` 的响应与旧版有两点差异:① `id` 为 UUID 而非整数;
>   ② 无 `cases` 关联(恒为 `[]`)。旧版疮疡病例本身通过 `patient_name` 反规范化存储,
>   迁移数据里 `patient_id` 全部为 NULL,故不影响病例展示。
> - 疮疡图片上传沿用基座 `uploads/` 目录与 `/uploads` 静态挂载(基座未显式挂载静态目录,
>   见下方"部署注意事项")。

### 3. 访问统计

| 文件 | 说明 |
| --- | --- |
| `app/models/visit.py` | **新增**。`visits` 表(id UUID、ts、module、path、ip_hash、ua_hash、referrer) |
| `app/api/v1/visits.py` | **新增**。`POST /api/v1/visits`(免鉴权),IP 加盐 SHA256、UA SHA256 后存储 |
| `app/api/v1/public_stats.py` | **新增**。`GET /api/v1/stats/public`(免鉴权),返回 totals/today/by_module/daily_30 |

> UV 口径:`distinct(ip_hash + ua_hash)` 组合(即"独立访客/设备")。
> "今天"与"近30天"按数据库时区的 `date(ts)` 分组,未做 UTC 强制对齐(与部署服务器时区一致即可)。

### 4. 数据迁移脚本

| 文件 | 说明 |
| --- | --- |
| `scripts/migrate_surgery.py` | **新增**。stdlib `sqlite3` 读源,SQLAlchemy(asyncpg)写 PG,先清空再全量插入(幂等),逐表输出对账 |

## 二、新增配置项(.env 示例)

```bash
# ── 全开放模式(新增) ──
# true 时,未携带 Authorization 头的请求自动落到"公开用户/公开租户",
# 所有依赖 get_current_user 的痔漏路由无需登录即可用;带合法 token 仍走原逻辑。
OPEN_ACCESS=false

# ── 访问统计 IP 哈希加盐(新增,可选) ──
# 为空时自动回退到 SECRET_KEY。建议生产显式设置独立盐值。
VISIT_SALT=
```

其余配置(如 `DEEPSEEK_API_KEY`、`QWEN_API_KEY`)基座已有,疮疡 AI 直接复用,无需新增。

## 三、迁移脚本用法

```bash
cd platform/backend

# 环境变量方式(推荐)
DATABASE_URL="postgresql+asyncpg://zhilou_user:PASSWORD@host:5432/zhilou_db" \
  python scripts/migrate_surgery.py

# 可选:覆盖源库路径 / 目标表前缀
SOURCE_DB=/abs/path/to/surgery.db \
TARGET_TABLE_PREFIX=surgery_ \
DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db" \
  python scripts/migrate_surgery.py
```

- 脚本用 ORM 模型(single source of truth)幂等创建 `surgery_*` 表(含索引/外键/类型)。
- 逐表"先 DELETE 再全量 INSERT",可重复执行。
- 输出形如 `diseases -> surgery_diseases: 源107行 -> 目标107行  [OK]`。
- 行数不一致时以非零退出码结束。
- 疮疡 `patients` 表复用基座 `patients`(源表为空,不迁移)。
- JSON 字段(`diseases.aliases`)解析后写入;日期字段解析 SQLite 时间串为 `datetime`。

## 四、部署注意事项(重要)

1. **建表方式**:`init_db`(启动时)用 `Base.metadata.create_all` 幂等建全部表(含新增的
   `surgery_*` 与 `visits`)。若生产用 Alembic 管理迁移,需另行补一条 migration 建这些新表;
   本工程未新增 Alembic 版本(仓库 `alembic/versions/` 为空)。
2. **依赖无变化**:未新增任何第三方依赖。疮疡/统计复用了既有的 `sqlalchemy[asyncio]`、
   `asyncpg`、`httpx`、`python-multipart`、`pydantic-settings` 等。迁移脚本用 stdlib `sqlite3` + SQLAlchemy。
3. **静态挂载**:疮疡诊断/病例上传图片写 `UPLOAD_DIR`(`./uploads`),访问路径为 `/uploads/<uuid>.<ext>`。
   基座当前**未挂载** `/uploads` 静态目录(上传走 `/api/v1/uploads/files/{tenant}/{file}` 接口)。
   若需 `/uploads/...` 直接可访问,请在 `main.py` 增加
   `app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")`
   (cy-backend-ref 的 `book/` 图版图片也放在该目录,可直接复用)。
4. **OPEN_ACCESS 安全**:开启后所有痔漏业务接口将公开可读写(落到公开租户)。
   请仅在确需"无需登录"时开启;生产如仅需疮疡/统计公开,可保持 `OPEN_ACCESS=false`,
   疮疡与统计路由本身不依赖登录。
5. **公开用户密码**:`open@tcm-platform.local` 无法登录(占位哈希)。请勿在数据库中修改该账户为可登录态。
6. **迁移前备份**:`migrate_surgery.py` 会**清空**目标 `surgery_*` 表再插入,首次部署或重新灌库时使用;
   如目标库已有疮疡生产数据,请先备份。
7. **统计 TZ**:`/api/v1/stats/public` 的"今日/近30天"依赖数据库时区,部署时保持应用与 PG 时区一致(或后续改为 UTC 分组)。
8. **AI 限流**:疮疡 AI(诊断/对比)沿用内存限流(每 IP 每分钟 10 次),多 worker 部署下为进程级限流,生产可改 Redis 共享限流。

## 五、验收对照(SPEC)

- ✅ `settings.OPEN_ACCESS` + `get_current_user` 无凭证降级公开用户;login/register 未动。
- ✅ 疮疡 12 个路由挂 `/api/v1/surgery/*`,AI 复用 DEEPSEEK/QWEN 配置,响应 schema 与旧版一致(患者除外,见上)。
- ✅ `POST /api/v1/visits` 免鉴权,IP 加盐哈希;`GET /api/v1/stats/public` 返回 totals/today/by_module/daily_30。
- ✅ `scripts/migrate_surgery.py` 全量迁移 + 对账 + 幂等。
- ✅ 痔漏路由路径与响应结构未改动。
