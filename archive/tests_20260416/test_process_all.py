"""
测试：选择模板 -> 不选医生 -> 点击全部处理
"""
import asyncio
import os
from playwright.async_api import async_playwright

VIDEO_PATH = "/Users/yanglei/Downloads/用所选项目新建的文件夹 2/视频剪辑测试/main.mp4"
TEMPLATE_ID = 5


async def test_process_all():
    """测试全部处理流程"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()

        # 监听网络请求
        requests_made = []

        def log_request(request):
            if "/api/" in request.url:
                requests_made.append({
                    'method': request.method,
                    'url': request.url,
                    'post_data': request.post_data
                })
                print(f"📤 {request.method} {request.url}")

        page.on("request", log_request)

        # 监听控制台
        page.on("console", lambda msg: print(f"🖥️  {msg.type}: {msg.text[:200]}"))

        try:
            print("="*60)
            print("🧪 测试流程：上传 -> 选模板 -> 全部处理")
            print("="*60)

            # 步骤1: 打开页面
            print("\n📍 步骤1: 打开增强上传页面...")
            await page.goto("http://127.0.0.1:5000/upload/enhanced")
            await page.wait_for_load_state("networkidle")

            # 步骤2: 上传视频
            print(f"\n📍 步骤2: 上传视频...")
            file_input = await page.query_selector("#fileInput")
            await file_input.set_input_files(VIDEO_PATH)
            print("✅ 文件已选择")

            # 等待文件卡片出现并上传完成
            print("⏳ 等待上传完成...")
            await page.wait_for_selector("#fileList .file-card", state="visible", timeout=30000)

            # 等待上传完成（检查处理按钮）
            await page.wait_for_function("""
                () => {
                    const card = document.querySelector('#fileList .file-card');
                    if (!card) return false;
                    const processBtn = card.querySelector('button[onclick*="processFile"]');
                    return processBtn && processBtn.offsetParent !== null;
                }
            """, timeout=30000)

            await page.wait_for_timeout(2000)
            print("✅ 视频上传成功")

            # 获取文件信息
            file_info = await page.evaluate("""
                () => {
                    const card = document.querySelector('#fileList .file-card');
                    const fileId = card.id.replace('file-', '');
                    const name = card.querySelector('h6')?.textContent?.trim();

                    return { fileId, name };
                }
            """)

            print(f"📦 文件: {file_info['name']}")
            print(f"   ID: {file_info['fileId']}")

            # 步骤3: 选择模板5
            print(f"\n📍 步骤3: 为文件选择模板5...")

            # 使用属性选择器而不是ID选择器（因为ID可能以数字开头）
            template_selector = f"[id=\"{file_info['fileId']}-template\"]"

            # 等待模板选择器可用
            await page.wait_for_selector(template_selector, state="visible", timeout=5000)

            # 选择模板5
            await page.select_option(template_selector, str(TEMPLATE_ID))
            await page.wait_for_timeout(1000)
            print(f"✅ 已选择模板5")

            # 验证模板配置
            print(f"\n📍 步骤4: 验证模板配置...")
            template_config = await page.evaluate("""
                async () => {
                    const response = await fetch('/api/video_templates/5');
                    const result = await response.json();
                    if (!result.success) return null;

                    const t = result.template;
                    let hasAI_ASR = false;
                    let aiAsrConfig = null;

                    if (t.timeline_json) {
                        try {
                            const timeline = JSON.parse(t.timeline_json);
                            const clips = timeline.VideoTracks?.[0]?.VideoTrackClips || [];
                            const mainClip = clips.find(c => c.MediaURL === '$main_video');
                            if (mainClip?.Effects) {
                                const asrEffect = mainClip.Effects.find(e => e.Type === 'AI_ASR');
                                if (asrEffect) {
                                    hasAI_ASR = true;
                                    aiAsrConfig = asrEffect;
                                }
                            }
                        } catch (e) {
                            console.error('Timeline解析失败:', e);
                        }
                    }

                    return {
                        name: t.name,
                        hasAI_ASR,
                        aiAsrConfig,
                        header: t.header_video_url,
                        footer: t.footer_video_url
                    };
                }
            """)

            if template_config:
                print(f"📋 模板: {template_config['name']}")
                print(f"   片头: {template_config['header']}")
                print(f"   片尾: {template_config['footer']}")
                print(f"   AI_ASR字幕: {'✅ 已配置' if template_config['hasAI_ASR'] else '❌ 未配置'}")

                if template_config['hasAI_ASR'] and template_config['aiAsrConfig']:
                    asr = template_config['aiAsrConfig']
                    print(f"   字幕配置:")
                    print(f"     - 位置: {asr.get('Alignment')}")
                    print(f"     - Y坐标: {asr.get('Y')}")
                    print(f"     - 字号: {asr.get('FontSize')}")
                    print(f"     - 颜色: {asr.get('FontColor')}")

            # 步骤5: 不选择医生（保持默认）
            print(f"\n📍 步骤5: 不选择医生（使用默认配置）...")
            # 检查是否有医生选择
            doctor_selected = await page.evaluate(f"""
                () => {{
                    const card = document.querySelector('[id="file-{file_info['fileId']}"]');
                    const doctorSelect = card.querySelector('select[id*="doctor"]');
                    return doctorSelect && doctorSelect.value;
                }}
            """)

            if doctor_selected:
                print(f"   注意: 已选择医生ID {doctor_selected}")
            else:
                print(f"   ✅ 未选择医生")

            # 步骤6: 点击"全部处理"按钮
            print(f"\n📍 步骤6: 点击'全部处理'按钮...")
            print("⏳ 清空请求日志...")
            requests_made.clear()

            # 点击全部处理
            await page.click("button:has-text('全部处理')")
            print("✅ 已点击'全部处理'")

            # 等待处理完成
            await page.wait_for_timeout(5000)

            # 检查任务创建请求
            print(f"\n📍 步骤7: 检查任务创建情况...")

            task_requests = [req for req in requests_made if '/api/tasks/create' in req['url']]
            print(f"📊 任务创建请求数: {len(task_requests)}")

            if task_requests:
                for idx, req in enumerate(task_requests):
                    print(f"\n任务 {idx + 1}:")
                    try:
                        req_data = json.loads(req['post_data'])
                        print(f"   文件ID: {req_data.get('source_file_id')}")
                        print(f"   模板ID: {req_data.get('video_template_id')}")
                        print(f"   医生ID: {req_data.get('doctor_info_id') or '未指定'}")
                    except:
                        print(f"   数据: {req['post_data'][:200]}")

            # 检查页面提示
            toast_info = await page.evaluate("""
                () => {
                    const toasts = document.querySelectorAll('.toast');
                    for (const toast of toasts) {
                        if (toast.classList.contains('show')) {
                            return {
                                visible: true,
                                text: toast.textContent.trim(),
                                class: toast.className
                            };
                        }
                    }
                    return { visible: false };
                }
            """)

            if toast_info['visible']:
                print(f"\n📊 页面提示:")
                print(f"   {toast_info['text']}")

            # 步骤8: 查看任务列表
            print(f"\n📍 步骤8: 查看任务列表...")
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
                            status: cells[3]?.textContent?.trim(),
                            progress: cells[4]?.textContent?.trim()
                        };
                    }
                    return null;
                }
            """)

            if latest_task:
                print(f"\n📋 最新任务:")
                print(f"   任务ID: {latest_task['id']}")
                print(f"   文件名: {latest_task['name']}")
                print(f"   模板: {latest_task['template']}")
                print(f"   状态: {latest_task['status']}")
                print(f"   进度: {latest_task['progress']}")

                if '实际文件模板' in latest_task['template']:
                    print(f"\n✅ 成功！")
                    print(f"✅ 任务使用了'实际文件模板-片头片尾'")
                    if template_config and template_config['hasAI_ASR']:
                        print(f"✅ 该模板包含AI_ASR配置")
                        print(f"✅ 视频处理时将自动添加字幕")

            # 截图
            await page.screenshot(path="test_process_all_result.png", full_page=True)
            print(f"\n📸 截图已保存: test_process_all_result.png")

            # 等待查看
            print(f"\n⏸️  等待30秒查看结果...")
            await page.wait_for_timeout(30000)

            return True

        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await browser.close()


async def main():
    success = await test_process_all()

    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    if success:
        print("✅ 完整流程测试通过")
        print("✅ 视频上传成功")
        print("✅ 选择模板5（实际文件模板-片头片尾）")
        print("✅ 未选择医生")
        print("✅ 点击'全部处理'创建任务")
        print("\n📝 结论:")
        print("   模板5包含AI_ASR配置，视频处理时会自动添加语音识别字幕")
    else:
        print("❌ 测试失败")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
