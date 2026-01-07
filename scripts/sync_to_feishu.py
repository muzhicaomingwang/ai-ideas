#!/opt/anaconda3/bin/python3
"""
自动同步调研报告到飞书文档
使用Playwright自动化操作
"""

import asyncio
import sys
from pathlib import Path

# 禁用输出缓冲
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

try:
    from playwright.async_api import async_playwright
    import pyperclip
except ImportError:
    print("请先安装依赖: pip install playwright pyperclip")
    sys.exit(1)


FEISHU_URL = "https://hf7l9aiqzx.feishu.cn/wiki/LBUEwgMRMie1BSk93MKcgOOvnSg"
REPORT_PATH = Path(__file__).parent.parent / "docs/research/proactive-ai-research-2026-01.md"


async def sync_to_feishu():
    """自动同步报告到飞书文档"""

    # 读取报告内容
    if not REPORT_PATH.exists():
        print(f"❌ 报告文件不存在: {REPORT_PATH}")
        return False

    report_content = REPORT_PATH.read_text(encoding="utf-8")
    print(f"✅ 已读取报告内容 ({len(report_content)} 字符)")

    # 复制到剪贴板
    pyperclip.copy(report_content)
    print("✅ 报告内容已复制到剪贴板")

    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(
            headless=False,
            channel="chrome"
        )
        context = await browser.new_context()
        page = await context.new_page()

        print(f"🌐 正在打开飞书文档...")
        await page.goto(FEISHU_URL)

        # 等待页面加载 - 检测是否需要登录
        print("⏳ 等待页面加载...")
        await page.wait_for_timeout(3000)

        # 检查是否在登录页面
        current_url = page.url
        if "accounts.feishu.cn" in current_url or "login" in current_url:
            print("\n" + "="*50)
            print("🔐 检测到需要登录，请在浏览器中完成登录...")
            print("   登录后脚本将自动继续")
            print("="*50 + "\n")

            # 等待登录完成（URL变回文档页面）
            try:
                await page.wait_for_url(
                    lambda url: "wiki" in url and "accounts" not in url,
                    timeout=300000  # 5分钟超时
                )
                print("✅ 登录成功！")
            except Exception as e:
                print(f"❌ 登录超时或失败: {e}")
                await browser.close()
                return False

        # 等待文档编辑器加载
        print("⏳ 等待文档编辑器加载...")
        await page.wait_for_timeout(3000)

        # 尝试点击文档区域进入编辑模式
        try:
            # 飞书文档的编辑区域选择器
            editor_selectors = [
                '[data-testid="doc-editor"]',
                '.doc-content',
                '.suite-markdown-container',
                '[contenteditable="true"]',
                '.editor-container',
                '.wiki-content',
                '.lark-editor',
            ]

            clicked = False
            for selector in editor_selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=2000)
                    if element:
                        await element.click()
                        clicked = True
                        print(f"✅ 已点击编辑区域: {selector}")
                        break
                except:
                    continue

            if not clicked:
                # 尝试点击页面中心区域
                print("⚠️  未找到编辑区域，尝试点击页面中心...")
                await page.click('body', position={'x': 500, 'y': 400})

            await page.wait_for_timeout(1000)

            # 全选现有内容（如果需要替换）
            print("📝 准备粘贴内容...")

            # 移动到文档末尾
            await page.keyboard.press('Meta+End')
            await page.wait_for_timeout(500)

            # 添加分隔线
            await page.keyboard.press('Enter')
            await page.keyboard.press('Enter')
            await page.keyboard.type('---')
            await page.keyboard.press('Enter')
            await page.keyboard.press('Enter')

            # 粘贴内容
            print("📋 正在粘贴报告内容...")
            await page.keyboard.press('Meta+v')

            await page.wait_for_timeout(2000)
            print("✅ 内容已粘贴！")

            # 等待用户确认
            print("\n" + "="*50)
            print("✅ 同步完成！")
            print("   请检查飞书文档内容是否正确")
            print("   确认后关闭浏览器窗口")
            print("="*50 + "\n")

            # 等待用户关闭浏览器
            try:
                await page.wait_for_event('close', timeout=300000)
            except:
                pass

        except Exception as e:
            print(f"❌ 粘贴失败: {e}")
            print("   请手动在文档中按 Cmd+V 粘贴")

            # 等待用户手动操作
            try:
                await page.wait_for_event('close', timeout=300000)
            except:
                pass

        await browser.close()
        print("✅ 浏览器已关闭")
        return True


if __name__ == "__main__":
    print("🚀 飞书文档自动同步工具")
    print("-" * 40)
    result = asyncio.run(sync_to_feishu())
    sys.exit(0 if result else 1)
