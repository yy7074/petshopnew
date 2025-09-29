#!/bin/bash
# MySQL 5.7 数据库恢复脚本
# 生成时间: 2025-09-29 08:41:32

# 配置信息
DB_HOST="localhost"
DB_PORT="3306"
DB_USER="root"
DB_PASSWORD="123456"
DB_NAME="petshop_auction"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔄 MySQL 5.7 数据库恢复工具"
echo "================================"

# 检查MySQL客户端
if ! command -v mysql &> /dev/null; then
    echo "${RED}❌ MySQL客户端未安装${NC}"
    exit 1
fi

# 获取备份文件
if [ -n "$1" ]; then
    BACKUP_FILE="$1"
else
    # 自动选择最新的完整备份
    BACKUP_FILE=$(ls -t backups/petshop_complete_mysql57_*.sql 2>/dev/null | head -n 1)
    if [ -z "$BACKUP_FILE" ]; then
        echo "${RED}❌ 没有找到备份文件${NC}"
        echo "用法: $0 [备份文件路径]"
        exit 1
    fi
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "${RED}❌ 备份文件不存在: $BACKUP_FILE${NC}"
    exit 1
fi

echo "${YELLOW}📁 使用备份文件: $BACKUP_FILE${NC}"

# 确认操作
echo "${YELLOW}⚠️  警告: 此操作将覆盖现有数据库 '$DB_NAME'${NC}"
read -p "是否继续? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "操作已取消"
    exit 0
fi

# 测试数据库连接
echo "🔍 测试数据库连接..."
if ! mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "SELECT 1;" > /dev/null 2>&1; then
    echo "${RED}❌ 数据库连接失败${NC}"
    exit 1
fi

# 创建数据库（如果不存在）
echo "🏗️  创建数据库..."
mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 恢复数据
echo "📥 正在恢复数据库..."
if mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD --default-character-set=utf8mb4 $DB_NAME < "$BACKUP_FILE"; then
    echo "${GREEN}✅ 数据库恢复成功!${NC}"
    
    # 验证恢复结果
    echo "🔍 验证恢复结果..."
    TABLE_COUNT=$(mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD -D$DB_NAME -e "SHOW TABLES;" | wc -l)
    echo "${GREEN}📊 恢复了 $((TABLE_COUNT-1)) 个表${NC}"
else
    echo "${RED}❌ 数据库恢复失败!${NC}"
    exit 1
fi

echo "${GREEN}🎉 恢复操作完成!${NC}"
