#!/usr/bin/env bash
# 本地构建统一前端并上传服务器(在本地 mac 运行)
set -euo pipefail
WEB_DIR="/Users/apple/Documents/deepseek项目/tcm-platform-merge/platform/web"
SERVER="root@47.245.39.78"
PASS="${SERVER_PASS:?请设置 SERVER_PASS 环境变量}"

cd "$WEB_DIR"
echo "==> npm install"
npm install --no-audit --no-fund >/dev/null
echo "==> vite build"
npm run build

echo "==> 上传 dist 到 /var/www/tcm-platform/dist"
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$SERVER" "rm -rf /var/www/tcm-platform/dist.new && mkdir -p /var/www/tcm-platform/dist.new"
sshpass -p "$PASS" rsync -az --delete dist/ "$SERVER":/var/www/tcm-platform/dist.new/
echo "==> 原子切换 dist -> dist.new"
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no "$SERVER" "
  cd /var/www/tcm-platform
  [ -d dist.old ] && rm -rf dist.old
  mv dist dist.old 2>/dev/null || true
  mv dist.new dist
  echo '✅ 前端已部署'
  ls dist | head
"
