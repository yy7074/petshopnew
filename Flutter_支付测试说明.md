# Flutter App 支付宝支付测试说明

## 📱 App端支付测试步骤

### 1. 环境准备
- ✅ 后端服务已在3000端口启动
- ✅ 支付宝正式环境密钥已配置
- ✅ 内网穿透域名: `https://catdog.dachaonet.com`
- ✅ Flutter App已集成tobias支付宝SDK

### 2. 测试页面访问
在Flutter App中导航到测试支付页面：
```dart
Get.toNamed(AppRoutes.testPayment);
```

### 3. 支付测试流程

#### A. 准备测试数据
1. 确保数据库中有测试订单（order_id = 1）
2. 确保有已登录的测试用户
3. 测试金额建议使用 0.01 元

#### B. 执行支付测试
1. 打开测试支付页面
2. 输入订单ID (例如: 1)
3. 输入测试金额 (例如: 0.01)
4. 点击 "测试支付宝支付" 按钮
5. App会自动跳转到支付宝客户端
6. 使用真实支付宝账号完成支付

#### C. 支付结果处理
- **支付成功**: 返回App显示成功信息
- **支付取消**: 显示用户取消支付
- **支付失败**: 显示具体失败原因
- **支付处理中**: 可使用查询功能确认状态

### 4. 核心文件说明

#### 支付服务 (`lib/services/payment_service.dart`)
```dart
class PaymentService {
  // 初始化支付宝SDK
  Future<void> initAlipay() async
  
  // 创建支付订单
  Future<PaymentResult> payWithAlipay(int orderId) async
  
  // 查询支付状态
  Future<String?> queryPaymentStatus(int paymentId) async
  
  // 申请退款
  Future<bool> requestRefund({...}) async
}
```

#### 支付页面 (`lib/pages/payment/payment_page.dart`)
正式的支付页面，包含:
- 订单信息显示
- 支付方式选择
- 支付金额确认
- 支付结果处理

#### 测试页面 (`lib/pages/test_payment_page.dart`)
开发测试用页面，包含:
- 订单ID输入
- 测试金额输入
- 支付功能测试
- 状态查询功能

### 5. API接口说明

#### 后端支付接口
- `POST /api/orders/{orderId}/alipay/app` - 创建App支付
- `POST /api/orders/{orderId}/alipay/web` - 创建网页支付
- `GET /api/orders/payments/{paymentId}/alipay/query` - 查询支付状态
- `POST /api/orders/payments/{paymentId}/alipay/refund` - 申请退款
- `POST /api/orders/payments/{paymentId}/alipay/notify` - 支付回调

### 6. 支付结果码说明

| 结果码 | 说明 | 处理方式 |
|--------|------|----------|
| 9000 | 支付成功 | 更新订单状态，显示成功信息 |
| 8000 | 正在处理中 | 需要查询最终支付状态 |
| 4000 | 订单支付失败 | 显示失败原因 |
| 5000 | 重复请求 | 提示重复请求 |
| 6001 | 用户中途取消 | 提示用户取消 |
| 6002 | 网络连接出错 | 提示网络错误 |

### 7. 测试注意事项

#### ⚠️ 重要提醒
- 这是**真实支付环境**，会产生真实交易
- 建议使用最小金额（0.01元）进行测试
- 测试完成后可申请退款
- 请确保有足够的支付宝余额

#### 🔧 调试技巧
1. 查看Flutter控制台日志
2. 检查后端API响应
3. 确认网络连接正常
4. 验证支付宝客户端已安装

#### 📋 测试检查清单
- [ ] 后端服务正常运行
- [ ] 支付宝密钥配置正确
- [ ] App已安装支付宝客户端
- [ ] 测试用户已登录
- [ ] 测试订单存在
- [ ] 网络连接正常

### 8. 常见问题解决

#### Q: 支付时提示"创建支付订单失败"
A: 检查订单是否存在，用户是否有权限支付该订单

#### Q: 跳转支付宝后无法返回App
A: 检查App的URL Scheme配置

#### Q: 支付成功但状态未更新
A: 检查支付回调接口是否正常接收

#### Q: 退款如何处理
A: 使用`requestRefund`方法申请退款

### 9. 生产环境部署建议

1. **安全配置**
   - 支付回调使用HTTPS
   - 验证回调签名
   - 添加IP白名单

2. **错误处理**
   - 完善异常捕获
   - 添加重试机制
   - 记录支付日志

3. **用户体验**
   - 支付加载状态
   - 支付结果引导
   - 订单状态同步

---

## 🎯 开始测试

1. 启动后端服务 (端口3000)
2. 启动Flutter App
3. 导航到测试支付页面
4. 执行支付流程测试

**测试愉快！** 🎉