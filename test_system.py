#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试脚本
测试钉钉打卡提醒系统的基本功能
"""

import os
import sys
import requests
import json
from datetime import datetime

def test_health_check():
    """测试健康检查接口"""
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                print("✅ 健康检查接口正常")
                return True
            else:
                print("❌ 健康检查接口异常")
                return False
        else:
            print(f"❌ 健康检查接口返回错误状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查接口测试失败: {str(e)}")
        return False

def test_login_page():
    """测试登录页面"""
    try:
        response = requests.get('http://localhost:5000/auth/login', timeout=10)
        if response.status_code == 200:
            if '登录' in response.text:
                print("✅ 登录页面正常")
                return True
            else:
                print("❌ 登录页面内容异常")
                return False
        else:
            print(f"❌ 登录页面返回错误状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 登录页面测试失败: {str(e)}")
        return False

def test_api_endpoints():
    """测试API接口"""
    endpoints = [
        ('/api/users', '用户列表'),
        ('/api/shift-types', '班次类型列表'),
        ('/api/scheduler/status', '调度器状态')
    ]
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f'http://localhost:5000{endpoint}', timeout=10)
            if response.status_code in [200, 401, 403]:  # 401/403表示需要认证，接口正常
                print(f"✅ {description}接口正常")
            else:
                print(f"❌ {description}接口异常: {response.status_code}")
        except Exception as e:
            print(f"❌ {description}接口测试失败: {str(e)}")

def test_database():
    """测试数据库连接"""
    try:
        # 检查数据库文件是否存在
        db_path = os.path.join('data', 'app.db')
        if os.path.exists(db_path):
            print("✅ 数据库文件存在")
            
            # 检查数据库文件大小
            size = os.path.getsize(db_path)
            if size > 0:
                print(f"✅ 数据库文件大小正常: {size} bytes")
            else:
                print("⚠️ 数据库文件为空")
        else:
            print("❌ 数据库文件不存在")
    except Exception as e:
        print(f"❌ 数据库测试失败: {str(e)}")

def test_static_files():
    """测试静态文件"""
    static_files = [
        ('/static/css/style.css', 'CSS样式文件'),
        ('/static/js/main.js', 'JavaScript文件'),
        ('/static/images/favicon.ico', '网站图标')
    ]
    
    for file_path, description in static_files:
        try:
            response = requests.get(f'http://localhost:5000{file_path}', timeout=10)
            if response.status_code == 200:
                print(f"✅ {description}可访问")
            else:
                print(f"❌ {description}访问异常: {response.status_code}")
        except Exception as e:
            print(f"❌ {description}测试失败: {str(e)}")

def main():
    """主测试函数"""
    print("🚀 开始测试钉钉打卡提醒系统...")
    print("=" * 50)
    
    # 测试基本功能
    print("\n📊 测试基本功能:")
    health_ok = test_health_check()
    login_ok = test_login_page()
    
    # 测试API接口
    print("\n🔌 测试API接口:")
    test_api_endpoints()
    
    # 测试数据库
    print("\n🗄️ 测试数据库:")
    test_database()
    
    # 测试静态文件
    print("\n📁 测试静态文件:")
    test_static_files()
    
    # 总结
    print("\n" + "=" * 50)
    if health_ok and login_ok:
        print("🎉 系统测试通过！基本功能正常")
        return 0
    else:
        print("⚠️ 系统测试发现问题，请检查相关配置")
        return 1

if __name__ == '__main__':
    sys.exit(main())