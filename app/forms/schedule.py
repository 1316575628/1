#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
排班管理表单
确保中文字符编码正确处理
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TextAreaField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Optional, ValidationError
from datetime import date
from ..models import User, ShiftType

class ScheduleForm(FlaskForm):
    """排班表单"""
    user_id = SelectField('用户', coerce=int, validators=[DataRequired(message='请选择用户')])
    work_date = DateField('工作日期', validators=[DataRequired(message='请选择工作日期')])
    shift_type_id = SelectField('班次类型', coerce=int, validators=[Optional()])
    is_rest_day = BooleanField('休息日', default=False)
    note = TextAreaField('备注', validators=[Optional()], render_kw={'rows': 3})
    
    submit = SubmitField('保存', render_kw={'class': 'btn btn-primary'})
    
    def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        # 动态加载用户选项
        self.user_id.choices = [(user.id, user.username) for user in 
                               User.query.filter_by(is_active=True).order_by(User.username).all()]
        self.user_id.choices.insert(0, (0, '请选择用户'))
        
        # 动态加载班次类型选项
        self.shift_type_id.choices = [(shift.id, f"{shift.name} ({shift.start_time}-{shift.end_time})") 
                                     for shift in ShiftType.query.filter_by(is_active=True).order_by(ShiftType.name).all()]
        self.shift_type_id.choices.insert(0, (0, '请选择班次类型'))
    
    def validate_work_date(self, work_date):
        """验证工作日期"""
        if work_date.data < date.today():
            raise ValidationError('工作日期不能早于今天')
    
    def validate(self):
        """自定义验证"""
        if not super(ScheduleForm, self).validate():
            return False
        
        # 检查休息日是否选择了班次类型
        if self.is_rest_day.data and self.shift_type_id.data:
            self.shift_type_id.errors.append('休息日不能选择班次类型')
            return False
        
        # 检查非休息日是否选择了班次类型
        if not self.is_rest_day.data and not self.shift_type_id.data:
            self.shift_type_id.errors.append('非休息日必须选择班次类型')
            return False
        
        return True

class BatchScheduleForm(FlaskForm):
    """批量排班表单"""
    user_id = SelectField('用户', coerce=int, validators=[DataRequired(message='请选择用户')])
    start_date = DateField('开始日期', validators=[DataRequired(message='请选择开始日期')])
    end_date = DateField('结束日期', validators=[DataRequired(message='请选择结束日期')])
    shift_type_id = SelectField('班次类型', coerce=int, validators=[DataRequired(message='请选择班次类型')])
    skip_weekends = BooleanField('跳过周末', default=True, description='是否跳过周六和周日')
    
    submit = SubmitField('批量创建', render_kw={'class': 'btn btn-primary'})
    
    def __init__(self, *args, **kwargs):
        super(BatchScheduleForm, self).__init__(*args, **kwargs)
        # 动态加载用户选项
        self.user_id.choices = [(user.id, user.username) for user in 
                               User.query.filter_by(is_active=True).order_by(User.username).all()]
        self.user_id.choices.insert(0, (0, '请选择用户'))
        
        # 动态加载班次类型选项
        self.shift_type_id.choices = [(shift.id, f"{shift.name} ({shift.start_time}-{shift.end_time})") 
                                     for shift in ShiftType.query.filter_by(is_active=True).order_by(ShiftType.name).all()]
        self.shift_type_id.choices.insert(0, (0, '请选择班次类型'))
    
    def validate_start_date(self, start_date):
        """验证开始日期"""
        if start_date.data < date.today():
            raise ValidationError('开始日期不能早于今天')
    
    def validate_end_date(self, end_date):
        """验证结束日期"""
        if end_date.data < self.start_date.data:
            raise ValidationError('结束日期不能早于开始日期')
        
        # 检查日期范围是否超过一年
        if (end_date.data - self.start_date.data).days > 365:
            raise ValidationError('日期范围不能超过一年')
    
    def validate(self):
        """自定义验证"""
        if not super(BatchScheduleForm, self).validate():
            return False
        
        # 检查日期范围
        if self.start_date.data and self.end_date.data:
            if (self.end_date.data - self.start_date.data).days < 0:
                self.end_date.errors.append('结束日期必须晚于开始日期')
                return False
        
        return True

class ScheduleImportForm(FlaskForm):
    """排班导入表单"""
    file = StringField('文件名', validators=[DataRequired(message='请选择文件')])
    
    submit = SubmitField('导入', render_kw={'class': 'btn btn-primary'})