# 🐾 宠物拍卖App项目

一个功能完整的宠物拍卖平台，包含Flutter移动端、Python后端API和HTML后台管理系统。

## 📱 项目结构

```
petshopnew/
├── petshop_app/          # Flutter移动端应用
├── backend/              # Python后端API
├── admin/                # HTML后台管理系统
├── download/             # 设计图资源
├── database_design.sql   # 数据库设计文件
└── README.md            # 项目说明文档
```

## 🚀 功能特性

### 📱 移动端功能
- **首页模块**: 轮播图、分类导航、一口价商品、专场活动、同城服务
- **分类模块**: 商品分类浏览、筛选功能
- **消息模块**: 系统通知、私信、拍卖提醒
- **个人中心**: 用户信息、关注系统、出价记录、订单管理、签到功能
- **商品功能**: 商品详情、出价系统、收藏功能
- **卖家功能**: 商品发布、店铺管理、数据统计

### 🔧 后端功能
- **用户管理**: 注册登录、个人信息、地址管理
- **商品管理**: 商品CRUD、分类管理、拍卖逻辑
- **订单系统**: 订单处理、支付集成、物流跟踪
- **消息系统**: 站内信、推送通知
- **店铺系统**: 店铺认证、数据统计
- **同城服务**: 本地服务发布与管理

### 💻 后台管理功能
- **数据统计**: 用户数据、销售数据、收入统计
- **用户管理**: 用户列表、状态管理、权限控制
- **商品管理**: 商品审核、分类管理、库存管理
- **订单管理**: 订单查看、状态更新、退款处理
- **内容管理**: 专场活动、轮播图、公告管理

## 🛠️ 技术栈

### 移动端 (Flutter)
- **框架**: Flutter 3.x
- **状态管理**: Provider + GetX
- **网络请求**: Dio
- **本地存储**: SharedPreferences + SQLite
- **UI组件**: Material Design + 自定义组件
- **图片处理**: cached_network_image
- **路由管理**: GetX路由

### 后端 (Python)
- **框架**: FastAPI
- **数据库**: MySQL + SQLAlchemy ORM
- **认证**: JWT Token
- **缓存**: Redis
- **任务队列**: Celery
- **文件存储**: 本地存储 + 云存储支持
- **API文档**: Swagger UI

### 后台管理 (HTML)
- **前端**: Bootstrap 5 + Vanilla JavaScript
- **图表**: Chart.js
- **图标**: Bootstrap Icons
- **样式**: 响应式设计

### 数据库设计
- **用户系统**: 用户信息、关注关系、地址管理
- **商品系统**: 商品信息、分类、出价记录
- **交易系统**: 订单管理、支付记录
- **内容系统**: 消息、专场活动、同城服务

## 🔧 推荐开发工具

### 移动端开发工具
1. **IDE**: 
   - Android Studio (推荐)
   - VS Code + Flutter插件
   - IntelliJ IDEA

2. **调试工具**:
   - Flutter Inspector
   - Dart DevTools
   - Firebase Crashlytics

3. **测试工具**:
   - Flutter Test
   - Integration Test
   - Golden Test

4. **性能分析**:
   - Flutter Performance
   - Memory Profiler
   - Network Profiler

### 后端开发工具
1. **IDE**:
   - PyCharm Professional (推荐)
   - VS Code + Python插件
   - Sublime Text

2. **API测试**:
   - Postman (推荐)
   - Insomnia
   - HTTPie
   - Swagger UI (内置)

3. **数据库工具**:
   - MySQL Workbench
   - phpMyAdmin
   - DBeaver
   - Navicat

4. **监控工具**:
   - Prometheus + Grafana
   - ELK Stack
   - Sentry

### 通用开发工具
1. **版本控制**:
   - Git + GitHub/GitLab
   - SourceTree (GUI)
   - GitKraken

2. **项目管理**:
   - Jira
   - Trello
   - Notion

3. **设计工具**:
   - Figma (UI设计)
   - Adobe XD
   - Sketch

4. **文档工具**:
   - Markdown编辑器
   - GitBook
   - Confluence

## 🚀 快速开始

### 环境要求
- Flutter SDK 3.x+
- Python 3.8+
- MySQL 8.0+
- Redis 6.0+
- Node.js 16+ (可选，用于前端构建)

### 1. 数据库初始化
```bash
# 创建数据库
mysql -u root -p < database_design.sql
```

### 2. 后端启动
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 移动端运行
```bash
cd petshop_app
flutter pub get
flutter run
```

### 4. 后台管理
```bash
cd admin
# 使用任意HTTP服务器运行，如：
python -m http.server 8080
# 或使用Live Server插件
```

## 📱 MCP工具推荐

### 开发阶段
1. **代码质量**:
   - ESLint/Prettier (代码格式化)
   - SonarQube (代码质量检查)
   - CodeClimate

2. **自动化测试**:
   - GitHub Actions
   - Jenkins
   - CircleCI

3. **依赖管理**:
   - Dependabot
   - Renovate
   - Snyk (安全扫描)

### 测试阶段
1. **移动端测试**:
   - Firebase Test Lab
   - BrowserStack
   - Sauce Labs

2. **API测试**:
   - Newman (Postman CLI)
   - Artillery (负载测试)
   - K6

3. **性能测试**:
   - JMeter
   - Gatling
   - WebPageTest

### 部署阶段
1. **容器化**:
   - Docker
   - Docker Compose
   - Kubernetes

2. **云服务**:
   - AWS/阿里云/腾讯云
   - Firebase
   - Vercel

3. **监控告警**:
   - Datadog
   - New Relic
   - PagerDuty

## 📋 开发计划

### 第一阶段 (基础功能)
- [x] 数据库设计
- [x] 后端API基础框架
- [x] Flutter项目结构
- [x] 后台管理界面
- [ ] 用户注册登录
- [ ] 商品基础CRUD
- [ ] 基础UI页面

### 第二阶段 (核心功能)
- [ ] 拍卖系统实现
- [ ] 支付系统集成
- [ ] 消息推送系统
- [ ] 图片上传处理
- [ ] 搜索功能
- [ ] 订单流程

### 第三阶段 (高级功能)
- [ ] 实时拍卖
- [ ] 地理位置服务
- [ ] 数据分析统计
- [ ] 性能优化
- [ ] 安全加固
- [ ] 自动化部署

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目维护者: [Your Name]
- 邮箱: your.email@example.com
- 项目链接: [https://github.com/yourusername/petshopnew](https://github.com/yourusername/petshopnew)

---

⭐ 如果这个项目对你有帮助，请给它一个星标！


