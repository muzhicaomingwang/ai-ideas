#!/usr/bin/env python3
"""
Reddit 搜索脚本
在 Reddit 全站或特定 subreddit 中搜索内容
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import praw
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


def create_reddit_client() -> praw.Reddit:
    """创建 Reddit API 客户端"""
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "research-by-reddit/1.0")

    if not client_id or not client_secret:
        print("错误: 请设置 REDDIT_CLIENT_ID 和 REDDIT_CLIENT_SECRET 环境变量", file=sys.stderr)
        print("参考 .env.example 文件配置", file=sys.stderr)
        sys.exit(1)

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )


def search_reddit(
    query: str,
    subreddit: str | None = None,
    limit: int = 25,
    time_filter: str = "all",
    sort: str = "relevance",
) -> dict:
    """
    搜索 Reddit 内容

    Args:
        query: 搜索关键词
        subreddit: 限定搜索的 subreddit（可选）
        limit: 返回结果数量
        time_filter: 时间范围 [all, year, month, week, day, hour]
        sort: 排序方式 [relevance, hot, top, new, comments]

    Returns:
        包含搜索结果的字典
    """
    reddit = create_reddit_client()

    # 确定搜索范围
    if subreddit:
        search_target = reddit.subreddit(subreddit)
    else:
        search_target = reddit.subreddit("all")

    # 执行搜索
    results = []
    try:
        for submission in search_target.search(
            query,
            sort=sort,
            time_filter=time_filter,
            limit=limit,
        ):
            result = {
                "id": submission.id,
                "title": submission.title,
                "author": str(submission.author) if submission.author else "[deleted]",
                "subreddit": submission.subreddit.display_name,
                "score": submission.score,
                "upvote_ratio": submission.upvote_ratio,
                "num_comments": submission.num_comments,
                "created_utc": int(submission.created_utc),
                "created_datetime": datetime.utcfromtimestamp(submission.created_utc).isoformat(),
                "url": f"https://reddit.com{submission.permalink}",
                "selftext": submission.selftext[:2000] if submission.selftext else "",
                "is_self": submission.is_self,
                "link_flair_text": submission.link_flair_text,
                "over_18": submission.over_18,
            }
            results.append(result)
    except Exception as e:
        print(f"搜索出错: {e}", file=sys.stderr)
        sys.exit(1)

    return {
        "query": query,
        "subreddit": subreddit or "all",
        "timestamp": datetime.utcnow().isoformat(),
        "parameters": {
            "limit": limit,
            "time_filter": time_filter,
            "sort": sort,
        },
        "total_results": len(results),
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(
        description="搜索 Reddit 内容",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 全站搜索
  python search_reddit.py --query "AI productivity tools" --limit 50

  # 在特定 subreddit 搜索
  python search_reddit.py --query "团建" --subreddit "China_irl" --limit 30

  # 按时间过滤
  python search_reddit.py --query "startup ideas" --time_filter month --sort top
        """,
    )

    parser.add_argument(
        "--query", "-q",
        required=True,
        help="搜索关键词",
    )
    parser.add_argument(
        "--subreddit", "-s",
        help="限定搜索的 subreddit（不指定则全站搜索）",
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=25,
        help="返回结果数量（默认 25，最大 100）",
    )
    parser.add_argument(
        "--time_filter", "-t",
        choices=["all", "year", "month", "week", "day", "hour"],
        default="all",
        help="时间范围（默认 all）",
    )
    parser.add_argument(
        "--sort",
        choices=["relevance", "hot", "top", "new", "comments"],
        default="relevance",
        help="排序方式（默认 relevance）",
    )
    parser.add_argument(
        "--output", "-o",
        help="输出文件路径（不指定则输出到 stdout）",
    )

    args = parser.parse_args()

    # 限制最大数量
    limit = min(args.limit, 100)

    # 执行搜索
    results = search_reddit(
        query=args.query,
        subreddit=args.subreddit,
        limit=limit,
        time_filter=args.time_filter,
        sort=args.sort,
    )

    # 输出结果
    output_json = json.dumps(results, ensure_ascii=False, indent=2)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_json, encoding="utf-8")
        print(f"结果已保存到: {args.output}", file=sys.stderr)
        print(f"共找到 {results['total_results']} 条结果", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
