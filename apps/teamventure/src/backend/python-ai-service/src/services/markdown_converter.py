from __future__ import annotations

from datetime import datetime

from src.integrations.openai_client import OpenAIClient


def _looks_like_standard_itinerary_markdown(md: str) -> bool:
    t = (md or "").strip()
    if not t:
        return False
    return "# 行程安排" in t and "> 版本:" in t and "## Day" in t and " | " in t


class MarkdownConverter:
    def __init__(self) -> None:
        self._client = OpenAIClient()

    async def convert_parsed_text_to_markdown(
        self,
        *,
        parsed_content: str,
        model: str | None = None,
    ) -> str:
        text = (parsed_content or "").strip()
        if not text:
            return ""

        if not self._client.is_configured():
            raise RuntimeError("OPENAI_API_KEY is not configured")

        prompt = (
            "你将获得一段“小红书笔记解析原文”（纯文本）。\n"
            "任务：把它转成 TeamVenture 应用的“标准行程 Markdown（v2）”，用于后续 /plans/generate。\n"
            "\n"
            "强约束（非常重要）：\n"
            "- 不能编造任何事实（地点/天数/预算/交通/酒店/价格等）。\n"
            "- 大量去除无效信息：分享包装、口令、emoji堆砌、无关标签等；只保留能用于行程安排的核心内容。\n"
            "- 不要丢失任何在原文中出现的景点/POI 名称；如需合并到同一条行程，也必须在“地点”列完整保留名称。\n"
            "- 不要输出“解释/分析/总结”，只输出最终 Markdown。\n"
            "- 如果原文没有明确日期：Day 标题里的日期请用“今天”为 Day1 起始日（仅用于展示占位，用户后续会确认）。\n"
            "- 如果原文包含 day1/day2/D1/第1天 等分天信息：必须输出对应的 Day1/Day2/Day3…\n"
            "- 每天输出多条行程条目，每条严格使用格式：\n"
            "  - HH:MM - HH:MM | 活动 | 地点 | 备注\n"
            "- 时间范围约束：周边游类最早 09:00，最晚 20:00；20:00 后不安排周边游。\n"
            "- 交通/住宿允许没有具体时间（可留空或用大致范围），但不要编造航班/高铁等跨城交通。\n"
            "\n"
            "标准 Markdown 输出格式（必须严格遵守）：\n"
            "# 行程安排\n"
            "> 版本: v2\n"
            "\n"
            "## Day N（YYYY-MM-DD）\n"
            "- 09:00 - 10:30 | 活动 | 地点 | \n"
            "- 11:00 - 12:00 | 活动 | 地点 | \n"
            "\n"
            "\n"
            "输入 parsed_content：\n"
            f"{text}\n"
            "\n"
            '返回 JSON：{"markdown_content":"..."}'
        )

        try:
            result = await self._client.generate_json(
                prompt,
                model=model,
                temperature=0.0,
                max_tokens=4000,
            )
            content = (result.get("markdown_content") or "").strip()
            if content and _looks_like_standard_itinerary_markdown(content):
                return content
            raise RuntimeError("AI returned non-standard markdown_content")
        except Exception:
            raise
