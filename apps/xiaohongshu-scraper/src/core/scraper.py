"""
小红书内容抓取器
"""
import asyncio
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from ..models.schemas import (
    Author,
    Comment,
    MediaItem,
    NoteContent,
    NoteStats,
    NoteType,
)
from ..utils.parser import XHSUrlParser
from .browser import BrowserManager


class XHSScraper:
    """
    小红书内容抓取器

    负责:
    - 解析笔记页面内容
    - 提取图片/视频
    - 抓取评论
    - 下载媒体文件
    """

    def __init__(
        self,
        browser_manager: BrowserManager,
        output_dir: str = "./output",
    ):
        self.browser = browser_manager
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def scrape_note(
        self,
        url: str,
        download_media: bool = True,
        fetch_comments: bool = True,
        comment_limit: int = 100,
    ) -> NoteContent:
        """
        抓取笔记内容

        Args:
            url: 小红书笔记链接
            download_media: 是否下载媒体文件
            fetch_comments: 是否抓取评论
            comment_limit: 评论数量限制

        Returns:
            笔记内容对象
        """
        # 解析 URL
        parsed = XHSUrlParser.parse(url)
        if not parsed["is_valid"]:
            raise ValueError(f"Invalid XHS URL: {url}")

        note_id = parsed["note_id"]
        normalized_url = parsed["normalized_url"]

        page = await self.browser.new_page()

        try:
            # 导航到笔记页面
            await page.goto(normalized_url)
            await page.wait_for_timeout(3000)

            # 检查是否需要登录
            if await self._check_login_required(page):
                raise PermissionError(
                    "Login required. Please run login_with_qrcode() first."
                )

            # 等待内容加载
            await self._wait_for_content(page)

            # 判断笔记类型
            note_type = await self._detect_note_type(page)

            # 提取基本信息
            title = await self._extract_title(page)
            content = await self._extract_content(page)
            tags = await self._extract_tags(page)
            author = await self._extract_author(page)
            stats = await self._extract_stats(page)

            # 提取媒体
            images = []
            video = None

            if note_type == NoteType.IMAGE:
                images = await self._extract_images(page)
            else:
                video = await self._extract_video(page)

            # 下载媒体文件
            if download_media:
                if images:
                    images = await self._download_images(images, note_id)
                if video:
                    video = await self._download_video(video, note_id)

            # 抓取评论
            comments = []
            if fetch_comments:
                comments = await self._fetch_comments(page, comment_limit)

            return NoteContent(
                note_id=note_id,
                url=url,
                type=note_type,
                title=title,
                content=content,
                tags=tags,
                author=author,
                stats=stats,
                images=images,
                video=video,
                comments=comments,
                crawled_at=datetime.now(),
            )

        finally:
            await page.close()

    async def _check_login_required(self, page: Page) -> bool:
        """检查是否需要登录"""
        # 检查是否显示登录弹窗
        login_modal = page.locator('[class*="login-modal"]')
        if await login_modal.count() > 0:
            return True

        # 检查是否显示"笔记暂时无法浏览"
        error_text = page.locator('text="当前笔记暂时无法浏览"')
        if await error_text.count() > 0:
            return True

        return False

    async def _wait_for_content(self, page: Page) -> None:
        """等待内容加载"""
        try:
            # 等待笔记容器出现
            await page.wait_for_selector(
                '[id="noteContainer"], [class*="note-container"], [class*="note-detail"]',
                timeout=10000,
            )
        except PlaywrightTimeout:
            # 尝试等待其他可能的容器
            await page.wait_for_selector(
                '[class*="content"], [class*="feeds-page"]',
                timeout=5000,
            )

    async def _detect_note_type(self, page: Page) -> NoteType:
        """检测笔记类型"""
        # 检查是否有视频元素
        video_element = page.locator('video, [class*="video-player"]')
        if await video_element.count() > 0:
            return NoteType.VIDEO
        return NoteType.IMAGE

    async def _extract_title(self, page: Page) -> str:
        """提取标题"""
        selectors = [
            '[id="detail-title"]',
            '[class*="title"]',
            'h1',
            '[class*="note-title"]',
        ]

        for selector in selectors:
            element = page.locator(selector).first
            if await element.count() > 0:
                text = await element.text_content()
                if text and text.strip():
                    return text.strip()

        return ""

    async def _extract_content(self, page: Page) -> str:
        """提取正文内容"""
        selectors = [
            '[id="detail-desc"]',
            '[class*="desc"]',
            '[class*="note-text"]',
            '[class*="content"]',
        ]

        for selector in selectors:
            element = page.locator(selector).first
            if await element.count() > 0:
                text = await element.text_content()
                if text and text.strip():
                    return text.strip()

        return ""

    async def _extract_tags(self, page: Page) -> list[str]:
        """提取标签"""
        tags = []

        # 从正文中提取 #标签
        content = await self._extract_content(page)
        tag_pattern = r"#([^\s#]+)"
        matches = re.findall(tag_pattern, content)
        tags.extend(matches)

        # 从标签元素中提取
        tag_elements = page.locator('[class*="tag"], [id*="tag"]')
        count = await tag_elements.count()
        for i in range(count):
            text = await tag_elements.nth(i).text_content()
            if text:
                tag = text.strip().lstrip("#")
                if tag and tag not in tags:
                    tags.append(tag)

        return tags

    async def _extract_author(self, page: Page) -> Author:
        """提取作者信息"""
        author_id = ""
        author_name = ""
        author_avatar = ""

        # 提取作者名称
        name_selectors = [
            '[class*="author-name"]',
            '[class*="user-name"]',
            '[class*="nickname"]',
        ]
        for selector in name_selectors:
            element = page.locator(selector).first
            if await element.count() > 0:
                text = await element.text_content()
                if text:
                    author_name = text.strip()
                    break

        # 提取作者头像
        avatar_selectors = [
            '[class*="author-avatar"] img',
            '[class*="user-avatar"] img',
            '[class*="avatar"] img',
        ]
        for selector in avatar_selectors:
            element = page.locator(selector).first
            if await element.count() > 0:
                src = await element.get_attribute("src")
                if src:
                    author_avatar = src
                    break

        # 提取作者ID（从链接中）
        author_link = page.locator('[href*="/user/profile/"]').first
        if await author_link.count() > 0:
            href = await author_link.get_attribute("href")
            if href:
                match = re.search(r"/user/profile/([a-zA-Z0-9]+)", href)
                if match:
                    author_id = match.group(1)

        return Author(
            id=author_id or "unknown",
            name=author_name or "Unknown",
            avatar=author_avatar,
        )

    async def _extract_stats(self, page: Page) -> NoteStats:
        """提取统计数据"""
        likes = 0
        collects = 0
        comments_count = 0
        shares = 0

        # 提取点赞数
        like_element = page.locator('[class*="like-count"], [class*="like"] [class*="count"]').first
        if await like_element.count() > 0:
            text = await like_element.text_content()
            likes = self._parse_count(text)

        # 提取收藏数
        collect_element = page.locator('[class*="collect-count"], [class*="collect"] [class*="count"]').first
        if await collect_element.count() > 0:
            text = await collect_element.text_content()
            collects = self._parse_count(text)

        # 提取评论数
        comment_element = page.locator('[class*="comment-count"], [class*="chat"] [class*="count"]').first
        if await comment_element.count() > 0:
            text = await comment_element.text_content()
            comments_count = self._parse_count(text)

        return NoteStats(
            likes=likes,
            collects=collects,
            comments=comments_count,
            shares=shares,
        )

    def _parse_count(self, text: Optional[str]) -> int:
        """解析数量文本（支持 1.2万 格式）"""
        if not text:
            return 0

        text = text.strip()
        if not text:
            return 0

        # 处理 "万" 单位
        if "万" in text:
            try:
                num = float(text.replace("万", ""))
                return int(num * 10000)
            except ValueError:
                return 0

        # 处理纯数字
        try:
            return int(re.sub(r"[^\d]", "", text))
        except ValueError:
            return 0

    async def _extract_images(self, page: Page) -> list[MediaItem]:
        """提取图片列表"""
        images = []

        # 图片选择器
        img_selectors = [
            '[class*="swiper"] img',
            '[class*="carousel"] img',
            '[class*="slide"] img',
            '[class*="note-image"] img',
        ]

        seen_urls = set()

        for selector in img_selectors:
            elements = page.locator(selector)
            count = await elements.count()

            for i in range(count):
                element = elements.nth(i)
                src = await element.get_attribute("src")

                if src and src not in seen_urls and "avatar" not in src.lower():
                    seen_urls.add(src)

                    # 尝试获取原图 URL
                    original_src = src.split("?")[0]  # 移除参数获取原图

                    # 获取尺寸
                    width = await element.get_attribute("width")
                    height = await element.get_attribute("height")

                    images.append(
                        MediaItem(
                            url=original_src,
                            width=int(width) if width and width.isdigit() else None,
                            height=int(height) if height and height.isdigit() else None,
                        )
                    )

        return images

    async def _extract_video(self, page: Page) -> Optional[MediaItem]:
        """提取视频信息"""
        video_element = page.locator("video").first

        if await video_element.count() > 0:
            src = await video_element.get_attribute("src")
            if src:
                return MediaItem(url=src)

            # 尝试从 source 标签获取
            source = page.locator("video source").first
            if await source.count() > 0:
                src = await source.get_attribute("src")
                if src:
                    return MediaItem(url=src)

        return None

    async def _download_images(
        self, images: list[MediaItem], note_id: str
    ) -> list[MediaItem]:
        """下载图片"""
        import httpx

        note_dir = self.output_dir / note_id / "images"
        note_dir.mkdir(parents=True, exist_ok=True)

        async with httpx.AsyncClient() as client:
            for i, img in enumerate(images):
                try:
                    response = await client.get(
                        img.url,
                        headers={
                            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                            "Referer": "https://www.xiaohongshu.com/",
                        },
                        follow_redirects=True,
                    )

                    if response.status_code == 200:
                        # 确定文件扩展名
                        content_type = response.headers.get("content-type", "")
                        ext = ".jpg"
                        if "png" in content_type:
                            ext = ".png"
                        elif "webp" in content_type:
                            ext = ".webp"
                        elif "gif" in content_type:
                            ext = ".gif"

                        filename = f"image_{i+1}{ext}"
                        filepath = note_dir / filename

                        with open(filepath, "wb") as f:
                            f.write(response.content)

                        img.local_path = str(filepath)
                        print(f"[Scraper] Downloaded: {filename}")

                except Exception as e:
                    print(f"[Scraper] Failed to download image {i+1}: {e}")

        return images

    async def _download_video(
        self, video: MediaItem, note_id: str
    ) -> MediaItem:
        """下载视频"""
        import httpx

        note_dir = self.output_dir / note_id / "video"
        note_dir.mkdir(parents=True, exist_ok=True)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    video.url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                        "Referer": "https://www.xiaohongshu.com/",
                    },
                    follow_redirects=True,
                )

                if response.status_code == 200:
                    filename = "video.mp4"
                    filepath = note_dir / filename

                    with open(filepath, "wb") as f:
                        f.write(response.content)

                    video.local_path = str(filepath)
                    print(f"[Scraper] Downloaded: {filename}")

        except Exception as e:
            print(f"[Scraper] Failed to download video: {e}")

        return video

    async def _fetch_comments(
        self, page: Page, limit: int = 100
    ) -> list[Comment]:
        """抓取评论"""
        comments = []

        try:
            # 滚动到评论区
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            await page.wait_for_timeout(1000)

            # 等待评论加载
            comment_container = page.locator('[class*="comment"], [class*="comments"]').first
            if await comment_container.count() == 0:
                return comments

            # 提取评论
            comment_items = page.locator('[class*="comment-item"], [class*="comment-content"]')
            count = min(await comment_items.count(), limit)

            for i in range(count):
                item = comment_items.nth(i)

                try:
                    # 提取评论内容
                    content_el = item.locator('[class*="content"], [class*="text"]').first
                    content = ""
                    if await content_el.count() > 0:
                        content = await content_el.text_content() or ""

                    # 提取用户名
                    user_el = item.locator('[class*="user-name"], [class*="nickname"]').first
                    user_name = ""
                    if await user_el.count() > 0:
                        user_name = await user_el.text_content() or ""

                    # 提取点赞数
                    like_el = item.locator('[class*="like-count"]').first
                    likes = 0
                    if await like_el.count() > 0:
                        likes = self._parse_count(await like_el.text_content())

                    if content.strip():
                        comments.append(
                            Comment(
                                id=f"comment_{i}",
                                user_id=f"user_{i}",
                                user_name=user_name.strip() or f"User{i}",
                                content=content.strip(),
                                likes=likes,
                            )
                        )

                except Exception as e:
                    print(f"[Scraper] Failed to extract comment {i}: {e}")
                    continue

        except Exception as e:
            print(f"[Scraper] Failed to fetch comments: {e}")

        return comments

    async def save_to_json(self, note: NoteContent, filepath: Optional[str] = None) -> str:
        """保存笔记内容到 JSON 文件"""
        if not filepath:
            filepath = str(self.output_dir / note.note_id / "note.json")

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(note.model_dump(mode="json"), f, ensure_ascii=False, indent=2)

        print(f"[Scraper] Saved to: {filepath}")
        return filepath
