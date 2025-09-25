#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
排班管理路由
确保中文字符编码正确处理
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from ..models import db, Schedule, ShiftType, User, SystemLog
from ..forms.schedule import ScheduleForm, BatchScheduleForm
from ..utils.decorators import admin_required

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

def log_schedule_action(action, message, level='INFO'):
    """记录排班操作日志"""
    try:
        log = SystemLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            log_type='schedule',
            log_level=level,
            message=message,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:200]
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        pass

@schedule_bp.route('/')
@login_required
def index():
    """排班管理首页"""
    return render_template('schedule/index.html', title='排班管理')

@schedule_bp.route('/list')
@login_required
def list_schedules():
    """获取排班列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        user_id = request.args.get('user_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询
        query = Schedule.query
        
        # 过滤条件
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Schedule.work_date >= start_date_obj)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Schedule.work_date <= end_date_obj)
            except ValueError:
                pass
        
        # 排序和分页
        schedules = query.order_by(Schedule.work_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False)
        
        # 转换为JSON格式
        data = {
            'schedules': [schedule.to_dict() for schedule in schedules.items],
            'pagination': {
                'page': schedules.page,
                'pages': schedules.pages,
                'per_page': schedules.per_page,
                'total': schedules.total,
                'has_prev': schedules.has_prev,
                'has_next': schedules.has_next,
                'prev_num': schedules.prev_num,
                'next_num': schedules.next_num
            }
        }
        
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取排班列表失败: {str(e)}'})

@schedule_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """创建排班"""
    form = ScheduleForm()
    
    if form.validate_on_submit():
        try:
            # 检查是否已存在该日期的排班
            existing = Schedule.query.filter_by(
                user_id=form.user_id.data,
                work_date=form.work_date.data
            ).first()
            
            if existing:
                flash('该日期已存在排班记录', 'error')
                return render_template('schedule/create.html', form=form, title='创建排班')
            
            # 创建新排班
            schedule = Schedule(
                user_id=form.user_id.data,
                work_date=form.work_date.data,
                shift_type_id=form.shift_type_id.data if not form.is_rest_day.data else None,
                is_rest_day=form.is_rest_day.data,
                note=form.note.data
            )
            
            db.session.add(schedule)
            db.session.commit()
            
            flash('排班创建成功', 'success')
            log_schedule_action('create_schedule', f'用户 {current_user.username} 创建排班: {schedule.work_date}')
            
            return redirect(url_for('schedule.index'))
        except Exception as e:
            db.session.rollback()
            flash('排班创建失败，请稍后重试', 'error')
            log_schedule_action('create_schedule_error', f'用户 {current_user.username} 创建排班失败: {str(e)}', 'ERROR')
    
    return render_template('schedule/create.html', form=form, title='创建排班')

@schedule_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """编辑排班"""
    schedule = Schedule.query.get_or_404(id)
    form = ScheduleForm(obj=schedule)
    
    if form.validate_on_submit():
        try:
            # 更新排班信息
            schedule.user_id = form.user_id.data
            schedule.work_date = form.work_date.data
            schedule.shift_type_id = form.shift_type_id.data if not form.is_rest_day.data else None
            schedule.is_rest_day = form.is_rest_day.data
            schedule.note = form.note.data
            
            db.session.commit()
            
            flash('排班更新成功', 'success')
            log_schedule_action('update_schedule', f'用户 {current_user.username} 更新排班: {schedule.work_date}')
            
            return redirect(url_for('schedule.index'))
        except Exception as e:
            db.session.rollback()
            flash('排班更新失败，请稍后重试', 'error')
            log_schedule_action('update_schedule_error', f'用户 {current_user.username} 更新排班失败: {str(e)}', 'ERROR')
    
    return render_template('schedule/edit.html', form=form, schedule=schedule, title='编辑排班')

@schedule_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """删除排班"""
    try:
        schedule = Schedule.query.get_or_404(id)
        work_date = schedule.work_date
        
        db.session.delete(schedule)
        db.session.commit()
        
        flash('排班删除成功', 'success')
        log_schedule_action('delete_schedule', f'用户 {current_user.username} 删除排班: {work_date}')
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除排班失败: {str(e)}'})

@schedule_bp.route('/batch-create', methods=['GET', 'POST'])
@login_required
@admin_required
def batch_create():
    """批量创建排班"""
    form = BatchScheduleForm()
    
    if form.validate_on_submit():
        try:
            created_count = 0
            start_date = form.start_date.data
            end_date = form.end_date.data
            
            # 计算日期范围
            current_date = start_date
            while current_date <= end_date:
                # 检查是否已存在排班
                existing = Schedule.query.filter_by(
                    user_id=form.user_id.data,
                    work_date=current_date
                ).first()
                
                if not existing:
                    # 判断是否为工作日
                    is_work_day = current_date.weekday() < 5  # 周一到周五为工作日
                    
                    if is_work_day or not form.skip_weekends.data:
                        schedule = Schedule(
                            user_id=form.user_id.data,
                            work_date=current_date,
                            shift_type_id=form.shift_type_id.data if is_work_day else None,
                            is_rest_day=not is_work_day
                        )
                        db.session.add(schedule)
                        created_count += 1
                
                current_date += timedelta(days=1)
            
            db.session.commit()
            flash(f'批量创建成功，共创建 {created_count} 条排班记录', 'success')
            log_schedule_action('batch_create_schedule', f'用户 {current_user.username} 批量创建排班: {created_count} 条')
            
            return redirect(url_for('schedule.index'))
        except Exception as e:
            db.session.rollback()
            flash('批量创建失败，请稍后重试', 'error')
            log_schedule_action('batch_create_schedule_error', f'用户 {current_user.username} 批量创建排班失败: {str(e)}', 'ERROR')
    
    return render_template('schedule/batch_create.html', form=form, title='批量创建排班')

@schedule_bp.route('/today')
@login_required
def today_schedule():
    """今日排班"""
    try:
        today = datetime.now().date()
        schedules = Schedule.query.filter_by(work_date=today).all()
        
        return render_template('schedule/today.html',
                             schedules=schedules,
                             today=today,
                             title='今日排班')
    except Exception as e:
        flash('获取今日排班失败', 'error')
        return redirect(url_for('schedule.index'))

@schedule_bp.route('/import', methods=['GET', 'POST'])
@login_required
@admin_required
def import_schedule():
    """导入排班数据"""
    if request.method == 'POST':
        try:
            # 这里可以实现Excel或CSV导入功能
            # 暂时返回提示信息
            flash('导入功能开发中，敬请期待', 'info')
            return redirect(url_for('schedule.index'))
        except Exception as e:
            flash('导入失败，请稍后重试', 'error')
    
    return render_template('schedule/import.html', title='导入排班数据')