#!/usr/bin/env bash
# KB 知识总库部署(服务器端单次执行:备份→切换代码→重建→迁移→验证)
set -euo pipefail
TS=$(date +%Y%m%d-%H%M%S)
echo "==> 1. 备份现网后端"
cp -a /root/zhilou-clinic/backend "/root/zhilou-clinic/backend.bak-kb-$TS"
echo "==> 2. 切换代码(保留 .env/uploads)"
rsync -a --delete --exclude '.env' --exclude 'uploads' --exclude '__pycache__' --exclude '*.pyc' \
  /root/tcm-platform/backend/ /root/zhilou-clinic/backend/
echo "==> 3. 重建后端镜像并启动"
cd /root/zhilou-clinic
docker compose up -d --build backend 2>&1 | tail -3
for i in $(seq 1 30); do
  curl -sf http://127.0.0.1:8001/api/health >/dev/null 2>&1 && break
  sleep 5
done
curl -s http://127.0.0.1:8001/api/health && echo
echo "==> 4. 上传迁移数据并执行 kb 迁移"
docker exec zhilou_clinic_backend sh -c 'rm -rf /kb-data && mkdir -p /kb-data'
docker cp /root/tcm-platform/kb-data/. zhilou_clinic_backend:/kb-data/
docker exec -w /app -e KB_DATA_DIR=/kb-data zhilou_clinic_backend python scripts/migrate_kb.py 2>&1 | tail -30
echo "==> 5. 验证 kb 接口"
curl -s -m 15 http://127.0.0.1:8001/api/v1/kb/stats | head -c 600; echo
curl -s -m 15 'http://127.0.0.1:8001/api/v1/kb/search?q=%E7%96%94' | head -c 400; echo
echo "==> 6. 前端 dist 切换"
cd /var/www/tcm-platform
[ -d dist.old ] && rm -rf dist.old
mv dist dist.old 2>/dev/null || true
mv dist.new dist
echo "✅ KB 部署完成(前端 dist 需先由本地 rsync 到 dist.new)"
