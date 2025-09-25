#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask应用初始化模块
确保中文字符编码正确处理
"""

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from .models import db

# 初始化扩展
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    """创建Flask应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # 配置登录管理器
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录以访问此页面'
    login_manager.login_message_category = 'info'
    
    # 注册蓝图
    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.schedule import schedule_bp
    from .routes.shift import shift_bp
    from .routes.logs import logs_bp
    from .routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(shift_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(api_bp)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        init_default_data()
    
    return app

def init_default_data():
    """初始化默认数据"""
    from .models import User, ShiftType, SystemConfig
    
    # 创建默认管理员用户
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@example.com',
            is_admin=True,
            is_active=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
    
    # 创建默认班次类型
    default_shifts = [
        {'name': 'A班', 'start_time': '09:00', 'end_time': '18:00', 'color': '#3498db', 'description': '正常班 (9:00-18:00)'},
        {'name': 'B班', 'start_time': '13:00', 'end_time': '22:00', 'color': '#e74c3c', 'description': '晚班 (13:00-22:00)'},
        {'name': '休', 'start_time': '00:00', 'end_time': '00:00', 'color': '#95a5a6', 'description': '休息日'},
    ]
    
    for shift_data in default_shifts:
        shift = ShiftType.query.filter_by(name=shift_data['name']).first()
        if not shift:
            shift = ShiftType(**shift_data)
            db.session.add(shift)
    
    # 创建系统配置
    default_configs = [
        {'key': 'api_token', 'value': '', 'description': 'API访问令牌'},
        {'key': 'check_url', 'value': '', 'description': '打卡检测API地址'},
        {'key': 'working_url', 'value': '', 'description': '上班提醒URL'},
        {'key': 'no_work_url', 'value': '', 'description': '下班提醒URL'},
        {'key': 'work_overtime', 'value': '0', 'description': '加班时间(分钟)'},
        {'key': 'reminder_enabled', 'value': 'true', 'description': '是否启用提醒功能'},
    ]
    
    for config_data in default_configs:
        config = SystemConfig.query.filter_by(key=config_data['key']).first()
        if not config:
            config = SystemConfig(**config_data)
            db.session.add(config)
    
    db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    """加载用户回调函数"""
    from .models import User
    return User.query.get(int(user_id))