#!/usr/bin/env python3
"""
每小时新闻收集脚本
定时从RSS源获取新闻并存储到缓存，供早上7点优选使用
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv
from news_sources import RSSFetcher

# 加载环境变量
load_dotenv(project_root / ".env")


def load_cache(cache_path: Path) -> list[dict]:
    """加载缓存的新闻"""
    if cache_path.exists():
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_cache(cache_path: Path, news_list: list[dict]):
    """保存新闻到缓存"""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)


def article_to_dict(article) -> dict:
    """将 Article 对象转换为字典"""
    return {
        "title": article.title,
        "summary": article.summary,
        "link": article.link,
        "source": article.source,
        "category": article.category,
        "published": article.published.isoformat() if article.published else None,
        "collected_at": datetime.now().isoformat()
    }


def is_duplicate(article_dict: dict, existing_news: list[dict]) -> bool:
    """检查是否重复"""
    # 基于 link 或 title 去重
    for existing in existing_news:
        if existing["link"] == article_dict["link"]:
            return True
        if existing["title"] == article_dict["title"]:
            return True
    return False


def main():
    """主入口"""
    today = datetime.now().strftime("%Y-%m-%d")
    cache_dir = project_root / "cache"
    cache_path = cache_dir / f"{today}-news.json"

    current_hour = datetime.now().strftime("%H:%M")

    print(f"⏰ [{current_hour}] 开始收集新闻...")

    # 加载现有缓存
    existing_news = load_cache(cache_path)
    print(f"📂 当前缓存: {len(existing_news)} 篇")

    # 获取新闻
    fetcher = RSSFetcher()
    articles = fetcher.fetch_all()

    if not articles:
        print("❌ 未获取到新闻")
        sys.exit(1)

    # 去重并追加
    new_count = 0
    for article in articles:
        article_dict = article_to_dict(article)
        if not is_duplicate(article_dict, existing_news):
            existing_news.append(article_dict)
            new_count += 1

    # 保存缓存
    save_cache(cache_path, existing_news)

    print(f"✅ 新增 {new_count} 篇，总计 {len(existing_news)} 篇")
    print(f"💾 已保存到: {cache_path}")


if __name__ == "__main__":
    main()
