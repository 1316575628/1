#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
班次管理表单
确保中文字符编码正确处理
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TimeField, TextAreaField, SubmitField, ColorField
from wtforms.validators import DataRequired, Length, ValidationError
from datetime import datetime

class ShiftTypeForm(FlaskForm):
    """班次类型表单"""
    name = StringField('班次名称', validators=[
        DataRequired(message='班次名称不能为空'),
        Length(min=1, max=50, message='班次名称长度必须在1-50个字符之间')
    ], render_kw={'class': 'form-control', 'placeholder': '请输入班次名称'})
    
    start_time = TimeField('开始时间', validators=[
        DataRequired(message='开始时间不能为空')
    ], render_kw={'class': 'form-control'})
    
    end_time = TimeField('结束时间', validators=[
        DataRequired(message='结束时间不能为空')
    ], render_kw={'class': 'form-control'})
    
    color = ColorField('显示颜色', render_kw={'class': 'form-control form-control-color'})
    
    description = TextAreaField('班次描述', validators=[
        Length(max=500, message='描述长度不能超过500个字符')
    ], render_kw={'class': 'form-control', 'rows': 3, 'placeholder': '请输入班次描述（可选）'})
    
    submit = SubmitField('保存', render_kw={'class': 'btn btn-primary'})
    
    def validate_end_time(self, end_time):
        """验证结束时间必须晚于开始时间"""
        if self.start_time.data and end_time.data:
            if end_time.data <= self.start_time.data:
                raise ValidationError('结束时间必须晚于开始时间')
    
    def validate_name(self, name):
        """验证班次名称格式"""
        # 检查是否包含特殊字符
        import re
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9\-_]+$', name.data):
            raise ValidationError('班次名称只能包含中文、字母、数字、下划线和短横线')
        
        # 检查长度（中文字符计为2个字符）
        length = sum(2 if ord(char) > 127 else 1 for char in name.data)
        if length > 50:
            raise ValidationError('班次名称长度不能超过50个字符（中文字符计为2个）')