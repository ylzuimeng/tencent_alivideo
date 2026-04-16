"""
检查文件卡片结构
"""
import asyncio
import os
from playwright.async_api import async_playwright

VIDEO_PATH = "/Users/yanglei/Downloads/用所选项目新建的文件夹 2/视频剪辑测试/main.mp4"


async def check_card_structure():
    """检查文件卡片结构"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()

        try:
            print("📍 打开上传页面...")
            await page.goto("http://127.0.0.1:5000/upload/enhanced")
            await page.wait_for_load_state("networkidle")

            print("📤 上传视频...")
            file_input = await page.query_selector("#fileInput")
            await file_input.set_input_files(VIDEO_PATH)

            print("⏳ 等待上传...")
            await page.wait_for_selector("#fileList .file-card", state="visible", timeout=30000)
            await page.wait_for_timeout(3000)
            print("✅ 文件卡片出现")

            # 检查文件卡片结构
            print("\n🔍 检查文件卡片结构...\n")

            card_info = await page.evaluate("""
                () => {
                    const card = document.querySelector('#fileList .file-card');
                    if (!card) return { error: 'No card found' };

                    const selects = Array.from(card.querySelectorAll('select')).map(s => ({
                        id: s.id,
                        name: s.name,
                        className: s.className,
                        selectedIndex: s.selectedIndex,
                        options: Array.from(s.options).slice(0, 3).map(o => ({
                            value: o.value,
                            text: o.text
                        }))
                    }));

                    const buttons = Array.from(card.querySelectorAll('button')).map(b => ({
                        text: b.textContent.trim(),
                        className: b.className,
                        onclick: b.getAttribute('onclick')
                    }));

                    return {
                        cardId: card.id,
                        cardClass: card.className,
                        innerHTML: card.innerHTML.substring(0, 3000),
                        selects,
                        buttons
                    };
                }
            """)

            print(f"卡片ID: {card_info['cardId']}")
            print(f"卡片类: {card_info['cardClass']}")

            print(f"\n找到 {len(card_info['selects'])} 个选择器:")
            for idx, sel in enumerate(card_info['selects']):
                print(f"\n  选择器 {idx + 1}:")
                print(f"    ID: {sel['id']}")
                print(f"    Name: {sel['name']}")
                print(f"    选项:")
                for opt in sel['options']:
                    print(f"      [{opt['value']}] {opt['text']}")

            print(f"\n找到 {len(card_info['buttons'])} 个按钮:")
            for idx, btn in enumerate(card_info['buttons']):
                print(f"  {idx + 1}. {btn['text']} ({btn['className']})")
                if btn['onclick']:
                    print(f"     onclick: {btn['onclick'][:50]}")

            print(f"\n卡片HTML片段:")
            print(card_info['innerHTML'][:1000])

            print("\n⏸️  等待60秒查看浏览器...")
            await page.wait_for_timeout(60000)

        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(check_card_structure())
