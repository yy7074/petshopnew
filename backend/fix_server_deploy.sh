#!/bin/bash
# 服务器部署修复脚本
# 用途：修复bcrypt兼容性问题

set -e  # 遇到错误立即退出

echo "🔧 服务器部署修复脚本"
echo "================================"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否在服务器上
if [ ! -d "/www/wwwroot/backend" ]; then
    echo -e "${YELLOW}⚠️  警告: 未检测到标准服务器路径${NC}"
    echo "请确认您在正确的服务器上运行此脚本"
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# 备份当前文件
echo "📦 备份当前文件..."
BACKUP_DIR="/www/wwwroot/backend_backup_$(date +%Y%m%d_%H%M%S)"
if [ -d "/www/wwwroot/backend" ]; then
    cp -r /www/wwwroot/backend "$BACKUP_DIR"
    echo -e "${GREEN}✅ 备份完成: $BACKUP_DIR${NC}"
fi

# 检查虚拟环境
echo "🔍 检查虚拟环境..."
VENV_PATH="/www/server/pyporject_evn/py312"
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ 虚拟环境不存在: $VENV_PATH${NC}"
    exit 1
fi

# 激活虚拟环境
echo "🔌 激活虚拟环境..."
source "$VENV_PATH/bin/activate"

# 检查当前bcrypt版本
echo "📊 检查当前依赖版本..."
echo "passlib版本:"
pip show passlib | grep Version || echo "未安装"
echo "bcrypt版本:"
pip show bcrypt | grep Version || echo "未安装"

# 升级依赖
echo "⬆️  升级依赖包..."
pip install --upgrade passlib bcrypt

# 显示新版本
echo "📊 新的依赖版本:"
echo "passlib版本:"
pip show passlib | grep Version
echo "bcrypt版本:"
pip show bcrypt | grep Version

# 检查security.py文件
SECURITY_FILE="/www/wwwroot/backend/app/core/security.py"
if [ -f "$SECURITY_FILE" ]; then
    echo "🔍 检查security.py文件..."
    if grep -q "password_bytes[:72]" "$SECURITY_FILE"; then
        echo -e "${GREEN}✅ security.py已包含密码长度修复${NC}"
    else
        echo -e "${YELLOW}⚠️  security.py可能需要更新${NC}"
        echo "请确保从本地上传最新的security.py文件"
    fi
else
    echo -e "${RED}❌ 找不到security.py文件${NC}"
fi

# 测试Python导入
echo "🧪 测试Python导入..."
python -c "
import sys
print('Python版本:', sys.version)
try:
    from passlib.context import CryptContext
    print('✅ passlib导入成功')
except Exception as e:
    print('❌ passlib导入失败:', e)
    sys.exit(1)

try:
    import bcrypt
    print('✅ bcrypt导入成功')
except Exception as e:
    print('❌ bcrypt导入失败:', e)
    sys.exit(1)

try:
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    test_hash = pwd_context.hash('test')
    result = pwd_context.verify('test', test_hash)
    print('✅ bcrypt功能测试通过')
except Exception as e:
    print('❌ bcrypt功能测试失败:', e)
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Python环境测试通过${NC}"
else
    echo -e "${RED}❌ Python环境测试失败${NC}"
    exit 1
fi

# 提示重启服务
echo ""
echo "🎉 修复完成！"
echo "================================"
echo "📝 下一步操作:"
echo "1. 如果使用宝塔面板："
echo "   - 进入 Python项目管理"
echo "   - 找到petshop项目"
echo "   - 点击【重启】按钮"
echo ""
echo "2. 如果使用supervisor："
echo "   supervisorctl restart petshop_backend"
echo ""
echo "3. 如果使用systemd："
echo "   systemctl restart petshop_backend"
echo ""
echo "4. 验证修复："
echo "   tail -f /www/wwwroot/backend/logs/error.log"
echo "   或者测试登录接口"
echo ""
echo -e "${GREEN}✅ 所有修复步骤已完成！${NC}"

