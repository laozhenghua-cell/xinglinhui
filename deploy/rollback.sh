#!/usr/bin/env bash
# 回滚后端到切换前版本(在服务器上运行)
set -euo pipefail
LATEST_BAK=$(ls -1dt /root/zhilou-clinic/backend.bak-* 2>/dev/null | head -1)
if [ -z "$LATEST_BAK" ]; then
  echo "!! 没有找到备份" >&2
  exit 1
fi
echo "==> 回滚到 $LATEST_BAK"
rsync -a --delete \
  --exclude '.env' --exclude 'uploads' --exclude '__pycache__' --exclude '*.pyc' \
  "$LATEST_BAK"/ /root/zhilou-clinic/backend/
cd /root/zhilou-clinic
docker compose up -d --build backend
echo "==> 健康检查"
sleep 10
curl -sf http://127.0.0.1:8001/api/health >/dev/null && echo "✅ 已回滚" || echo "!! 检查日志 docker logs zhilou_clinic_backend --tail 50"
