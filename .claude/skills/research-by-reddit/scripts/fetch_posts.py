#!/usr/bin/env python3
"""
Reddit 帖子获取脚本
获取指定 subreddit 的热门/最新帖子及评论
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


def fetch_comments(submission, limit: int = 10) -> list:
    """获取帖子评论"""
    comments = []
    submission.comments.replace_more(limit=0)  # 移除 "more comments" 占位符

    for comment in submission.comments[:limit]:
        if hasattr(comment, "body"):
            comments.append({
                "id": comment.id,
                "author": str(comment.author) if comment.author else "[deleted]",
                "body": comment.body[:1500] if comment.body else "",
                "score": comment.score,
                "created_utc": int(comment.created_utc),
                "created_datetime": datetime.utcfromtimestamp(comment.created_utc).isoformat(),
                "is_submitter": comment.is_submitter,
            })

    return comments


def fetch_posts(
    subreddit_name: str,
    sort: str = "hot",
    limit: int = 25,
    time_filter: str = "week",
    include_comments: bool = False,
    comment_limit: int = 10,
) -> dict:
    """
    获取 subreddit 帖子

    Args:
        subreddit_name: 目标 subreddit
        sort: 排序方式 [hot, new, top, rising, controversial]
        limit: 帖子数量
        time_filter: 时间范围（仅对 top/controversial 有效）
        include_comments: 是否包含评论
        comment_limit: 每个帖子的评论数量

    Returns:
        包含帖子数据的字典
    """
    reddit = create_reddit_client()
    subreddit = reddit.subreddit(subreddit_name)

    # 获取帖子列表
    if sort == "hot":
        submissions = subreddit.hot(limit=limit)
    elif sort == "new":
        submissions = subreddit.new(limit=limit)
    elif sort == "top":
        submissions = subreddit.top(time_filter=time_filter, limit=limit)
    elif sort == "rising":
        submissions = subreddit.rising(limit=limit)
    elif sort == "controversial":
        submissions = subreddit.controversial(time_filter=time_filter, limit=limit)
    else:
        submissions = subreddit.hot(limit=limit)

    # 处理帖子
    posts = []
    try:
        for submission in submissions:
            post = {
                "id": submission.id,
                "title": submission.title,
                "author": str(submission.author) if submission.author else "[deleted]",
                "score": submission.score,
                "upvote_ratio": submission.upvote_ratio,
                "num_comments": submission.num_comments,
                "created_utc": int(submission.created_utc),
                "created_datetime": datetime.utcfromtimestamp(submission.created_utc).isoformat(),
                "url": f"https://reddit.com{submission.permalink}",
                "selftext": submission.selftext[:3000] if submission.selftext else "",
                "is_self": submission.is_self,
                "link_flair_text": submission.link_flair_text,
                "over_18": submission.over_18,
                "stickied": submission.stickied,
                "distinguished": submission.distinguished,
            }

            # 获取评论
            if include_comments:
                post["comments"] = fetch_comments(submission, comment_limit)

            posts.append(post)
    except Exception as e:
        print(f"获取帖子出错: {e}", file=sys.stderr)
        sys.exit(1)

    # 获取 subreddit 信息
    try:
        subreddit_info = {
            "name": subreddit.display_name,
            "title": subreddit.title,
            "description": subreddit.public_description[:500] if subreddit.public_description else "",
            "subscribers": subreddit.subscribers,
            "created_utc": int(subreddit.created_utc),
            "over18": subreddit.over18,
        }
    except Exception:
        subreddit_info = {"name": subreddit_name}

    return {
        "subreddit": subreddit_info,
        "timestamp": datetime.utcnow().isoformat(),
        "parameters": {
            "sort": sort,
            "limit": limit,
            "time_filter": time_filter,
            "include_comments": include_comments,
            "comment_limit": comment_limit,
        },
        "total_posts": len(posts),
        "posts": posts,
    }


def main():
    parser = argparse.ArgumentParser(
        description="获取 subreddit 帖子",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 获取热门帖子
  python fetch_posts.py --subreddit startups --sort hot --limit 20

  # 获取帖子及评论
  python fetch_posts.py --subreddit smallbusiness --include_comments --comment_limit 20

  # 获取本周热门
  python fetch_posts.py --subreddit programming --sort top --time_filter week
        """,
    )

    parser.add_argument(
        "--subreddit", "-s",
        required=True,
        help="目标 subreddit",
    )
    parser.add_argument(
        "--sort",
        choices=["hot", "new", "top", "rising", "controversial"],
        default="hot",
        help="排序方式（默认 hot）",
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=25,
        help="帖子数量（默认 25）",
    )
    parser.add_argument(
        "--time_filter", "-t",
        choices=["all", "year", "month", "week", "day", "hour"],
        default="week",
        help="时间范围，仅对 top/controversial 有效（默认 week）",
    )
    parser.add_argument(
        "--include_comments", "-c",
        action="store_true",
        help="是否包含评论",
    )
    parser.add_argument(
        "--comment_limit",
        type=int,
        default=10,
        help="每个帖子的评论数量（默认 10）",
    )
    parser.add_argument(
        "--output", "-o",
        help="输出文件路径（不指定则输出到 stdout）",
    )

    args = parser.parse_args()

    # 执行获取
    results = fetch_posts(
        subreddit_name=args.subreddit,
        sort=args.sort,
        limit=args.limit,
        time_filter=args.time_filter,
        include_comments=args.include_comments,
        comment_limit=args.comment_limit,
    )

    # 输出结果
    output_json = json.dumps(results, ensure_ascii=False, indent=2)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_json, encoding="utf-8")
        print(f"结果已保存到: {args.output}", file=sys.stderr)
        print(f"共获取 {results['total_posts']} 篇帖子", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
