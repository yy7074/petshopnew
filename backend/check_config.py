#!/usr/bin/env python3
"""
配置检查脚本
用于验证环境变量配置是否正确
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.env_config import env_config

def check_config():
    """检查配置项"""
    print("🔍 检查环境变量配置...")
    print("=" * 50)
    
    # 检查必需配置
    missing_configs = env_config.validate_required_configs()
    
    if missing_configs:
        print("❌ 缺少必需的配置项:")
        for config in missing_configs:
            print(f"   - {config}")
        print("\n💡 请设置环境变量或创建 .env 文件")
        return False
    
    print("✅ 所有必需配置项都已设置")
    
    # 显示当前配置（隐藏敏感信息）
    print("\n📋 当前配置:")
    print(f"   应用名称: {env_config.APP_NAME}")
    print(f"   调试模式: {env_config.DEBUG}")
    print(f"   版本: {env_config.VERSION}")
    print(f"   数据库: {env_config.DATABASE_URL.split('@')[1] if '@' in env_config.DATABASE_URL else '未设置'}")
    print(f"   Redis: {env_config.REDIS_URL}")
    print(f"   短信服务: {'已配置' if env_config.SMS_ACCESS_KEY else '未配置'}")
    print(f"   短信签名: {env_config.SMS_SIGN_NAME}")
    print(f"   短信模板: {env_config.SMS_TEMPLATE_ID}")
    
    return True

def main():
    """主函数"""
    print("🚀 宠物拍卖API - 配置检查工具")
    print("=" * 50)
    
    # 检查.env文件是否存在
    env_file = project_root / ".env"
    if env_file.exists():
        print("✅ 找到 .env 文件")
    else:
        print("⚠️  未找到 .env 文件，使用默认配置")
        print("💡 建议创建 .env 文件来管理敏感配置")
    
    print()
    
    # 检查配置
    if check_config():
        print("\n🎉 配置检查通过！")
        sys.exit(0)
    else:
        print("\n❌ 配置检查失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
