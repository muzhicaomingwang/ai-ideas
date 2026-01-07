#!/usr/bin/env python3
"""
连接到已运行的 Chrome 浏览器（复用登录状态）

使用方法:
1. 先运行 ./start_chrome_debug.sh 启动 Chrome
2. 在 Chrome 中手动登录小红书
3. 运行此脚本连接并测试
"""
import asyncio
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from playwright.async_api import async_playwright


async def connect_to_chrome(debug_url: str = "http://localhost:9222"):
    """连接到已运行的 Chrome"""

    print(f"正在连接到 Chrome: {debug_url}")

    async with async_playwright() as p:
        try:
            # 通过 CDP 连接到 Chrome
            browser = await p.chromium.connect_over_cdp(debug_url)
            print(f"✓ 已连接到 Chrome")
            print(f"  版本: {browser.version}")

            # 获取所有上下文
            contexts = browser.contexts
            print(f"  上下文数量: {len(contexts)}")

            if not contexts:
                print("  创建新上下文...")
                context = await browser.new_context()
            else:
                context = contexts[0]

            # 获取所有页面
            pages = context.pages
            print(f"  页面数量: {len(pages)}")

            for i, page in enumerate(pages):
                print(f"    [{i}] {page.url[:60]}...")

            return browser, context, pages

        except Exception as e:
            print(f"✗ 连接失败: {e}")
            print("")
            print("请确保:")
            print("  1. 已运行 ./start_chrome_debug.sh")
            print("  2. Chrome 正在监听端口 9222")
            return None, None, None


async def test_xiaohongshu(context):
    """测试小红书访问"""

    print("\n正在测试小红书访问...")

    page = await context.new_page()

    try:
        # 访问小红书
        await page.goto("https://www.xiaohongshu.com/explore")
        await page.wait_for_timeout(3000)

        # 检查登录状态
        login_btn = page.locator('button:has-text("登录")')
        if await login_btn.count() > 0:
            print("✗ 未登录小红书")
            print("  请在 Chrome 中手动登录后重试")
            return False
        else:
            print("✓ 已登录小红书")

            # 获取用户信息
            avatar = page.locator('img[class*="avatar"]')
            if await avatar.count() > 0:
                print("  检测到用户头像")

            return True

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

    finally:
        await page.close()


async def scrape_note(context, url: str):
    """抓取指定笔记"""

    print(f"\n正在抓取: {url}")

    page = await context.new_page()

    try:
        await page.goto(url)
        await page.wait_for_timeout(3000)

        # 检查是否能访问
        error_text = page.locator('text="当前笔记暂时无法浏览"')
        if await error_text.count() > 0:
            print("✗ 笔记无法访问（可能需要登录或已删除）")
            return None

        # 提取标题
        title_el = page.locator('[id="detail-title"], [class*="title"]').first
        title = ""
        if await title_el.count() > 0:
            title = await title_el.text_content()
            title = title.strip() if title else ""

        # 提取内容
        content_el = page.locator('[id="detail-desc"], [class*="desc"]').first
        content = ""
        if await content_el.count() > 0:
            content = await content_el.text_content()
            content = content.strip() if content else ""

        # 提取作者
        author_el = page.locator('[class*="author-name"], [class*="user-name"]').first
        author = ""
        if await author_el.count() > 0:
            author = await author_el.text_content()
            author = author.strip() if author else ""

        # 提取图片数量
        images = page.locator('[class*="swiper"] img, [class*="slide"] img')
        image_count = await images.count()

        print(f"✓ 抓取成功")
        print(f"  标题: {title[:50]}..." if len(title) > 50 else f"  标题: {title}")
        print(f"  作者: {author}")
        print(f"  内容: {content[:100]}..." if len(content) > 100 else f"  内容: {content}")
        print(f"  图片: {image_count} 张")

        return {
            "title": title,
            "content": content,
            "author": author,
            "image_count": image_count,
        }

    except Exception as e:
        print(f"✗ 抓取失败: {e}")
        return None

    finally:
        await page.close()


async def main():
    """主函数"""

    print("=" * 60)
    print("Playwright Chrome 连接测试")
    print("=" * 60)

    # 连接 Chrome
    browser, context, pages = await connect_to_chrome()

    if not browser:
        return

    try:
        # 测试小红书登录状态
        logged_in = await test_xiaohongshu(context)

        if logged_in:
            # 测试抓取一个笔记
            test_url = input("\n请输入小红书笔记链接（或按 Enter 跳过）: ").strip()

            if test_url:
                await scrape_note(context, test_url)

        print("\n" + "=" * 60)
        print("测试完成！")
        print("Chrome 会话保持连接，可继续使用")
        print("=" * 60)

    finally:
        # 注意：不要关闭 browser，保持连接
        pass


if __name__ == "__main__":
    asyncio.run(main())
