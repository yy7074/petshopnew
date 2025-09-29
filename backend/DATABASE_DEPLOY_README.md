# 拍宠有道数据库部署指南

## 📋 备份文件说明

已为您生成以下数据库备份文件：

1. **petshop_auction_backup_20250928_234943.sql** (157K)
   - 项目专用数据库备份
   - 包含所有表结构和数据
   - **推荐用于生产环境部署**

2. **petshop_full_backup_20250928_234930.sql** (19M)
   - 完整MySQL实例备份
   - 包含所有数据库
   - 用于完整系统迁移

## 🚀 服务器部署步骤

### 方法一：使用自动化脚本（推荐）

1. 将以下文件上传到服务器：
   ```bash
   - petshop_auction_backup_20250928_234943.sql
   - deploy_database.sh
   ```

2. 修改脚本中的数据库连接信息：
   ```bash
   vi deploy_database.sh
   # 修改以下变量
   DB_USER="your_username"
   DB_PASSWORD="your_password"
   ```

3. 执行部署脚本：
   ```bash
   chmod +x deploy_database.sh
   ./deploy_database.sh
   ```

### 方法二：手动部署

1. **创建数据库**
   ```sql
   CREATE DATABASE petshop_auction CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. **导入数据**
   ```bash
   mysql -u root -p petshop_auction < petshop_auction_backup_20250928_234943.sql
   ```

3. **验证导入**
   ```sql
   USE petshop_auction;
   SHOW TABLES;
   SELECT COUNT(*) FROM users; -- 检查用户表
   SELECT COUNT(*) FROM products; -- 检查商品表
   ```

## 📊 数据库结构概览

### 核心表结构
- **users** - 用户信息表
- **products** - 商品信息表
- **auctions** - 拍卖信息表
- **bids** - 出价记录表
- **orders** - 订单表
- **payments** - 支付记录表
- **messages** - 消息表
- **local_services** - 同城服务表
- **stores** - 店铺信息表
- **wallets** - 钱包表

### 功能模块表
- **ai_recognitions** - AI识宠记录
- **checkins** - 签到记录
- **deposits** - 保证金记录
- **follows** - 关注关系
- **lottery_records** - 抽奖记录
- **notifications** - 通知表
- **sms_codes** - 短信验证码
- **store_applications** - 店铺申请

## ⚙️ 环境配置

### 1. 更新应用配置
修改服务器上的环境配置文件：

```bash
# .env.local 或 .env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/petshop_auction
```

### 2. 安装Python依赖
```bash
pip install -r requirements.txt
```

### 3. 启动应用
```bash
python main.py
```

## 🔧 常见问题解决

### 问题1：字符集问题
如果遇到中文乱码，确保：
```sql
ALTER DATABASE petshop_auction CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 问题2：连接失败
检查MySQL服务状态：
```bash
systemctl status mysql
systemctl start mysql
```

### 问题3：权限问题
创建专用数据库用户：
```sql
CREATE USER 'petshop'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON petshop_auction.* TO 'petshop'@'localhost';
FLUSH PRIVILEGES;
```

## 📋 部署检查清单

- [ ] MySQL服务正常运行
- [ ] 数据库备份文件已上传
- [ ] 数据库连接信息已配置
- [ ] 数据库创建成功
- [ ] 数据导入完成
- [ ] 表结构验证通过
- [ ] 应用配置已更新
- [ ] 应用启动成功
- [ ] API接口测试通过

## 📞 技术支持

如遇到部署问题，请检查：
1. MySQL版本兼容性（推荐8.0+）
2. 字符集设置正确
3. 用户权限充足
4. 网络连接正常

---

**重要提示：** 
- 生产环境部署前请先在测试环境验证
- 建议定期备份数据库
- 注意保护数据库连接信息的安全性
