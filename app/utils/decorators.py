#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
装饰器工具模块
确保中文字符编码正确处理
"""

from functools import wraps
from flask import abort, flash, redirect, url_for, request, jsonify
from flask_login import current_user
from ..models import User

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'success': False, 'message': '请先登录'}), 401
            else:
                flash('请先登录', 'warning')
                return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.is_admin:
            if request.is_json:
                return jsonify({'success': False, 'message': '需要管理员权限'}), 403
            else:
                abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def active_user_required(f):
    """活跃用户权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'success': False, 'message': '请先登录'}), 401
            else:
                flash('请先登录', 'warning')
                return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.is_active:
            if request.is_json:
                return jsonify({'success': False, 'message': '账户已被禁用'}), 403
            else:
                flash('您的账户已被禁用，请联系管理员', 'error')
                return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission):
    """权限检查装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'success': False, 'message': '请先登录'}), 401
                else:
                    flash('请先登录', 'warning')
                    return redirect(url_for('auth.login', next=request.url))
            
            # 这里可以根据需要扩展权限系统
            if not current_user.is_admin:
                if request.is_json:
                    return jsonify({'success': False, 'message': '权限不足'}), 403
                else:
                    abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator