"""
浏览器管理器 - 管理 Playwright 浏览器实例
复用自 xiaohongshu-scraper，简化为通用版本
"""
import json
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class BrowserManager:
    """
    浏览器管理器

    负责:
    - 浏览器实例生命周期管理
    - Cookie 持久化（用于需要登录的网站）
    - 页面管理
    """

    def __init__(
        self,
        headless: bool = True,
        cookie_file: str = "cookies.json",
        data_dir: str = "./data",
    ):
        """
        初始化

        Args:
            headless: 是否无头模式
            cookie_file: Cookie文件名
            data_dir: 数据目录路径
        """
        self.headless = headless
        self.cookie_file = Path(data_dir) / cookie_file
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None

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

        # 创建浏览器上下文
        self._context = await self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        # 加载 Cookie（如果存在）
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
        """
        创建新页面

        Returns:
            Page实例
        """
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
                print(f"[BrowserManager] Loaded {len(cookies)} cookies")
            except Exception as e:
                print(f"[BrowserManager] Failed to load cookies: {e}")

    async def _save_cookies(self) -> None:
        """保存当前 Cookie"""
        if self._context:
            try:
                cookies = await self._context.cookies()
                with open(self.cookie_file, "w", encoding="utf-8") as f:
                    json.dump(cookies, f, ensure_ascii=False, indent=2)
                print(f"[BrowserManager] Saved {len(cookies)} cookies")
            except Exception as e:
                print(f"[BrowserManager] Failed to save cookies: {e}")

    @property
    def is_ready(self) -> bool:
        """浏览器是否就绪"""
        return self._browser is not None and self._context is not None

    async def __aenter__(self):
        """上下文管理器入口"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        await self.stop()
