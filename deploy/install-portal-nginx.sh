#!/usr/bin/env bash
# 服务器:安装门户 nginx 配置 + 签发证书(在服务器上运行;需 tcm.llixz.cn DNS 已解析)
set -euo pipefail
DOMAIN=tcm.llixz.cn

# 0. 校验 DNS
IP=$(getent hosts $DOMAIN | awk '{print $1}' | head -1)
if [ "$IP" != "47.245.39.78" ]; then
  echo "!! $DOMAIN 未解析到本机(当前: ${IP:-无}),请先在阿里云 DNS 添加 A 记录" >&2
  exit 1
fi

# 1. 安装 conf
cp /root/tcm-platform/deploy/nginx/tcm-portal.conf /etc/nginx/conf.d/tcm-portal.conf

# 2. 签发证书(acme.sh,与 dan/erke 同源)
if [ ! -d /etc/nginx/ssl/$DOMAIN ]; then
  /root/.acme.sh/acme.sh --issue -d $DOMAIN --webroot /var/www/tcm-platform/certbot-webroot --server letsencrypt
  /root/.acme.sh/acme.sh --install-cert -d $DOMAIN \
    --key-file /etc/nginx/ssl/$DOMAIN/$DOMAIN.key \
    --fullchain-file /etc/nginx/ssl/$DOMAIN/fullchain.cer \
    --reloadcmd "nginx -s reload"
fi

# 3. 语法检查 + reload
nginx -t && nginx -s reload
echo "==> 本地验证(Host 头)"
curl -s -o /dev/null -w 'HTTP %{http_code}\n' -H "Host: $DOMAIN" http://127.0.0.1/
echo "✅ 门户 nginx 已就绪(HTTPS 待 DNS 生效后 curl https://$DOMAIN/healthz 验证)"
