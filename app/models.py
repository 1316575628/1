#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模型定义
确保中文字符编码正确处理
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关联关系
    schedules = db.relationship('Schedule', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    logs = db.relationship('SystemLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class ShiftType(db.Model):
    """班次类型表"""
    __tablename__ = 'shift_types'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # 班次名称
    start_time = db.Column(db.String(5), nullable=False)  # 开始时间 (HH:MM)
    end_time = db.Column(db.String(5), nullable=False)  # 结束时间 (HH:MM)
    color = db.Column(db.String(7), default='#3498db', nullable=False)  # 显示颜色
    description = db.Column(db.Text, nullable=True)  # 班次描述
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关联关系
    schedules = db.relationship('Schedule', backref='shift_type', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'color': self.color,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Schedule(db.Model):
    """排班表"""
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    shift_type_id = db.Column(db.Integer, db.ForeignKey('shift_types.id'), nullable=True, index=True)
    work_date = db.Column(db.Date, nullable=False, index=True)  # 工作日期
    is_rest_day = db.Column(db.Boolean, default=False, nullable=False)  # 是否休息日
    note = db.Column(db.Text, nullable=True)  # 备注
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """转换为字典格式"""
        shift_info = None
        if self.shift_type:
            shift_info = {
                'id': self.shift_type.id,
                'name': self.shift_type.name,
                'start_time': self.shift_type.start_time,
                'end_time': self.shift_type.end_time,
                'color': self.shift_type.color
            }
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.username if self.user else None,
            'shift_type_id': self.shift_type_id,
            'shift_info': shift_info,
            'work_date': self.work_date.strftime('%Y-%m-%d'),
            'is_rest_day': self.is_rest_day,
            'note': self.note,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class SystemConfig(db.Model):
    """系统配置表"""
    __tablename__ = 'system_configs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)  # 配置键
    value = db.Column(db.Text, nullable=True)  # 配置值
    description = db.Column(db.Text, nullable=True)  # 配置描述
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class SystemLog(db.Model):
    """系统日志表"""
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    log_type = db.Column(db.String(50), nullable=False, index=True)  # 日志类型
    log_level = db.Column(db.String(20), nullable=False, default='INFO')  # 日志级别
    message = db.Column(db.Text, nullable=False)  # 日志内容
    ip_address = db.Column(db.String(45), nullable=True)  # IP地址
    user_agent = db.Column(db.Text, nullable=True)  # 用户代理
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'log_type': self.log_type,
            'log_level': self.log_level,
            'message': self.message,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class AttendanceRecord(db.Model):
    """考勤记录表"""
    __tablename__ = 'attendance_records'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    work_date = db.Column(db.Date, nullable=False, index=True)
    shift_type_id = db.Column(db.Integer, db.ForeignKey('shift_types.id'), nullable=True)
    clock_in_status = db.Column(db.String(20), default='未打卡', nullable=False)  # 上班打卡状态
    clock_out_status = db.Column(db.String(20), default='未打卡', nullable=False)  # 下班打卡状态
    clock_in_reminded = db.Column(db.Boolean, default=False, nullable=False)  # 上班提醒已发送
    clock_out_reminded = db.Column(db.Boolean, default=False, nullable=False)  # 下班提醒已发送
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'work_date': self.work_date.strftime('%Y-%m-%d'),
            'shift_type_id': self.shift_type_id,
            'shift_name': self.shift_type.name if self.shift_type else None,
            'clock_in_status': self.clock_in_status,
            'clock_out_status': self.clock_out_status,
            'clock_in_reminded': self.clock_in_reminded,
            'clock_out_reminded': self.clock_out_reminded,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }