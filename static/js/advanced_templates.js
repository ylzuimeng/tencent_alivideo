// 当前预览的模板ID
let currentPreviewTemplateId = null;

// 加载模板列表
async function loadTemplates() {
    try {
        const response = await fetch('/api/video_templates/advanced');
        const data = await response.json();

        const container = document.getElementById('templatesContainer');

        if (data.success && data.templates.length > 0) {
            container.innerHTML = data.templates.map(template => `
                <div class="col-md-4 mb-4">
                    <div class="card h-100">
                        ${template.thumbnail_url ?
                            `<img src="${template.thumbnail_url}" class="card-img-top" alt="${template.name}" style="height: 200px; object-fit: cover;">` :
                            `<div class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 200px;">
                                <i class="bi bi-file-earmark-code text-muted" style="font-size: 3rem;"></i>
                            </div>`
                        }
                        <div class="card-body">
                            <h5 class="card-title">${escapeHtml(template.name)}</h5>
                            <p class="card-text text-muted small">${escapeHtml(template.description || '暂无描述')}</p>
                            <div class="mb-2">
                                <span class="badge bg-info">${getCategoryName(template.category)}</span>
                                <span class="badge bg-secondary">${template.formatter_type}</span>
                            </div>
                            <small class="text-muted">
                                <i class="bi bi-clock"></i> ${formatDate(template.created_at)}
                            </small>
                        </div>
                        <div class="card-footer">
                            <button class="btn btn-sm btn-outline-primary" onclick="viewTemplate(${template.id})">
                                <i class="bi bi-eye"></i> 查看
                            </button>
                            <button class="btn btn-sm btn-outline-success" onclick="openPreviewModal(${template.id})">
                                <i class="bi bi-play-circle"></i> 预览
                            </button>
                            <button class="btn btn-sm btn-outline-secondary" onclick="useTemplate(${template.id})">
                                <i class="bi bi-plus-circle"></i> 使用
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        } else if (data.success && data.templates.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="bi bi-inbox text-muted" style="font-size: 4rem;"></i>
                    <p class="mt-3 text-muted">暂无高级模板</p>
                    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#createTemplateModal">
                        <i class="bi bi-plus-lg"></i> 创建第一个模板
                    </button>
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="bi bi-exclamation-triangle text-warning" style="font-size: 4rem;"></i>
                    <p class="mt-3 text-danger">加载失败: ${data.message || '未知错误'}</p>
                    <button class="btn btn-primary" onclick="loadTemplates()">
                        <i class="bi bi-arrow-clockwise"></i> 重试
                    </button>
                </div>
            `;
        }
    } catch (error) {
        console.error('加载模板失败:', error);
        document.getElementById('templatesContainer').innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="bi bi-exclamation-triangle text-danger" style="font-size: 4rem;"></i>
                <p class="mt-3 text-danger">加载失败: ${error.message}</p>
                <button class="btn btn-primary" onclick="loadTemplates()">
                    <i class="bi bi-arrow-clockwise"></i> 重试
                </button>
            </div>
        `;
    }
}

// 创建模板
async function createTemplate() {
    const form = document.getElementById('createTemplateForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    // 验证必填字段
    if (!data.name || !data.name.trim()) {
        alert('请输入模板名称');
        return;
    }

    if (!data.timeline_json || !data.timeline_json.trim()) {
        alert('请输入Timeline JSON');
        return;
    }

    // 验证JSON格式
    try {
        JSON.parse(data.timeline_json);
    } catch (e) {
        alert('Timeline JSON格式错误: ' + e.message);
        return;
    }

    try {
        const response = await fetch('/api/video_templates/advanced', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            alert('✅ 模板创建成功！');
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('createTemplateModal'));
            modal.hide();
            // 重置表单
            form.reset();
            // 重新加载列表
            loadTemplates();
        } else {
            alert('❌ 创建失败: ' + result.message);
        }
    } catch (error) {
        console.error('创建模板失败:', error);
        alert('❌ 创建模板失败: ' + error.message);
    }
}

// 查看模板详情
async function viewTemplate(templateId) {
    try {
        const response = await fetch(`/api/video_templates/advanced/${templateId}`);
        const data = await response.json();

        if (data.success) {
            const t = data.template;
            const info = `
模板名称: ${t.name}
分类: ${getCategoryName(t.category)}
格式化器: ${t.formatter_type}
描述: ${t.description || '暂无描述'}

Timeline JSON:
${JSON.stringify(JSON.parse(t.timeline_json), null, 2)}

${t.output_media_config ? `输出配置:\n${JSON.stringify(JSON.parse(t.output_media_config), null, 2)}\n` : ''}
${t.editing_produce_config ? `制作配置:\n${JSON.stringify(JSON.parse(t.editing_produce_config), null, 2)}` : ''}
            `;
            alert(info);
        } else {
            alert('获取失败: ' + data.message);
        }
    } catch (error) {
        console.error('获取模板详情失败:', error);
        alert('获取失败: ' + error.message);
    }
}

// 打开预览模态框
function openPreviewModal(templateId) {
    currentPreviewTemplateId = templateId;
    // 重置预览输出
    document.getElementById('previewOutput').textContent = '点击"生成预览"查看结果...';
    // 显示模态框
    const modal = new bootstrap.Modal(document.getElementById('previewModal'));
    modal.show();
}

// 运行预览
async function runPreview() {
    if (!currentPreviewTemplateId) {
        alert('请先选择模板');
        return;
    }

    const testData = {
        main_video_url: document.getElementById('preview_main_video_url').value,
        hospital: document.getElementById('preview_hospital').value,
        department: document.getElementById('preview_department').value,
        name: document.getElementById('preview_name').value,
        title: document.getElementById('preview_title').value,
        video_title: document.getElementById('preview_video_title').value
    };

    try {
        const response = await fetch(`/api/video_templates/advanced/${currentPreviewTemplateId}/preview`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(testData)
        });

        const data = await response.json();

        if (data.success) {
            // 格式化显示Timeline
            const timeline = JSON.parse(data.timeline);
            document.getElementById('previewOutput').textContent = JSON.stringify(timeline, null, 2);
        } else {
            alert('预览失败: ' + data.message);
        }
    } catch (error) {
        console.error('预览失败:', error);
        alert('预览失败: ' + error.message);
    }
}

// 使用模板创建任务
function useTemplate(templateId) {
    // 跳转到任务创建页面（需要实现该页面）
    window.location.href = `/tasks?template_id=${templateId}`;
}

// 工具函数：转义HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 工具函数：格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

// 工具函数：获取分类名称
function getCategoryName(category) {
    const map = {
        'medical': '医疗健康宣教',
        'education': '教育培训',
        'general': '通用'
    };
    return map[category] || category;
}

// 页面加载时执行
document.addEventListener('DOMContentLoaded', loadTemplates);

// 快速模板功能
function insertQuickTemplate(preset) {
    const textarea = document.querySelector('[name="timeline_json"]');

    const templates = {
        'standard': {
            "VideoTracks": [{
                "VideoTrackClips": [
                    {"MediaURL": "$header_video", "Duration": 3},
                    {"MediaURL": "$main_video", "MainTrack": true},
                    {"MediaURL": "$footer_video", "Duration": 3}
                ]
            }]
        },
        'main-first': {
            "VideoTracks": [{
                "VideoTrackClips": [
                    {"MediaURL": "$main_video", "MainTrack": true},
                    {"MediaURL": "$header_video", "Duration": 3},
                    {"MediaURL": "$footer_video", "Duration": 3}
                ]
            }]
        },
        'main-last': {
            "VideoTracks": [{
                "VideoTrackClips": [
                    {"MediaURL": "$header_video", "Duration": 3},
                    {"MediaURL": "$footer_video", "Duration": 3},
                    {"MediaURL": "$main_video", "MainTrack": true}
                ]
            }]
        }
    };

    if (templates[preset]) {
        textarea.value = JSON.stringify(templates[preset], null, 2);
    }
}

