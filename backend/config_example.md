# 环境变量配置说明

## 创建 .env 文件

在 `backend` 目录下创建 `.env` 文件，并填入以下配置：

```bash
# 数据库配置
DATABASE_URL=mysql+pymysql://root:123456@localhost:3306/petshop_auction

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
```

## 安全注意事项

1. **不要将 .env 文件提交到版本控制系统**
2. **生产环境使用强密码和密钥**
3. **定期轮换敏感密钥**
4. **使用环境变量或密钥管理服务**

## 配置验证

系统启动时会自动验证必需的配置项，如果缺少关键配置会显示警告。
