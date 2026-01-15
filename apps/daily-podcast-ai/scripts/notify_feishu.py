#!/usr/bin/env python3
"""
飞书消息通知脚本
在播客发布成功后发送飞书卡片消息通知

Requirements:
- pip install httpx python-dotenv
- Environment variables: FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_RECEIVER_OPEN_ID

Usage:
    python scripts/notify_feishu.py --date 2026-01-14 --rss-url "https://rss.com/..."
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FeishuNotifier:
    """飞书消息通知客户端（简化版）"""

    BASE_URL = "https://open.feishu.cn/open-apis"

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self._tenant_access_token: Optional[str] = None
        self._token_expires_at: float = 0

    async def _get_tenant_access_token(self) -> str:
        """获取 tenant_access_token"""
        # 检查缓存
        if self._tenant_access_token and time.time() < self._token_expires_at:
            return self._tenant_access_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/auth/v3/tenant_access_token/internal",
                json={
                    "app_id": self.app_id,
                    "app_secret": self.app_secret,
                },
                timeout=30.0,
            )
            data = response.json()

            if data.get("code") != 0:
                raise Exception(f"获取 token 失败: {data}")

            self._tenant_access_token = data["tenant_access_token"]
            self._token_expires_at = time.time() + data["expire"] - 60

            logger.info(f"✅ 获取飞书 token 成功，有效期至: {time.ctime(self._token_expires_at)}")
            return self._tenant_access_token

    async def send_card(
        self,
        receive_id: str,
        title: str,
        content: str,
        template: str = "blue",
        receive_id_type: str = "open_id",
    ) -> dict:
        """发送卡片消息

        Args:
            receive_id: 接收者 ID (open_id/user_id/chat_id)
            title: 卡片标题
            content: Markdown 格式内容
            template: 卡片颜色模板 (blue/green/orange/red/purple/grey)
            receive_id_type: ID 类型 (open_id/user_id/chat_id)

        Returns:
            API 响应
        """
        token = await self._get_tenant_access_token()

        card = {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": template,
            },
            "elements": [
                {"tag": "markdown", "content": content},
            ],
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/im/v1/messages",
                params={"receive_id_type": receive_id_type},
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "receive_id": receive_id,
                    "msg_type": "interactive",
                    "content": json.dumps(card),
                },
                timeout=30.0,
            )
            result = response.json()

            if result.get("code") != 0:
                raise Exception(f"发送消息失败: {result}")

            logger.info(f"✅ 飞书消息发送成功: message_id={result.get('data', {}).get('message_id')}")
            return result


def build_podcast_notification(
    date: str,
    rss_url: Optional[str] = None,
    episode_url: Optional[str] = None,
    article_count: int = 10,
) -> tuple[str, str]:
    """构建播客发布通知卡片

    Args:
        date: 播客日期 (YYYY-MM-DD)
        rss_url: RSS feed URL
        episode_url: 单集URL
        article_count: 文章数量

    Returns:
        (title, content) 元组
    """
    title = "🎙️ 今日科技早报已发布"

    content_parts = [
        f"**📅 日期**: {date}",
        f"**📰 内容**: 精选 {article_count} 篇科技新闻",
        "",
        "**📢 发布状态**:",
        "- ✅ RSS.com 发布成功",
        "- ⏳ 小宇宙同步中（预计1小时内）",
        "",
    ]

    if episode_url:
        content_parts.append(f"**🔗 单集链接**: {episode_url}")
        content_parts.append("")

    if rss_url:
        content_parts.append(f"**📡 RSS Feed**: {rss_url}")
        content_parts.append("")

    content_parts.extend([
        "---",
        "💡 **小宇宙订阅步骤**:",
        "1. 打开小宇宙创作者平台: https://podcaster.xiaoyuzhoufm.com/",
        "2. 点击「立即同步」查看最新单集",
        "3. 首次设置需添加RSS订阅（仅需一次）",
    ])

    return title, "\n".join(content_parts)


async def main_async():
    """异步主函数"""
    parser = argparse.ArgumentParser(description="发送播客发布通知到飞书")
    parser.add_argument("--date", required=True, help="播客日期 (YYYY-MM-DD)")
    parser.add_argument("--rss-url", help="RSS feed URL")
    parser.add_argument("--episode-url", help="单集URL")
    parser.add_argument("--article-count", type=int, default=10, help="文章数量")
    args = parser.parse_args()

    # 加载环境变量
    load_dotenv()

    # 验证必需的环境变量
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    receiver_id = os.getenv("FEISHU_RECEIVER_OPEN_ID")

    if not all([app_id, app_secret, receiver_id]):
        logger.warning("⚠️  飞书配置未完整设置，跳过通知")
        logger.info("需要配置: FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_RECEIVER_OPEN_ID")
        sys.exit(0)  # 不报错，允许流程继续

    try:
        # 创建通知客户端
        notifier = FeishuNotifier(app_id, app_secret)

        # 构建通知内容
        title, content = build_podcast_notification(
            date=args.date,
            rss_url=args.rss_url,
            episode_url=args.episode_url,
            article_count=args.article_count,
        )

        logger.info(f"📤 发送飞书通知: {title}")
        logger.debug(f"接收者: {receiver_id}")

        # 发送卡片消息
        result = await notifier.send_card(
            receive_id=receiver_id,
            title=title,
            content=content,
            template="blue",
        )

        logger.info(f"🎉 通知发送成功!")

    except Exception as e:
        logger.error(f"❌ 飞书通知发送失败: {e}", exc_info=True)
        # 不影响主流程，仅记录错误
        sys.exit(0)


def main():
    """同步主函数入口"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
