#!/bin/bash
set -e

BACKUP_DIR=/root/zhilou-clinic/backups
RETENTION_DAYS=14
DB_CONTAINER=zhilou_db
DB_USER=zhilou_user
DB_NAME=zhilou_clinic

# 从 .env 读取数据库密码
DB_PASSWORD=$(grep '^DATABASE_URL=' /root/zhilou-clinic/backend/.env | sed -E 's#.*://[^:]+:([^@]+)@.*#\1#')

mkdir -p "$BACKUP_DIR"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="zhilou_${DATE}.sql.gz"

# 备份并 gzip 压缩
docker exec -e PGPASSWORD="$DB_PASSWORD" "$DB_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" | gzip > "$BACKUP_DIR/$FILENAME"

# 校验备份非空（太小说明失败）
SIZE=$(stat -c%s "$BACKUP_DIR/$FILENAME" 2>/dev/null || stat -f%z "$BACKUP_DIR/$FILENAME")
if [ "$SIZE" -lt 1000 ]; then
  echo "$(date '+%F %T') 备份失败：文件过小 ($SIZE bytes)"
  rm -f "$BACKUP_DIR/$FILENAME"
  exit 1
fi

# 清理超过保留期的旧备份
find "$BACKUP_DIR" -name "zhilou_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "$(date '+%F %T') 备份完成: $FILENAME ($(du -h "$BACKUP_DIR/$FILENAME" | cut -f1))"
