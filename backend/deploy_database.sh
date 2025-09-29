#!/bin/bash
# 数据库部署脚本
# 用于在服务器上恢复数据库

echo "==================================="
echo "拍宠有道数据库部署脚本"
echo "==================================="

# 配置变量
DB_USER="root"
DB_PASSWORD="123456"
DB_NAME="petshop_auction"
BACKUP_FILE="petshop_auction_backup_20250928_234943.sql"

# 检查备份文件是否存在
if [ ! -f "$BACKUP_FILE" ]; then
    echo "错误: 备份文件 $BACKUP_FILE 不存在!"
    exit 1
fi

echo "1. 检查MySQL服务状态..."
if ! command -v mysql &> /dev/null; then
    echo "错误: MySQL未安装或未在PATH中!"
    exit 1
fi

echo "2. 创建数据库 $DB_NAME (如果不存在)..."
mysql -u $DB_USER -p$DB_PASSWORD -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

if [ $? -eq 0 ]; then
    echo "✓ 数据库创建成功或已存在"
else
    echo "✗ 数据库创建失败"
    exit 1
fi

echo "3. 恢复数据库数据..."
mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME < $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✓ 数据库恢复成功"
else
    echo "✗ 数据库恢复失败"
    exit 1
fi

echo "4. 验证数据库表..."
TABLE_COUNT=$(mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='$DB_NAME';" -s -N)
echo "数据库中共有 $TABLE_COUNT 个表"

echo "==================================="
echo "数据库部署完成!"
echo "数据库名: $DB_NAME"
echo "表数量: $TABLE_COUNT"
echo "==================================="

# 显示主要表的记录数
echo "主要表记录统计:"
mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME -e "
SELECT 
    table_name as '表名',
    table_rows as '记录数'
FROM information_schema.tables 
WHERE table_schema = '$DB_NAME' 
    AND table_type = 'BASE TABLE'
ORDER BY table_rows DESC;
"
