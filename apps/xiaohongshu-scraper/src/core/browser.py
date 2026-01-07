"""
浏览器管理器 - 管理 Playwright 浏览器实例
"""
import asyncio
import json
import os
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class BrowserManager:
    """
    浏览器管理器

    负责:
    - 浏览器实例生命周期管理
    - 登录态（Cookie）管理
    - 页面池管理
    """

    def __init__(
        self,
        headless: bool = True,
        cookie_file: str = "cookies.json",
        data_dir: str = "./data",
    ):
        self.headless = headless
        self.cookie_file = Path(data_dir) / cookie_file
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._is_logged_in = False

    async def start(self) -> None:
        """启动浏览器"""
        if self._browser:
            return

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )

        # 创建上下文
        self._context = await self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        # 加载 Cookie
        await self._load_cookies()

    async def stop(self) -> None:
        """停止浏览器"""
        if self._context:
            # 保存 Cookie
            await self._save_cookies()
            await self._context.close()
            self._context = None

        if self._browser:
            await self._browser.close()
            self._browser = None

        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def new_page(self) -> Page:
        """获取新页面"""
        if not self._context:
            await self.start()
        return await self._context.new_page()

    async def _load_cookies(self) -> None:
        """加载保存的 Cookie"""
        if self.cookie_file.exists():
            try:
                with open(self.cookie_file, "r", encoding="utf-8") as f:
                    cookies = json.load(f)
                await self._context.add_cookies(cookies)
                self._is_logged_in = True
                print(f"[BrowserManager] Loaded {len(cookies)} cookies")
            except Exception as e:
                print(f"[BrowserManager] Failed to load cookies: {e}")

    async def _save_cookies(self) -> None:
        """保存 Cookie"""
        if self._context:
            try:
                cookies = await self._context.cookies()
                with open(self.cookie_file, "w", encoding="utf-8") as f:
                    json.dump(cookies, f, ensure_ascii=False, indent=2)
                print(f"[BrowserManager] Saved {len(cookies)} cookies")
            except Exception as e:
                print(f"[BrowserManager] Failed to save cookies: {e}")

    async def login_with_qrcode(self) -> bool:
        """
        二维码登录

        Returns:
            是否登录成功
        """
        page = await self.new_page()

        try:
            # 导航到登录页
            await page.goto("https://www.xiaohongshu.com/explore")
            await page.wait_for_timeout(2000)

            # 点击登录按钮
            login_btn = page.locator('button:has-text("登录")')
            if await login_btn.count() > 0:
                await login_btn.first.click()
                await page.wait_for_timeout(1000)

            print("[BrowserManager] Please scan the QR code to login...")
            print("[BrowserManager] Waiting for login (timeout: 120s)...")

            # 等待登录成功（检测用户头像出现）
            try:
                await page.wait_for_selector(
                    'img[class*="avatar"]',
                    timeout=120000,
                )
                self._is_logged_in = True
                await self._save_cookies()
                print("[BrowserManager] Login successful!")
                return True
            except Exception:
                print("[BrowserManager] Login timeout")
                return False

        finally:
            await page.close()

    async def check_login_status(self) -> bool:
        """
        检查登录状态

        Returns:
            是否已登录
        """
        page = await self.new_page()

        try:
            await page.goto("https://www.xiaohongshu.com/explore")
            await page.wait_for_timeout(3000)

            # 检查是否有登录按钮
            login_btn = page.locator('button:has-text("登录")')
            if await login_btn.count() > 0:
                self._is_logged_in = False
                return False

            self._is_logged_in = True
            return True

        except Exception as e:
            print(f"[BrowserManager] Check login status failed: {e}")
            return False

        finally:
            await page.close()

    @property
    def is_logged_in(self) -> bool:
        """是否已登录"""
        return self._is_logged_in

    @property
    def is_ready(self) -> bool:
        """浏览器是否就绪"""
        return self._browser is not None and self._context is not None
