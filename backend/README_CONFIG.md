# 环境变量配置指南

## 概述

为了保护敏感信息（如API密钥、数据库密码等），项目使用环境变量来管理配置。

## 快速开始

### 1. 创建 .env 文件

在 `backend` 目录下创建 `.env` 文件：

```bash
cd backend
cp config_example.md .env
```

### 2. 编辑 .env 文件

根据你的实际环境修改配置值：

```bash
# 数据库配置
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/petshop_auction

# JWT配置
SECRET_KEY=your-very-secure-secret-key-here

# 阿里云短信配置
SMS_ACCESS_KEY=your_aliyun_access_key
SMS_SECRET_KEY=your_aliyun_secret_key
SMS_SIGN_NAME=your_sms_sign_name
SMS_TEMPLATE_ID=your_sms_template_id
```

### 3. 验证配置

运行配置检查脚本：

```bash
python check_config.py
```

## 配置项说明

### 必需配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `SMS_ACCESS_KEY` | 阿里云AccessKey ID | `your_aliyun_access_key` |
| `SMS_SECRET_KEY` | 阿里云AccessKey Secret | `your_aliyun_secret_key` |
| `SMS_SIGN_NAME` | 短信签名 | `大潮网络` |
| `SMS_TEMPLATE_ID` | 短信模板ID | `SMS_474780238` |

### 可选配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | 数据库连接字符串 | `mysql+pymysql://root:123456@localhost:3306/petshop_auction` |
| `SECRET_KEY` | JWT密钥 | `your-secret-key-here-change-in-production` |
| `DEBUG` | 调试模式 | `true` |
| `REDIS_URL` | Redis连接字符串 | `redis://localhost:6379/0` |

## 安全最佳实践

### 1. 不要提交敏感信息

确保 `.env` 文件在 `.gitignore` 中：

```gitignore
# 环境变量文件
.env
```

### 2. 使用强密码

- JWT密钥至少32个字符
- 数据库密码使用复杂密码
- 定期轮换API密钥

### 3. 生产环境配置

生产环境建议：

```bash
# 生产环境示例
DEBUG=false
SECRET_KEY=your-very-long-and-secure-secret-key-for-production
DATABASE_URL=mysql+pymysql://prod_user:secure_password@prod_host:3306/petshop_auction
```

### 4. 环境变量优先级

配置加载优先级（从高到低）：

1. 系统环境变量
2. `.env` 文件
3. 默认值

## 故障排除

### 配置检查失败

如果运行 `python check_config.py` 失败：

1. 检查 `.env` 文件是否存在
2. 检查必需配置项是否设置
3. 检查配置值格式是否正确

### 短信服务不工作

1. 验证阿里云AccessKey是否正确
2. 检查短信签名是否已审核通过
3. 确认短信模板ID是否正确

### 数据库连接失败

1. 检查数据库服务是否运行
2. 验证连接字符串格式
3. 确认用户名密码是否正确

## 开发环境设置

### 使用默认配置

如果只是本地开发，可以直接使用默认配置，系统会自动使用内置的默认值。

### 自定义配置

创建 `.env` 文件并只设置需要修改的配置项，其他配置会使用默认值。

## 生产环境部署

### Docker环境

在Docker容器中设置环境变量：

```dockerfile
ENV SMS_ACCESS_KEY=your_key
ENV SMS_SECRET_KEY=your_secret
```

### 服务器环境

在服务器上设置系统环境变量：

```bash
export SMS_ACCESS_KEY=your_key
export SMS_SECRET_KEY=your_secret
```

### 云服务配置

使用云服务的密钥管理服务（如AWS Secrets Manager、Azure Key Vault等）来管理敏感配置。
