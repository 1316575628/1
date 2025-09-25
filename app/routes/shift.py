#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
班次管理路由
确保中文字符编码正确处理
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models import db, ShiftType, SystemLog
from ..forms.shift import ShiftTypeForm
from ..utils.decorators import admin_required

shift_bp = Blueprint('shift', __name__, url_prefix='/shift')

def log_shift_action(action, message, level='INFO'):
    """记录班次操作日志"""
    try:
        log = SystemLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            log_type='shift',
            log_level=level,
            message=message,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:200]
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        pass

@shift_bp.route('/')
@login_required
def index():
    """班次管理首页"""
    return render_template('shift/index.html', title='班次管理')

@shift_bp.route('/list')
@login_required
def list_shifts():
    """获取班次列表"""
    try:
        shifts = ShiftType.query.filter_by(is_active=True).order_by(ShiftType.name).all()
        return jsonify({
            'success': True,
            'data': [shift.to_dict() for shift in shifts]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取班次列表失败: {str(e)}'
        })

@shift_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """创建班次"""
    form = ShiftTypeForm()
    
    if form.validate_on_submit():
        try:
            # 检查班次名称是否已存在
            existing = ShiftType.query.filter_by(name=form.name.data).first()
            if existing:
                flash('该班次名称已存在', 'error')
                return render_template('shift/create.html', form=form, title='创建班次')
            
            # 创建新班次
            shift = ShiftType(
                name=form.name.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                color=form.color.data,
                description=form.description.data
            )
            
            db.session.add(shift)
            db.session.commit()
            
            flash('班次创建成功', 'success')
            log_shift_action('create_shift', f'用户 {current_user.username} 创建班次: {shift.name}')
            
            return redirect(url_for('shift.index'))
        except Exception as e:
            db.session.rollback()
            flash('班次创建失败，请稍后重试', 'error')
            log_shift_action('create_shift_error', f'用户 {current_user.username} 创建班次失败: {str(e)}', 'ERROR')
    
    return render_template('shift/create.html', form=form, title='创建班次')

@shift_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    """编辑班次"""
    shift = ShiftType.query.get_or_404(id)
    form = ShiftTypeForm(obj=shift)
    
    if form.validate_on_submit():
        try:
            # 检查班次名称是否已存在（排除当前班次）
            existing = ShiftType.query.filter(
                ShiftType.name == form.name.data,
                ShiftType.id != id
            ).first()
            
            if existing:
                flash('该班次名称已存在', 'error')
                return render_template('shift/edit.html', form=form, shift=shift, title='编辑班次')
            
            # 更新班次信息
            shift.name = form.name.data
            shift.start_time = form.start_time.data
            shift.end_time = form.end_time.data
            shift.color = form.color.data
            shift.description = form.description.data
            
            db.session.commit()
            
            flash('班次更新成功', 'success')
            log_shift_action('update_shift', f'用户 {current_user.username} 更新班次: {shift.name}')
            
            return redirect(url_for('shift.index'))
        except Exception as e:
            db.session.rollback()
            flash('班次更新失败，请稍后重试', 'error')
            log_shift_action('update_shift_error', f'用户 {current_user.username} 更新班次失败: {str(e)}', 'ERROR')
    
    return render_template('shift/edit.html', form=form, shift=shift, title='编辑班次')

@shift_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    """删除班次"""
    try:
        shift = ShiftType.query.get_or_404(id)
        shift_name = shift.name
        
        # 软删除，将is_active设置为False
        shift.is_active = False
        db.session.commit()
        
        flash('班次删除成功', 'success')
        log_shift_action('delete_shift', f'用户 {current_user.username} 删除班次: {shift_name}')
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除班次失败: {str(e)}'})

@shift_bp.route('/<int:id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_status(id):
    """切换班次状态"""
    try:
        shift = ShiftType.query.get_or_404(id)
        shift.is_active = not shift.is_active
        db.session.commit()
        
        status = '启用' if shift.is_active else '禁用'
        log_shift_action('toggle_shift_status', f'用户 {current_user.username} {status}班次: {shift.name}')
        
        return jsonify({
            'success': True,
            'data': {
                'id': shift.id,
                'is_active': shift.is_active
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'切换班次状态失败: {str(e)}'
        })