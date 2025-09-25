#!/bin/bash
# 钉钉打卡提醒系统预构建镜像一键部署脚本

set -e

echo "🚀 使用预构建镜像部署钉钉打卡提醒系统..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    log_error "未找到Docker，请先安装Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    log_error "未找到Docker Compose，请先安装Docker Compose"
    exit 1
fi

# 检查依赖完整性
check_dependencies() {
    log_info "检查依赖完整性..."
    
    # 检查必要文件
    local required_files=("docker-compose.yml" "config.py")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "缺少必要文件: $file"
            exit 1
        fi
    done
    
    log_info "依赖检查通过"
}

# 拉取预构建镜像
log_info "拉取预构建镜像..."
if ! docker pull ghcr.io/yourusername/dingding-attendance-system:latest; then
    log_error "镜像拉取失败，请检查网络连接或镜像名称"
    exit 1
fi

# 创建必要目录
log_info "创建数据目录..."
mkdir -p data logs uploads

# 检查环境文件
if [ ! -f ".env" ]; then
    log_warn "未找到.env文件，将使用默认配置"
    # 可以在这里添加创建默认.env文件的逻辑
fi

# 检查依赖完整性
check_dependencies

# 启动服务
log_info "启动服务..."
if ! docker-compose up -d; then
    log_error "服务启动失败"
    echo "请查看日志：docker-compose logs"
    exit 1
fi

# 等待服务启动
log_info "等待服务启动..."
sleep 10

# 检查服务状态
log_info "检查服务状态..."
if docker-compose ps | grep -q "Up"; then
    log_info "✅ 服务启动成功！"
    echo "应用地址：http://localhost:5000"
    echo "默认管理员账号：admin，密码：admin123"
    echo ""
    echo "常用命令："
    echo "  查看日志：docker-compose logs -f web"
    echo "  停止服务：docker-compose down"
    echo "  重启服务：docker-compose restart"
else
    log_error "服务启动失败"
    echo "请查看日志：docker-compose logs"
    exit 1
fi