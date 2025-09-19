# 支付系统配置指南

## 支付宝支付配置

### 1. 申请支付宝开放平台账号

1. 访问 [支付宝开放平台](https://open.alipay.com/)
2. 注册开发者账号并完成实名认证
3. 创建应用，选择"移动应用"类型
4. 添加"App支付"功能

### 2. 配置应用信息

在支付宝开放平台应用管理中配置：

- **应用名称**: 拍宠有道
- **应用包名**: 与Flutter项目的包名一致
- **应用签名**: Android应用的签名信息
- **支付宝公钥**: 系统自动生成

### 3. 生成应用密钥

```bash
# 使用支付宝提供的密钥生成工具
# 下载地址：https://docs.open.alipay.com/291/105971

# 生成2048位RSA密钥对
openssl genrsa -out app_private_key.pem 2048
openssl rsa -in app_private_key.pem -pubout -out app_public_key.pem

# 格式化私钥（去除首尾标识）
openssl rsa -in app_private_key.pem -out app_private_key_pkcs8.pem -outform PEM -nocrypt
```

### 4. 配置环境变量

在 `backend/.env` 文件中配置：

```bash
# 支付宝配置
ALIPAY_APP_ID=你的应用APPID
ALIPAY_PRIVATE_KEY=你的应用私钥（PKCS8格式，单行）
ALIPAY_PUBLIC_KEY=支付宝公钥（单行）

# 支付回调地址（可选）
ALIPAY_NOTIFY_URL=https://yourdomain.com/api/v1/orders/payments/{payment_id}/alipay/notify
ALIPAY_RETURN_URL=https://yourdomain.com/payment/success
```

### 5. 沙箱环境测试

支付宝提供沙箱环境进行测试：

```bash
# 沙箱环境配置
DEBUG=true  # 自动使用沙箱环境
ALIPAY_APP_ID=沙箱APPID
ALIPAY_PRIVATE_KEY=沙箱应用私钥
ALIPAY_PUBLIC_KEY=沙箱支付宝公钥
```

## 微信支付配置（预留）

### 1. 申请微信商户号

1. 访问 [微信支付商户平台](https://pay.weixin.qq.com/)
2. 注册商户号并完成资质审核
3. 开通"App支付"功能

### 2. 配置环境变量

```bash
# 微信支付配置
WECHAT_APP_ID=微信开放平台AppID
WECHAT_MCH_ID=微信支付商户号
WECHAT_API_KEY=微信支付API密钥
WECHAT_CERT_PATH=apiclient_cert.pem路径
WECHAT_KEY_PATH=apiclient_key.pem路径
```

## 支付流程说明

### 1. App支付流程

```
用户选择商品 -> 创建订单 -> 选择支付方式 -> 调起支付 -> 支付结果处理
```

### 2. 支付状态说明

- `1`: 待支付
- `2`: 已支付
- `3`: 支付失败
- `4`: 已退款
- `5`: 部分退款

### 3. 支付安全

1. **签名验证**: 所有支付请求都进行RSA签名
2. **订单校验**: 回调时验证订单金额和状态
3. **重复通知**: 支持支付平台的重复通知机制
4. **超时处理**: 设置合理的支付超时时间

## 测试账号信息

### 支付宝沙箱买家账号
- 账号: buyer001@example.com
- 登录密码: 111111
- 支付密码: 111111

### 测试流程

1. 在Flutter应用中创建测试订单
2. 选择支付宝支付
3. 使用沙箱账号完成支付
4. 验证支付回调和订单状态更新

## 常见问题

### 1. 签名错误
- 检查私钥格式是否正确
- 确认参数排序和编码方式
- 验证时间戳是否准确

### 2. 支付失败
- 检查App ID是否正确
- 确认应用包名和签名匹配
- 验证网络连接和服务器配置

### 3. 回调处理
- 确保回调URL可以外网访问
- 验证回调数据的签名
- 正确处理重复通知

## 部署注意事项

1. **生产环境**: 使用正式的支付宝应用配置
2. **HTTPS**: 生产环境必须使用HTTPS
3. **日志**: 记录所有支付相关的关键操作
4. **监控**: 监控支付成功率和异常情况
5. **备份**: 定期备份支付相关数据

## 联系方式

如有技术问题，请联系：
- 技术支持邮箱: tech@petchongdao.com
- 客服电话: 400-xxx-xxxx

