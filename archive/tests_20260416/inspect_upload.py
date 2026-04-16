"""
检查上传后的页面结构
"""
import asyncio
import os
from playwright.async_api import async_playwright

VIDEO_PATH = "/Users/yanglei/Downloads/用所选项目新建的文件夹 2/视频剪辑测试/main.mp4"


async def inspect_upload():
    """检查上传后的页面结构"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            print("📍 打开上传页面...")
            await page.goto("http://127.0.0.1:5000/upload/enhanced")
            await page.wait_for_load_state("networkidle")

            print("📤 上传视频...")
            file_input = await page.query_selector("#fileInput")
            await file_input.set_input_files(VIDEO_PATH)

            print("⏳ 等待上传...")
            await page.wait_for_timeout(5000)

            # 检查页面结构
            print("\n🔍 检查页面结构...")

            structure = await page.evaluate("""
                () => {
                    const result = {
                        fileCards: [],
                        allButtons: [],
                        allSelects: []
                    };

                    // 查找文件卡片
                    const cards = document.querySelectorAll('[class*="file"], [class*="card"], [id*="file"]');
                    cards.forEach(card => {
                        const buttons = Array.from(card.querySelectorAll('button')).map(b => ({
                            text: b.textContent.trim(),
                            class: b.className,
                            onclick: b.getAttribute('onclick')
                        }));

                        const selects = Array.from(card.querySelectorAll('select')).map(s => ({
                            id: s.id,
                            name: s.name,
                            options: Array.from(s.options).map(o => o.text)
                        }));

                        result.fileCards.push({
                            tagName: card.tagName,
                            id: card.id,
                            className: card.className,
                            innerHTML: card.innerHTML.substring(0, 300),
                            buttons,
                            selects
                        });
                    });

                    // 查找所有按钮
                    const allButtons = document.querySelectorAll('button');
                    result.allButtons = Array.from(allButtons).map(b => ({
                        text: b.textContent.trim(),
                        className: b.className,
                        onclick: b.getAttribute('onclick')
                    }));

                    // 查找所有select
                    const allSelects = document.querySelectorAll('select');
                    result.allSelects = Array.from(allSelects).map(s => s.id);

                    // 检查window.uploadedFiles
                    result.uploadedFiles = window.uploadedFiles ? window.uploadedFiles.length : 0;

                    return result;
                }
            """)

            print("\n📋 页面结构分析:")
            print(f"\n文件卡片数量: {len(structure['fileCards'])}")
            for idx, card in enumerate(structure['fileCards'][:3]):
                print(f"\n卡片 {idx + 1}:")
                print(f"  标签: {card['tagName']}")
                print(f"  ID: {card['id']}")
                print(f"  类名: {card['className']}")
                print(f"  HTML片段: {card['innerHTML'][:100]}")
                if card['buttons']:
                    print(f"  按钮:")
                    for btn in card['buttons']:
                        print(f"    - {btn['text']} ({btn['class']})")

            print(f"\n所有按钮: {len(structure['allButtons'])}")
            for btn in structure['allButtons'][:10]:
                if btn['text']:
                    print(f"  - {btn['text']}")

            print(f"\n所有Select:")
            for sel_id in structure['allSelects']:
                print(f"  - #{sel_id}")

            print(f"\nuploadedFiles: {structure['uploadedFiles']}")

            # 截图
            await page.screenshot(path="inspect_upload.png", full_page=True)
            print("\n📸 截图已保存: inspect_upload.png")

            # 等待查看
            print("\n⏸️  等待30秒，请查看浏览器...")
            await page.wait_for_timeout(30000)

        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(inspect_upload())
