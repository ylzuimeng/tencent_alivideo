// 全局状态
let currentTemplateId = null;
let currentMode = 'simple';  // 'simple' 或 'advanced'
let templatesCache = [];

// ========== 模式切换逻辑 ==========

function switchMode(mode) {
    currentMode = mode;

    // 更新UI
    const modeDisplay = document.getElementById('currentModeDisplay');
    const convertBtn = document.getElementById('convertModeBtn');

    if (mode === 'simple') {
        modeDisplay.textContent = '简单模式';
        convertBtn.innerHTML = '<i class="fas fa-magic me-1"></i>切换到高级模式（自动生成Timeline）';
        convertBtn.onclick = convertToAdvanced;
    } else {
        modeDisplay.textContent = '高级模式';
        convertBtn.innerHTML = '<i class="fas fa-hand-pointer me-1"></i>切换到简单模式（尝试解析字段）';
        convertBtn.onclick = convertToSimple;
    }

    // 同步基本信息
    if (mode === 'simple') {
        document.getElementById('templateName').value = document.getElementById('templateNameAdvanced').value;
    } else {
        document.getElementById('templateNameAdvanced').value = document.getElementById('templateName').value;
    }
}

// ========== 模式转换 ==========

async function convertToAdvanced() {
    const simpleData = collectSimpleFormData();

    if (!simpleData.name) {
        alert('请先输入模板名称');
        return;
    }

    try {
        showToast('正在生成Timeline...', 'info');

        const response = await fetch('/api/video_templates/convert-demo', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                mode: 'simple-to-advanced',
                data: simpleData
            })
        });

        const result = await response.json();

        if (result.success) {
            // 填充高级模式字段
            document.getElementById('timelineJson').value = result.timeline_json;
            if (result.output_media_config) {
                document.getElementById('outputMediaConfig').value = result.output_media_config;
            }

            // 切换到高级模式标签
            const advancedTab = new bootstrap.Tab(document.getElementById('advancedModeTab'));
            advancedTab.show();

            showToast('✅ Timeline已自动生成！', 'success');
            updateTimelinePreview();
        } else {
            showToast('转换失败: ' + result.message, 'error');
        }
    } catch (error) {
        console.error('转换失败:', error);
        // 降级：前端自动生成简单Timeline
        const timeline = generateSimpleTimeline(simpleData);
        document.getElementById('timelineJson').value = timeline;
        const advancedTab = new bootstrap.Tab(document.getElementById('advancedModeTab'));
        advancedTab.show();
        showToast('⚠️ 使用前端生成Timeline', 'warning');
        updateTimelinePreview();
    }
}

async function convertToSimple() {
    const timelineJson = document.getElementById('timelineJson').value;

    if (!timelineJson.trim()) {
        showToast('Timeline JSON为空', 'warning');
        return;
    }

    try {
        showToast('正在解析Timeline...', 'info');

        const response = await fetch('/api/video_templates/convert-demo', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                mode: 'advanced-to-simple',
                timeline_json: timelineJson
            })
        });

        const result = await response.json();

        if (result.success) {
            const data = result.data;

            // 填充简单模式字段
            if (data.header_video_url) {
                document.getElementById('headerVideo').value = data.header_video_url;
            }
            if (data.footer_video_url) {
                document.getElementById('footerVideo').value = data.footer_video_url;
            }
            if (data.enable_subtitle !== undefined) {
                document.getElementById('enableSubtitle').checked = data.enable_subtitle;
            }
            if (data.subtitle_position) {
                document.getElementById('subtitlePosition').value = data.subtitle_position;
            }

            // 切换到简单模式标签
            const simpleTab = new bootstrap.Tab(document.getElementById('simpleModeTab'));
            simpleTab.show();

            const warnings = data.warnings || [];
            if (warnings.length > 0) {
                showToast('⚠️ ' + warnings.join('; '), 'warning');
            } else {
                showToast('✅ 已解析到简单字段', 'success');
            }
        } else {
            showToast('无法自动解析，请手动配置', 'warning');
        }
    } catch (error) {
        console.error('解析失败:', error);
        showToast('⚠️ 无法自动解析，请手动配置简单字段', 'warning');
    }
}

function convertCurrentMode() {
    if (currentMode === 'simple') {
        convertToAdvanced();
    } else {
        convertToSimple();
    }
}

// ========== 数据收集 ==========

function collectSimpleFormData() {
    const textOverlayConfig = {
        fontSize: document.getElementById('fontSize').value,
        fontColor: document.getElementById('fontColor').value,
        positionX: document.getElementById('positionX').value,
        positionY: document.getElementById('positionY').value,
        boldText: document.getElementById('boldText').checked
    };

    return {
        name: document.getElementById('templateName').value,
        category: document.getElementById('templateCategory').value,
        description: document.getElementById('templateDescription').value,
        header_video_url: document.getElementById('headerVideo').value,
        footer_video_url: document.getElementById('footerVideo').value,
        enable_subtitle: document.getElementById('enableSubtitle').checked,
        subtitle_position: document.getElementById('subtitlePosition').value,
        subtitle_extract_audio: document.getElementById('extractAudio').checked,
        text_overlay_config: JSON.stringify(textOverlayConfig)
    };
}

function collectAdvancedFormData() {
    return {
        name: document.getElementById('templateNameAdvanced').value,
        category: document.getElementById('templateCategory').value,
        description: document.getElementById('templateDescription').value,
        formatter_type: document.getElementById('formatterType').value,
        thumbnail_url: document.getElementById('thumbnailUrl').value,
        timeline_json: document.getElementById('timelineJson').value,
        output_media_config: document.getElementById('outputMediaConfig').value,
        editing_produce_config: document.getElementById('editingProduceConfig').value
    };
}

// ========== 保存模板 ==========

async function saveTemplate(mode) {
    let data, isValid;

    if (mode === 'simple') {
        data = collectSimpleFormData();
        isValid = validateSimpleForm();
    } else {
        data = collectAdvancedFormData();
        isValid = validateAdvancedForm();
    }

    if (!isValid) return;

    // 添加模式标识
    data.edit_mode = mode;
    data.is_advanced = (mode === 'advanced');

    try {
        showToast('正在保存模板...', 'info');

        // 统一使用相同的API端点
        const url = currentTemplateId
            ? `/api/video_templates/${currentTemplateId}`
            : '/api/video_templates';

        const method = currentTemplateId ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        const result = await response.json();
        handleSaveResult(result);

    } catch (error) {
        console.error('保存失败:', error);
        showToast('保存失败: ' + error.message, 'error');
    }
}

function handleSaveResult(result) {
    if (result.success) {
        showToast('✅ 模板保存成功！', 'success');
        if (!currentTemplateId) {
            currentTemplateId = result.template_id;
        }
        setTimeout(() => showTemplatesList(), 1500);
    } else {
        showToast('保存失败: ' + result.message, 'error');
    }
}

// ========== 表单验证 ==========

function validateSimpleForm() {
    const name = document.getElementById('templateName').value.trim();
    if (!name) {
        showToast('请输入模板名称', 'error');
        return false;
    }
    return true;
}

function validateAdvancedForm() {
    const name = document.getElementById('templateNameAdvanced').value.trim();
    const timelineJson = document.getElementById('timelineJson').value.trim();

    if (!name) {
        showToast('请输入模板名称', 'error');
        return false;
    }

    if (!timelineJson) {
        showToast('请输入Timeline JSON', 'error');
        return false;
    }

    try {
        JSON.parse(timelineJson);
    } catch (e) {
        showToast('Timeline JSON格式错误: ' + e.message, 'error');
        return false;
    }

    return true;
}

// ========== Timeline生成和预览 ==========

function generateSimpleTimeline(data) {
    const timeline = {
        "VideoTracks": [{
            "VideoTrackClips": []
        }]
    };

    if (data.header_video_url) {
        timeline.VideoTracks[0].VideoTrackClips.push({
            "MediaURL": data.header_video_url,
            "Duration": 3
        });
    }

    timeline.VideoTracks[0].VideoTrackClips.push({
        "MediaURL": "$main_video",
        "MainTrack": true
    });

    if (data.footer_video_url) {
        timeline.VideoTracks[0].VideoTrackClips.push({
            "MediaURL": data.footer_video_url,
            "Duration": 3
        });
    }

    return JSON.stringify(timeline, null, 2);
}

function updateTimelinePreview() {
    const timelinePre = document.getElementById('timelinePreview');

    if (currentMode === 'simple') {
        const simpleData = collectSimpleFormData();
        const timeline = generateSimpleTimeline(simpleData);
        timelinePre.textContent = timeline;
    } else {
        timelinePre.textContent = document.getElementById('timelineJson').value;
    }
}

function previewTimeline() {
    updateTimelinePreview();
    showToast('Timeline已更新', 'success');
}

// ========== JSON工具函数 ==========

function formatTimelineJSON() {
    const textarea = document.getElementById('timelineJson');
    try {
        const json = JSON.parse(textarea.value);
        textarea.value = JSON.stringify(json, null, 2);
        showToast('JSON已格式化', 'success');
    } catch (e) {
        showToast('JSON格式错误，无法格式化', 'error');
    }
}

async function validateTimelineJSON() {
    const textarea = document.getElementById('timelineJson');
    try {
        const response = await fetch('/api/video_templates/validate-timeline', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({timeline_json: textarea.value})
        });
        const result = await response.json();
        if (result.valid) {
            showToast('✅ JSON格式正确', 'success');
        } else {
            showToast('❌ ' + result.message, 'error');
        }
    } catch (e) {
        showToast('验证失败: ' + e.message, 'error');
    }
}

function insertQuickTemplate(preset) {
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
        }
    };

    if (templates[preset]) {
        document.getElementById('timelineJson').value = JSON.stringify(templates[preset], null, 2);
        updateTimelinePreview();
    }
}

// ========== 视图切换 ==========

function showTemplatesList() {
    document.getElementById('mainEditor').style.display = 'none';
    document.getElementById('templatesList').style.display = 'block';
    loadTemplatesList();
}

function createNewTemplate() {
    currentTemplateId = null;
    resetForm();
    resetAdvancedForm();
    document.getElementById('templatesList').style.display = 'none';
    document.getElementById('mainEditor').style.display = 'flex';
    switchMode('simple');
}

function resetForm() {
    document.getElementById('templateName').value = '';
    document.getElementById('templateCategory').value = 'general';
    document.getElementById('templateDescription').value = '';
    document.getElementById('headerVideo').value = '';
    document.getElementById('footerVideo').value = '';
    document.getElementById('enableSubtitle').checked = false;
    document.getElementById('subtitlePosition').value = 'bottom';
    document.getElementById('extractAudio').checked = true;
    document.getElementById('fontSize').value = '30';
    document.getElementById('fontColor').value = '#ffffff';
    document.getElementById('positionX').value = '10';
    document.getElementById('positionY').value = '10';
    document.getElementById('boldText').checked = true;
}

function resetAdvancedForm() {
    document.getElementById('templateNameAdvanced').value = '';
    document.getElementById('formatterType').value = 'default';
    document.getElementById('thumbnailUrl').value = '';
    document.getElementById('timelineJson').value = '';
    document.getElementById('outputMediaConfig').value = '';
    document.getElementById('editingProduceConfig').value = '';
}

// ========== 取消编辑 ==========
function cancelEdit() {
    // 检查是否有未保存的更改
    const hasChanges = checkForUnsavedChanges();

    if (hasChanges) {
        // 使用自定义确认对话框
        if (confirm('您有未保存的更改，确定要取消编辑吗？')) {
            returnToTemplateList();
        }
    } else {
        returnToTemplateList();
    }
}

function checkForUnsavedChanges() {
    // 检查简单模式表单是否有内容
    const simpleName = document.getElementById('templateName').value.trim();
    const simpleDesc = document.getElementById('templateDescription').value.trim();

    // 检查高级模式表单是否有内容
    const advancedName = document.getElementById('templateNameAdvanced').value.trim();
    const timelineJson = document.getElementById('timelineJson').value.trim();

    // 如果是新建模板（currentTemplateId为null），检查表单是否有内容
    if (!currentTemplateId) {
        return !!(simpleName || simpleDesc || advancedName || timelineJson);
    } else {
        // 如果是编辑现有模板，这里可以添加更复杂的比较逻辑
        // 简化版本：总是提示用户确认
        return true;
    }
}

function returnToTemplateList() {
    // 清空当前编辑状态
    currentTemplateId = null;
    currentMode = 'simple';

    // 重置表单
    resetForm();
    resetAdvancedForm();

    // 返回模板列表视图
    document.getElementById('mainEditor').style.display = 'none';
    document.getElementById('templatesList').style.display = 'block';

    // 切换到简单模式标签
    const simpleTab = document.getElementById('simpleModeTab');
    const advancedTab = document.getElementById('advancedModeTab');

    if (simpleTab && advancedTab) {
        simpleTab.classList.add('active');
        advancedTab.classList.remove('active');

        // 显示简单模式面板，隐藏高级模式面板
        document.getElementById('simpleMode').classList.add('show', 'active');
        document.getElementById('advancedMode').classList.remove('show', 'active');
    }

    // 重新加载模板列表
    loadTemplatesList();

    showToast('已取消编辑', 'info');
}

// ========== 模板列表 ==========

async function loadTemplatesList() {
    try {
        const response = await fetch('/api/video_templates');
        const result = await response.json();

        if (result.success) {
            templatesCache = result.templates;
            const tbody = document.getElementById('templatesTableBody');

            if (result.templates.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center text-muted">
                            <i class="fas fa-inbox me-2"></i>暂无模板
                            <a href="#" onclick="createNewTemplate()" class="ms-2">创建第一个模板 →</a>
                        </td>
                    </tr>
                `;
                return;
            }

            tbody.innerHTML = result.templates.map(t => `
                <tr>
                    <td><strong>${escapeHtml(t.name)}</strong></td>
                    <td>
                        <span class="badge ${t.is_advanced ? 'bg-danger' : 'bg-success'}">
                            ${t.is_advanced ? '高级' : '简单'}
                        </span>
                    </td>
                    <td>${escapeHtml(t.category || '-')}</td>
                    <td><small>${escapeHtml(t.description || '-')}</small></td>
                    <td><small>${formatDate(t.created_at)}</small></td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1"
                                onclick="editTemplate(${t.id}, ${t.is_advanced})">
                            <i class="fas fa-edit"></i> 编辑
                        </button>
                        <button class="btn btn-sm btn-outline-danger"
                                onclick="deleteTemplate(${t.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('加载模板列表失败:', error);
        document.getElementById('templatesTableBody').innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-danger">
                    加载失败: ${error.message}
                </td>
            </tr>
        `;
    }
}

async function editTemplate(templateId, isAdvanced) {
    try {
        currentTemplateId = templateId;

        // 使用统一的API端点（高级模板和简单模板使用相同的端点）
        const url = `/api/video_templates/${templateId}`;

        const response = await fetch(url);
        const result = await response.json();

        if (result.success) {
            const t = result.template;

            // 填充基本信息
            document.getElementById('templateName').value = t.name || '';
            document.getElementById('templateNameAdvanced').value = t.name || '';
            document.getElementById('templateCategory').value = t.category || 'general';
            document.getElementById('templateDescription').value = t.description || '';

            if (isAdvanced) {
                // 填充高级模式字段
                document.getElementById('formatterType').value = t.formatter_type || 'default';
                document.getElementById('thumbnailUrl').value = t.thumbnail_url || '';
                document.getElementById('timelineJson').value = t.timeline_json || '';
                document.getElementById('outputMediaConfig').value = t.output_media_config || '';
                document.getElementById('editingProduceConfig').value = t.editing_produce_config || '';

                switchMode('advanced');
            } else {
                // 填充简单模式字段
                document.getElementById('headerVideo').value = t.header_video_url || '';
                document.getElementById('footerVideo').value = t.footer_video_url || '';
                document.getElementById('enableSubtitle').checked = t.enable_subtitle || false;
                document.getElementById('subtitlePosition').value = t.subtitle_position || 'bottom';

                if (t.text_overlay_config) {
                    try {
                        const config = JSON.parse(t.text_overlay_config);
                        document.getElementById('fontSize').value = config.fontSize || 30;
                        document.getElementById('fontColor').value = config.fontColor || '#ffffff';
                        document.getElementById('positionX').value = config.positionX || 10;
                        document.getElementById('positionY').value = config.positionY || 10;
                        document.getElementById('boldText').checked = config.boldText !== false;
                    } catch (e) {
                        console.error('解析文字叠加配置失败:', e);
                    }
                }

                switchMode('simple');
            }

            // 显示编辑区域
            document.getElementById('templatesList').style.display = 'none';
            document.getElementById('mainEditor').style.display = 'flex';

            updateTimelinePreview();
        } else {
            showToast('加载模板失败: ' + result.message, 'error');
        }
    } catch (error) {
        console.error('加载模板失败:', error);
        showToast('加载模板失败: ' + error.message, 'error');
    }
}

async function deleteTemplate(templateId) {
    if (!confirm('确定要删除这个模板吗？')) {
        return;
    }

    try {
        const response = await fetch(`/api/video_templates/${templateId}`, {
            method: 'DELETE'
        });
        const result = await response.json();

        if (result.success) {
            showToast('✅ 模板已删除', 'success');
            loadTemplatesList();
        } else {
            showToast('删除失败: ' + result.message, 'error');
        }
    } catch (error) {
        console.error('删除模板失败:', error);
        showToast('删除失败: ' + error.message, 'error');
    }
}

// ========== 工具函数 ==========

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

function showToast(message, type = 'info') {
    console.log(`[${type}] ${message}`);

    const toast = document.getElementById('toast');
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    const toastIcon = document.getElementById('toastIcon');

    // 设置样式和图标
    const typeConfig = {
        'success': {
            title: '成功',
            icon: 'fas fa-check-circle text-success',
            class: 'text-success'
        },
        'error': {
            title: '错误',
            icon: 'fas fa-exclamation-circle text-danger',
            class: 'text-danger'
        },
        'warning': {
            title: '警告',
            icon: 'fas fa-exclamation-triangle text-warning',
            class: 'text-warning'
        },
        'info': {
            title: '提示',
            icon: 'fas fa-info-circle text-primary',
            class: 'text-primary'
        }
    };

    const config = typeConfig[type] || typeConfig['info'];

    toastTitle.textContent = config.title;
    toastMessage.textContent = message;
    toastIcon.className = config.icon;

    // 显示Toast
    const bsToast = new bootstrap.Toast(toast, {
        delay: 3000,
        animation: true
    });
    bsToast.show();
}

async function loadVideoFiles() {
    try {
        const response = await fetch('/api/files');
        const result = await response.json();

        if (result.success && result.files) {
            const headerSelect = document.getElementById('headerVideo');
            const footerSelect = document.getElementById('footerVideo');

            // 保留第一个选项
            headerSelect.innerHTML = '<option value="">无片头</option>';
            footerSelect.innerHTML = '<option value="">无片尾</option>';

            result.files.forEach(file => {
                const option1 = new Option(file.filename, file.oss_url);
                const option2 = new Option(file.filename, file.oss_url);
                headerSelect.add(option1);
                footerSelect.add(option2);
            });
        }
    } catch (error) {
        console.error('加载视频列表失败:', error);
    }
}

// ========== 初始化 ==========

document.addEventListener('DOMContentLoaded', function() {
    // 加载视频列表
    loadVideoFiles();

    // 设置实时预览
    const simpleInputs = [
        'headerVideo', 'footerVideo', 'enableSubtitle',
        'subtitlePosition', 'fontSize', 'fontColor',
        'positionX', 'positionY', 'boldText'
    ];

    simpleInputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', updateTimelinePreview);
            element.addEventListener('input', updateTimelinePreview);
        }
    });

    // 监听高级模式Timeline变化
    const timelineTextarea = document.getElementById('timelineJson');
    if (timelineTextarea) {
        timelineTextarea.addEventListener('input', updateTimelinePreview);
    }

    // 默认显示模板列表
    showTemplatesList();
});
