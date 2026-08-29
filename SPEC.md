# 中医专科辅助诊疗平台 — 合并工程规格(v1)

## 目标
将 4 个系统合并为 1 个"全开放(无需登录)+ 可统计使用人数"的平台:
- 肛肠痔漏(原 zl.llixz.cn,zhilou-clinic)
- 外科疮疡(原 cy.llixz.cn,tcm-surgery)
- 儿科(原 erke.llixz.cn,纯静态)
- 丹药研究(原 dan.llixz.cn,纯静态)

## 目录约定(本地)
- `platform/backend` — 统一后端(zl 后端副本为基座)
- `platform/web` — 统一前端(zl 前端副本为基座)
- `platform/cy-backend-ref` — 疮疡旧后端(参考,只读)
- `platform/ulcer-ref` — 疮疡新版工程(参考,只读)
- `platform/surgery.db` — 疮疡 SQLite(迁移数据源)
- 本地源码参考:`/Users/apple/Documents/deepseek项目/程氏儿科/webapp`(儿科)、`/Users/apple/Documents/deepseek项目/中国炼丹术与丹药体系/03-web`(丹药)

## 后端规格(platform/backend)
1. **全开放模式**:新增 settings `OPEN_ACCESS=true` 时,`get_current_user` 允许无凭证请求,自动落到"公开用户/公开租户"(启动时自动创建,如 open@platform / 公开诊所)。带合法 token 的请求仍按原逻辑。所有现有痔漏路由不变。
2. **疮疡模块**:在 `app/api/v1/surgery.py`(或 surgery/ 包)新增前缀 `/api/v1/surgery`,把 cy-backend-ref 的 routers(cases, diagnosis, diseases, expert, formulas, images, patients, search, stats, syndromes, tips, treatment)移植到 PostgreSQL(SQLAlchemy 2.0 async 模型,surgery_* 表名),API 路径与响应 schema 尽量与旧版一致(旧前缀替换为 /api/v1/surgery/...)。AI 服务沿用现有 deepseek/qwen 配置。
3. **访问统计**:新增 `/api/v1/visits`(POST,免鉴权:{module, path, referrer?})记录 PV;`/api/v1/stats/public`(GET):总 PV、总 UV(IP+UA 哈希)、今日/近30天按天 PV、按模块 PV/UV。IP 哈希加盐,不存明文 IP。
4. **数据迁移脚本**:`platform/backend/scripts/migrate_surgery.py` — 从 platform/surgery.db(SQLite)全量导入 surgery_* 表(行数对账输出)。幂等(可重复执行)。
5. 其余 zl 功能(肛肠知识库、辨证、收费、库存、随访、识图等)全部保留且路径不变。

## 前端规格(platform/web)
1. **壳与门户**:Layout 顶部导航 + 首页门户(4 模块卡片 + 简介 + 总访问量入口)。路由:`/`(门户)、`/stats`(使用统计页,调 /api/v1/stats/public)、模块前缀路由。
2. **全开放**:去掉登录门禁(store/router 不再强制跳转 /login),所有页面直接可用。
3. **肛肠模块**:原 zl views 原样保留(路径 /anorectal/* 或保持原路径亦可,但导航需归入模块)。
4. **儿科模块**:从 `程氏儿科/webapp/src` 移植 views/data/components 到 `src/modules/pediatrics/`,路由 `/pediatrics/*`,保持功能一致(辨证/方剂/医案/图谱/自测/检索等)。
5. **丹药模块**:从 `中国炼丹术与丹药体系/03-web/src` 移植到 `src/modules/alchemy/`,路由 `/alchemy/*`;章节页图片放 `web/public/pages/`(图片源:`中国炼丹术与丹药体系` 目录下 w-*.jpg 或 server-src 中 dan-dist)。
6. **疮疡模块**:`src/modules/surgery/` 新建页面,调用 `/api/v1/surgery/*`(契约见 cy-backend-ref/routers):疾病库(分类/列表/详情/搜索)、证型、方剂库、医案、名医经验、治法辨证(AI)、临床要诀、统计概览。UI 风格与 zl 现有 Knowledge/Diagnosis 一致(Element Plus)。
7. **统计埋点**:router.afterEach 触发 POST /api/v1/visits {module, path};同会话只报一次 UV。
8. `npm install && npm run build` 必须成功(Vite 5,base '/')。

## 验收标准
- 后端:uvicorn 能启动;公开模式无 token 可调痔漏与疮疡接口;migrate 脚本对账输出与 SQLite 行数一致;visits/stats 接口可用。
- 前端:build 通过;4 模块路由可访问;无登录页跳转。
