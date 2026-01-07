"""
RSS 新闻获取模块
从配置的 RSS 源获取新闻文章
"""

import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import feedparser
import requests
import yaml


@dataclass
class Article:
    """新闻文章数据类"""
    title: str
    summary: str
    link: str
    source: str
    category: str
    published: Optional[datetime] = None

    def __str__(self) -> str:
        return f"[{self.source}] {self.title}"


class RSSFetcher:
    """RSS 新闻获取器"""

    def __init__(self, config_path: str = "config/sources.yaml"):
        """
        初始化 RSS 获取器

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.fetch_config = self.config.get("fetch", {})
        self.filters = self.config.get("filters", {})

    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        path = Path(config_path)
        if not path.exists():
            # 尝试从项目根目录加载
            project_root = Path(__file__).parent.parent.parent
            path = project_root / config_path

        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _get_enabled_sources(self) -> list[dict]:
        """获取启用的 RSS 源"""
        sources = self.config.get("sources", {}).get("rss", [])
        return [s for s in sources if s.get("enabled", False)]

    def _fetch_feed(self, url: str) -> Optional[feedparser.FeedParserDict]:
        """
        获取单个 RSS feed

        Args:
            url: RSS feed URL

        Returns:
            解析后的 feed 或 None（失败时）
        """
        timeout = self.fetch_config.get("timeout", 30)
        user_agent = self.fetch_config.get("user_agent", "DailyPodcastAI/1.0")
        max_retries = self.fetch_config.get("max_retries", 3)

        headers = {"User-Agent": user_agent}

        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                feed = feedparser.parse(response.content)

                if feed.bozo and not feed.entries:
                    print(f"  ⚠️ RSS 解析警告: {feed.bozo_exception}")
                    continue

                return feed

            except requests.RequestException as e:
                print(f"  ❌ 请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)

        return None

    def _parse_published_date(self, entry: dict) -> Optional[datetime]:
        """解析发布时间"""
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                return datetime(*entry.published_parsed[:6])
            except (TypeError, ValueError):
                pass

        if hasattr(entry, "updated_parsed") and entry.updated_parsed:
            try:
                return datetime(*entry.updated_parsed[:6])
            except (TypeError, ValueError):
                pass

        return None

    def _matches_filters(self, article: Article) -> bool:
        """
        检查文章是否符合过滤条件

        Args:
            article: 文章对象

        Returns:
            True 如果文章应该保留
        """
        include_keywords = self.filters.get("include_keywords", [])
        exclude_keywords = self.filters.get("exclude_keywords", [])

        text = f"{article.title} {article.summary}".lower()

        # 检查黑名单
        for keyword in exclude_keywords:
            if keyword.lower() in text:
                return False

        # 如果有白名单，检查是否包含任一关键词
        if include_keywords:
            for keyword in include_keywords:
                if keyword.lower() in text:
                    return True
            return False

        return True

    def _is_recent(self, article: Article, hours: int = 24) -> bool:
        """检查文章是否在指定时间内发布"""
        if not article.published:
            return True  # 无发布时间则默认保留

        cutoff = datetime.now() - timedelta(hours=hours)
        return article.published >= cutoff

    def fetch_from_source(self, source: dict) -> list[Article]:
        """
        从单个源获取文章

        Args:
            source: 源配置字典

        Returns:
            文章列表
        """
        name = source.get("name", "未知")
        url = source.get("url", "")
        category = source.get("category", "综合")
        max_articles = self.filters.get("max_articles_per_source", 10)

        print(f"📰 获取 {name} ...")

        feed = self._fetch_feed(url)
        if not feed:
            print(f"  ❌ 获取失败")
            return []

        articles = []
        for entry in feed.entries[:max_articles * 2]:  # 获取更多以便过滤
            title = entry.get("title", "").strip()
            summary = entry.get("summary", entry.get("description", "")).strip()
            link = entry.get("link", "")

            if not title:
                continue

            # 清理 HTML 标签（简单处理）
            import re
            summary = re.sub(r"<[^>]+>", "", summary)
            summary = summary[:500]  # 限制摘要长度

            article = Article(
                title=title,
                summary=summary,
                link=link,
                source=name,
                category=category,
                published=self._parse_published_date(entry)
            )

            # 应用过滤
            if self._matches_filters(article) and self._is_recent(article):
                articles.append(article)

            if len(articles) >= max_articles:
                break

        print(f"  ✅ 获取 {len(articles)} 篇文章")
        return articles

    def fetch_all(self) -> list[Article]:
        """
        从所有启用的源获取文章

        Returns:
            所有文章列表（已排序、去重、限制数量）
        """
        sources = self._get_enabled_sources()
        if not sources:
            print("⚠️ 没有启用的 RSS 源")
            return []

        print(f"🚀 开始获取新闻，共 {len(sources)} 个源")
        print("-" * 40)

        all_articles = []
        request_interval = self.fetch_config.get("request_interval", 2)

        for i, source in enumerate(sources):
            articles = self.fetch_from_source(source)
            all_articles.extend(articles)

            # 请求间隔
            if i < len(sources) - 1:
                time.sleep(request_interval)

        # 去重（基于标题）
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            if article.title not in seen_titles:
                seen_titles.add(article.title)
                unique_articles.append(article)

        # 按发布时间排序（最新在前）
        unique_articles.sort(
            key=lambda a: a.published or datetime.min,
            reverse=True
        )

        # 限制总数
        max_total = self.filters.get("max_total_articles", 20)
        final_articles = unique_articles[:max_total]

        print("-" * 40)
        print(f"📊 总计: {len(final_articles)} 篇文章 (去重后)")

        return final_articles


def main():
    """测试入口"""
    fetcher = RSSFetcher()
    articles = fetcher.fetch_all()

    print("\n" + "=" * 50)
    print("📰 今日新闻列表")
    print("=" * 50)

    for i, article in enumerate(articles, 1):
        print(f"\n{i}. [{article.category}] {article.title}")
        print(f"   来源: {article.source}")
        if article.published:
            print(f"   时间: {article.published.strftime('%Y-%m-%d %H:%M')}")
        print(f"   摘要: {article.summary[:100]}...")


if __name__ == "__main__":
    main()
