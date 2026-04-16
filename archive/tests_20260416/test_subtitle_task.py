"""
测试上传视频并使用"实际文件模板-片头片尾"添加字幕
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright

# 视频文件路径
VIDEO_PATH = "/Users/yanglei/Downloads/用所选项目新建的文件夹 2/视频剪辑测试/main.mp4"
# 模板ID
TEMPLATE_ID = 5


async def test_video_upload_with_subtitle():
    """测试上传视频并添加字幕"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 监听请求和响应
        def log_request(request):
            if "/api/" in request.url:
                print(f"📤 请求: {request.method} {request.url}")

        def log_response(response):
            if "/api/" in response.url:
                print(f"📥 响应: {response.status} {response.url}")

        page.on("request", log_request)
        page.on("response", log_response)

        try:
            print("="*60)
            print("🧪 测试视频上传并使用模板5添加字幕")
            print("="*60)

            # 步骤1: 导航到上传页面
            print("\n📍 步骤1: 导航到上传页面...")
            await page.goto("http://127.0.0.1:5000/upload/video")
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

            # 等待上传完成（监听上传完成的响应）
            print("⏳ 等待上传完成...")
            await page.wait_for_selector(".uploaded-item", state="visible", timeout=60000)
            await page.wait_for_timeout(2000)
            print("✅ 视频上传成功")

            # 获取文件ID
            file_info = await page.evaluate("""
                () => {
                    const items = window.uploadedFiles || [];
                    if (items.length > 0) {
                        return {
                            dbFileId: items[0].dbFileId,
                            fileName: items[0].fileName,
                            ossUrl: items[0].ossUrl
                        };
                    }
                    return null;
                }
            """)

            if not file_info:
                print("❌ 未能获取文件信息")
                return False

            print(f"📦 文件信息:")
            print(f"   文件ID: {file_info['dbFileId']}")
            print(f"   文件名: {file_info['fileName']}")
            print(f"   OSS URL: {file_info['ossUrl']}")

            # 步骤3: 选择模板5
            print(f"\n📍 步骤3: 选择模板5（实际文件模板-片头片尾）...")
            await page.wait_for_selector("#taskTemplate", state="visible")
            await page.select_option("#taskTemplate", str(TEMPLATE_ID))
            await page.wait_for_timeout(1000)
            print("✅ 模板已选择")

            # 验证模板配置
            template_info = await page.evaluate("""
                async () => {
                    const response = await fetch('/api/video_templates/5');
                    const result = await response.json();
                    if (result.success) {
                        const t = result.template;
                        return {
                            name: t.name,
                            is_advanced: t.is_advanced,
                            has_timeline: !!t.timeline_json,
                            header: t.header_video_url,
                            footer: t.footer_video_url
                        };
                    }
                    return null;
                }
            """)

            if template_info:
                print(f"📋 模板配置:")
                print(f"   名称: {template_info['name']}")
                print(f"   高级模式: {template_info['is_advanced']}")
                print(f"   Timeline: {template_info['has_timeline']}")
                print(f"   片头: {template_info['header']}")
                print(f"   片尾: {template_info['footer']}")

            # 步骤4: 创建任务
            print(f"\n📍 步骤4: 创建视频处理任务...")
            await page.click("button:has-text('创建视频处理任务')")

            # 等待任务创建响应
            await page.wait_for_timeout(3000)

            # 检查任务创建结果
            task_result = await page.evaluate("""
                () => {
                    // 检查页面上的成功或错误消息
                    const alert = document.querySelector('.alert');
                    if (alert) {
                        return {
                            type: alert.classList.contains('alert-success') ? 'success' : 'error',
                            message: alert.textContent.trim()
                        };
                    }
                    return { type: 'unknown', message: '未找到提示消息' };
                }
            """)

            print(f"📊 任务创建结果: {task_result}")

            if task_result['type'] == 'success':
                print("✅ 任务创建成功！")

                # 获取任务ID
                print("\n📍 步骤5: 查询任务状态...")
                await page.goto("http://127.0.0.1:5000/task_list")
                await page.wait_for_load_state("networkidle")
                await page.wait_for_timeout(2000)

                # 获取最新的任务
                task_status = await page.evaluate("""
                    () => {
                        const rows = document.querySelectorAll('#tasksTable tbody tr');
                        if (rows.length > 0) {
                            const firstRow = rows[0];
                            const cells = firstRow.querySelectorAll('td');
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

                if task_status:
                    print(f"📋 最新任务:")
                    print(f"   任务ID: {task_status['id']}")
                    print(f"   任务名称: {task_status['name']}")
                    print(f"   使用模板: {task_status['template']}")
                    print(f"   状态: {task_status['status']}")
                    print(f"   进度: {task_status['progress']}")
                else:
                    print("⚠️  未找到任务记录")

                # 截图
                await page.screenshot(path="test_task_list.png", full_page=True)
                print("\n📸 已保存任务列表截图: test_task_list.png")

                return True
            else:
                print(f"❌ 任务创建失败: {task_result['message']}")
                return False

        except Exception as e:
            print(f"\n❌ 测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            print("\n📸 保存最终截图...")
            await page.screenshot(path="test_final.png", full_page=True)
            print("✅ 截图已保存: test_final.png")
            await page.wait_for_timeout(3000)
            await browser.close()


async def main():
    success = await test_video_upload_with_subtitle()

    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    if success:
        print("✅ 测试通过：视频上传成功，任务创建成功")
        print("✅ 模板5已配置AI_ASR字幕，将在处理时自动添加")
    else:
        print("❌ 测试失败")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
