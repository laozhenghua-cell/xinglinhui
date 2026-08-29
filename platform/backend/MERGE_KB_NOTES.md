# 统一共用知识总库(KB v1)后端实现说明

## 改动清单
| 文件 | 说明 |
|---|---|
| `app/models/kb.py` | 新增 8 个模型:`kb_formulas/kb_herbs/kb_diseases/kb_syndromes/kb_cases/kb_tips/kb_terms/kb_dulong`。全部带 `module` + `origin_id`(联合唯一,幂等 upsert 依据)、`id`(UUID)、`created_at`;`aliases/composition/meridians/extra` 用 JSONB,长文本用 Text。 |
| `app/models/__init__.py` | 注册 8 个 kb 模型进 metadata(create_all 自动建表)。 |
| `app/api/v1/kb.py` | 新增免鉴权路由(prefix `/kb`,挂到 `/api/v1/kb`):`/stats`、`/{type}` 列表、`/{type}/{id}` 详情、`/search`、`/linked`。 |
| `app/main.py` | include kb 路由,不动既有路由。 |
| `scripts/migrate_kb.py` | 幂等迁移脚本(按 `(module, origin_id)` upsert,每类输出对账)。 |
| `MERGE_KB_NOTES.md` | 本说明。 |

## 迁移用法
```bash
cd platform/backend
DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db" python scripts/migrate_kb.py
```
- 复用 `app.database` 的 async engine(`settings.DATABASE_URL`,读 `.env` / 环境变量),可重复执行(幂等)。
- JSON 数据默认从 `<repo>/kb-data/` 读取,可用环境变量 `KB_DATA_DIR` 覆盖。
- 前置条件:PG 中已有 `surgery_*`、`anorectal_*`、`syndrome_rules`、`safety_rules`、`prevention_guides`、`medical_cases`(由既有迁移脚本建表)。

## 数据映射要点
- **surgery**:`surgery_formulas`(composition 文本按 、，,；; 切分 → `[{name,dose:''}]`)→ kb_formulas;`surgery_diseases`→kb_diseases;`surgery_syndromes`→kb_syndromes;`surgery_cases`+`surgery_expert_cases`(expert_name 区分)→kb_cases;`surgery_clinical_tips`→kb_tips;`surgery_expert_experiences`→kb_tips(category=名家经验);`surgery_formulas.composition` 提取去重→kb_herbs(module=surgery,extra.source=方剂组成提取)。
- **anorectal**:`anorectal_formulas`(composition JSONB 若为 `[{name,dose}]` 直接用,否则转 `[]` 并放 extra)→kb_formulas;`anorectal_herbs`→kb_herbs;`anorectal_cases`+`medical_cases`→kb_cases;`syndrome_rules`→kb_syndromes(字段按 diagnosis.py 模型映射,其余放 extra);`safety_rules`/`prevention_guides`→kb_tips;`disease_types`+`disease_type` 去重→kb_diseases。
- **JSON**:`pediatrics.json`/`alchemy.json` 全量导入(缺 origin_id 的集合用稳定 id 补:pediatrics tips=`tip-<idx>`、alchemy terms=`term-<idx>`、alchemy tips=`tip-<idx>`、alchemy dulong=`dulong-<section>-<n>`)。

## 对账预期数(/api/v1/kb/stats)
| 类型 | 预期 | 构成 |
|---|---|---|
| formulas | 662 | 508(surgery)+75(anorectal)+45(儿科)+34(丹药) |
| herbs | 72 + 提取数 | 72(anorectal)+手术方剂组成去重提取 |
| diseases | 107 + 提取数 | 107(surgery)+anorectal 病种提取去重 |
| syndromes | 59 | 13(surgery)+38(syndrome_rules)+8(儿科) |
| cases | 133 | 40+40(surgery/expert)+14+7(anorectal/medical)+32(儿科) |
| tips | 291 + 名家经验 | 59+67+6+159 + alchemy 1 + surgery_expert_experiences |
| terms | 48 | alchemy |
| dulong | 245 | alchemy |

> herbs/diseases 的"提取数"与 tips 的"名家经验"取决于实际库内数据,迁移后以 `/stats` 实际计数为准。

## 自测
- `python3 -m py_compile` 全部通过;`.venv-test` 导入 `app.main`、模型、路由通过。
- 已用本地 PostgreSQL(临时库)端到端跑通:`migrate_kb.py` 两次执行幂等(计数不翻倍),API 的 stats/list/search(转义 `%`/`_`)/detail/linked 均验证正常。
