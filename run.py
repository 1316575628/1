#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主应用入口文件
确保中文字符编码正确处理
"""

import os
import sys
from app import create_app, db
from app.models import User, ShiftType, SystemConfig
from config import config

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 获取配置
config_name = os.environ.get('FLASK_CONFIG') or 'default'
app = create_app(config[config_name])

@app.shell_context_processor
def make_shell_context():
    """Shell上下文处理器"""
    return {
        'db': db,
        'User': User,
        'ShiftType': ShiftType,
        'SystemConfig': SystemConfig,
        'app': app
    }

@app.cli.command()
def init_db():
    """初始化数据库"""
    db.create_all()
    print('数据库初始化完成')

@app.cli.command()
def create_admin():
    """创建管理员用户"""
    from getpass import getpass
    
    username = input('请输入管理员用户名: ')
    email = input('请输入管理员邮箱: ')
    password = getpass('请输入管理员密码: ')
    confirm_password = getpass('请再次输入密码: ')
    
    if password != confirm_password:
        print('两次输入的密码不一致')
        return
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        print('用户名已存在')
        return
    
    admin = User(
        username=username,
        email=email,
        is_admin=True,
        is_active=True
    )
    admin.set_password(password)
    
    db.session.add(admin)
    db.session.commit()
    
    print(f'管理员用户 {username} 创建成功')

@app.cli.command()
def test_notification():
    """测试通知功能"""
    from app.utils.notification import notification_service
    
    # 获取第一个用户进行测试
    user = User.query.first()
    if not user:
        print('没有找到用户')
        return
    
    try:
        notification_service.send_notification(
            user,
            '这是一条测试通知消息',
            'test'
        )
        print('测试通知发送成功')
    except Exception as e:
        print(f'测试通知发送失败: {str(e)}')

if __name__ == '__main__':
    # 启动应用
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=True
    )