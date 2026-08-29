#!/usr/bin/env bash
# 服务器:切换旧 4 域名 301(在服务器上运行;portal 已验证后执行)
set -euo pipefail
TS=$(date +%Y%m%d-%H%M%S)
cd /etc/nginx/conf.d
mkdir -p /root/tcm-platform/nginx-backup-$TS
for f in dan-alchemy.conf erke.conf tcm-surgery.conf zhilou-assistant.conf; do
  [ -f "$f" ] && cp -v "$f" /root/tcm-platform/nginx-backup-$TS/
done
cp /root/tcm-platform/deploy/nginx/tcm-legacy-301.conf /etc/nginx/conf.d/tcm-legacy-301.conf
# 移除旧 vhost(备份已留)
rm -f dan-alchemy.conf erke.conf tcm-surgery.conf zhilou-assistant.conf
nginx -t && nginx -s reload
echo '==> 301 验证'
for d in dan erke cy zl; do
  code=$(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' "https://$d.llixz.cn/")
  echo "$d.llixz.cn -> $code"
done
# 更新巡检脚本(原 erke-check 检查 /healthz,301 后会误报)
sed -i 's|https://$DOMAIN/healthz|https://$DOMAIN/|; s|"$CODE" = "200"|"$CODE" = "200" -o "$CODE" = "301"|' /usr/local/bin/erke-check.sh 2>/dev/null || true
echo '✅ 旧域名已切换到 301'
