#!/bin/bash
# 钉钉打卡提醒系统启动脚本

set -e

echo "🚀 启动钉钉打卡提醒系统..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ 未找到requirements.txt文件"
    exit 1
fi

pip install --upgrade pip
pip install -r requirements.txt

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p data logs uploads

# 初始化数据库
echo "🗄️ 初始化数据库..."
python run.py init_db

# 检查是否需要创建管理员用户
if [ ! -f ".env" ]; then
    echo "⚠️ 未找到.env文件，使用默认配置"
else
    echo "✅ 加载环境配置文件"
fi

# 启动应用
echo "🌐 启动Web应用..."
echo "应用将在 http://localhost:5000 启动"
echo "默认管理员账号：admin，密码：admin123"
echo "按 Ctrl+C 停止应用"

# 启动Flask应用
python run.py