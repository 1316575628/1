#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户认证路由
确保中文字符编码正确处理
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from datetime import datetime
from ..models import db, User, SystemLog
from ..forms.auth import LoginForm, ChangePasswordForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def log_user_action(action, message, level='INFO'):
    """记录用户操作日志"""
    try:
        log = SystemLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            log_type='auth',
            log_level=level,
            message=message,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:200]
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        # 日志记录失败不应影响主要功能
        pass

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            # 查找用户
            user = User.query.filter_by(username=form.username.data).first()
            
            if user and user.check_password(form.password.data):
                if not user.is_active:
                    flash('账户已被禁用，请联系管理员', 'error')
                    log_user_action('login_failed', f'用户 {form.username.data} 尝试登录但被禁用', 'WARNING')
                    return render_template('auth/login.html', form=form)
                
                # 登录用户
                login_user(user, remember=form.remember_me.data)
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                # 记录登录日志
                log_user_action('login_success', f'用户 {user.username} 登录成功')
                
                # 重定向到原始页面或首页
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('main.index')
                
                flash('登录成功！', 'success')
                return redirect(next_page)
            else:
                flash('用户名或密码错误', 'error')
                log_user_action('login_failed', f'用户 {form.username.data} 登录失败：密码错误', 'WARNING')
        except Exception as e:
            flash('登录过程中发生错误，请稍后重试', 'error')
            log_user_action('login_error', f'用户 {form.username.data} 登录时发生错误: {str(e)}', 'ERROR')
    
    return render_template('auth/login.html', form=form, title='登录')

@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    try:
        username = current_user.username
        logout_user()
        log_user_action('logout', f'用户 {username} 登出成功')
        flash('您已成功登出', 'success')
    except Exception as e:
        flash('登出过程中发生错误', 'error')
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """修改密码"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        try:
            if not current_user.check_password(form.old_password.data):
                flash('当前密码错误', 'error')
                return render_template('auth/change_password.html', form=form, title='修改密码')
            
            # 更新密码
            current_user.set_password(form.new_password.data)
            db.session.commit()
            
            flash('密码修改成功，请重新登录', 'success')
            log_user_action('change_password', f'用户 {current_user.username} 修改密码成功')
            
            # 强制重新登录
            logout_user()
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('密码修改失败，请稍后重试', 'error')
            log_user_action('change_password_error', f'用户 {current_user.username} 修改密码失败: {str(e)}', 'ERROR')
    
    return render_template('auth/change_password.html', form=form, title='修改密码')

@auth_bp.route('/profile')
@login_required
def profile():
    """用户个人资料"""
    return render_template('auth/profile.html', user=current_user, title='个人资料')

@auth_bp.route('/api/check-auth')
def check_auth():
    """API接口：检查认证状态"""
    return jsonify({
        'authenticated': current_user.is_authenticated,
        'user': current_user.to_dict() if current_user.is_authenticated else None
    })