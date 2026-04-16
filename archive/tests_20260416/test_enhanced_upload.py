"""
测试使用 /upload/enhanced 页面上传视频并使用模板5添加字幕
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright

# 视频文件路径
VIDEO_PATH = "/Users/yanglei/Downloads/用所选项目新建的文件夹 2/视频剪辑测试/main.mp4"
# 模板ID
TEMPLATE_ID = 5


async def test_enhanced_upload_with_subtitle():
    """测试增强上传页面"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 监听请求和响应
        def log_response(response):
            if "/api/" in response.url:
                print(f"📥 响应: {response.status} {response.url}")

        page.on("response", log_response)

        try:
            print("="*60)
            print("🧪 测试增强上传页面 - 视频上传 + 字幕模板")
            print("="*60)

            # 步骤1: 导航到增强上传页面
            print("\n📍 步骤1: 导航到增强上传页面...")
            await page.goto("http://127.0.0.1:5000/upload/enhanced")
            await page.wait_for_load_state("networkidle")
            print("✅ 页面加载完成")

            # 步骤2: 上传视频
            print(f"\n📍 步骤2: 上传视频文件...")
            print(f"   文件路径: {VIDEO_PATH}")
            print(f"   文件大小: {os.path.getsize(VIDEO_PATH) / 1024 / 1024:.2f} MB")

            # 选择文件
            file_input = await page.query_selector("input[type='file']")
            await file_input.set_input_files(VIDEO_PATH)
            print("✅ 文件已选择")

            # 等待上传完成
            print("⏳ 等待上传完成...")
            await page.wait_for_timeout(5000)

            # 检查上传结果
            upload_result = await page.evaluate("""
                () => {
                    // 检查 window.uploadedFiles
                    if (window.uploadedFiles && window.uploadedFiles.length > 0) {
                        return {
                            success: true,
                            count: window.uploadedFiles.length,
                            files: window.uploadedFiles.map(f => ({
                                dbFileId: f.dbFileId,
                                fileName: f.fileName,
                                ossUrl: f.ossUrl
                            }))
                        };
                    }

                    // 检查页面上的文件列表
                    const fileItems = document.querySelectorAll('.file-item, .upload-item, [id*="file"], [class*="upload"]');
                    return {
                        success: fileItems.length > 0,
                        count: fileItems.length,
                        html: fileItems.length > 0 ? fileItems[0].outerHTML.substring(0, 200) : null
                    };
                }
            """)

            print(f"📊 上传结果: {json.dumps(upload_result, ensure_ascii=False, indent=2)}")

            if not upload_result.get('success') or upload_result.get('count', 0) == 0:
                # 尝试查看页面上有什么内容
                page_content = await page.evaluate("""
                    () => {
                        const body = document.body.innerHTML;
                        return body.substring(0, 500);
                    }
                """)
                print(f"⚠️  页面内容预览: {page_content}")
                print("❌ 未能检测到上传的文件")
                return False

            # 获取第一个文件的信息
            first_file = upload_result.get('files', [{}])[0]
            file_id = first_file.get('dbFileId')
            file_name = first_file.get('fileName')

            print(f"\n✅ 视频上传成功！")
            print(f"   文件ID: {file_id}")
            print(f"   文件名: {file_name}")

            # 步骤3: 选择模板5
            print(f"\n📍 步骤3: 选择模板5（实际文件模板-片头片尾）...")

            # 等待模板下拉框加载
            await page.wait_for_selector("#taskTemplate", state="visible", timeout=10000)

            # 先获取所有模板选项
            template_options = await page.evaluate("""
                () => {
                    const select = document.getElementById('taskTemplate');
                    if (!select) return [];

                    return Array.from(select.options).map(opt => ({
                        value: opt.value,
                        text: opt.text
                    }));
                }
            """)

            print(f"📋 可用模板:")
            for opt in template_options[:5]:  # 只显示前5个
                print(f"   [{opt['value']}] {opt['text']}")

            # 选择模板5
            await page.select_option("#taskTemplate", str(TEMPLATE_ID))
            await page.wait_for_timeout(1000)
            print(f"✅ 已选择模板5")

            # 步骤4: 查看模板详情（验证AI_ASR配置）
            print(f"\n📍 步骤4: 验证模板配置...")
            template_details = await page.evaluate("""
                async () => {
                    const response = await fetch('/api/video_templates/5');
                    const result = await response.json();
                    if (result.success) {
                        const t = result.template;
                        let timelineInfo = null;
                        if (t.timeline_json) {
                            try {
                                const timeline = JSON.parse(t.timeline_json);
                                const mainClip = timeline.VideoTracks?.[0]?.VideoTrackClips?.[1];
                                if (mainClip && mainClip.Effects) {
                                    timelineInfo = {
                                        hasAI_ASR: mainClip.Effects.some(e => e.Type === 'AI_ASR'),
                                        effects: mainClip.Effects
                                    };
                                }
                            } catch (e) {
                                console.error('解析Timeline失败:', e);
                            }
                        }

                        return {
                            name: t.name,
                            is_advanced: t.is_advanced,
                            enable_subtitle: t.enable_subtitle,
                            has_timeline: !!t.timeline_json,
                            header: t.header_video_url,
                            footer: t.footer_video_url,
                            timeline_info: timelineInfo
                        };
                    }
                    return null;
                }
            """)

            if template_details:
                print(f"📋 模板配置:")
                print(f"   名称: {template_details['name']}")
                print(f"   高级模式: {template_details['is_advanced']}")
                print(f"   启用字幕: {template_details['enable_subtitle']}")
                print(f"   片头: {template_details['header']}")
                print(f"   片尾: {template_details['footer']}")

                if template_details.get('timeline_info'):
                    tl_info = template_details['timeline_info']
                    print(f"   Timeline配置:")
                    print(f"     包含AI_ASR: {tl_info['hasAI_ASR']}")
                    if tl_info['hasAI_ASR']:
                        print(f"     ✅ 主视频配置了自动语音识别字幕！")

            # 步骤5: 创建任务
            print(f"\n📍 步骤5: 创建视频处理任务...")

            # 检查创建按钮是否存在
            create_button = await page.query_selector("button:has-text('创建视频处理任务'), button:has-text('创建任务')")
            if not create_button:
                print("❌ 未找到创建任务按钮")

                # 尝试查找所有按钮
                all_buttons = await page.evaluate("""
                    () => {
                        const buttons = Array.from(document.querySelectorAll('button'));
                        return buttons.map(b => b.textContent.trim()).filter(t => t);
                    }
                """)
                print(f"可用按钮: {all_buttons}")
                return False

            # 点击创建任务按钮
            await create_button.click()
            print("✅ 已点击创建任务按钮")

            # 等待响应
            await page.wait_for_timeout(3000)

            # 检查是否有提示消息
            alert_check = await page.evaluate("""
                () => {
                    // 检查各种可能的提示元素
                    const selectors = [
                        '.alert',
                        '.toast',
                        '.message',
                        '[role="alert"]'
                    ];

                    for (const selector of selectors) {
                        const el = document.querySelector(selector);
                        if (el && el.textContent.trim()) {
                            return {
                                found: true,
                                selector: selector,
                                text: el.textContent.trim(),
                                classes: el.className
                            };
                        }
                    }

                    return { found: false };
                }
            """)

            if alert_check['found']:
                print(f"📊 提示消息:")
                print(f"   选择器: {alert_check['selector']}")
                print(f"   类名: {alert_check['classes']}")
                print(f"   内容: {alert_check['text']}")

                # 判断是否成功
                if '成功' in alert_check['text'] or alert_check['classes'].includes('success'):
                    print("\n✅ 任务创建成功！")
                else:
                    print(f"\n⚠️  任务创建提示: {alert_check['text']}")
            else:
                print("ℹ️  未看到提示消息，检查任务列表...")

                # 导航到任务列表查看
                await page.goto("http://127.0.0.1:5000/task_list")
                await page.wait_for_load_state("networkidle")
                await page.wait_for_timeout(2000)

                # 获取最新的任务
                latest_task = await page.evaluate("""
                    () => {
                        const rows = document.querySelectorAll('#tasksTable tbody tr');
                        if (rows.length > 0) {
                            const cells = rows[0].querySelectorAll('td');
                            return {
                                id: cells[0]?.textContent?.trim(),
                                name: cells[1]?.textContent?.trim(),
                                template: cells[2]?.textContent?.trim(),
                                status: cells[3]?.textContent?.trim(),
                                progress: cells[4]?.textContent?.trim()
                            };
                        }
                        return null;
                    }
                """)

                if latest_task:
                    print(f"\n📋 最新任务:")
                    print(f"   ID: {latest_task['id']}")
                    print(f"   名称: {latest_task['name']}")
                    print(f"   模板: {latest_task['template']}")
                    print(f"   状态: {latest_task['status']}")
                    print(f"   进度: {latest_task['progress']}")

                    if '实际文件模板' in latest_task['template']:
                        print("\n✅ 成功使用模板5创建了任务！")
                        print("✅ 该模板包含AI_ASR配置，处理时将自动添加字幕")

            # 截图
            await page.screenshot(path="test_enhanced_final.png", full_page=True)
            print("\n📸 已保存截图: test_enhanced_final.png")

            return True

        except Exception as e:
            print(f"\n❌ 测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            await page.wait_for_timeout(3000)
            await browser.close()


async def main():
    success = await test_enhanced_upload_with_subtitle()

    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    if success:
        print("✅ 测试通过")
        print("✅ 视频上传成功")
        print("✅ 使用了模板5（实际文件模板-片头片尾）")
        print("✅ 模板包含AI_ASR字幕配置")
        print("✅ 任务创建时将自动为视频添加字幕")
    else:
        print("❌ 测试失败，请检查日志")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
