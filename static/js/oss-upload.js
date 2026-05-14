/**
 * OSS直传上传模块
 *
 * 支持分片上传、断点续传、取消上传。
 * 依赖 ali-oss SDK (通过CDN加载)。
 */
class OSSUploader {
    constructor() {
        this.client = null;
        this.tokenExpiration = null;
        this.activeUploads = {};  // fileId -> { abort: Function }
    }

    /**
     * 初始化OSS客户端（获取STS凭证）
     */
    async initClient() {
        if (this.client && this.tokenExpiration && Date.now() < this.tokenExpiration - 300000) {
            return;  // 客户端有效
        }

        const response = await fetch('/api/upload/sts-token');
        const result = await response.json();

        if (!result.success) {
            throw new Error(result.message || '获取STS凭证失败');
        }

        const data = result.data;
        this.tokenExpiration = new Date(data.expiration).getTime();

        this.client = new OSS({
            region: data.region,
            accessKeyId: data.access_key_id,
            accessKeySecret: data.access_key_secret,
            stsToken: data.security_token,
            bucket: data.bucket,
            refreshSTSToken: async () => {
                const resp = await fetch('/api/upload/sts-token');
                const r = await resp.json();
                if (!r.success) throw new Error('刷新STS凭证失败');
                const d = r.data;
                this.tokenExpiration = new Date(d.expiration).getTime();
                return {
                    accessKeyId: d.access_key_id,
                    accessKeySecret: d.access_key_secret,
                    stsToken: d.security_token
                };
            },
            refreshSTSTokenInterval: 300000
        });
    }

    /**
     * 分片上传文件到OSS
     * @param {Object} fileInfo - { id, file, ... }
     * @param {string} ossPath - OSS存储路径
     * @param {Function} onProgress - 进度回调 (percent: number)
     * @returns {Promise<{success: boolean, url?: string}>}
     */
    async upload(fileInfo, ossPath, onProgress) {
        await this.initClient();

        const checkpoint = this.loadCheckpoint(fileInfo.id);

        const options = {
            parallel: 4,
            partSize: 10 * 1024 * 1024,  // 10MB 分片
            progress: (percentage, cp) => {
                const percent = Math.round(percentage * 100);
                if (onProgress) onProgress(percent);

                // 保存断点
                if (cp) {
                    this.saveCheckpoint(fileInfo.id, cp);
                }
            }
        };

        // 有断点则续传
        if (checkpoint) {
            options.checkpoint = checkpoint;
        }

        try {
            const result = await this.client.multipartUpload(ossPath, fileInfo.file, options);

            // 存储 abort 引用
            if (result && result.name) {
                this.clearCheckpoint(fileInfo.id);
                const url = result.res?.requestUrls?.[0]?.split('?')[0] || '';
                return { success: true, url: url };
            }

            return { success: true, url: '' };
        } catch (err) {
            if (err.name === 'cancel') {
                return { success: false, cancelled: true };
            }
            throw err;
        }
    }

    /**
     * 取消上传
     */
    cancel(fileId) {
        // ali-oss multipartUpload 返回的 promise 有 abort 方法
        if (this.activeUploads[fileId]) {
            this.activeUploads[fileId].abort();
            delete this.activeUploads[fileId];
        }
    }

    /**
     * 注册可取消的上传
     */
    registerCancellable(fileId, uploadPromise) {
        this.activeUploads[fileId] = uploadPromise;
    }

    /**
     * 保存断点到 localStorage
     */
    saveCheckpoint(fileId, checkpoint) {
        try {
            const serializable = {
                uploadId: checkpoint.uploadId,
                name: checkpoint.name,
                file: {
                    name: checkpoint.file?.name || '',
                    size: checkpoint.file?.size || 0,
                    lastModified: checkpoint.file?.lastModified || 0
                },
                parts: checkpoint.parts || [],
                done: checkpoint.done || 0
            };
            localStorage.setItem(`oss_cp_${fileId}`, JSON.stringify(serializable));
        } catch (e) {
            console.warn('保存断点失败:', e);
        }
    }

    /**
     * 加载断点
     */
    loadCheckpoint(fileId) {
        try {
            const data = localStorage.getItem(`oss_cp_${fileId}`);
            if (!data) return null;
            return JSON.parse(data);
        } catch (e) {
            return null;
        }
    }

    /**
     * 清除断点
     */
    clearCheckpoint(fileId) {
        localStorage.removeItem(`oss_cp_${fileId}`);
    }

    /**
     * 检查是否有未完成的上传
     */
    getPendingUploads() {
        const pending = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('oss_cp_')) {
                try {
                    const data = JSON.parse(localStorage.getItem(key));
                    pending.push({
                        fileId: key.replace('oss_cp_', ''),
                        ...data
                    });
                } catch (e) {
                    localStorage.removeItem(key);
                }
            }
        }
        return pending;
    }

    /**
     * 清除所有过期断点（超过24小时）
     */
    clearStaleCheckpoints() {
        const now = Date.now();
        const keysToRemove = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('oss_cp_')) {
                try {
                    const data = JSON.parse(localStorage.getItem(key));
                    if (data.file?.lastModified && now - data.file.lastModified > 86400000) {
                        keysToRemove.push(key);
                    }
                } catch (e) {
                    keysToRemove.push(key);
                }
            }
        }
        keysToRemove.forEach(k => localStorage.removeItem(k));
    }
}

// 全局实例
const ossUploader = new OSSUploader();
