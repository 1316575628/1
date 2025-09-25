# 钉钉打卡提醒系统部署指南

## 部署方式选择

### 1. Docker部署（推荐）

#### 1.1 使用预构建镜像部署（最简单）

```bash
# 克隆项目
git clone https://github.com/yourusername/dingding-attendance-system.git
cd dingding-attendance-system

# 使用预构建镜像一键部署
./deploy-from-image.sh
```

#### 1.2 使用Docker Compose（传统方式）

```bash
# 克隆项目
git clone https://github.com/yourusername/dingding-attendance-system.git
cd dingding-attendance-system

# 启动服务
./docker-start.sh
```

#### 1.3 手动Docker部署

```bash
# 构建镜像
docker build -t dingding-attendance:latest .

# 运行容器
docker run -d \
  --name dingding \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e SECRET_KEY=131657 \
  -e API_TOKEN=131657 \
  1316575628/1:latest
```

### 2. 原生部署

#### 2.1 环境准备

```bash
# 安装Python 3.9+
python3 --version

# 克隆项目
git clone https://github.com/yourusername/dingding-attendance-system.git
cd dingding-attendance-system
```

#### 2.2 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 2.3 配置环境

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件
vim .env
```

#### 2.4 初始化数据库

```bash
# 初始化数据库
python run.py init_db

# 创建管理员用户
python run.py create_admin
```

#### 2.5 启动应用

```bash
# 开发模式
python run.py

# 生产模式（使用Gunicorn）
gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
```

## 服务器部署

### 1. 使用Nginx反向代理

```nginx
# /etc/nginx/sites-available/dingding-attendance
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /path/to/your/app/static;
        expires 30d;
    }
}
```

### 2. 使用Systemd服务

```ini
# /etc/systemd/system/dingding-attendance.service
[Unit]
Description=DingDing Attendance System
After=network.target

[Service]
Type=exec
User=your-user
WorkingDirectory=/path/to/your/app
Environment=FLASK_CONFIG=production
Environment=SECRET_KEY=your-secret-key
ExecStart=/path/to/your/app/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 启用并启动服务
sudo systemctl enable dingding-attendance
sudo systemctl start dingding-attendance
```

## 环境变量配置

### 必需配置

```bash
# Flask密钥（必须修改）
SECRET_KEY=your-secret-key-change-this

# API配置
API_TOKEN=your-api-token-here
CHECK_URL=https://your-check-api-url.com
WORKING_URL=https://your-working-webhook-url.com
NO_WORK_URL=https://your-no-work-webhook-url.com
```

### 可选配置

```bash
# 数据库配置
DATABASE_URL=sqlite:///data/app.db

# 时区配置
TIMEZONE=Asia/Shanghai

# 加班时间（分钟）
WORK_OVERTIME=0

# 提醒开关
REMINDER_ENABLED=true
```

## 安全配置

### 1. 修改默认密码

首次登录后必须修改默认管理员密码：
- 用户名：admin
- 默认密码：admin123

### 2. 配置防火墙

```bash
# Ubuntu/Debian
sudo ufw allow 5000/tcp
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

### 3. 使用HTTPS

```bash
# 使用Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 监控和维护

### 1. 查看日志

```bash
# Docker日志
docker-compose logs -f web

# 系统日志
sudo journalctl -u dingding-attendance -f

# 应用日志
tail -f logs/app.log
```

### 2. 备份数据

```bash
# 备份数据库
cp data/app.db backup/app_$(date +%Y%m%d_%H%M%S).db

# 备份配置
cp .env backup/env_$(date +%Y%m%d_%H%M%S).bak
```

### 3. 更新应用

```bash
# Docker部署
docker-compose pull
docker-compose up -d

# 原生部署
git pull
pip install -r requirements.txt
sudo systemctl restart dingding-attendance
```

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 检查端口占用
   lsof -i :5000
   # 或修改端口
   export PORT=5001
   ```

2. **数据库权限问题**
   ```bash
   # 修改数据目录权限
   sudo chown -R $USER:$USER data/
   ```

3. **时区问题**
   ```bash
   # 设置系统时区
   sudo timedatectl set-timezone Asia/Shanghai
   ```

4. **内存不足**
   ```bash
   # 减少工作进程数
   gunicorn --bind 0.0.0.0:5000 --workers 2 run:app
   ```

## 性能优化

### 1. 数据库优化

```python
# 在config.py中添加
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

### 2. Gunicorn优化

```bash
# 生产环境配置
gunicorn run:app \
  --bind 0.0.0.0:5000 \
  --workers 4 \
  --worker-class gthread \
  --threads 2 \
  --worker-connections 1000 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --timeout 30 \
  --keep-alive 2 \
  --preload
```

### 3. Nginx优化

```nginx
# Nginx配置优化
http {
    upstream app {
        server 127.0.0.1:5000;
    }
    
    server {
        listen 80;
        
        location / {
            proxy_pass http://app;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            proxy_read_timeout 86400;
        }
        
        location /static {
            alias /path/to/your/app/static;
            expires 30d;
            add_header Cache-Control "public, max-age=2592000";
        }
    }
}
```

## 扩展功能

### 1. 添加Redis缓存

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
```

### 2. 添加监控

```yaml
# docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

## 支持

如有部署问题，请查看：
- [README.md](README.md) - 详细使用说明
- [GitHub Issues](https://github.com/yourusername/dingding-attendance-system/issues) - 问题反馈
- 系统日志 - `logs/app.log`

---

**享受使用钉钉打卡提醒系统！** 🎉