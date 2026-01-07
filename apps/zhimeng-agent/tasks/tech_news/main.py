"""科技新闻聚合任务

每早 7 点执行，自动抓取科技新闻并生成摘要。

数据来源：
1. Hacker News Top Stories
2. GitHub Trending
3. Product Hunt (可选)

输出目标：
- Obsidian News 文件夹
- 飞书消息推送
- Notion 页面（可选）
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tasks.config import config
from tasks.sync_utils import create_syncer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# API 配置
HACKER_NEWS_API = "https://hacker-news.firebaseio.com/v0"
GITHUB_TRENDING_API = "https://api.github.com/search/repositories"

# 默认获取数量
DEFAULT_HN_COUNT = 15
DEFAULT_GITHUB_COUNT = 10

# 请求超时（秒）
REQUEST_TIMEOUT = 15


@dataclass
class NewsItem:
    """新闻条目"""
    title: str
    url: str
    source: str
    score: int = 0
    comments: int = 0
    author: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class NewsStats:
    """新闻聚合统计"""
    total_items: int = 0
    by_source: Dict[str, int] = field(default_factory=dict)
    fetch_time: float = 0.0  # 抓取耗时（秒）
    errors: List[str] = field(default_factory=list)


class TechNewsAggregator:
    """科技新闻聚合器"""

    def __init__(
        self,
        dry_run: bool = False,
        hn_count: int = DEFAULT_HN_COUNT,
        github_count: int = DEFAULT_GITHUB_COUNT,
    ):
        """
        Args:
            dry_run: 如果为 True，只生成不同步
            hn_count: Hacker News 获取数量
            github_count: GitHub Trending 获取数量
        """
        self.dry_run = dry_run
        self.hn_count = hn_count
        self.github_count = github_count
        self.stats = NewsStats()
        self.news_items: List[NewsItem] = []

    def _fetch_url(self, url: str, headers: Optional[Dict] = None) -> Optional[Dict]:
        """通用 URL 获取"""
        try:
            req = Request(url)
            req.add_header("User-Agent", "zhimeng-agent/1.0")
            if headers:
                for key, value in headers.items():
                    req.add_header(key, value)

            with urlopen(req, timeout=REQUEST_TIMEOUT) as response:
                return json.loads(response.read().decode("utf-8"))

        except (URLError, HTTPError) as e:
            logger.warning(f"获取 {url} 失败: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.warning(f"解析 {url} JSON 失败: {e}")
            return None

    def _fetch_hn_item(self, item_id: int) -> Optional[NewsItem]:
        """获取单个 Hacker News 条目"""
        url = f"{HACKER_NEWS_API}/item/{item_id}.json"
        data = self._fetch_url(url)

        if not data or data.get("type") != "story":
            return None

        return NewsItem(
            title=data.get("title", ""),
            url=data.get("url", f"https://news.ycombinator.com/item?id={item_id}"),
            source="HackerNews",
            score=data.get("score", 0),
            comments=data.get("descendants", 0),
            author=data.get("by", ""),
        )

    def fetch_hacker_news(self) -> List[NewsItem]:
        """获取 Hacker News 热门文章"""
        items = []
        logger.info("正在获取 Hacker News...")

        # 获取 Top Stories IDs
        top_url = f"{HACKER_NEWS_API}/topstories.json"
        story_ids = self._fetch_url(top_url)

        if not story_ids:
            self.stats.errors.append("无法获取 Hacker News Top Stories")
            return items

        # 并行获取文章详情
        story_ids = story_ids[: self.hn_count * 2]  # 多获取一些，过滤后保留目标数量

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self._fetch_hn_item, sid): sid for sid in story_ids
            }
            for future in as_completed(futures):
                item = future.result()
                if item and item.title:
                    items.append(item)
                    if len(items) >= self.hn_count:
                        break

        # 按分数排序
        items.sort(key=lambda x: x.score, reverse=True)
        items = items[: self.hn_count]

        logger.info(f"获取到 {len(items)} 条 Hacker News")
        return items

    def fetch_github_trending(self) -> List[NewsItem]:
        """获取 GitHub 今日热门仓库"""
        items = []
        logger.info("正在获取 GitHub Trending...")

        # 搜索过去24小时创建的高星仓库
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        params = f"q=created:>{yesterday}&sort=stars&order=desc&per_page={self.github_count}"
        url = f"{GITHUB_TRENDING_API}?{params}"

        data = self._fetch_url(url)

        if not data or "items" not in data:
            # 降级：搜索本周热门
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            params = f"q=created:>{week_ago}&sort=stars&order=desc&per_page={self.github_count}"
            url = f"{GITHUB_TRENDING_API}?{params}"
            data = self._fetch_url(url)

        if not data or "items" not in data:
            self.stats.errors.append("无法获取 GitHub Trending")
            return items

        for repo in data["items"][: self.github_count]:
            tags = []
            if repo.get("language"):
                tags.append(repo["language"])
            if repo.get("topics"):
                tags.extend(repo["topics"][:3])

            items.append(
                NewsItem(
                    title=repo.get("full_name", ""),
                    url=repo.get("html_url", ""),
                    source="GitHub",
                    score=repo.get("stargazers_count", 0),
                    author=repo.get("owner", {}).get("login", ""),
                    description=repo.get("description", "")[:200] if repo.get("description") else "",
                    tags=tags,
                )
            )

        logger.info(f"获取到 {len(items)} 个 GitHub 仓库")
        return items

    def aggregate(self) -> List[NewsItem]:
        """聚合所有新闻源"""
        import time

        start_time = time.time()
        logger.info("开始聚合科技新闻...")

        # 获取各源新闻
        hn_items = self.fetch_hacker_news()
        github_items = self.fetch_github_trending()

        # 合并
        self.news_items = hn_items + github_items

        # 统计
        self.stats.total_items = len(self.news_items)
        self.stats.by_source["HackerNews"] = len(hn_items)
        self.stats.by_source["GitHub"] = len(github_items)
        self.stats.fetch_time = time.time() - start_time

        logger.info(
            f"聚合完成: {self.stats.total_items} 条, "
            f"耗时 {self.stats.fetch_time:.1f}s"
        )

        return self.news_items

    def generate_report(self) -> str:
        """生成新闻报告 Markdown"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][now.weekday()]

        lines = [
            f"# {date_str} ({weekday}) 科技早报",
            "",
            f"> 自动生成于 {now.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 概览",
            "",
            f"- 新闻总数: {self.stats.total_items} 条",
            f"- 抓取耗时: {self.stats.fetch_time:.1f} 秒",
        ]

        for source, count in self.stats.by_source.items():
            lines.append(f"- {source}: {count} 条")
        lines.append("")

        # Hacker News 部分
        hn_items = [item for item in self.news_items if item.source == "HackerNews"]
        if hn_items:
            lines.extend([
                "## Hacker News 热门",
                "",
            ])
            for i, item in enumerate(hn_items, 1):
                score_str = f"({item.score}分, {item.comments}评论)"
                lines.append(f"{i}. [{item.title}]({item.url}) {score_str}")
            lines.append("")

        # GitHub 部分
        github_items = [item for item in self.news_items if item.source == "GitHub"]
        if github_items:
            lines.extend([
                "## GitHub 热门仓库",
                "",
            ])
            for item in github_items:
                star_str = f"⭐ {item.score}"
                tags_str = " ".join([f"`{tag}`" for tag in item.tags[:3]]) if item.tags else ""
                lines.append(f"- **[{item.title}]({item.url})** {star_str} {tags_str}")
                if item.description:
                    lines.append(f"  > {item.description}")
            lines.append("")

        # 错误日志
        if self.stats.errors:
            lines.extend([
                "## 抓取问题",
                "",
            ])
            for error in self.stats.errors:
                lines.append(f"- {error}")
            lines.append("")

        # 无内容提示
        if self.stats.total_items == 0:
            lines.extend([
                "## 提示",
                "",
                "_今日未能获取到新闻，请检查网络连接_",
                "",
            ])

        return "\n".join(lines)

    def run(self) -> Dict[str, bool]:
        """执行新闻聚合和同步"""
        # 聚合新闻
        self.aggregate()

        # 生成报告
        report = self.generate_report()
        date_str = datetime.now().strftime("%Y%m%d")
        report_title = f"tech-news-{date_str}"

        if self.dry_run:
            logger.info("[DRY RUN] 跳过同步")
            return {"dry_run": True}

        # 同步到各平台
        syncer = create_syncer()
        results = syncer.sync_content(
            title=report_title,
            content=report,
            targets=["obsidian", "feishu"],  # 新闻推送到 Obsidian 和飞书
            obsidian_folder="News",
            feishu_receive_id=config.FEISHU_RECIPIENT_OPEN_ID,
        )

        logger.info(f"科技新闻同步结果: {results}")
        return results


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="科技新闻聚合任务")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅聚合，不同步",
    )
    parser.add_argument(
        "--hn-count",
        type=int,
        default=DEFAULT_HN_COUNT,
        help=f"Hacker News 获取数量 (默认 {DEFAULT_HN_COUNT})",
    )
    parser.add_argument(
        "--github-count",
        type=int,
        default=DEFAULT_GITHUB_COUNT,
        help=f"GitHub Trending 获取数量 (默认 {DEFAULT_GITHUB_COUNT})",
    )

    args = parser.parse_args()

    aggregator = TechNewsAggregator(
        dry_run=args.dry_run,
        hn_count=args.hn_count,
        github_count=args.github_count,
    )

    if args.dry_run:
        aggregator.aggregate()
        report = aggregator.generate_report()
        print(report)
    else:
        results = aggregator.run()
        success = all(results.values()) if results else False
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
