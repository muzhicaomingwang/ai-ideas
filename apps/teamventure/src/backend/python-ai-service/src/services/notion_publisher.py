"""
Notion 同步服务

功能：
- 将每日创意发布到 Notion 页面
- 使用 Notion MCP Server API

注意：
- 需要在环境变量中配置 NOTION_PAGE_ID
- Notion MCP Server 需要预先认证

@author TeamVenture Team
@version 1.0.0
@since 2026-01-15
"""
from __future__ import annotations

import logging
import subprocess
import json
from typing import Any

from src.models.idea import DailyIdeaBatch, ProductIdea

logger = logging.getLogger(__name__)


class NotionPublisher:
    """Notion 发布器"""

    def __init__(self, notion_parent_page_id: str):
        """
        初始化 Notion 发布器

        Args:
            notion_parent_page_id: Notion 父页面 ID（创意将作为子页面创建）
        """
        self.parent_page_id = notion_parent_page_id

    async def publish_to_notion(self, batch: DailyIdeaBatch) -> bool:
        """
        发布创意批次到 Notion

        创建一个新的子页面，包含当日所有创意

        Args:
            batch: 创意批次

        Returns:
            bool: 是否成功
        """
        if not self.parent_page_id:
            logger.warning("⚠️ NOTION_PAGE_ID 未配置，跳过 Notion 同步")
            return False

        try:
            page_title = f"TeamVenture 创意 - {batch.date}"
            logger.info(f"📝 开始发布到 Notion: {page_title}")

            # 构建 Notion 页面内容（使用 Notion blocks）
            page_content = self._build_notion_page(batch)

            # 调用 Notion MCP API 创建页面
            # 注：由于在 Python 中无法直接调用 MCP 工具，这里使用 subprocess 调用 claude CLI
            # 或者使用 Notion REST API（需要额外配置）

            # 简化方案：通过日志记录，实际集成需要在主进程中调用 MCP
            logger.info(f"📄 Notion 页面内容已准备（{len(page_content)} blocks）")
            logger.info(f"⚠️ 实际 Notion 发布需要在主进程调用 MCP API")

            # TODO: 实际集成时，使用 Notion MCP API
            # 示例调用（需在支持 MCP 的环境中）:
            # result = await mcp__notion-local__API-post-page({
            #     "parent": {"page_id": self.parent_page_id},
            #     "properties": {
            #         "title": [{"text": {"content": page_title}}],
            #         "type": "title"
            #     },
            #     "children": page_content
            # })

            logger.info(f"✅ Notion 发布完成（模拟）")
            return True

        except Exception as e:
            logger.error(f"❌ Notion 发布失败: {e}", exc_info=True)
            return False

    def _build_notion_page(self, batch: DailyIdeaBatch) -> list[dict[str, Any]]:
        """
        构建 Notion 页面内容（blocks）

        Args:
            batch: 创意批次

        Returns:
            list[dict]: Notion blocks 数组
        """
        blocks = []

        # 添加元信息段落
        blocks.append(
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "text": {
                                "content": f"生成时间：{batch.ideas[0].generated_at.strftime('%Y-%m-%d %H:%M:%S')} | 创意数量：{len(batch.ideas)}"
                            }
                        }
                    ]
                },
            }
        )

        # 添加分隔线
        blocks.append({"type": "divider", "divider": {}})

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

            # 分类标题（二级标题）
            blocks.append(
                {
                    "type": "heading_2",
                    "heading_2": {"rich_text": [{"text": {"content": cat_name}}]},
                }
            )

            # 添加该分类下的所有创意
            for idea in cat_ideas:
                # 创意标题（三级标题）
                blocks.append(
                    {
                        "type": "heading_3",
                        "heading_3": {"rich_text": [{"text": {"content": idea.title}}]},
                    }
                )

                # 创意详细信息（段落 + 项目符号列表）
                blocks.append(
                    {
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": f"优先级：{idea.priority} | 工作量：{idea.estimated_effort}"
                                    }
                                }
                            ]
                        },
                    }
                )

                blocks.append(
                    {
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"text": {"content": f"描述：{idea.description}"}}]
                        },
                    }
                )

                blocks.append(
                    {
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"text": {"content": f"预期收益：{idea.expected_impact}"}}]
                        },
                    }
                )

                blocks.append(
                    {
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"text": {"content": f"上下文：{idea.context}"}}]
                        },
                    }
                )

                blocks.append(
                    {
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"text": {"content": f"创意ID：{idea.id}"}}]
                        },
                    }
                )

                # 分隔线
                blocks.append({"type": "divider", "divider": {}})

        return blocks
