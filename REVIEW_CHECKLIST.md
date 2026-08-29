# 子代理交付审查清单(待两代理完成后逐项核对)

## 后端(platform/backend)
- [ ] config.py: OPEN_ACCESS 配置项存在
- [ ] security.py: get_current_user 在 OPEN_ACCESS 下无凭证→公开用户;HTTPBearer auto_error=False
- [ ] open_access.py: ensure_public_user 在 lifespan/init_db 调用
- [ ] 公开用户 role 兼容各路由权限(患者/就诊写入落在公开租户)
- [ ] app/api/v1/surgery*.py: 前缀 /api/v1/surgery,路径与 cy-backend-ref 契约一致(逐 router 对照)
- [ ] schemas/surgery.py 与 cy schemas 兼容(JSON 字段 parse)
- [ ] models/surgery.py 表名 surgery_*;patients 复用
- [ ] visits API: POST /api/v1/visits 免鉴权;GET /api/v1/stats/public 聚合正确(与 zl /stats/overview、/trends 无冲突)
- [ ] main.py 挂载全部新路由;既有路由未破坏
- [ ] scripts/migrate_surgery.py: 幂等、清空重灌、行数对账输出(107/13/508/280/18/40/40/59/6/0/0/0)
- [ ] 迁移处理 aliases JSON 字符串、DATETIME、uploads 路径不变
- [ ] python 语法编译全过;import app.main 成功(venv 依赖装齐后)
- [ ] MERGE_NOTES.md 存在且说明 .env 新配置

## 前端(platform/web)
- [ ] npm run build 通过(硬性)
- [ ] router: / 门户、/stats、/anorectal/*、/surgery/*、/pediatrics/*、/alchemy/*
- [ ] 无强制跳转 /login(auth store + beforeEach + axios 401 拦截均移除)
- [ ] 门户 PortalHome.vue: 4 模块卡片 + 平台名
- [ ] StatsView.vue 调 /api/v1/stats/public(echarts 趋势)
- [ ] afterEach 埋点 POST /api/v1/visits(module/path,同会话一次)
- [ ] pediatrics 模块功能页齐全(辨证/方剂/医案/图谱/自测/检索/换算),内部跳转路径修复
- [ ] alchemy 模块:chapters md 加载、pages 图片路径、assist 辨证、毒龙丹、安全页
- [ ] surgery 模块:疾病/方剂/医案/名医经验/辨证AI/治法/要诀/统计,对接 /api/v1/surgery/*
- [ ] 原 zl 肛肠页面路径全部改到 /anorectal 且内部 push 同步
- [ ] Layout 导航含门户入口与统计入口

## 部署(服务器)
- [ ] DNS: tcm.llixz.cn → 47.245.39.78(需用户)
- [ ] rsync 排除 .venv-test/tests/uploads/.env
- [ ] docker compose up -d --build backend 后健康检查
- [ ] 迁移执行 + 对账输出留档
- [ ] 前端 dist 上传 /var/www/tcm-platform/dist
- [ ] 门户 nginx 上线 + 证书 + https 验证
- [ ] 旧 4 域名 301 + 备份旧 conf + erke-check 适配
- [ ] 停 cy:8010、zl 前端容器;不动 api.llixz.cn/主站
- [ ] 验证:各模块页面可访问、AI 接口联调、stats 有数据、回滚演练路径可用
