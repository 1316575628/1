# ARM64服务器部署指南

本文档详细说明了如何在ARM64架构服务器上部署钉钉打卡提醒系统。

## 部署前准备

### 1. 服务器要求
- ARM64架构服务器（如AWS Graviton、树莓派4等）
- 至少2GB内存
- 至少20GB存储空间
- Ubuntu 20.04或更高版本（推荐）

### 2. 系统依赖
确保服务器已安装以下软件：
- Docker 20.10或更高版本
- Docker Compose 1.29或更高版本

## 部署方案

### 方案一：使用预构建镜像部署（推荐）

#### 1. 拉取镜像
```bash
docker pull ghcr.io/yourusername/dingding-attendance-system:latest
```

#### 2. 创建必要的目录
```bash
mkdir -p data logs uploads
```

#### 3. 创建环境配置文件
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

#### 4. 创建docker-compose.yml文件
```bash
wget https://raw.githubusercontent.com/yourusername/dingding-attendance-system/main/docker-compose.yml
```

#### 5. 启动服务
```bash
docker-compose up -d
```

### 方案二：从源码构建部署

#### 1. 克隆项目
```bash
git clone https://github.com/yourusername/dingding-attendance-system.git
cd dingding-attendance-system
```

#### 2. 创建必要的目录
```bash
mkdir -p data logs uploads
```

#### 3. 复制环境配置文件
```bash
cp .env.example .env
# 编辑.env文件，配置必要的环境变量
vim .env
```

#### 4. 构建并启动服务
```bash
./docker-start.sh
```

## 验证部署

### 1. 检查服务状态
```bash
docker-compose ps
```

### 2. 查看应用日志
```bash
docker-compose logs -f web
```

### 3. 访问应用
打开浏览器访问 `http://your-server-ip:5000`

### 4. 测试API健康检查
```bash
curl http://your-server-ip:5000/api/health
```

## 系统维护

### 1. 查看日志
```bash
# 查看实时日志
docker-compose logs -f web

# 查看最近的日志
docker-compose logs --tail 100 web
```

### 2. 重启服务
```bash
docker-compose restart
```

### 3. 停止服务
```bash
docker-compose down
```

### 4. 更新应用
```bash
# 拉取最新镜像
docker-compose pull

# 重启服务
docker-compose up -d
```

## 故障排除

### 1. 容器无法启动
- 检查端口是否被占用：`netstat -tlnp | grep 5000`
- 检查数据目录权限：`ls -la data/`

### 2. 数据库连接失败
- 检查数据库文件权限：`ls -la data/app.db`
- 确认数据库路径配置正确

### 3. 定时任务不执行
- 检查`REMINDER_ENABLED`配置是否为true
- 查看调度器日志：`docker-compose logs web | grep scheduler`

### 4. 通知发送失败
- 验证Webhook地址是否正确
- 检查网络连接是否正常
- 确认API令牌是否有效

## 性能优化建议

### 1. 资源限制
在docker-compose.yml中添加资源限制：
```yaml
services:
  web:
    # ... 其他配置
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### 2. 数据库优化
- 定期清理旧的日志数据
- 为常用查询字段添加索引

### 3. 日志管理
配置日志轮转以避免磁盘空间不足：
```bash
# 在服务器上配置logrotate
sudo tee /etc/logrotate.d/dingding-attendance << EOF
/path/to/project/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF
```