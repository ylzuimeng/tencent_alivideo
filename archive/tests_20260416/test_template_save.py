"""
测试统一模板管理页面的保存功能
"""
import asyncio
import json
from playwright.async_api import async_playwright

# 测试 Timeline JSON（使用 AI_ASR 模式）
TEST_TIMELINE = json.dumps({
    "VideoTracks": [
        {
            "VideoTrackClips": [
                {
                    "MediaURL": "https://krillin-3.oss-cn-shanghai.aliyuncs.com/uploads/20260411_054117_start.mp4",
                    "Duration": 3
                },
                {
                    "MediaURL": "$main_video",
                    "MainTrack": True,
                    "Effects": [
                        {
                            "Type": "AI_ASR",
                            "Font": "AlibabaPuHuiTi",
                            "Alignment": "BottomCenter",
                            "Y": 1700,
                            "Outline": 3,
                            "OutlineColour": "#000000",
                            "FontSize": 50,
                            "FontColor": "#FFFFFF",
                            "FontFace": {
                                "Bold": False,
                                "Italic": False,
                                "Underline": False
                            }
                        }
                    ]
                },
                {
                    "MediaURL": "https://krillin-3.oss-cn-shanghai.aliyuncs.com/uploads/20260411_054117_start.mp4",
                    "Duration": 3
                }
            ]
        }
    ]
}, ensure_ascii=False)


async def test_advanced_template_save():
    """测试高级模板保存功能"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            print("🌐 导航到模板管理页面...")
            await page.goto("http://127.0.0.1:5000/templates/unified")
            await page.wait_for_load_state("networkidle")

            print("✅ 页面加载成功")

            # 点击"新建模板"按钮
            print("\n📝 点击新建模板按钮...")
            await page.click("button:has-text('新建模板')")
            await page.wait_for_timeout(500)

            # 切换到高级模式
            print("🔄 切换到高级模式...")
            await page.click("a#advancedModeTab")
            await page.wait_for_timeout(500)

            # 填写表单
            print("⌨️  填写表单...")

            # 模板名称
            await page.fill("#templateNameAdvanced", "测试AI_ASR字幕模板")
            print("  ✓ 模板名称")

            # Timeline JSON
            await page.fill("#timelineJson", TEST_TIMELINE)
            print("  ✓ Timeline JSON (带AI_ASR)")

            # 输出配置
            output_config = json.dumps({
                "Width": 1280,
                "Height": 720
            }, ensure_ascii=False)
            await page.fill("#outputMediaConfig", output_config)
            print("  ✓ 输出配置")

            # 点击"保存高级模板"按钮
            print("\n💾 保存模板...")
            async with page.expect_response(
                lambda resp: "/api/video_templates" in resp.url and resp.status in [200, 201]
            ) as response_info:
                await page.click("button:has-text('保存高级模板')")

            response = await response_info.value
            result = await response.json()

            print(f"\n📊 响应状态码: {response.status}")
            print(f"📦 响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")

            # 验证结果
            if result.get('success'):
                print("\n✅ 模板保存成功！")
                print(f"   模板ID: {result.get('template_id')}")

                # 等待 Toast 提示
                await page.wait_for_timeout(2000)

                # 验证模板是否出现在列表中
                print("\n🔍 验证模板是否出现在列表中...")
                await page.click("button:has-text('模板列表')")
                await page.wait_for_timeout(1000)

                # 检查是否包含新模板
                page_content = await page.content()
                if "测试AI_ASR字幕模板" in page_content:
                    print("✅ 模板已成功添加到列表！")
                    return True
                else:
                    print("⚠️  模板未在列表中找到")
                    return False
            else:
                print(f"\n❌ 模板保存失败: {result.get('message')}")
                return False

        except Exception as e:
            print(f"\n❌ 测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            print("\n📸 截图保存为: test_template_save.png")
            await page.screenshot(path="test_template_save.png", full_page=True)
            await page.wait_for_timeout(2000)
            await browser.close()


async def test_simple_template_save():
    """测试简单模板保存功能"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            print("\n" + "="*50)
            print("📝 测试简单模式保存")
            print("="*50)

            print("🌐 导航到模板管理页面...")
            await page.goto("http://127.0.0.1:5000/templates/unified")
            await page.wait_for_load_state("networkidle")

            # 点击"新建模板"按钮
            print("\n📝 点击新建模板按钮...")
            await page.click("button:has-text('新建模板')")
            await page.wait_for_timeout(500)

            # 确保在简单模式
            print("✅ 确认简单模式...")
            simple_tab = await page.is_visible("#simpleModeTab.active")
            if not simple_tab:
                await page.click("a#simpleModeTab")
                await page.wait_for_timeout(500)

            # 填写表单
            print("⌨️  填写简单模式表单...")

            # 模板名称
            await page.fill("#templateName", "测试简单模板")
            print("  ✓ 模板名称")

            # 选择分类
            await page.select_option("#templateCategory", "medical")
            print("  ✓ 分类: 医疗健康宣教")

            # 启用字幕
            await page.check("#enableSubtitle")
            print("  ✓ 启用字幕")

            # 字幕位置
            await page.select_option("#subtitlePosition", "bottom")
            print("  ✓ 字幕位置: 底部")

            # 点击"保存模板"按钮
            print("\n💾 保存简单模板...")
            async with page.expect_response(
                lambda resp: "/api/video_templates" in resp.url and resp.status in [200, 201]
            ) as response_info:
                await page.click("button:has-text('保存模板')")

            response = await response_info.value
            result = await response.json()

            print(f"\n📊 响应状态码: {response.status}")
            print(f"📦 响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")

            # 验证结果
            if result.get('success'):
                print("\n✅ 简单模板保存成功！")
                print(f"   模板ID: {result.get('template_id')}")
                return True
            else:
                print(f"\n❌ 简单模板保存失败: {result.get('message')}")
                return False

        except Exception as e:
            print(f"\n❌ 测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            print("\n📸 截图保存为: test_simple_template_save.png")
            await page.screenshot(path="test_simple_template_save.png", full_page=True)
            await page.wait_for_timeout(2000)
            await browser.close()


async def main():
    """运行所有测试"""
    print("\n" + "="*50)
    print("🧪 统一模板管理页面 - 保存功能测试")
    print("="*50 + "\n")

    # 测试高级模板
    advanced_result = await test_advanced_template_save()

    # 测试简单模板
    simple_result = await test_simple_template_save()

    # 总结
    print("\n" + "="*50)
    print("📊 测试总结")
    print("="*50)
    print(f"高级模板保存: {'✅ 通过' if advanced_result else '❌ 失败'}")
    print(f"简单模板保存: {'✅ 通过' if simple_result else '❌ 失败'}")
    print("="*50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
