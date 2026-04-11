/**
 * UI工具函数库
 * 提供通用的UI反馈组件
 */

// Toast通知系统
class Toast {
    static show(message, type = 'info', duration = 3000) {
        // 创建toast容器（如果不存在）
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 350px;
            `;
            document.body.appendChild(container);
        }

        // 创建toast元素
        const toast = document.createElement('div');
        const bgColor = {
            'success': '#28a745',
            'error': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8'
        }[type] || '#17a2b8';

        const icon = {
            'success': 'fa-check-circle',
            'error': 'fa-exclamation-circle',
            'warning': 'fa-exclamation-triangle',
            'info': 'fa-info-circle'
        }[type] || 'fa-info-circle';

        toast.style.cssText = `
            background: ${bgColor};
            color: white;
            padding: 15px 20px;
            margin-bottom: 10px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            align-items: center;
            gap: 10px;
            animation: slideIn 0.3s ease-out;
            cursor: pointer;
        `;

        toast.innerHTML = `
            <i class="fas ${icon}"></i>
            <span style="flex: 1">${this.escapeHtml(message)}</span>
            <i class="fas fa-times" style="opacity: 0.7; font-size: 0.9em;"></i>
        `;

        // 添加点击关闭
        toast.onclick = () => this.dismiss(toast);

        container.appendChild(toast);

        // 自动关闭
        if (duration > 0) {
            setTimeout(() => this.dismiss(toast), duration);
        }

        return toast;
    }

    static dismiss(toast) {
        if (!toast) return;
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // 便捷方法
    static success(message, duration) { return this.show(message, 'success', duration); }
    static error(message, duration) { return this.show(message, 'error', duration); }
    static warning(message, duration) { return this.show(message, 'warning', duration); }
    static info(message, duration) { return this.show(message, 'info', duration); }
}

// 加载指示器
class Loading {
    static show(message = '加载中...', container = null) {
        const loading = document.createElement('div');
        loading.className = 'loading-overlay';
        loading.style.cssText = `
            position: ${container ? 'absolute' : 'fixed'};
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 9998;
            color: white;
            font-size: 16px;
        `;

        loading.innerHTML = `
            <div class="spinner-border text-light mb-3" role="status" style="width: 3rem; height: 3rem;">
                <span class="visually-hidden">加载中...</span>
            </div>
            <div>${this.escapeHtml(message)}</div>
        `;

        if (container) {
            container.style.position = 'relative';
            container.appendChild(loading);
        } else {
            document.body.appendChild(loading);
        }

        return loading;
    }

    static hide(loading) {
        if (loading && loading.parentNode) {
            loading.parentNode.removeChild(loading);
        }
    }

    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// 进度条
class ProgressBar {
    static show(container, message = '处理中...') {
        const progressContainer = document.createElement('div');
        progressContainer.className = 'progress-container';
        progressContainer.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            z-index: 9999;
            min-width: 400px;
        `;

        progressContainer.innerHTML = `
            <div style="text-align: center; margin-bottom: 20px;">
                <i class="fas fa-spinner fa-spin fa-2x text-primary mb-3"></i>
                <div class="progress-message">${this.escapeHtml(message)}</div>
            </div>
            <div class="progress" style="height: 25px; margin-bottom: 10px;">
                <div class="progress-bar progress-bar-striped progress-bar-animated"
                     role="progressbar"
                     style="width: 0%"
                     data-progress="0">
                    0%
                </div>
            </div>
            <div class="progress-details text-muted small text-center"></div>
        `;

        if (container) {
            container.appendChild(progressContainer);
        } else {
            document.body.appendChild(progressContainer);
        }

        return progressContainer;
    }

    static update(progressContainer, percent, message = null) {
        const progressBar = progressContainer.querySelector('.progress-bar');
        const percentText = progressContainer.querySelector('.progress-bar');
        const messageEl = progressContainer.querySelector('.progress-message');
        const detailsEl = progressContainer.querySelector('.progress-details');

        if (progressBar) {
            progressBar.style.width = `${percent}%`;
            progressBar.setAttribute('data-progress', percent);
            progressBar.textContent = `${percent}%`;
        }

        if (message && messageEl) {
            messageEl.textContent = message;
        }

        if (detailsEl) {
            const now = new Date().toLocaleTimeString();
            detailsEl.textContent = `更新时间: ${now}`;
        }
    }

    static hide(progressContainer) {
        if (progressContainer && progressContainer.parentNode) {
            progressContainer.parentNode.removeChild(progressContainer);
        }
    }

    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// 确认对话框
class ConfirmDialog {
    static show(message, title = '确认', onConfirm = null, onCancel = null) {
        const modal = document.createElement('div');
        modal.className = 'confirm-modal-overlay';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        `;

        modal.innerHTML = `
            <div class="confirm-dialog" style="
                background: white;
                border-radius: 12px;
                padding: 30px;
                max-width: 500px;
                width: 90%;
                box-shadow: 0 8px 24px rgba(0,0,0,0.3);
                animation: confirmSlideIn 0.3s ease-out;
            ">
                <div class="confirm-header" style="
                    font-size: 20px;
                    font-weight: 600;
                    margin-bottom: 15px;
                    color: #333;
                ">
                    <i class="fas fa-question-circle text-warning me-2"></i>
                    ${this.escapeHtml(title)}
                </div>
                <div class="confirm-body" style="
                    color: #666;
                    line-height: 1.6;
                    margin-bottom: 25px;
                ">
                    ${this.escapeHtml(message)}
                </div>
                <div class="confirm-footer" style="
                    display: flex;
                    gap: 10px;
                    justify-content: flex-end;
                ">
                    <button class="btn btn-secondary confirm-cancel">取消</button>
                    <button class="btn btn-primary confirm-confirm">确认</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // 绑定事件
        const cancelBtn = modal.querySelector('.confirm-cancel');
        const confirmBtn = modal.querySelector('.confirm-confirm');

        cancelBtn.onclick = () => {
            this.hide(modal);
            if (onCancel) onCancel();
        };

        confirmBtn.onclick = () => {
            this.hide(modal);
            if (onConfirm) onConfirm();
        };

        // 点击背景关闭
        modal.onclick = (e) => {
            if (e.target === modal) {
                this.hide(modal);
                if (onCancel) onCancel();
            }
        };

        return modal;
    }

    static hide(modal) {
        if (modal && modal.parentNode) {
            modal.style.animation = 'confirmSlideOut 0.3s ease-in';
            setTimeout(() => {
                if (modal.parentNode) {
                    modal.parentNode.removeChild(modal);
                }
            }, 300);
        }
    }

    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }

    @keyframes confirmSlideIn {
        from {
            transform: scale(0.9);
            opacity: 0;
        }
        to {
            transform: scale(1);
            opacity: 1;
        }
    }

    @keyframes confirmSlideOut {
        from {
            transform: scale(1);
            opacity: 1;
        }
        to {
            transform: scale(0.9);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// 导出到全局
window.Toast = Toast;
window.Loading = Loading;
window.ProgressBar = ProgressBar;
window.ConfirmDialog = ConfirmDialog;
