#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主要路由模块
确保中文字符编码正确处理
"""

from flask import Blueprint, render_template, current_app, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from ..models import db, User, Schedule, ShiftType, SystemLog, AttendanceRecord, SystemConfig
from ..utils.scheduler import SchedulerService
from ..utils.notification import NotificationService

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
@login_required
def index():
    """系统首页 - 仪表板"""
    try:
        # 获取统计数据
        total_users = User.query.filter_by(is_active=True).count()
        total_shifts = ShiftType.query.filter_by(is_active=True).count()
        
        # 获取今日排班
        today = datetime.now().date()
        today_schedules = Schedule.query.filter_by(work_date=today).all()
        
        # 获取今日考勤记录
        today_attendance = AttendanceRecord.query.filter_by(work_date=today).all()
        
        # 获取最近的系统日志
        recent_logs = SystemLog.query.order_by(SystemLog.created_at.desc()).limit(10).all()
        
        # 获取本月排班统计
        month_start = today.replace(day=1)
        month_schedules = Schedule.query.filter(
            Schedule.work_date >= month_start,
            Schedule.work_date <= today
        ).all()
        
        # 计算统计数据
        work_days = len([s for s in month_schedules if not s.is_rest_day])
        rest_days = len([s for s in month_schedules if s.is_rest_day])
        
        # 获取提醒状态
        reminder_enabled = SystemConfig.query.filter_by(key='reminder_enabled').first()
        reminder_status = reminder_enabled.value.lower() == 'true' if reminder_enabled else False
        
        return render_template('main/index.html',
                             title='仪表板',
                             total_users=total_users,
                             total_shifts=total_shifts,
                             today_schedules=today_schedules,
                             today_attendance=today_attendance,
                             recent_logs=recent_logs,
                             work_days=work_days,
                             rest_days=rest_days,
                             reminder_status=reminder_status,
                             current_date=today)
    except Exception as e:
        current_app.logger.error(f'仪表板加载错误: {str(e)}')
        return render_template('main/index.html',
                             title='仪表板',
                             error='数据加载失败')

@main_bp.route('/dashboard-data')
@login_required
def dashboard_data():
    """获取仪表板数据（API）"""
    try:
        today = datetime.now().date()
        
        # 获取今日排班统计
        today_schedules = Schedule.query.filter_by(work_date=today).all()
        work_count = len([s for s in today_schedules if not s.is_rest_day])
        rest_count = len([s for s in today_schedules if s.is_rest_day])
        
        # 获取考勤状态统计
        today_attendance = AttendanceRecord.query.filter_by(work_date=today).all()
        clocked_in = len([a for a in today_attendance if a.clock_in_status == '已打卡'])
        not_clocked_in = len([a for a in today_attendance if a.clock_in_status == '未打卡'])
        
        return jsonify({
            'success': True,
            'data': {
                'today_work': work_count,
                'today_rest': rest_count,
                'clocked_in': clocked_in,
                'not_clocked_in': not_clocked_in,
                'total_schedules': len(today_schedules)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取数据失败: {str(e)}'
        })

@main_bp.route('/system-status')
@login_required
def system_status():
    """系统状态检查"""
    try:
        # 检查数据库连接
        db.session.execute('SELECT 1')
        
        # 检查系统配置
        configs = SystemConfig.query.all()
        config_count = len(configs)
        
        # 检查定时任务状态
        scheduler_status = SchedulerService.get_status()
        
        return jsonify({
            'success': True,
            'data': {
                'database': 'connected',
                'configs': config_count,
                'scheduler': scheduler_status,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'系统状态检查失败: {str(e)}'
        })

@main_bp.route('/calendar')
@login_required
def calendar():
    """排班日历视图"""
    return render_template('main/calendar.html', title='排班日历')

@main_bp.route('/calendar-events')
@login_required
def calendar_events():
    """获取日历事件数据"""
    try:
        start_str = request.args.get('start')
        end_str = request.args.get('end')
        
        if not start_str or not end_str:
            return jsonify({'success': False, 'message': '缺少日期参数'})
        
        start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        
        # 获取指定日期范围内的排班
        schedules = Schedule.query.filter(
            Schedule.work_date >= start_date,
            Schedule.work_date <= end_date
        ).all()
        
        events = []
        for schedule in schedules:
            if schedule.is_rest_day:
                events.append({
                    'id': schedule.id,
                    'title': '休息',
                    'start': schedule.work_date.strftime('%Y-%m-%d'),
                    'color': '#95a5a6',
                    'allDay': True,
                    'extendedProps': {
                        'type': 'rest',
                        'user': schedule.user.username if schedule.user else '未知',
                        'note': schedule.note or ''
                    }
                })
            elif schedule.shift_type:
                events.append({
                    'id': schedule.id,
                    'title': f'{schedule.shift_type.name} ({schedule.user.username})',
                    'start': schedule.work_date.strftime('%Y-%m-%d'),
                    'color': schedule.shift_type.color,
                    'allDay': True,
                    'extendedProps': {
                        'type': 'work',
                        'shift_name': schedule.shift_type.name,
                        'start_time': schedule.shift_type.start_time,
                        'end_time': schedule.shift_type.end_time,
                        'user': schedule.user.username if schedule.user else '未知',
                        'note': schedule.note or ''
                    }
                })
        
        return jsonify(events)
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取日历事件失败: {str(e)}'})

@main_bp.route('/about')
@login_required
def about():
    """关于页面"""
    return render_template('main/about.html', 
                         title='关于系统',
                         version=current_app.config.get('APP_VERSION', '1.0.0'))