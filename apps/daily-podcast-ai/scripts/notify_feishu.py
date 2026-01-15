#!/usr/bin/env python3
"""
飞书消息通知脚本 (支持离线队列和失败重试)
在播客发布成功/失败后发送飞书卡片消息通知

Features:
- 成功/失败通知
- 离线消息队列（网络恢复后自动重试）
- 自动重试机制

Requirements:
- pip install httpx python-dotenv
- Environment variables: FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_RECEIVER_OPEN_ID

Usage:
    python scripts/notify_feishu.py --date 2026-01-14 --article-count 10
    python scripts/notify_feishu.py --date 2026-01-14 --status failed --error "网络错误"
    python scripts/notify_feishu.py --retry-queue  # 重试队列中的消息
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

import httpx
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 离线消息队列文件
QUEUE_DIR = Path(__file__).parent.parent / "logs" / "notification_queue"
QUEUE_DIR.mkdir(parents=True, exist_ok=True)
QUEUE_FILE = QUEUE_DIR / "pending_messages.json"


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


def add_to_queue(notification_data: Dict) -> None:
    """添加通知到离线队列"""
    queue = load_queue()
    notification_data["queued_at"] = datetime.now().isoformat()
    queue.append(notification_data)
    save_queue(queue)
    logger.info(f"📥 消息已加入离线队列（当前队列: {len(queue)} 条）")


def remove_from_queue(notification_id: str) -> None:
    """从队列中移除已发送的通知"""
    queue = load_queue()
    queue = [msg for msg in queue if msg.get("id") != notification_id]
    save_queue(queue)


def load_queue() -> List[Dict]:
    """加载离线消息队列"""
    if not QUEUE_FILE.exists():
        return []
    try:
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载队列失败: {e}")
        return []


def save_queue(queue: List[Dict]) -> None:
    """保存离线消息队列"""
    try:
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存队列失败: {e}")


def build_podcast_notification(
    date: str,
    rss_url: Optional[str] = None,
    episode_url: Optional[str] = None,
    article_count: int = 10,
    local_mode: bool = False,
    status: str = "success",
    error_message: Optional[str] = None,
) -> tuple[str, str]:
    """构建播客发布通知卡片

    Args:
        date: 播客日期 (YYYY-MM-DD)
        rss_url: RSS feed URL
        episode_url: 单集URL
        article_count: 文章数量
        local_mode: 是否为本地模式（不上传，仅通知文件生成）
        status: 执行状态 (success/failed)
        error_message: 错误信息（仅status=failed时）

    Returns:
        (title, content) 元组
    """
    if status == "failed":
        # 失败通知
        title = "❌ 今日科技早报生成失败"

        content_parts = [
            f"**📅 日期**: {date}",
            f"**❌ 状态**: 播客生成失败",
            "",
            f"**⚠️ 错误信息**:",
            f"```",
            f"{error_message or '未知错误'}",
            f"```",
            "",
            "**📂 请检查**:",
            f"- 日志文件: `logs/daily-{date}.log`",
            f"- 错误日志: `logs/daily_error.log`",
            "",
            "---",
            "💡 **排查建议**:",
            "1. 检查 API Key 是否有效",
            "2. 确认网络连接正常",
            "3. 查看详细日志定位问题",
            "4. 可手动重试: `./scripts/run_daily.sh`",
        ]

        return title, "\n".join(content_parts)

    if local_mode:
        # 本地模式：仅通知内容已生成
        title = "🎙️ 今日科技早报已生成"

        content_parts = [
            f"**📅 日期**: {date}",
            f"**📰 内容**: 精选 {article_count} 篇科技新闻",
            "",
            "**✅ 生成状态**: 内容生成完成",
            "",
            "**📂 生成文件**:",
            f"- 🎙️ `podcast-{date}.mp3` (音频)",
            f"- 🖼️ `cover-{date}.png` (封面)",
            f"- 📝 `script-{date}.md` (讲稿)",
            "",
            f"**📁 文件位置**: `output/{date}/dailyReport/`",
            "",
            "---",
            "💡 **下一步操作**:",
            "- 查看讲稿确认内容质量",
            "- 试听音频检查语音效果",
            "- 手动上传到播客平台（或稍后配置自动发布）",
        ]
    else:
        # RSS模式：已上传到RSS.com
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


async def send_notification_with_retry(
    notifier: FeishuNotifier,
    receiver_id: str,
    title: str,
    content: str,
    notification_data: Dict,
    max_retries: int = 3,
) -> bool:
    """发送通知，失败时加入队列

    Args:
        notifier: 飞书通知客户端
        receiver_id: 接收者ID
        title: 通知标题
        content: 通知内容
        notification_data: 通知元数据（用于队列）
        max_retries: 最大重试次数

    Returns:
        是否发送成功
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"📤 发送飞书通知 (尝试 {attempt + 1}/{max_retries}): {title}")

            # 判断模板颜色（失败用红色，成功用蓝色）
            template = "red" if "失败" in title else "blue"

            result = await notifier.send_card(
                receive_id=receiver_id,
                title=title,
                content=content,
                template=template,
            )

            logger.info(f"✅ 通知发送成功!")
            return True

        except httpx.NetworkError as e:
            logger.warning(f"⚠️ 网络错误 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 指数退避
            continue
        except Exception as e:
            logger.error(f"❌ 发送失败: {e}")
            break

    # 所有重试失败，加入离线队列
    logger.warning("📥 发送失败，消息已加入离线队列（网络恢复后将自动重试）")
    add_to_queue(notification_data)
    return False


async def retry_queued_messages() -> int:
    """重试队列中的所有消息

    Returns:
        成功发送的消息数量
    """
    queue = load_queue()
    if not queue:
        logger.info("📭 离线队列为空")
        return 0

    logger.info(f"📬 发现 {len(queue)} 条待发送消息，开始重试...")

    # 加载环境变量
    load_dotenv()
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    receiver_id = os.getenv("FEISHU_RECEIVER_OPEN_ID")

    if not all([app_id, app_secret, receiver_id]):
        logger.error("❌ 飞书配置未设置，无法重试")
        return 0

    notifier = FeishuNotifier(app_id, app_secret)
    success_count = 0

    for msg in queue:
        try:
            msg_id = msg.get("id")
            title = msg.get("title")
            content = msg.get("content")

            logger.info(f"🔄 重试消息: {title} (入队时间: {msg.get('queued_at')})")

            template = "red" if "失败" in title else "blue"
            await notifier.send_card(
                receive_id=receiver_id,
                title=title,
                content=content,
                template=template,
            )

            logger.info(f"✅ 消息发送成功")
            remove_from_queue(msg_id)
            success_count += 1

        except Exception as e:
            logger.warning(f"⚠️ 消息仍然发送失败: {e}")
            continue

    logger.info(f"📊 重试结果: {success_count}/{len(queue)} 条消息发送成功")
    return success_count


async def main_async():
    """异步主函数"""
    parser = argparse.ArgumentParser(description="发送播客发布通知到飞书（支持离线队列）")
    parser.add_argument("--date", help="播客日期 (YYYY-MM-DD)")
    parser.add_argument("--rss-url", help="RSS feed URL")
    parser.add_argument("--episode-url", help="单集URL")
    parser.add_argument("--article-count", type=int, default=10, help="文章数量")
    parser.add_argument("--status", choices=["success", "failed"], default="success", help="执行状态")
    parser.add_argument("--error", help="错误信息（status=failed时）")
    parser.add_argument("--retry-queue", action="store_true", help="重试离线队列中的消息")
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

    # 模式1: 重试队列
    if args.retry_queue:
        success_count = await retry_queued_messages()
        sys.exit(0 if success_count > 0 else 1)

    # 模式2: 发送新通知
    if not args.date:
        logger.error("❌ 错误: --date 参数必需（除非使用 --retry-queue）")
        sys.exit(1)

    try:
        # 创建通知客户端
        notifier = FeishuNotifier(app_id, app_secret)

        # 先尝试发送队列中的旧消息
        queue = load_queue()
        if queue:
            logger.info(f"📬 检测到 {len(queue)} 条待发送消息，先尝试发送...")
            await retry_queued_messages()

        # 判断是否为本地模式（没有提供 RSS URL）
        local_mode = not args.rss_url

        # 构建通知内容
        title, content = build_podcast_notification(
            date=args.date,
            rss_url=args.rss_url,
            episode_url=args.episode_url,
            article_count=args.article_count,
            local_mode=local_mode,
            status=args.status,
            error_message=args.error,
        )

        # 准备队列数据（如果发送失败）
        notification_data = {
            "id": f"podcast_{args.date}_{int(time.time())}",
            "title": title,
            "content": content,
            "date": args.date,
            "status": args.status,
        }

        # 发送通知（带重试和队列）
        success = await send_notification_with_retry(
            notifier=notifier,
            receiver_id=receiver_id,
            title=title,
            content=content,
            notification_data=notification_data,
        )

        sys.exit(0 if success else 1)

    except Exception as e:
        logger.error(f"❌ 飞书通知发送失败: {e}", exc_info=True)
        # 不影响主流程，仅记录错误
        sys.exit(0)


def main():
    """同步主函数入口"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
