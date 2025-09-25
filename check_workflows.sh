#!/bin/bash

# 检查GitHub工作流配置脚本

echo "检查GitHub工作流配置..."

# 检查工作流目录是否存在
if [ ! -d ".github/workflows" ]; then
    echo "错误: .github/workflows 目录不存在"
    exit 1
fi

# 检查CI工作流
if [ -f ".github/workflows/ci.yml" ]; then
    echo "✓ CI工作流文件存在"
else
    echo "警告: CI工作流文件不存在"
fi

# 检查Docker构建工作流
if [ -f ".github/workflows/docker-build.yml" ]; then
    echo "✓ Docker构建工作流文件存在"
    
    # 检查关键配置
    if grep -q "docker/setup-qemu-action" ".github/workflows/docker-build.yml"; then
        echo "✓ QEMU设置已配置"
    else
        echo "警告: QEMU设置未配置"
    fi
    
    if grep -q "push: \${{ github.event_name != 'pull_request' }}" ".github/workflows/docker-build.yml"; then
        echo "✓ 推送条件已优化"
    else
        echo "警告: 推送条件可能需要优化"
    fi
else
    echo "错误: Docker构建工作流文件不存在"
    exit 1
fi

echo "工作流配置检查完成"