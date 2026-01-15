"""
新榜小红书数据抓取器
抓取 https://xh.newrank.cn/content/topicRank/hotTopic
"""
import re
import time
import yaml
from pathlib import Path
from typing import Optional
from datetime import datetime

from playwright.async_api import Page, Locator

from .browser_manager import BrowserManager
from ..models.topic import XHSTopic
from ..utils.logger import get_logger

logger = get_logger()


class SelectorConfig:
    """选择器配置管理"""

    def __init__(self, config_path: str = "config/scraper.yaml"):
        """
        初始化

        Args:
            config_path: 配置文件路径
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_file, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.newrank = self.config.get("newrank", {})
        self.selectors = self.newrank.get("selectors", {})
        self.wait_config = self.newrank.get("wait", {})
        self.scroll_config = self.newrank.get("scroll", {})
        self.request_config = self.newrank.get("request", {})
        self.filters = self.config.get("filters", {})

    @property
    def base_url(self) -> str:
        """获取基础URL"""
        return self.newrank.get("base_url", "")

    @property
    def timeout(self) -> int:
        """获取超时时间"""
        return self.wait_config.get("timeout", 15000)

    @property
    def scroll_enabled(self) -> bool:
        """是否启用滚动"""
        return self.scroll_config.get("enabled", True)

    @property
    def max_scrolls(self) -> int:
        """最大滚动次数"""
        return self.scroll_config.get("max_scrolls", 5)

    @property
    def scroll_pause_ms(self) -> int:
        """滚动暂停时间（毫秒）"""
        return self.scroll_config.get("pause_ms", 2000)

    @property
    def min_heat_score(self) -> int:
        """最小热度值"""
        return self.filters.get("min_heat_score", 1000)

    @property
    def max_topics(self) -> int:
        """最大话题数"""
        return self.filters.get("max_topics", 50)


class NewRankScraper:
    """新榜小红书数据抓取器"""

    def __init__(
        self, browser_manager: BrowserManager, config_path: str = "config/scraper.yaml"
    ):
        """
        初始化

        Args:
            browser_manager: 浏览器管理器
            config_path: 配置文件路径
        """
        self.browser = browser_manager
        self.config = SelectorConfig(config_path)

    async def scrape_hot_topics(self, limit: int = 50) -> list[XHSTopic]:
        """
        抓取热门话题

        Args:
            limit: 最大话题数量

        Returns:
            话题列表
        """
        logger.info(f"开始抓取新榜小红书热门话题，目标数量: {limit}")

        page = await self.browser.new_page()

        try:
            # 1. 导航到目标页面
            logger.info(f"导航到: {self.config.base_url}")
            await page.goto(
                self.config.base_url, timeout=self.config.request_config.get("timeout", 30000)
            )

            # 2. 等待内容加载
            logger.info("等待内容加载...")
            await self._wait_for_content(page)

            # 3. 滚动加载更多（如果启用）
            if self.config.scroll_enabled:
                logger.info("滚动加载更多数据...")
                await self._scroll_to_load_more(page)

            # 4. 提取话题数据
            logger.info("开始提取话题数据...")
            topics = await self._extract_all_topics(page, limit)

            logger.info(f"抓取完成，共获取 {len(topics)} 个话题")
            return topics

        except Exception as e:
            logger.error(f"抓取失败: {e}")
            # 截图保存（用于调试）
            screenshot_path = f"logs/error-screenshot-{int(time.time())}.png"
            await page.screenshot(path=screenshot_path)
            logger.info(f"错误截图已保存: {screenshot_path}")
            raise

        finally:
            await page.close()

    async def _wait_for_content(self, page: Page):
        """
        等待内容加载（多选择器容错）

        Args:
            page: Playwright页面实例

        Raises:
            TimeoutError: 所有选择器都超时
        """
        selectors = self.config.selectors.get("topic_list", [])

        for selector in selectors:
            try:
                logger.info(f"  尝试选择器: {selector}")
                await page.wait_for_selector(selector, timeout=self.config.timeout)
                logger.info(f"  ✅ 选择器匹配成功: {selector}")
                return
            except Exception as e:
                logger.info(f"  选择器失败: {selector}")
                continue

        raise TimeoutError("无法找到话题列表容器，所有选择器均失败")

    async def _scroll_to_load_more(self, page: Page):
        """
        滚动页面加载更多内容

        Args:
            page: Playwright页面实例
        """
        for i in range(self.config.max_scrolls):
            logger.info(f"  滚动 {i + 1}/{self.config.max_scrolls}")

            # 滚动到底部
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

            # 等待加载
            await page.wait_for_timeout(self.config.scroll_pause_ms)

    async def _extract_all_topics(self, page: Page, limit: int) -> list[XHSTopic]:
        """
        提取所有话题数据

        Args:
            page: Playwright页面实例
            limit: 最大数量

        Returns:
            话题列表
        """
        topics = []

        # 查找所有话题项
        topic_items = await self._find_topic_items(page)
        logger.info(f"  找到 {len(topic_items)} 个话题项")

        for i, item in enumerate(topic_items[:limit]):
            try:
                topic = await self._extract_topic_from_element(item, i + 1)
                if topic:
                    topics.append(topic)
                    logger.info(f"  [{i + 1}/{limit}] {topic.title} - 热度: {topic.heat_score_formatted}")
            except Exception as e:
                logger.error(f"  提取话题 {i + 1} 失败: {e}")
                continue

        return topics

    async def _find_topic_items(self, page: Page) -> list[Locator]:
        """
        查找所有话题项元素

        Args:
            page: Playwright页面实例

        Returns:
            话题元素列表
        """
        selectors = self.config.selectors.get("topic_item", [])

        for selector in selectors:
            try:
                items = page.locator(selector)
                count = await items.count()
                if count > 0:
                    logger.info(f"  使用选择器 {selector}，找到 {count} 个元素")
                    return [items.nth(i) for i in range(count)]
            except Exception:
                continue

        logger.warning("  未找到话题项，返回空列表")
        return []

    async def _extract_topic_from_element(
        self, element: Locator, index: int
    ) -> Optional[XHSTopic]:
        """
        从DOM元素提取话题数据

        Args:
            element: 话题项元素
            index: 索引（用作排名）

        Returns:
            话题对象，提取失败返回None
        """
        try:
            # 提取各字段
            title = await self._try_extract_text(element, "title")
            if not title:
                return None  # 标题为必需字段

            heat_score = await self._try_extract_number(element, "heat_score")
            category = await self._try_extract_text(element, "category")
            trend = await self._extract_trend(element)

            # 生成唯一ID
            topic_id = f"topic_{index}_{int(time.time())}"

            return XHSTopic(
                topic_id=topic_id,
                title=title.strip(),
                heat_score=heat_score,
                category=category or "未分类",
                rank=index,
                trend_direction=trend["direction"],
                trend_icon=trend["icon"],
                rank_change=trend["change"],
                crawled_at=datetime.now(),
            )

        except Exception as e:
            logger.error(f"  提取话题数据失败 (index={index}): {e}")
            return None

    async def _try_extract_text(
        self, element: Locator, field_name: str
    ) -> str:
        """
        尝试多个选择器提取文本

        Args:
            element: 父元素
            field_name: 字段名（在config中的key）

        Returns:
            提取的文本，失败返回空字符串
        """
        selectors = self.config.selectors.get(field_name, [])

        for selector in selectors:
            try:
                el = element.locator(selector).first
                if await el.count() > 0:
                    text = await el.text_content()
                    if text and text.strip():
                        return text.strip()
            except Exception:
                continue

        return ""

    async def _try_extract_number(
        self, element: Locator, field_name: str
    ) -> int:
        """
        尝试提取数值（支持"万"、"亿"单位）

        Args:
            element: 父元素
            field_name: 字段名

        Returns:
            提取的数值，失败返回0
        """
        text = await self._try_extract_text(element, field_name)
        if not text:
            return 0

        return self._parse_number(text)

    def _parse_number(self, text: str) -> int:
        """
        解析数值字符串（支持中文单位）

        Args:
            text: 数值字符串，如"12.5万"、"1.2亿"

        Returns:
            整数值
        """
        text = text.strip()

        # 移除逗号
        text = text.replace(",", "")

        # 匹配数字
        match = re.search(r"([\d.]+)\s*([万亿]?)", text)
        if not match:
            return 0

        num_str, unit = match.groups()

        try:
            num = float(num_str)
        except ValueError:
            return 0

        # 单位转换
        if unit == "万":
            return int(num * 10_000)
        elif unit == "亿":
            return int(num * 100_000_000)
        else:
            return int(num)

    async def _extract_trend(self, element: Locator) -> dict:
        """
        提取趋势信息

        Args:
            element: 话题项元素

        Returns:
            趋势信息字典 {"direction": "up/down/stable", "icon": "↑/↓/→", "change": 0}
        """
        trend_text = await self._try_extract_text(element, "trend")

        if not trend_text:
            return {"direction": "stable", "icon": "→", "change": 0}

        # 检测趋势方向
        if "↑" in trend_text or "up" in trend_text.lower() or "上升" in trend_text:
            direction = "up"
            icon = "↑"
        elif "↓" in trend_text or "down" in trend_text.lower() or "下降" in trend_text:
            direction = "down"
            icon = "↓"
        elif "new" in trend_text.lower() or "新" in trend_text:
            direction = "new"
            icon = "🆕"
        else:
            direction = "stable"
            icon = "→"

        # 提取变化数值
        change_match = re.search(r"(\d+)", trend_text)
        change = int(change_match.group(1)) if change_match else 0

        # 下降趋势的变化值为负数
        if direction == "down":
            change = -change

        return {"direction": direction, "icon": icon, "change": change}

    async def scrape_with_retry(
        self, max_retries: int = 3, limit: int = 50
    ) -> list[XHSTopic]:
        """
        带重试的抓取

        Args:
            max_retries: 最大重试次数
            limit: 最大话题数

        Returns:
            话题列表

        Raises:
            Exception: 重试失败后抛出异常
        """
        for attempt in range(max_retries):
            try:
                return await self.scrape_hot_topics(limit)
            except Exception as e:
                logger.warning(f"抓取失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise
