#!/bin/bash
# 快速部署修复文件到服务器

SERVER_IP="39.96.177.57"
SERVER_USER="root"
SERVER_PATH="/www/wwwroot/backend"

echo "🚀 快速部署修复文件到服务器"
echo "================================"

# 1. 上传修复后的security.py
echo "📤 上传security.py到服务器..."
scp app/core/security.py ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/app/core/security.py

if [ $? -eq 0 ]; then
    echo "✅ 文件上传成功"
else
    echo "❌ 文件上传失败"
    exit 1
fi

# 2. 重启服务（需要根据实际情况调整）
echo ""
echo "📝 下一步操作："
echo "1. 在宝塔面板中重启Python项目"
echo "2. 或者SSH登录服务器执行："
echo "   supervisorctl restart petshop_backend"
echo ""
echo "3. 验证修复："
echo "   curl -X POST http://39.96.177.57:3000/api/v1/auth/login \\"
echo "     -d 'username=testuser&password=testpass'"
echo ""
echo "✅ 部署完成！请重启服务后测试"

