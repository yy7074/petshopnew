#!/bin/bash
# 导入数据到远程服务器
# 使用最新的MySQL 5.7兼容备份

set -e

# 远程服务器配置
REMOTE_HOST="39.96.177.57"
REMOTE_PORT="3306"
REMOTE_USER="root"
REMOTE_PASSWORD="123456"
REMOTE_DB="petshop_auction"

# 本地备份文件
BACKUP_FILE="backups/petshop_complete_mysql57_20251001_144842.sql"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🚀 导入数据到远程服务器"
echo "================================"
echo "远程服务器: ${REMOTE_HOST}:${REMOTE_PORT}"
echo "数据库: ${REMOTE_DB}"
echo "备份文件: ${BACKUP_FILE}"
echo ""

# 检查备份文件是否存在
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ 备份文件不存在: ${BACKUP_FILE}${NC}"
    exit 1
fi

# 测试远程MySQL连接
echo "🔍 测试远程MySQL连接..."
if mysql -h${REMOTE_HOST} -P${REMOTE_PORT} -u${REMOTE_USER} -p${REMOTE_PASSWORD} -e "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 连接成功${NC}"
else
    echo -e "${RED}❌ 无法连接到远程MySQL服务器${NC}"
    echo "请检查："
    echo "  1. 服务器IP是否正确"
    echo "  2. MySQL端口是否开放"
    echo "  3. 用户名密码是否正确"
    echo "  4. 防火墙是否允许3306端口"
    exit 1
fi

# 确认操作
echo ""
echo -e "${YELLOW}⚠️  警告: 此操作将覆盖远程数据库 '${REMOTE_DB}' 的所有数据${NC}"
read -p "是否继续? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "操作已取消"
    exit 0
fi

# 创建数据库（如果不存在）
echo "🏗️  创建数据库..."
mysql -h${REMOTE_HOST} -P${REMOTE_PORT} -u${REMOTE_USER} -p${REMOTE_PASSWORD} \
    -e "CREATE DATABASE IF NOT EXISTS ${REMOTE_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 数据库已准备就绪${NC}"
else
    echo -e "${RED}❌ 创建数据库失败${NC}"
    exit 1
fi

# 导入数据
echo "📥 正在导入数据..."
echo "这可能需要几分钟，请稍候..."

mysql -h${REMOTE_HOST} -P${REMOTE_PORT} -u${REMOTE_USER} -p${REMOTE_PASSWORD} \
    --default-character-set=utf8mb4 ${REMOTE_DB} < ${BACKUP_FILE}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 数据导入成功！${NC}"
else
    echo -e "${RED}❌ 数据导入失败${NC}"
    exit 1
fi

# 验证导入结果
echo ""
echo "🔍 验证导入结果..."

# 获取表数量
TABLE_COUNT=$(mysql -h${REMOTE_HOST} -P${REMOTE_PORT} -u${REMOTE_USER} -p${REMOTE_PASSWORD} \
    -D${REMOTE_DB} -e "SHOW TABLES;" --skip-column-names | wc -l)

echo -e "${GREEN}📊 共导入 ${TABLE_COUNT} 个表${NC}"

# 检查专场活动数据
EVENT_COUNT=$(mysql -h${REMOTE_HOST} -P${REMOTE_PORT} -u${REMOTE_USER} -p${REMOTE_PASSWORD} \
    -D${REMOTE_DB} -e "SELECT COUNT(*) FROM special_events;" --skip-column-names 2>/dev/null || echo "0")

echo -e "${GREEN}🎯 专场活动数量: ${EVENT_COUNT}${NC}"

# 检查用户数据
USER_COUNT=$(mysql -h${REMOTE_HOST} -P${REMOTE_PORT} -u${REMOTE_USER} -p${REMOTE_PASSWORD} \
    -D${REMOTE_DB} -e "SELECT COUNT(*) FROM users;" --skip-column-names 2>/dev/null || echo "0")

echo -e "${GREEN}👥 用户数量: ${USER_COUNT}${NC}"

# 检查商品数据
PRODUCT_COUNT=$(mysql -h${REMOTE_HOST} -P${REMOTE_PORT} -u${REMOTE_USER} -p${REMOTE_PASSWORD} \
    -D${REMOTE_DB} -e "SELECT COUNT(*) FROM products;" --skip-column-names 2>/dev/null || echo "0")

echo -e "${GREEN}📦 商品数量: ${PRODUCT_COUNT}${NC}"

# 检查店铺申请数据
STORE_APP_COUNT=$(mysql -h${REMOTE_HOST} -P${REMOTE_PORT} -u${REMOTE_USER} -p${REMOTE_PASSWORD} \
    -D${REMOTE_DB} -e "SELECT COUNT(*) FROM store_applications;" --skip-column-names 2>/dev/null || echo "0")

echo -e "${GREEN}🏪 店铺申请数量: ${STORE_APP_COUNT}${NC}"

echo ""
echo -e "${GREEN}🎉 数据导入完成！${NC}"
echo "================================"
echo "📝 下一步操作："
echo "1. 重启远程服务器上的Python应用"
echo "2. 测试APP登录和专场活动功能"
echo "3. 检查所有数据是否正常显示"
echo ""
echo "✅ 所有操作完成！"

