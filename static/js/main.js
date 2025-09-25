/**
 * 钉钉打卡提醒系统主要JavaScript文件
 * 确保中文字符编码正确处理
 */

// 全局配置
const CONFIG = {
    API_BASE_URL: '',
    TIMEZONE: 'Asia/Shanghai',
    LOCALE: 'zh-CN',
    DATE_FORMAT: 'YYYY-MM-DD',
    TIME_FORMAT: 'HH:mm:ss'
};

// 工具函数
const Utils = {
    // 格式化日期
    formatDate: function(date, format = 'YYYY-MM-DD') {
        if (!date) return '';
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        const seconds = String(d.getSeconds()).padStart(2, '0');
        
        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day)
            .replace('HH', hours)
            .replace('mm', minutes)
            .replace('ss', seconds);
    },
    
    // 格式化时间
    formatTime: function(date) {
        if (!date) return '';
        return new Date(date).toLocaleTimeString('zh-CN');
    },
    
    // 显示友好时间
    formatRelativeTime: function(date) {
        const now = new Date();
        const target = new Date(date);
        const diff = now - target;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return '刚刚';
        if (minutes < 60) return `${minutes}分钟前`;
        if (hours < 24) return `${hours}小时前`;
        if (days < 7) return `${days}天前`;
        return this.formatDate(date);
    },
    
    // 显示加载状态
    showLoading: function(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        if (element) {
            element.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">加载中...</span></div><p class="mt-2 text-muted">加载中...</p></div>';
        }
    },
    
    // 显示错误信息
    showError: function(element, message) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        if (element) {
            element.innerHTML = `<div class="text-center py-4 text-danger"><i class="bi bi-exclamation-triangle-fill" style="font-size: 2rem;"></i><p class="mt-2">${message}</p></div>`;
        }
    },
    
    // 显示成功消息
    showSuccess: function(message, duration = 3000) {
        this.showToast(message, 'success', duration);
    },
    
    // 显示错误消息
    showErrorToast: function(message, duration = 5000) {
        this.showToast(message, 'danger', duration);
    },
    
    // 显示提示消息
    showToast: function(message, type = 'info', duration = 3000) {
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        // 创建toast容器
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(container);
        }
        
        container.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { delay: duration });
        toast.show();
        
        // 自动移除
        setTimeout(() => {
            if (toastElement && toastElement.parentNode) {
                toastElement.parentNode.removeChild(toastElement);
            }
        }, duration + 1000);
    },
    
    // 确认对话框
    confirm: function(message, callback) {
        const modalId = 'confirm-modal-' + Date.now();
        const modalHtml = `
            <div class="modal fade" id="${modalId}" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">确认操作</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>${message}</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-primary" id="confirm-btn">确认</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        const modal = new bootstrap.Modal(document.getElementById(modalId));
        const confirmBtn = document.getElementById('confirm-btn');
        
        confirmBtn.addEventListener('click', () => {
            callback(true);
            modal.hide();
        });
        
        document.getElementById(modalId).addEventListener('hidden.bs.modal', () => {
            document.getElementById(modalId).remove();
        });
        
        modal.show();
    },
    
    // AJAX请求
    request: function(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        };
        
        const config = Object.assign(defaultOptions, options);
        
        return fetch(url, config)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .catch(error => {
                console.error('Request failed:', error);
                throw error;
            });
    }
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 初始化弹出框
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // 自动隐藏警告框
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // 表单验证增强
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // 表格行悬停效果
    const tableRows = document.querySelectorAll('.table-hover tbody tr');
    tableRows.forEach(function(row) {
        row.addEventListener('mouseenter', function() {
            this.style.cursor = 'pointer';
        });
    });
    
    // 全局错误处理
    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
        Utils.showErrorToast('页面发生错误，请刷新页面重试');
    });
    
    // 全局未处理的Promise拒绝
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        Utils.showErrorToast('操作失败，请稍后重试');
    });
});

// 导出到全局
window.Utils = Utils;
window.CONFIG = CONFIG;