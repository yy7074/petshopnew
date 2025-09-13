#!/usr/bin/env python3
"""
环境变量设置模板脚本
用于创建.env.local文件模板
"""
import os
from pathlib import Path

def create_env_template():
    """创建.env.local文件模板"""
    env_content = """# 本地开发环境配置
# 此文件包含真实的配置信息，不会被提交到Git

# 数据库配置
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/petshop_auction

# JWT配置
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# 阿里云短信配置
SMS_ACCESS_KEY=your_aliyun_access_key
SMS_SECRET_KEY=your_aliyun_secret_key
SMS_SIGN_NAME=your_sms_sign_name
SMS_TEMPLATE_ID=your_sms_template_id
SMS_REGION=cn-hangzhou

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 应用配置
APP_NAME=宠物拍卖API
DEBUG=true
VERSION=1.0.0

# CORS配置
ALLOWED_HOSTS=*

# 文件上传配置
UPLOAD_DIR=static/uploads
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=.jpg,.jpeg,.png,.gif,.webp

# 分页配置
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# 支付配置
ALIPAY_APP_ID=
ALIPAY_PRIVATE_KEY=
ALIPAY_PUBLIC_KEY=

WECHAT_APP_ID=
WECHAT_MCH_ID=
WECHAT_API_KEY=

# 推送配置
JPUSH_APP_KEY=
JPUSH_MASTER_SECRET=
"""
    
    env_file = Path(__file__).parent / ".env.template"
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ .env.template 文件创建成功")
    print("💡 请复制此文件为 .env.local 并填入真实配置")
    return True

def main():
    """主函数"""
    print("🔧 创建环境变量模板")
    print("=" * 40)
    
    if create_env_template():
        print("\n🎉 模板创建完成！")
        print("请执行以下步骤：")
        print("1. cp .env.template .env.local")
        print("2. 编辑 .env.local 填入真实配置")
        print("3. 运行: python check_config.py")
    else:
        print("\n❌ 模板创建失败！")

if __name__ == "__main__":
    main()
