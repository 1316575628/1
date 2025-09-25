# 钉钉打卡提醒系统

一个基于Web的钉钉打卡提醒系统，支持排班管理、班次配置、定时提醒等功能。

## 功能特性

- ✅ **用户认证系统** - 支持多用户登录和权限管理
- ✅ **排班管理** - 可视化排班表，支持批量创建和导入
- ✅ **班次配置** - 灵活的班次类型设置，支持自定义时间和颜色
- ✅ **定时提醒** - 根据排班自动发送上下班打卡提醒
- ✅ **通知集成** - 支持钉钉和飞书双平台通知
- ✅ **日志记录** - 完整的操作日志和考勤记录
- ✅ **响应式设计** - 支持PC和移动端访问
- ✅ **Docker支持** - 一键部署，支持ARM64架构
- ✅ **CI/CD集成** - 自动化构建和部署

## 技术栈

### 后端
- **Flask** - Web框架
- **SQLAlchemy** - ORM框架
- **Flask-Login** - 用户认证
- **APScheduler** - 定时任务
- **Requests** - HTTP请求库

### 前端
- **Bootstrap 5** - CSS框架
- **jQuery** - JavaScript库
- **FullCalendar** - 日历组件
- **DataTables** - 表格组件

### 数据库
- **SQLite** - 轻量级数据库

### 部署
- **Docker** - 容器化部署
- **GitHub Actions** - CI/CD自动化

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/dingding-attendance-system.git
cd dingding-attendance-system
```

### 2. 环境配置

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件
vim .env
```

### 3. Docker部署

```bash
# 使用Docker Compose启动
docker-compose up -d

# 或者使用Docker直接运行
docker build -t dingding-attendance .
docker run -d -p 5000:5000 --name dingding-app dingding-attendance
```

### 4. 本地开发

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python run.py init_db

# 创建管理员用户
python run.py create_admin

# 启动应用
python run.py
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | Flask密钥 | 随机生成 |
| `DATABASE_URL` | 数据库连接 | sqlite:///data/app.db |
| `API_TOKEN` | API访问令牌 | 空 |
| `CHECK_URL` | 打卡检测API地址 | 空 |
| `WORKING_URL` | 上班提醒Webhook | 空 |
| `NO_WORK_URL` | 下班提醒Webhook | 空 |
| `WORK_OVERTIME` | 加班时间(分钟) | 0 |
| `REMINDER_ENABLED` | 启用提醒功能 | true |

### 默认账号

系统初始化后会创建默认管理员账号：
- **用户名**: admin
- **密码**: admin123

**⚠️ 重要**: 首次登录后请立即修改默认密码！

## 使用说明

### 1. 系统配置

登录后首先配置系统参数：
1. 进入"系统配置"页面
2. 设置API访问令牌和Webhook地址
3. 配置加班时间和提醒开关

### 2. 班次管理

1. 进入"班次管理"页面
2. 创建需要的班次类型（如：A班、B班等）
3. 设置班次的开始时间、结束时间和显示颜色

### 3. 排班管理

1. 进入"排班管理"页面
2. 点击"创建排班"为每个用户设置排班
3. 或使用"批量创建"功能快速生成排班表
4. 在"排班日历"中查看整体排班情况

### 4. 定时提醒

系统会根据排班表自动检查打卡状态：
- **上班提醒**: 上班前15分钟发送
- **下班提醒**: 下班后30分钟发送（包含加班时间）

## API接口

系统提供RESTful API接口，方便第三方集成：

### 用户管理
- `GET /api/users` - 获取用户列表
- `GET /api/shift-types` - 获取班次类型

### 系统状态
- `GET /api/scheduler/status` - 获取调度器状态
- `POST /api/scheduler/start` - 启动定时任务
- `POST /api/scheduler/stop` - 停止定时任务

### 配置管理
- `GET /api/config/<key>` - 获取配置
- `PUT /api/config/<key>` - 更新配置

## 部署指南

### Docker部署

```bash
# 构建镜像
docker build -t dingding-attendance:latest .

# 运行容器
docker run -d \
  --name dingding-app \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e SECRET_KEY=your-secret-key \
  -e API_TOKEN=your-api-token \
  dingding-attendance:latest
```

### Docker Compose部署

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f web

# 停止服务
docker-compose down
```

### 生产环境部署

1. **使用Gunicorn**:
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
```

2. **使用Nginx反向代理**:
``nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### ARM64服务器部署

本项目原生支持ARM64架构，可在树莓派、AWS Graviton等ARM64服务器上部署。

详细部署指南请参考 [ARM64部署指南](DEPLOYMENT_ARM64.md)

## 开发指南

### 项目结构

```
├── app/                    # 应用代码
│   ├── models.py          # 数据模型
│   ├── routes/            # 路由模块
│   ├── forms/             # 表单验证
│   ├── templates/         # HTML模板
│   └── utils/             # 工具模块
├── static/                # 静态文件
├── data/                  # 数据文件
├── logs/                  # 日志文件
├── docker/                # Docker配置
├── migrations/            # 数据库迁移
├── tests/                 # 测试代码
└── requirements.txt       # 依赖列表
```

### 添加新功能

1. **创建数据模型** - 在 `app/models.py` 中定义
2. **创建表单验证** - 在 `app/forms/` 目录中添加
3. **创建路由** - 在 `app/routes/` 目录中添加
4. **创建模板** - 在 `app/templates/` 目录中添加
5. **添加静态文件** - 在 `static/` 目录中添加

### 代码规范

- 使用UTF-8编码
- 遵循PEP 8 Python编码规范
- 函数和变量使用英文命名
- 注释和文档使用中文

## 故障排除

### 常见问题

1. **中文乱码问题**
   - 确保所有文件使用UTF-8编码
   - 检查数据库字符集设置

2. **定时任务不执行**
   - 检查 `REMINDER_ENABLED` 配置
   - 确认API配置是否正确
   - 查看系统日志获取详细信息

3. **通知发送失败**
   - 检查网络连接
   - 验证Webhook地址是否正确
   - 确认API令牌是否有效

4. **Docker部署失败**
   - 检查端口是否被占用
   - 确认数据卷权限
   - 查看容器日志

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看系统日志
journalctl -u your-service-name

# Docker日志
docker logs -f dingding-app
```

## 贡献指南

欢迎提交Issue和Pull Request来改进项目！

### 开发流程

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 更新日志

### v1.0.0 (2024-09-25)
- ✨ 初始版本发布
- 🚀 支持用户认证和权限管理
- 📅 排班管理功能
- ⏰ 定时提醒功能
- 🐳 Docker支持
- 🔄 CI/CD集成

## 联系方式

如有问题或建议，欢迎联系：
- 提交Issue: [GitHub Issues](https://github.com/yourusername/dingding-attendance-system/issues)
- 邮箱: your.email@example.com

---

**享受使用钉钉打卡提醒系统！** 🎉