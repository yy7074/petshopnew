#!/bin/bash
# 上传备份文件到服务器并在服务器上导入

set -e

# 服务器配置
SERVER_IP="39.96.177.57"
SERVER_USER="root"
SERVER_PATH="/www/wwwroot/backend"

# 本地备份文件
BACKUP_FILE="backups/petshop_complete_mysql57_20251001_144842.sql"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🚀 上传并导入数据到远程服务器"
echo "================================"

# 检查备份文件
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ 备份文件不存在: ${BACKUP_FILE}${NC}"
    exit 1
fi

echo "📦 备份文件: ${BACKUP_FILE}"
BACKUP_SIZE=$(ls -lh ${BACKUP_FILE} | awk '{print $5}')
echo "📊 文件大小: ${BACKUP_SIZE}"
echo ""

# 1. 上传备份文件到服务器
echo "📤 步骤1: 上传备份文件到服务器..."
scp ${BACKUP_FILE} ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/backup_temp.sql

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 文件上传成功${NC}"
else
    echo -e "${RED}❌ 文件上传失败${NC}"
    exit 1
fi

# 2. 在服务器上执行导入
echo ""
echo "📥 步骤2: 在服务器上导入数据..."
echo "请确认操作..."

ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd /www/wwwroot/backend

echo "🔍 检查MySQL服务..."
if ! systemctl is-active --quiet mysql && ! systemctl is-active --quiet mysqld; then
    echo -e "${YELLOW}⚠️  MySQL服务未运行，尝试启动...${NC}"
    systemctl start mysql || systemctl start mysqld
fi

echo "🏗️  创建/重置数据库..."
mysql -uroot -p123456 << 'EOSQL'
DROP DATABASE IF EXISTS petshop_auction;
CREATE DATABASE petshop_auction CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE petshop_auction;
EOSQL

echo "📥 导入数据..."
mysql -uroot -p123456 --default-character-set=utf8mb4 petshop_auction < backup_temp.sql

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 数据导入成功！${NC}"
    
    # 验证数据
    echo ""
    echo "🔍 验证导入结果..."
    
    mysql -uroot -p123456 petshop_auction << 'EOSQL'
SELECT '📊 数据库统计信息' as '';
SELECT 'users' as '表名', COUNT(*) as '记录数' FROM users
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'special_events', COUNT(*) FROM special_events
UNION ALL
SELECT 'store_applications', COUNT(*) FROM store_applications
UNION ALL
SELECT 'stores', COUNT(*) FROM stores
UNION ALL
SELECT 'orders', COUNT(*) FROM orders;
EOSQL
    
    # 删除临时文件
    rm -f backup_temp.sql
    echo -e "${GREEN}🎉 导入完成！${NC}"
else
    echo -e "${RED}❌ 数据导入失败${NC}"
    exit 1
fi

ENDSSH

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}✅ 所有操作完成！${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo "📝 下一步："
    echo "1. 重启Python应用（在宝塔面板中）"
    echo "2. 测试APP功能：登录、专场活动、商品等"
    echo "3. 检查数据是否完整"
else
    echo -e "${RED}❌ 操作失败${NC}"
    exit 1
fi

