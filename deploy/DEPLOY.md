# 部署文档 — 中医专科辅助诊疗平台

## 部署形态(服务器 47.245.39.78)
- 复用现有 docker 栈 `zhilou-clinic`(PG16 卷 `zhilou-clinic_pgdata`、redis),只重建 backend 镜像为合并后代码。
- 前端:合并后的 SPA 静态文件由**宿主机 nginx** 直接服务(`/var/www/tcm-platform/dist`),不再使用 frontend 容器(切换后停掉)。
- 新门户域名:`tcm.llixz.cn`(需用户在阿里云 DNS 添加 A 记录 → 47.245.39.78)。
- 旧域名 dan/erke/cy/zl.llixz.cn → 301 到 `https://tcm.llixz.cn/<模块路径>`。

## rsync 排除清单(所有部署命令通用)
`--exclude .env uploads __pycache__ *.pyc .venv-test tests _selftest_merge.py _test_migrate.db *.db`

## 后端代码路径(服务器)
- 现有(切换前): /root/zhilou-clinic/backend
- 合并后: /root/zhilou-clinic/backend(直接替换,先备份 backend.bak-<ts>)
- .env 增加: OPEN_ACCESS=true(其余 DEEPSEEK/QWEN/SECRET 保持不变)

## 切换步骤(顺序执行,夜间低峰)
1. 部署后端: `bash deploy/deploy-backend.sh`(rsync → build → up → health)
2. 数据迁移: `docker compose exec backend python scripts/migrate_surgery.py`(对账输出归档)
3. 部署前端: 本地 `npm run build` → rsync dist 到 `/var/www/tcm-platform/dist`
4. nginx: 安装 `deploy/nginx/tcm-portal.conf`(先只用 Host 头测试 `curl -H "Host: tcm.llixz.cn" http://127.0.0.1/`),证书就绪后启用 443
5. 旧域名 301: 用 `deploy/nginx/tcm-legacy-301.conf` 替换 4 个旧 conf(先备份)
6. 验证: 4 旧域名分别 301 → 门户模块;`/api/v1/stats/public` 有数据;cy 8010、zl 前端容器停用观察
7. 回滚: 若异常 → `bash deploy/rollback.sh`(恢复 backend.bak 代码重建镜像 + 恢复旧 nginx conf)
