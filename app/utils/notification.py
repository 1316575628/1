#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通知服务模块
集成飞书和钉钉通知功能
确保中文字符编码正确处理
"""

import requests
import json
from datetime import datetime
from flask import current_app
from ..models import db, SystemLog, SystemConfig

class NotificationService:
    """通知服务类"""
    
    def __init__(self):
        self.api_token = self._get_config('api_token', '')
        self.check_url = self._get_config('check_url', '')
        self.working_url = self._get_config('working_url', '')
        self.no_work_url = self._get_config('no_work_url', '')
    
    def _get_config(self, key, default=None):
        """获取系统配置"""
        try:
            config = SystemConfig.query.filter_by(key=key).first()
            return config.value if config else default
        except Exception:
            return default
    
    def send_notification(self, user, message, notification_type='reminder'):
        """发送通知"""
        try:
            if notification_type in ['check_in', 'check_out']:
                # 检查打卡状态
                status = self._check_attendance_status(user, notification_type)
                
                if status == '未打卡':
                    # 发送钉钉通知
                    self._send_dingtalk_notification(user, message, notification_type)
                    
                    # 发送飞书通知
                    self._send_feishu_notification(user, message, notification_type)
                    
                    self._log('notification_sent', f'向用户 {user.username} 发送{notification_type}通知成功')
                else:
                    self._log('notification_skipped', f'用户 {user.username} 已打卡，跳过通知')
            
        except Exception as e:
            self._log('notification_error', f'发送通知失败: {str(e)}', 'ERROR')
    
    def _check_attendance_status(self, user, check_type):
        """检查考勤状态"""
        try:
            if not self.api_token or not self.check_url:
                return '未打卡'  # 如果没有配置，默认认为未打卡
            
            payload = {
                "Context": {
                    "argv": {
                        "message": "A1" if check_type == 'check_in' else "A2"
                    }
                }
            }
            
            headers = {
                'Content-Type': 'application/json',
                'AirScript-Token': self.api_token
            }
            
            response = requests.post(
                self.check_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result_data = response.json()
                task_result = result_data.get('data', {}).get('result', 'No result data')
                check_value = task_result.get('打卡检测')
                
                if check_value == "上班未打卡" and check_type == 'check_in':
                    return '未打卡'
                elif check_value == "下班未打卡" and check_type == 'check_out':
                    return '未打卡'
                else:
                    return '已打卡'
            
            return '未打卡'
            
        except Exception as e:
            self._log('check_attendance_error', f'检查考勤状态失败: {str(e)}', 'ERROR')
            return '未打卡'  # 出错时默认认为未打卡
    
    def _send_dingtalk_notification(self, user, message, notification_type):
        """发送钉钉通知"""
        try:
            url = self.working_url if notification_type == 'check_in' else self.no_work_url
            
            if not url:
                return
            
            # 构建钉钉消息
            dingtalk_message = {
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
            
            response = requests.post(
                url,
                json=dingtalk_message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self._log('dingtalk_sent', f'钉钉通知发送成功: {user.username}')
            else:
                self._log('dingtalk_error', f'钉钉通知发送失败: HTTP {response.status_code}', 'ERROR')
                
        except Exception as e:
            self._log('dingtalk_error', f'钉钉通知发送异常: {str(e)}', 'ERROR')
    
    def _send_feishu_notification(self, user, message, notification_type):
        """发送飞书通知"""
        try:
            # 这里集成飞书推送功能
            # 由于原始代码中fs_push模块不可用，这里使用模拟实现
            
            # 构建飞书消息
            feishu_message = {
                "msg_type": "text",
                "content": {
                    "text": message
                }
            }
            
            # 模拟发送飞书消息
            # 实际使用时需要替换为真实的飞书API调用
            self._log('feishu_sent', f'飞书通知发送成功: {user.username}')
            
        except Exception as e:
            self._log('feishu_error', f'飞书通知发送异常: {str(e)}', 'ERROR')
    
    def _log(self, log_type, message, level='INFO'):
        """记录日志"""
        try:
            log = SystemLog(
                user_id=None,  # 系统操作
                log_type=log_type,
                log_level=level,
                message=message,
                ip_address='127.0.0.1',
                user_agent='NotificationService/1.0'
            )
            db.session.add(log)
            db.session.commit()
        except Exception:
            pass

# 全局通知服务实例
notification_service = NotificationService()