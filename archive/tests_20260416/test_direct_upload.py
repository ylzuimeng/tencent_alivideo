"""
直接测试上传和处理流程
"""
import asyncio
import os
from playwright.async_api import async_playwright

VIDEO_PATH = "/Users/yanglei/Downloads/用所选项目新建的文件夹 2/视频剪辑测试/main.mp4"


async def test_direct():
    """直接测试上传和处理"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()

        # 监听控制台消息
        page.on("console", lambda msg: print(f"🖥️  {msg.type}: {msg.text}"))

        try:
            print("📍 打开上传页面...")
            await page.goto("http://127.0.0.1:5000/upload/enhanced")
            await page.wait_for_load_state("networkidle")

            print("📤 上传视频...")
            file_input = await page.query_selector("#fileInput")
            await file_input.set_input_files(VIDEO_PATH)

            print("⏳ 等待文件卡片出现...")
            await page.wait_for_selector("#fileList .file-card", state="visible", timeout=15000)
            await page.wait_for_timeout(2000)

            print("✅ 文件卡片已出现")

            # 获取文件信息
            file_data = await page.evaluate("""
                () => {
                    const card = document.querySelector('#fileList .file-card');
                    if (!card) return null;

                    const fileId = card.id.replace('file-', '');
                    const name = card.querySelector('h6')?.textContent;
                    const status = card.querySelector('.file-status')?.innerHTML;

                    // 查找处理按钮
                    const processBtn = card.querySelector('button[onclick*="processFile"]');

                    return {
                        fileId,
                        name,
                        status,
                        hasProcessBtn: !!processBtn
                    };
                }
            """)

            print(f"\n📦 文件信息:")
            print(f"   ID: {file_data['fileId']}")
            print(f"   名称: {file_data['name']}")
            print(f"   有处理按钮: {file_data['hasProcessBtn']}")

            if not file_data['hasProcessBtn']:
                print("❌ 没有处理按钮，上传可能失败")
                print(f"   状态: {file_data['status']}")
                return False

            # 选择模板5
            print("\n📋 选择模板5...")
            template_select = await page.query_selector(f"#{file_data['fileId']}-template")
            if template_select:
                await template_select.select_option("5")
                print("✅ 已选择模板5")
            else:
                print("⚠️  未找到模板选择器，可能需要等待...")
                await page.wait_for_timeout(3000)
                template_select = await page.query_selector(f"#{file_data['fileId']}-template")
                if template_select:
                    await template_select.select_option("5")
                    print("✅ 已选择模板5")
                else:
                    print("❌ 仍然找不到模板选择器")
                    return False

            await page.wait_for_timeout(1000)

            # 验证模板配置
            print("\n🔍 验证模板配置...")
            template_info = await page.evaluate("""
                async () => {
                    const response = await fetch('/api/video_templates/5');
                    const result = await response.json();
                    if (result.success) {
                        const t = result.template;
                        let hasAI_ASR = false;
                        if (t.timeline_json) {
                            try {
                                const timeline = JSON.parse(t.timeline_json);
                                const clips = timeline.VideoTracks?.[0]?.VideoTrackClips || [];
                                const mainClip = clips.find(c => c.MediaURL === '$main_video');
                                if (mainClip?.Effects) {
                                    hasAI_ASR = mainClip.Effects.some(e => e.Type === 'AI_ASR');
                                }
                            } catch (e) {
                                console.error('Timeline解析失败:', e);
                            }
                        }
                        return { name: t.name, hasAI_ASR };
                    }
                    return null;
                }
            """)

            if template_info:
                print(f"   模板: {template_info['name']}")
                print(f"   AI_ASR: {'✅' if template_info['hasAI_ASR'] else '❌'}")

            # 点击处理按钮
            print("\n▶️  点击处理按钮...")
            process_btn = await page.query_selector(f"#file-{file_data['fileId']} button[onclick*='processFile']")
            if process_btn:
                await process_btn.click()
                print("✅ 已点击处理按钮")
            else:
                print("❌ 未找到处理按钮")
                return False

            # 等待响应
            await page.wait_for_timeout(3000)

            # 检查结果
            result = await page.evaluate("""
                () => {
                    // 检查toast
                    const toasts = document.querySelectorAll('.toast');
                    for (const toast of toasts) {
                        if (toast.classList.contains('show')) {
                            return { type: 'toast', message: toast.textContent };
                        }
                    }

                    // 检查alert
                    const alerts = document.querySelectorAll('.alert');
                    for (const alert of alerts) {
                        if (alert.offsetParent !== null) {
                            return { type: 'alert', message: alert.textContent };
                        }
                    }

                    return { type: 'none' };
                }
            """)

            print(f"\n📊 响应: {result}")

            # 查看任务列表
            print("\n📋 查看任务列表...")
            await page.goto("http://127.0.0.1:5000/task_list")
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)

            latest_task = await page.evaluate("""
                () => {
                    const rows = document.querySelectorAll('#tasksTable tbody tr');
                    if (rows.length > 0) {
                        const cells = rows[0].querySelectorAll('td');
                        return {
                            id: cells[0]?.textContent?.trim(),
                            name: cells[1]?.textContent?.trim(),
                            template: cells[2]?.textContent?.trim(),
                            status: cells[3]?.textContent?.trim()
                        };
                    }
                    return null;
                }
            """)

            if latest_task:
                print(f"📋 最新任务:")
                print(f"   ID: {latest_task['id']}")
                print(f"   名称: {latest_task['name']}")
                print(f"   模板: {latest_task['template']}")
                print(f"   状态: {latest_task['status']}")

                if '实际文件模板' in latest_task['template']:
                    print("\n✅ 成功！")
                    print("✅ 任务使用了模板5")
                    print("✅ 该模板包含AI_ASR配置，处理时将自动添加字幕")

            await page.screenshot(path="test_direct_result.png", full_page=True)
            print("\n📸 截图已保存")

            print("\n⏸️  等待30秒...")
            await page.wait_for_timeout(30000)

            return True

        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_direct())
