# 钉钉打卡提醒系统预构建镜像一键部署方案

## 1. 概述

本设计文档详细说明了如何从GitHub Container Registry拉取钉钉打卡提醒系统的预构建Docker镜像并实现一键部署。该系统是一个基于Flask的Web应用，支持用户认证、排班管理、班次配置和定时提醒等功能。通过使用预构建的Docker镜像，可以跳过本地编译过程，直接部署应用，大大简化了部署流程。

## 2. 项目架构

### 2.1 技术栈
- **后端框架**: Flask 2.3.3
- **数据库**: SQLite
- **容器化**: Docker
- **部署工具**: Docker Compose
- **WSGI服务器**: Gunicorn

### 2.2 应用结构
```
钉钉打卡提醒系统
├── Web应用层 (Flask)
├── 数据访问层 (SQLAlchemy)
├── 定时任务层 (APScheduler)
├── 通知服务层 (钉钉/飞书Webhook)
└── 数据存储层 (SQLite数据库)
```

## 3. 预构建镜像拉取

### 3.1 镜像仓库信息
钉钉打卡提醒系统的预构建Docker镜像托管在GitHub Container Registry (GHCR)中：
- 镜像仓库地址：`ghcr.io/{用户名}/dingding-attendance-system`
- 最新版本标签：`latest`
- ARM64架构支持：镜像支持多架构构建，包括ARM64

### 3.2 镜像拉取步骤
1. 确保已安装Docker环境
2. 执行镜像拉取命令：
   ```bash
   docker pull ghcr.io/yourusername/dingding-attendance-system:latest
   ```
3. 验证镜像拉取结果：
   ```bash
   docker images | grep dingding-attendance-system
   ```

## 4. 基于预构建镜像的一键部署方案

### 4.1 Docker Compose部署（推荐）
使用`docker-compose.yml`文件定义服务配置，但修改为使用拉取的镜像而非本地构建：

```yaml
version: '3.8'
services:
  web:
    image: ghcr.io/yourusername/dingding-attendance-system:latest
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    environment:
      - FLASK_CONFIG=production
      - SECRET_KEY=${SECRET_KEY:-your-secret-key-change-this}
      - DATABASE_URL=${DATABASE_URL:-sqlite:///data/app.db}
      - TZ=Asia/Shanghai
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 4.2 一键部署脚本
创建专门用于预构建镜像部署的脚本`deploy-from-image.sh`：

```bash
#!/bin/bash
# 检查Docker安装
# 拉取预构建镜像
# 创建必要目录
# 启动服务
# 检查服务状态
```

### 4.3 部署执行流程
1. 环境检查（Docker安装）
2. 拉取预构建Docker镜像
3. 创建数据目录（data、logs、uploads）
4. 配置环境变量
5. 启动容器服务
6. 验证服务状态

## 5. 部署配置管理

### 5.1 环境变量配置
通过`.env`文件管理环境变量：
- `SECRET_KEY`: Flask应用密钥
- `DATABASE_URL`: 数据库连接URL
- `API_TOKEN`: API访问令牌
- `CHECK_URL`: 打卡检测API地址
- `WORKING_URL`: 上班提醒Webhook
- `NO_WORK_URL`: 下班提醒Webhook
- `REMINDER_ENABLED`: 定时提醒功能开关
- `WORK_OVERTIME`: 加班时间配置

### 5.2 数据持久化
通过Docker卷实现数据持久化：
- `/app/data`: 数据库存储
- `/app/logs`: 日志文件
- `/app/uploads`: 上传文件

### 5.3 配置文件准备
1. 创建`.env`配置文件：
   ```bash
   cat > .env << EOF
   FLASK_CONFIG=production
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///data/app.db
   API_TOKEN=your-api-token-here
   WORKING_URL=https://your-working-webhook-url.com
   NO_WORK_URL=https://your-no-work-webhook-url.com
   REMINDER_ENABLED=true
   EOF
   ```
2. 创建必要的目录结构
3. 验证配置文件正确性

## 6. 服务管理命令

### 6.1 常用Docker Compose命令
| 命令 | 说明 |
|------|------|
| `docker-compose up -d` | 后台启动服务 |
| `docker-compose down` | 停止并删除服务 |
| `docker-compose logs -f web` | 查看服务日志 |
| `docker-compose restart` | 重启服务 |
| `docker-compose pull` | 拉取最新镜像 |

### 6.2 应用管理命令
| 命令 | 说明 |
|------|------|
| `docker exec -it dingding-attendance-web-1 bash` | 进入容器bash |
| `docker exec dingding-attendance-web-1 python run.py init_db` | 初始化数据库 |
| `docker exec dingding-attendance-web-1 python run.py create_admin` | 创建管理员用户 |

### 6.3 镜像管理命令
| 命令 | 说明 |
|------|------|
| `docker pull ghcr.io/yourusername/dingding-attendance-system:latest` | 拉取最新镜像 |
| `docker images | grep dingding` | 查看已拉取的镜像 |
| `docker rmi ghcr.io/yourusername/dingding-attendance-system:latest` | 删除镜像 |

## 7. 部署验证

### 7.1 服务状态检查
- 容器运行状态检查
- 应用健康检查接口访问
- 数据库连接验证

### 7.2 功能验证
- Web界面访问 (http://localhost:5000)
- 默认管理员登录 (admin/admin123)
- 排班管理功能测试
- 定时任务状态检查

## 8. 故障排除

### 8.1 常见问题及解决方案
1. **镜像拉取失败**
   - 问题：无法从GitHub Container Registry拉取镜像
   - 解决方案：检查网络连接和镜像名称是否正确

2. **端口冲突**
   - 解决方案：修改docker-compose.yml中的端口映射

3. **权限问题**
   - 解决方案：检查数据目录权限设置

4. **数据库连接失败**
   - 解决方案：检查DATABASE_URL环境变量配置

5. **定时任务未执行**
   - 解决方案：检查REMINDER_ENABLED配置和API设置

### 8.2 日志查看
- Docker容器日志：`docker-compose logs -f web`
- 应用日志：`logs/app.log`
- 系统日志：`journalctl -u dingding-attendance`

### 8.3 镜像相关问题
- 验证镜像完整性：`docker inspect ghcr.io/yourusername/dingding-attendance-system:latest`
- 清理悬空镜像：`docker image prune`

## 9. 安全考虑

### 9.1 配置安全
- 修改默认SECRET_KEY
- 更改默认管理员密码
- 配置HTTPS证书

### 9.2 访问控制
- 防火墙配置
- 反向代理设置
- 用户权限管理

## 9. 一键部署脚本示例

### 9.1 deploy-from-image.sh脚本
```bash
#!/bin/bash
# 钉钉打卡提醒系统预构建镜像一键部署脚本

set -e

echo "🚀 使用预构建镜像部署钉钉打卡提醒系统..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 未找到Docker，请先安装Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 未找到Docker Compose，请先安装Docker Compose"
    exit 1
fi

# 拉取预构建镜像
echo "📥 拉取预构建镜像..."
docker pull ghcr.io/yourusername/dingding-attendance-system:latest

# 创建必要目录
echo "📁 创建数据目录..."
mkdir -p data logs uploads

# 检查环境文件
if [ ! -f ".env" ]; then
    echo "⚠️ 未找到.env文件，请创建.env配置文件"
    exit 1
fi

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
if docker-compose ps | grep -q "Up"; then
    echo "✅ 服务启动成功！"
    echo "应用地址：http://localhost:5000"
    echo "默认管理员账号：admin，密码：admin123"
    echo ""
    echo "常用命令："
    echo "  查看日志：docker-compose logs -f web"
    echo "  停止服务：docker-compose down"
    echo "  重启服务：docker-compose restart"
else
    echo "❌ 服务启动失败"
    echo "请查看日志：docker-compose logs"
    exit 1
fi
```

## 10. 性能优化建议

### 10.1 Docker优化
- 使用多阶段构建减小镜像大小
- 合理配置资源限制
- 使用.dockerignore排除不必要文件

### 10.2 应用优化
- Gunicorn工作进程调优
- 数据库连接池配置
- 静态资源缓存设置