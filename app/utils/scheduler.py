#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务调度服务
确保中文字符编码正确处理
"""

import threading
import time
from datetime import datetime, timedelta, date
from flask import current_app
from ..models import db, Schedule, ShiftType, AttendanceRecord, SystemLog, SystemConfig, User
from ..utils.notification import NotificationService

class SchedulerService:
    """定时任务调度服务"""
    
    _instance = None
    _running = False
    _thread = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SchedulerService, cls).__new__(cls)
        return cls._instance
    
    def start(self):
        """启动定时任务"""
        with self._lock:
            if not self._running:
                self._running = True
                self._thread = threading.Thread(target=self._run, daemon=True)
                self._thread.start()
                self._log('scheduler_started', '定时任务调度器已启动')
    
    def stop(self):
        """停止定时任务"""
        with self._lock:
            if self._running:
                self._running = False
                self._log('scheduler_stopped', '定时任务调度器已停止')
    
    def get_status(self):
        """获取调度器状态"""
        return {
            'running': self._running,
            'thread_alive': self._thread.is_alive() if self._thread else False,
            'last_check': getattr(self, '_last_check', None)
        }
    
    def _run(self):
        """主运行循环"""
        while self._running:
            try:
                # 每分钟检查一次
                if datetime.now().second == 0:
                    self._check_schedules()
                    self._last_check = datetime.now()
                
                time.sleep(1)  # 每秒检查一次是否需要执行任务
            except Exception as e:
                self._log('scheduler_error', f'调度器运行错误: {str(e)}', 'ERROR')
                time.sleep(60)  # 出错后等待1分钟再试
    
    def _check_schedules(self):
        """检查排班并执行相应操作"""
        try:
            now = datetime.now()
            today = now.date()
            current_time = now.time()
            
            # 获取今日所有排班
            today_schedules = Schedule.query.filter_by(work_date=today).all()
            
            for schedule in today_schedules:
                if schedule.is_rest_day:
                    continue
                
                if not schedule.shift_type:
                    continue
                
                shift = schedule.shift_type
                user = schedule.user
                
                if not user or not user.is_active:
                    continue
                
                # 获取系统配置
                overtime_minutes = self._get_system_config('work_overtime', 0)
                reminder_enabled = self._get_system_config('reminder_enabled', 'true') == 'true'
                
                if not reminder_enabled:
                    continue
                
                # 计算时间
                start_time = datetime.strptime(shift.start_time, '%H:%M').time()
                end_time = datetime.strptime(shift.end_time, '%H:%M').time()
                
                # 上班前15分钟
                start_datetime = datetime.combine(today, start_time)
                check_in_start = (start_datetime - timedelta(minutes=15)).time()
                
                # 下班后30分钟（包含加班时间）
                end_datetime = datetime.combine(today, end_time)
                end_datetime += timedelta(minutes=int(overtime_minutes))
                check_out_end = (end_datetime + timedelta(minutes=30)).time()
                
                # 获取或创建考勤记录
                attendance = AttendanceRecord.query.filter_by(
                    user_id=user.id,
                    work_date=today
                ).first()
                
                if not attendance:
                    attendance = AttendanceRecord(
                        user_id=user.id,
                        work_date=today,
                        shift_type_id=shift.id
                    )
                    db.session.add(attendance)
                    db.session.commit()
                
                # 检查上班打卡提醒
                if (check_in_start <= current_time < start_time and 
                    attendance.clock_in_status == '未打卡' and 
                    not attendance.clock_in_reminded):
                    
                    self._send_check_in_reminder(user, shift, schedule)
                    attendance.clock_in_reminded = True
                    db.session.commit()
                
                # 检查下班打卡提醒
                elif (end_datetime.time() <= current_time <= check_out_end and 
                      attendance.clock_out_status == '未打卡' and 
                      not attendance.clock_out_reminded):
                    
                    self._send_check_out_reminder(user, shift, schedule)
                    attendance.clock_out_reminded = True
                    db.session.commit()
                
        except Exception as e:
            self._log('check_schedules_error', f'检查排班时发生错误: {str(e)}', 'ERROR')
            db.session.rollback()
    
    def _send_check_in_reminder(self, user, shift, schedule):
        """发送上班打卡提醒"""
        try:
            message = f"【上班提醒】{user.username}，您好！您今天{shift.name}的上班时间是{shift.start_time}，请记得按时打卡。"
            
            notification_service = NotificationService()
            notification_service.send_notification(user, message, 'check_in')
            
            self._log('check_in_reminder_sent', f'向用户 {user.username} 发送上班打卡提醒')
            
        except Exception as e:
            self._log('check_in_reminder_error', f'发送上班提醒失败: {str(e)}', 'ERROR')
    
    def _send_check_out_reminder(self, user, shift, schedule):
        """发送下班打卡提醒"""
        try:
            message = f"【下班提醒】{user.username}，您好！您今天{shift.name}的下班时间是{shift.end_time}，请记得按时打卡。"
            
            notification_service = NotificationService()
            notification_service.send_notification(user, message, 'check_out')
            
            self._log('check_out_reminder_sent', f'向用户 {user.username} 发送下班打卡提醒')
            
        except Exception as e:
            self._log('check_out_reminder_error', f'发送下班提醒失败: {str(e)}', 'ERROR')
    
    def _get_system_config(self, key, default=None):
        """获取系统配置"""
        try:
            config = SystemConfig.query.filter_by(key=key).first()
            return config.value if config else default
        except Exception:
            return default
    
    def _log(self, log_type, message, level='INFO'):
        """记录日志"""
        try:
            log = SystemLog(
                user_id=None,  # 系统操作
                log_type=log_type,
                log_level=level,
                message=message,
                ip_address='127.0.0.1',
                user_agent='SchedulerService/1.0'
            )
            db.session.add(log)
            db.session.commit()
        except Exception:
            pass

# 全局调度器实例
scheduler = SchedulerService()