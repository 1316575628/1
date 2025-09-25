#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户认证表单
确保中文字符编码正确处理
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from ..models import User

class LoginForm(FlaskForm):
    """登录表单"""
    username = StringField('用户名', validators=[
        DataRequired(message='用户名不能为空'),
        Length(min=3, max=20, message='用户名长度必须在3-20个字符之间')
    ], render_kw={'placeholder': '请输入用户名', 'class': 'form-control'})
    
    password = PasswordField('密码', validators=[
        DataRequired(message='密码不能为空'),
        Length(min=6, max=128, message='密码长度必须在6-128个字符之间')
    ], render_kw={'placeholder': '请输入密码', 'class': 'form-control'})
    
    remember_me = BooleanField('记住我', default=False)
    
    submit = SubmitField('登录', render_kw={'class': 'btn btn-primary btn-block'})

class ChangePasswordForm(FlaskForm):
    """修改密码表单"""
    old_password = PasswordField('当前密码', validators=[
        DataRequired(message='当前密码不能为空')
    ], render_kw={'placeholder': '请输入当前密码', 'class': 'form-control'})
    
    new_password = PasswordField('新密码', validators=[
        DataRequired(message='新密码不能为空'),
        Length(min=6, max=128, message='密码长度必须在6-128个字符之间')
    ], render_kw={'placeholder': '请输入新密码', 'class': 'form-control'})
    
    confirm_password = PasswordField('确认新密码', validators=[
        DataRequired(message='确认密码不能为空'),
        EqualTo('new_password', message='两次输入的密码不一致')
    ], render_kw={'placeholder': '请再次输入新密码', 'class': 'form-control'})
    
    submit = SubmitField('修改密码', render_kw={'class': 'btn btn-primary'})

class UserForm(FlaskForm):
    """用户管理表单"""
    username = StringField('用户名', validators=[
        DataRequired(message='用户名不能为空'),
        Length(min=3, max=20, message='用户名长度必须在3-20个字符之间')
    ], render_kw={'class': 'form-control'})
    
    email = StringField('邮箱', validators=[
        Email(message='请输入有效的邮箱地址'),
        Length(max=120, message='邮箱长度不能超过120个字符')
    ], render_kw={'class': 'form-control'})
    
    password = PasswordField('密码', validators=[
        Length(min=6, max=128, message='密码长度必须在6-128个字符之间')
    ], render_kw={'class': 'form-control', 'placeholder': '留空则不修改密码'})
    
    is_admin = BooleanField('管理员权限', default=False)
    is_active = BooleanField('启用账户', default=True)
    
    submit = SubmitField('保存', render_kw={'class': 'btn btn-primary'})
    
    def __init__(self, original_username=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
    
    def validate_username(self, username):
        """验证用户名唯一性"""
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('该用户名已被使用，请选择其他用户名')
    
    def validate_email(self, email):
        """验证邮箱唯一性"""
        if email.data:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('该邮箱已被使用，请选择其他邮箱')