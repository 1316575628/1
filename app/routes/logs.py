#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理路由
确保中文字符编码正确处理
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from ..models import db, SystemLog, AttendanceRecord
from ..utils.decorators import admin_required

logs_bp = Blueprint('logs', __name__, url_prefix='/logs')

@logs_bp.route('/system')
@login_required
@admin_required
def system_logs():
    """系统日志页面"""
    return render_template('logs/system.html', title='系统日志')

@logs_bp.route('/system/list')
@login_required
@admin_required
def list_system_logs():
    """获取系统日志列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        log_type = request.args.get('log_type', '')
        log_level = request.args.get('log_level', '')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询
        query = SystemLog.query
        
        # 过滤条件
        if log_type:
            query = query.filter_by(log_type=log_type)
        
        if log_level:
            query = query.filter_by(log_level=log_level)
        
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(SystemLog.created_at >= start_date_obj)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(SystemLog.created_at < end_date_obj)
            except ValueError:
                pass
        
        # 排序和分页
        logs = query.order_by(SystemLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False)
        
        # 转换为JSON格式
        data = {
            'logs': [log.to_dict() for log in logs.items],
            'pagination': {
                'page': logs.page,
                'pages': logs.pages,
                'per_page': logs.per_page,
                'total': logs.total,
                'has_prev': logs.has_prev,
                'has_next': logs.has_next,
                'prev_num': logs.prev_num,
                'next_num': logs.next_num
            }
        }
        
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取系统日志失败: {str(e)}'})

@logs_bp.route('/attendance')
@login_required
@admin_required
def attendance_logs():
    """考勤日志页面"""
    return render_template('logs/attendance.html', title='考勤日志')

@logs_bp.route('/attendance/list')
@login_required
@admin_required
def list_attendance_logs():
    """获取考勤日志列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        user_id = request.args.get('user_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询
        query = AttendanceRecord.query
        
        # 过滤条件
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(AttendanceRecord.work_date >= start_date_obj)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(AttendanceRecord.work_date <= end_date_obj)
            except ValueError:
                pass
        
        # 排序和分页
        records = query.order_by(AttendanceRecord.work_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False)
        
        # 转换为JSON格式
        data = {
            'records': [record.to_dict() for record in records.items],
            'pagination': {
                'page': records.page,
                'pages': records.pages,
                'per_page': records.per_page,
                'total': records.total,
                'has_prev': records.has_prev,
                'has_next': records.has_next,
                'prev_num': records.prev_num,
                'next_num': records.next_num
            }
        }
        
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取考勤日志失败: {str(e)}'})

@logs_bp.route('/statistics')
@login_required
@admin_required
def statistics():
    """日志统计页面"""
    try:
        # 获取统计信息
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        this_month = today.replace(day=1)
        
        # 今日日志统计
        today_logs = SystemLog.query.filter(
            SystemLog.created_at >= datetime.combine(today, datetime.min.time()),
            SystemLog.created_at < datetime.combine(today + timedelta(days=1), datetime.min.time())
        )
        
        today_error_count = today_logs.filter_by(log_level='ERROR').count()
        today_warning_count = today_logs.filter_by(log_level='WARNING').count()
        today_info_count = today_logs.filter_by(log_level='INFO').count()
        
        # 日志类型统计
        log_types = db.session.query(
            SystemLog.log_type,
            db.func.count(SystemLog.id).label('count')
        ).group_by(SystemLog.log_type).all()
        
        # 考勤统计
        this_month_attendance = AttendanceRecord.query.filter(
            AttendanceRecord.work_date >= this_month,
            AttendanceRecord.work_date <= today
        )
        
        total_work_days = this_month_attendance.count()
        clocked_in_count = this_month_attendance.filter(
            AttendanceRecord.clock_in_status == '已打卡'
        ).count()
        not_clocked_in_count = this_month_attendance.filter(
            AttendanceRecord.clock_in_status == '未打卡'
        ).count()
        
        stats = {
            'today': {
                'total': today_logs.count(),
                'errors': today_error_count,
                'warnings': today_warning_count,
                'info': today_info_count
            },
            'log_types': [{'type': t[0], 'count': t[1]} for t in log_types],
            'attendance': {
                'total_days': total_work_days,
                'clocked_in': clocked_in_count,
                'not_clocked_in': not_clocked_in_count,
                'attendance_rate': round((clocked_in_count / total_work_days * 100) if total_work_days > 0 else 0, 2)
            }
        }
        
        return render_template('logs/statistics.html', 
                             title='日志统计',
                             statistics=stats)
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取统计信息失败: {str(e)}'})