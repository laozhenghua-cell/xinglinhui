#!/bin/bash
# 续期 zl.llixz.cn 证书（Docker certbot）→ 复制到宿主机 → 重载宿主机 nginx
cd /root/zhilou-clinic
docker run --rm \
  -v /root/zhilou-clinic/certbot/conf:/etc/letsencrypt \
  -v /root/zhilou-clinic/certbot/www:/var/www/certbot \
  certbot/certbot renew --webroot -w /var/www/certbot --quiet

# 若证书已续期，复制到宿主机并重载 nginx
if [ -f /root/zhilou-clinic/certbot/conf/live/zl.llixz.cn/fullchain.pem ]; then
  cp -f /root/zhilou-clinic/certbot/conf/live/zl.llixz.cn/fullchain.pem /etc/letsencrypt/live/zl.llixz.cn/fullchain.pem
  cp -f /root/zhilou-clinic/certbot/conf/live/zl.llixz.cn/privkey.pem /etc/letsencrypt/live/zl.llixz.cn/privkey.pem
  systemctl reload nginx
fi
