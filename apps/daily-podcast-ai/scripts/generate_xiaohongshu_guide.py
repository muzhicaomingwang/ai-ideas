#!/usr/bin/env python3
"""
小红书蹭热点指南生成脚本
基于每日科技新闻，生成小红书创作者可用的热点选题和文案模板
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv(project_root / ".env")


def load_articles_from_cache(date_str: str) -> list:
    """
    从缓存加载新闻

    Args:
        date_str: 日期字符串 (YYYY-MM-DD)

    Returns:
        Article 对象列表
    """
    import json
    from news_sources.rss_fetcher import Article

    cache_path = project_root / "cache" / f"{date_str}-news.json"

    if not cache_path.exists():
        print(f"  ⚠️ 缓存文件不存在: {cache_path}")
        return []

    with open(cache_path, "r", encoding="utf-8") as f:
        news_list = json.load(f)

    # 转换为 Article 对象
    articles = []
    for news in news_list:
        article = Article(
            title=news["title"],
            summary=news["summary"],
            link=news["link"],
            source=news["source"],
            category=news["category"],
            published=datetime.fromisoformat(news["published"]) if news.get("published") else None
        )
        articles.append(article)

    print(f"  📂 从缓存加载 {len(articles)} 篇新闻")
    return articles


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="小红书蹭热点指南生成器 - 将科技新闻转化为小红书创作指南",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 生成今日指南
  python generate_xiaohongshu_guide.py

  # 生成指定日期的指南
  python generate_xiaohongshu_guide.py --date 2026-01-16

  # 限制热点数量
  python generate_xiaohongshu_guide.py --max-hotspots 10

  # 指定输出路径
  python generate_xiaohongshu_guide.py --output ./my-guides

  # 详细输出模式
  python generate_xiaohongshu_guide.py --verbose
        """
    )

    parser.add_argument(
        "--date", "-d",
        type=str,
        default=None,
        help="指南日期 (格式: YYYY-MM-DD，默认为今天)"
    )

    parser.add_argument(
        "--max-hotspots", "-n",
        type=int,
        default=20,
        help="最大热点数量 (默认: 20)"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default="output/xiaohongshu-guides",
        help="输出目录 (默认: output/xiaohongshu-guides)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细输出"
    )

    args = parser.parse_args()

    # 解析日期
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print(f"❌ 日期格式错误: {args.date}，请使用 YYYY-MM-DD 格式")
            sys.exit(1)
    else:
        target_date = datetime.now()

    date_str = target_date.strftime("%Y-%m-%d")

    # 打印横幅
    print_banner(date_str)

    # 运行生成流程
    try:
        result = generate_xiaohongshu_guide(
            target_date=target_date,
            max_hotspots=args.max_hotspots,
            output_dir=args.output,
            verbose=args.verbose
        )

        if result:
            print_summary(result)
            sys.exit(0)
        else:
            print("\n❌ 指南生成失败")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def print_banner(date_str: str):
    """打印横幅"""
    print()
    print("=" * 50)
    print("📱  小红书蹭热点指南生成器")
    print("=" * 50)
    print(f"📅 日期: {date_str}")
    print()


def print_summary(result: dict):
    """打印生成摘要"""
    print()
    print("=" * 50)
    print("🎉 指南生成完成!")
    print("=" * 50)

    if result.get("output_path"):
        print(f"📝 指南文件: {result['output_path']}")

    if result.get("total_hotspots"):
        print(f"📰 热点总数: {result['total_hotspots']}")

    if result.get("high_priority_count"):
        print(f"🔥 高适配（4-5星）: {result['high_priority_count']} 条")

    if result.get("medium_priority_count"):
        print(f"⭐ 中适配（3星）: {result['medium_priority_count']} 条")

    if result.get("low_priority_count"):
        print(f"💡 低适配（1-2星）: {result['low_priority_count']} 条")

    if result.get("hot_keywords"):
        print(f"🏷️ 趋势关键词: {', '.join(result['hot_keywords'][:5])}...")

    print()


def generate_xiaohongshu_guide(
    target_date: datetime,
    max_hotspots: int = 20,
    output_dir: str = "output/xiaohongshu-guides",
    verbose: bool = False
) -> dict:
    """
    生成小红书蹭热点指南的主流程

    Args:
        target_date: 目标日期
        max_hotspots: 最大热点数量
        output_dir: 输出目录
        verbose: 详细输出

    Returns:
        结果字典
    """
    from processors.xiaohongshu_guide_writer import XiaohongshuGuideWriter

    date_str = target_date.strftime("%Y-%m-%d")

    result = {
        "date": date_str,
        "output_path": None,
        "total_hotspots": 0,
        "high_priority_count": 0,
        "medium_priority_count": 0,
        "low_priority_count": 0,
        "hot_keywords": []
    }

    # ========== 步骤 1: 从缓存读取新闻 ==========
    print("📰 步骤 1/2: 读取新闻缓存")
    print("-" * 40)

    articles = load_articles_from_cache(date_str)

    if not articles:
        print("❌ 没有找到新闻缓存")
        print(f"   提示：请先运行 hourly_collect.py 或 daily_generate.py 来收集新闻")
        return None

    # 限制数量
    if len(articles) > max_hotspots:
        articles = articles[:max_hotspots]
        print(f"  ✂️ 限制为前 {max_hotspots} 条")

    print(f"✅ 准备分析 {len(articles)} 条新闻")

    # ========== 步骤 2: 生成小红书指南 ==========
    print("\n🎨 步骤 2/2: 生成小红书蹭热点指南")
    print("-" * 40)

    try:
        writer = XiaohongshuGuideWriter()
        guide = writer.generate_guide(articles, target_date)

        # 保存 Markdown
        output_path = Path(output_dir) / f"guide-{date_str}.md"
        saved_path = guide.save_to_markdown(str(output_path))

        print(f"✅ 指南已保存: {saved_path}")

        # 填充结果
        result["output_path"] = saved_path
        result["total_hotspots"] = guide.total_hotspots
        result["high_priority_count"] = len(guide.high_priority)
        result["medium_priority_count"] = len(guide.medium_priority)
        result["low_priority_count"] = len(guide.low_priority)
        result["hot_keywords"] = guide.hot_keywords

        return result

    except ValueError as e:
        print(f"  ❌ 初始化失败: {e}")
        return None
    except Exception as e:
        print(f"  ❌ 生成失败: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
