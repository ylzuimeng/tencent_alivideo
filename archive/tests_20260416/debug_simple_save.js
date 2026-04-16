/**
 * 调试简单模式保存功能的浏览器脚本
 * 在浏览器控制台中运行此脚本
 */

console.log("🔍 开始调试简单模式保存...");

// 收集表单数据
function collectSimpleFormData() {
    const textOverlayConfig = {
        fontSize: document.getElementById('fontSize').value,
        fontColor: document.getElementById('fontColor').value,
        positionX: document.getElementById('positionX').value,
        positionY: document.getElementById('positionY').value,
        boldText: document.getElementById('boldText').checked
    };

    const data = {
        name: document.getElementById('templateName').value,
        category: document.getElementById('templateCategory').value,
        description: document.getElementById('templateDescription').value,
        header_video_url: document.getElementById('headerVideo').value,
        footer_video_url: document.getElementById('footerVideo').value,
        enable_subtitle: document.getElementById('enableSubtitle').checked,
        subtitle_position: document.getElementById('subtitlePosition').value,
        subtitle_extract_audio: document.getElementById('extractAudio').checked,
        text_overlay_config: JSON.stringify(textOverlayConfig),
        is_advanced: false
    };

    console.log("📦 收集的表单数据:", data);
    return data;
}

// 测试保存
async function debugSave() {
    try {
        const data = collectSimpleFormData();

        console.log("🚀 发送保存请求...");

        const response = await fetch('/api/video_templates', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        console.log("📊 响应状态:", response.status);
        console.log("📋 响应头:", Object.fromEntries(response.headers.entries()));

        const result = await response.json();
        console.log("✅ 响应数据:", result);

        return result;
    } catch (error) {
        console.error("❌ 保存失败:", error);
        throw error;
    }
}

// 执行测试
debugSave().then(result => {
    if (result.success) {
        console.log("✅ 调试完成，保存成功！");
    } else {
        console.error("❌ 调试完成，保存失败:", result.message);
    }
});

// 使用方法：
// 1. 打开 http://127.0.0.1:5000/templates/unified
// 2. 点击"新建模板"
// 3. 填写简单模式表单
// 4. 打开浏览器开发者工具（F12）
// 5. 在Console标签页中粘贴并运行此脚本
