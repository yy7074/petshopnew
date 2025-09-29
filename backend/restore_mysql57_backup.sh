#!/bin/bash
# MySQL 5.7 数据库恢复脚本

# 配置信息
DB_HOST="localhost"
DB_PORT="3306"
DB_USER="root"
DB_PASSWORD="123456"
DB_NAME="petshop_auction"

# 获取最新的备份文件
BACKUP_FILE=$(ls -t petshop_auction_mysql57_backup_*.sql | head -n 1)

if [ -z "$BACKUP_FILE" ]; then
    echo "❌ 没有找到备份文件"
    exit 1
fi

echo "🔄 正在恢复数据库: $BACKUP_FILE"

# 创建数据库（如果不存在）
mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 恢复数据
mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD --default-character-set=utf8mb4 $DB_NAME < "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ 数据库恢复成功!"
else
    echo "❌ 数据库恢复失败!"
    exit 1
fi
