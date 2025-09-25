#!/bin/bash
# 钉钉打卡提醒系统Docker启动脚本

set -e

echo "🐳 使用Docker启动钉钉打卡提醒系统..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 未找到Docker，请先安装Docker"
    echo "安装指南：https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 未找到Docker Compose，请先安装Docker Compose"
    echo "安装指南：https://docs.docker.com/compose/install/"
    exit 1
fi

# 创建必要目录
echo "📁 创建数据目录..."
mkdir -p data logs uploads

# 检查环境文件
if [ ! -f ".env" ]; then
    echo "⚠️ 未找到.env文件，使用默认配置"
    echo "如需自定义配置，请复制.env.example为.env并修改"
fi

# 构建Docker镜像
echo "🔨 构建Docker镜像..."
docker-compose build

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