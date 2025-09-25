#!/bin/bash
# 钉钉打卡提醒系统项目检查脚本

echo "🔍 检查钉钉打卡提醒系统项目结构..."
echo "=" * 60

# 检查核心目录
check_directory() {
    if [ -d "$1" ]; then
        echo "✅ 目录存在: $1"
        return 0
    else
        echo "❌ 目录缺失: $1"
        return 1
    fi
}

# 检查核心文件
check_file() {
    if [ -f "$1" ]; then
        echo "✅ 文件存在: $1"
        return 0
    else
        echo "❌ 文件缺失: $1"
        return 1
    fi
}

# 检查Python文件
echo "📁 检查Python文件:"
check_file "run.py"
check_file "app/__init__.py"
check_file "app/models.py"
check_file "config.py"

# 检查路由文件
echo "🛣️  检查路由文件:"
check_file "app/routes/auth.py"
check_file "app/routes/main.py"
check_file "app/routes/schedule.py"
check_file "app/routes/shift.py"
check_file "app/routes/logs.py"
check_file "app/routes/api.py"

# 检查表单文件
echo "📝 检查表单文件:"
check_file "app/forms/auth.py"
check_file "app/forms/schedule.py"
check_file "app/forms/shift.py"

# 检查工具文件
echo "🛠️  检查工具文件:"
check_file "app/utils/scheduler.py"
check_file "app/utils/notification.py"
check_file "app/utils/decorators.py"

# 检查模板文件
echo "🎨 检查模板文件:"
check_file "app/templates/base.html"
check_file "app/templates/auth/login.html"
check_file "app/templates/main/index.html"
check_file "app/templates/main/calendar.html"
check_file "app/templates/schedule/index.html"
check_file "app/templates/shift/index.html"
check_file "app/templates/main/about.html"

# 检查静态文件
echo "📦 检查静态文件:"
check_file "static/css/style.css"
check_file "static/js/main.js"

# 检查配置文件
echo "⚙️  检查配置文件:"
check_file "requirements.txt"
check_file "Dockerfile"
check_file "docker-compose.yml"
check_file ".env.example"
check_file ".gitignore"

# 检查文档
echo "📚 检查文档文件:"
check_file "README.md"
check_file "DEPLOYMENT.md"
check_file "PROJECT_SUMMARY.md"
check_file "LICENSE"

# 检查脚本文件
echo "🔧 检查脚本文件:"
check_file "start.sh"
check_file "docker-start.sh"
check_file "test_system.py"

# 检查GitHub Actions
echo "🔄 检查GitHub Actions:"
if [ -d ".github/workflows" ]; then
    echo "✅ GitHub Actions目录存在"
    check_file ".github/workflows/docker-build.yml"
    check_file ".github/workflows/ci.yml"
else
    echo "❌ GitHub Actions目录缺失"
fi

# 检查数据目录
echo "🗄️  检查数据目录:"
check_directory "data"
check_directory "logs"
check_directory "uploads"

# 统计文件数量
echo ""
echo "📊 项目统计:"
echo "Python文件: $(find . -name "*.py" | wc -l)"
echo "HTML模板: $(find . -name "*.html" | wc -l)"
echo "CSS文件: $(find . -name "*.css" | wc -l)"
echo "JavaScript文件: $(find . -name "*.js" | wc -l)"
echo "配置文件: $(find . -name "*.yml" -o -name "*.yaml" -o -name "Dockerfile" -o -name "*.txt" | wc -l)"
echo "文档文件: $(find . -name "*.md" | wc -l)"

echo ""
echo "✨ 项目检查完成！"
echo "🚀 您现在可以启动钉钉打卡提醒系统了！"
echo ""
echo "启动方式:"
echo "  Docker部署: ./docker-start.sh"
echo "  原生部署: ./start.sh"
echo ""
echo "默认访问地址: http://localhost:5000"
echo "默认管理员账号: admin"
echo "默认管理员密码: admin123"