"""
调试简单模式保存功能
"""
import asyncio
import json
from playwright.async_api import async_playwright


async def test_simple_save_with_debug():
    """测试简单模式保存，带详细调试信息"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 监听所有请求
        def log_request(request):
            print(f"📤 请求: {request.method} {request.url}")

        def log_response(response):
            if "/api/" in response.url:
                print(f"📥 响应: {response.status} {response.url}")
                try:
                    # 尝试获取响应体
                    body = response.text()
                    print(f"   内容: {body[:200]}")
                except:
                    pass

        page.on("request", log_request)
        page.on("response", log_response)

        # 监听控制台消息
        def log_console(msg):
            print(f"🖥️  控制台 [{msg.type}]: {msg.text}")

        page.on("console", log_console)

        try:
            print("🌐 导航到模板管理页面...")
            await page.goto("http://127.0.0.1:5000/templates/unified")
            await page.wait_for_load_state("networkidle")

            # 点击"新建模板"
            print("\n📝 点击新建模板...")
            await page.click("button:has-text('新建模板')")
            await page.wait_for_timeout(1000)

            # 填写表单
            print("⌨️  填写表单...")

            # 等待表单出现
            await page.wait_for_selector("#templateName", state="visible")

            # 模板名称
            await page.fill("#templateName", "调试简单模板")
            print("  ✓ 模板名称")

            # 分类
            await page.select_option("#templateCategory", "medical")
            print("  ✓ 分类")

            # 描述
            await page.fill("#templateDescription", "这是一个测试模板")
            print("  ✓ 描述")

            # 启用字幕
            await page.check("#enableSubtitle")
            print("  ✓ 启用字幕")

            # 字幕位置
            await page.select_option("#subtitlePosition", "bottom")
            print("  ✓ 字幕位置")

            # 提取音频
            await page.check("#extractAudio")
            print("  ✓ 提取音频")

            # 打印表单数据
            print("\n📋 当前表单数据:")
            template_name = await page.input_value("#templateName")
            category = await page.input_value("#templateCategory")
            enable_subtitle = await page.is_checked("#enableSubtitle")
            print(f"  name: {template_name}")
            print(f"  category: {category}")
            print(f"  enable_subtitle: {enable_subtitle}")

            # 截图
            await page.screenshot(path="debug_form.png")
            print("📸 已截图: debug_form.png")

            # 点击保存按钮
            print("\n💾 点击保存按钮...")

            # 使用 JavaScript 执行保存，以便捕获错误
            save_result = await page.evaluate("""
                async () => {
                    try {
                        const data = {
                            name: document.getElementById('templateName').value,
                            category: document.getElementById('templateCategory').value,
                            description: document.getElementById('templateDescription').value,
                            header_video_url: document.getElementById('headerVideo').value,
                            footer_video_url: document.getElementById('footerVideo').value,
                            enable_subtitle: document.getElementById('enableSubtitle').checked,
                            subtitle_position: document.getElementById('subtitlePosition').value,
                            subtitle_extract_audio: document.getElementById('extractAudio').checked,
                            is_advanced: false
                        };

                        console.log("发送数据:", data);

                        const response = await fetch('/api/video_templates', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify(data)
                        });

                        const result = await response.json();
                        console.log("响应结果:", result);

                        return {success: true, status: response.status, data: result};
                    } catch (error) {
                        console.error("保存错误:", error);
                        return {success: false, error: error.message};
                    }
                }
            """)

            print(f"\n📊 保存结果: {json.dumps(save_result, ensure_ascii=False, indent=2)}")

            if save_result.get('success'):
                result_data = save_result.get('data', {})
                if result_data.get('success'):
                    print("\n✅ 简单模板保存成功！")
                    print(f"   模板ID: {result_data.get('template_id')}")
                else:
                    print(f"\n❌ 保存失败: {result_data.get('message')}")
            else:
                print(f"\n❌ 保存异常: {save_result.get('error')}")

            await page.wait_for_timeout(2000)

        except Exception as e:
            print(f"\n❌ 测试异常: {str(e)}")
            import traceback
            traceback.print_exc()

        finally:
            await page.screenshot(path="debug_final.png", full_page=True)
            print("📸 已截图: debug_final.png")
            await page.wait_for_timeout(2000)
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_simple_save_with_debug())
