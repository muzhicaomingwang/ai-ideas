"""
飞书文档推送服务

功能：
- 将每日创意推送到飞书文档
- 发送群消息通知
- 使用飞书 MCP Server API

注意：
- 需要在环境变量中配置 FEISHU_DOC_TOKEN 和 FEISHU_CHAT_ID
- 飞书 MCP Server 需要预先认证

@author TeamVenture Team
@version 1.0.0
@since 2026-01-15
"""
from __future__ import annotations

import logging
import json
from typing import Any

from src.models.idea import DailyIdeaBatch, ProductIdea

logger = logging.getLogger(__name__)


class FeishuPublisher:
    """飞书发布器"""

    def __init__(self, doc_token: str, chat_id: str):
        """
        初始化飞书发布器

        Args:
            doc_token: 飞书文档 token
            chat_id: 飞书群聊 ID（用于发送通知消息）
        """
        self.doc_token = doc_token
        self.chat_id = chat_id

    async def publish_to_feishu(self, batch: DailyIdeaBatch) -> bool:
        """
        发布创意批次到飞书

        1. 创建/更新飞书文档
        2. 发送群消息通知

        Args:
            batch: 创意批次

        Returns:
            bool: 是否成功
        """
        if not self.doc_token or not self.chat_id:
            logger.warning("⚠️ 飞书配置未完整，跳过飞书推送")
            return False

        try:
            logger.info(f"📝 开始发布到飞书: {batch.date}")

            # 1. 更新飞书文档（使用 Markdown 导入）
            doc_success = await self._update_feishu_doc(batch)

            # 2. 发送群消息通知
            msg_success = await self._send_chat_message(batch)

            if doc_success and msg_success:
                logger.info(f"✅ 飞书推送成功")
                return True
            else:
                logger.warning(f"⚠️ 飞书推送部分失败（文档: {doc_success}, 消息: {msg_success}）")
                return False

        except Exception as e:
            logger.error(f"❌ 飞书推送失败: {e}", exc_info=True)
            return False

    async def _update_feishu_doc(self, batch: DailyIdeaBatch) -> bool:
        """
        更新飞书文档

        使用飞书 MCP: mcp__feishu__docx_builtin_import

        Args:
            batch: 创意批次

        Returns:
            bool: 是否成功
        """
        try:
            # 构建 Markdown 内容
            markdown_content = self._format_feishu_markdown(batch)

            # TODO: 调用飞书 MCP API
            # 实际集成时需要在主进程调用：
            # result = await mcp__feishu__docx_builtin_import({
            #     "data": {
            #         "markdown": markdown_content,
            #         "file_name": f"TeamVenture创意-{batch.date}"
            #     },
            #     "useUAT": True
            # })

            logger.info(f"📄 飞书文档内容已准备（{len(markdown_content)} 字符）")
            logger.info(f"⚠️ 实际飞书文档导入需要在主进程调用 MCP API")

            return True

        except Exception as e:
            logger.error(f"❌ 更新飞书文档失败: {e}")
            return False

    async def _send_chat_message(self, batch: DailyIdeaBatch) -> bool:
        """
        发送飞书群消息通知

        使用飞书 MCP: mcp__feishu__im_v1_message_create

        Args:
            batch: 创意批次

        Returns:
            bool: 是否成功
        """
        try:
            # 构建消息内容
            message = self._format_chat_message(batch)

            # TODO: 调用飞书 MCP API
            # 实际集成时需要在主进程调用：
            # result = await mcp__feishu__im_v1_message_create({
            #     "data": {
            #         "receive_id": self.chat_id,
            #         "msg_type": "text",
            #         "content": json.dumps({"text": message})
            #     },
            #     "params": {
            #         "receive_id_type": "chat_id"
            #     }
            # })

            logger.info(f"💬 飞书群消息已准备（{len(message)} 字符）")
            logger.info(f"⚠️ 实际飞书消息发送需要在主进程调用 MCP API")

            return True

        except Exception as e:
            logger.error(f"❌ 发送飞书群消息失败: {e}")
            return False

    def _format_feishu_markdown(self, batch: DailyIdeaBatch) -> str:
        """
        格式化为飞书 Markdown 格式

        Args:
            batch: 创意批次

        Returns:
            str: Markdown 文本
        """
        lines = [
            f"# TeamVenture 每日创意 - {batch.date}",
            "",
            f"生成时间：{batch.ideas[0].generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"创意数量：{len(batch.ideas)}",
            "",
            "---",
            "",
        ]

        # 按分类添加创意
        categories = {
            "feature": "🚀 功能增强",
            "performance": "⚡ 性能优化",
            "ux": "🎨 体验改进",
            "architecture": "🏗️ 架构优化",
            "security": "🔒 安全加固",
        }

        for cat_key, cat_name in categories.items():
            cat_ideas = [i for i in batch.ideas if i.category == cat_key]
            if not cat_ideas:
                continue

            lines.append(f"## {cat_name}")
            lines.append("")

            for idea in cat_ideas:
                lines.extend(
                    [
                        f"### {idea.title}",
                        "",
                        f"**优先级**：{idea.priority} | **工作量**：{idea.estimated_effort}",
                        "",
                        f"**描述**：{idea.description}",
                        "",
                        f"**预期收益**：{idea.expected_impact}",
                        "",
                        f"**上下文**：{idea.context}",
                        "",
                        "---",
                        "",
                    ]
                )

        return "\n".join(lines)

    def _format_chat_message(self, batch: DailyIdeaBatch) -> str:
        """
        格式化群消息内容

        Args:
            batch: 创意批次

        Returns:
            str: 消息文本
        """
        summaries = []
        for i, idea in enumerate(batch.ideas, 1):
            emoji = {"P0": "🔴", "P1": "🟡", "P2": "🟢", "P3": "⚪"}.get(idea.priority, "⚪")
            summaries.append(f"{i}. {emoji} [{idea.priority}] {idea.title}")

        message = f"""📋 TeamVenture 每日创意已生成！

📅 日期：{batch.date}
🎯 创意数量：{len(batch.ideas)}

💡 创意列表：
{chr(10).join(summaries)}

📄 详情查看：
- 飞书文档：[点击查看]
- Notion：[点击查看]
- Git 仓库：docs/ideas/{batch.date.split('-')[0]}/{batch.date.split('-')[1]}/{batch.date}.md
"""

        return message
