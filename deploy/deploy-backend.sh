#!/usr/bin/env bash
# 部署合并后端到服务器(在服务器上运行)
set -euo pipefail
SRC_DIR="/root/tcm-platform/backend"          # rsync 目标(代码源由本地推送)
LIVE_DIR="/root/zhilou-clinic/backend"
TS=$(date +%Y%m%d-%H%M%S)

echo "==> 备份现有后端"
cp -a "$LIVE_DIR" "/root/zhilou-clinic/backend.bak-$TS"
echo "    备份完成: /root/zhilou-clinic/backend.bak-$TS"

echo "==> 同步合并后代码(排除 .env / uploads / __pycache__)"
if [ -d "$SRC_DIR" ]; then
  rsync -a --delete \
    --exclude '.env' --exclude 'uploads' --exclude '__pycache__' --exclude '*.pyc' \
    --exclude '.venv-test' --exclude 'tests' \
    "$SRC_DIR"/ "$LIVE_DIR"/
else
  echo "!! $SRC_DIR 不存在,请先在本地 rsync 代码到服务器" >&2
  exit 1
fi

echo "==> 重建 backend 镜像并启动"
cd /root/zhilou-clinic
docker compose up -d --build backend

echo "==> 健康检查(最多 60s)"
for i in $(seq 1 12); do
  if curl -sf http://127.0.0.1:8001/api/health >/dev/null 2>&1; then
    echo "✅ 后端健康"
    exit 0
  fi
  sleep 5
done
echo "!! 后端健康检查失败,查看: docker logs zhilou_clinic_backend --tail 50" >&2
exit 1
