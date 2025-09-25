#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由模块
提供RESTful API接口
确保中文字符编码正确处理
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from ..models import db, User, ShiftType, Schedule, SystemConfig
from ..utils.decorators import admin_required
from ..utils.scheduler import scheduler

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/users')
@login_required
def get_users():
    """获取用户列表"""
    try:
        users = User.query.filter_by(is_active=True).order_by(User.username).all()
        return jsonify({
            'success': True,
            'data': [user.to_dict() for user in users]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户列表失败: {str(e)}'
        })

@api_bp.route('/shift-types')
@login_required
def get_shift_types():
    """获取班次类型列表"""
    try:
        shifts = ShiftType.query.filter_by(is_active=True).order_by(ShiftType.name).all()
        return jsonify({
            'success': True,
            'data': [shift.to_dict() for shift in shifts]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取班次类型列表失败: {str(e)}'
        })

@api_bp.route('/config/<key>')
@login_required
@admin_required
def get_config(key):
    """获取系统配置"""
    try:
        config = SystemConfig.query.filter_by(key=key).first()
        if config:
            return jsonify({
                'success': True,
                'data': {
                    'key': config.key,
                    'value': config.value,
                    'description': config.description
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '配置项不存在'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取配置失败: {str(e)}'
        })

@api_bp.route('/config/<key>', methods=['PUT'])
@login_required
@admin_required
def update_config(key):
    """更新系统配置"""
    try:
        data = request.get_json()
        if not data or 'value' not in data:
            return jsonify({
                'success': False,
                'message': '缺少配置值'
            })
        
        config = SystemConfig.query.filter_by(key=key).first()
        if not config:
            return jsonify({
                'success': False,
                'message': '配置项不存在'
            })
        
        config.value = data['value']
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '配置更新成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新配置失败: {str(e)}'
        })

@api_bp.route('/scheduler/status')
@login_required
@admin_required
def get_scheduler_status():
    """获取调度器状态"""
    try:
        status = scheduler.get_status()
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取调度器状态失败: {str(e)}'
        })

@api_bp.route('/scheduler/start', methods=['POST'])
@login_required
@admin_required
def start_scheduler():
    """启动定时任务"""
    try:
        scheduler.start()
        return jsonify({
            'success': True,
            'message': '定时任务已启动'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'启动定时任务失败: {str(e)}'
        })

@api_bp.route('/scheduler/stop', methods=['POST'])
@login_required
@admin_required
def stop_scheduler():
    """停止定时任务"""
    try:
        scheduler.stop()
        return jsonify({
            'success': True,
            'message': '定时任务已停止'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'停止定时任务失败: {str(e)}'
        })

@api_bp.route('/dashboard/stats')
@login_required
def get_dashboard_stats():
    """获取仪表板统计数据"""
    try:
        from datetime import date, datetime, timedelta
        
        today = date.today()
        
        # 今日排班统计
        today_schedules = Schedule.query.filter_by(work_date=today).all()
        work_count = len([s for s in today_schedules if not s.is_rest_day])
        rest_count = len([s for s in today_schedules if s.is_rest_day])
        
        # 考勤统计
        from ..models import AttendanceRecord
        today_attendance = AttendanceRecord.query.filter_by(work_date=today).all()
        clocked_in = len([a for a in today_attendance if a.clock_in_status == '已打卡'])
        not_clocked_in = len([a for a in today_attendance if a.clock_in_status == '未打卡'])
        
        # 最近7天考勤趋势
        week_data = []
        for i in range(7):
            check_date = today - timedelta(days=i)
            day_attendance = AttendanceRecord.query.filter_by(work_date=check_date).all()
            day_schedules = Schedule.query.filter_by(work_date=check_date).all()
            
            week_data.append({
                'date': check_date.strftime('%m-%d'),
                'total': len([s for s in day_schedules if not s.is_rest_day]),
                'clocked_in': len([a for a in day_attendance if a.clock_in_status == '已打卡'])
            })
        
        return jsonify({
            'success': True,
            'data': {
                'today': {
                    'work': work_count,
                    'rest': rest_count,
                    'clocked_in': clocked_in,
                    'not_clocked_in': not_clocked_in
                },
                'week_trend': week_data
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计数据失败: {str(e)}'
        })

@api_bp.route('/test-notification', methods=['POST'])
@login_required
@admin_required
def test_notification():
    """测试通知功能"""
    try:
        from ..utils.notification import notification_service
        
        data = request.get_json()
        message = data.get('message', '测试通知消息')
        notification_type = data.get('type', 'test')
        
        # 发送测试通知
        notification_service.send_notification(
            current_user,
            message,
            notification_type
        )
        
        return jsonify({
            'success': True,
            'message': '测试通知已发送'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'发送测试通知失败: {str(e)}'
        })

@api_bp.route('/health')
def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500