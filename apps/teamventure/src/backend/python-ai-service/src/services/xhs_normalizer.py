from __future__ import annotations

import re

from src.integrations.openai_client import OpenAIClient


def _is_mostly_hashtags(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return True
    # If there are very few CJK/letters and mostly #tags/whitespace, treat as hashtag-only.
    letters = re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", t)
    tags = re.findall(r"#\S+", t)
    if len(letters) < 40 and len(tags) >= 1:
        return True
    return False


class XhsNormalizer:
    def __init__(self) -> None:
        self._client = OpenAIClient()

    async def normalize_original_text(
        self,
        *,
        url: str,
        title: str,
        extracted_text: str,
        model: str | None = None,
    ) -> str:
        text = (extracted_text or "").strip()
        if not self._client.is_configured():
            return text

        prompt = (
            "You will be given content extracted from a Xiaohongshu (RED) note.\n"
            "Task: Return ONLY the original note text content, as plain text.\n"
            "- Do NOT summarize.\n"
            "- Do NOT add headings, explanations, or markdown.\n"
            "- Preserve emojis, hashtags, punctuation, and wording.\n"
            "- Remove only obvious share-wrapper noise (e.g., '复制口令', '打开小红书App查看', duplicated links).\n"
            "- If the extracted_text looks like it contains only hashtags or is incomplete, still return the best-possible original text from what you have (do not invent facts).\n"
            "\n"
            f"url: {url}\n"
            f"title: {title}\n"
            "extracted_text:\n"
            f"{text}\n"
            "\n"
            'Return JSON: {"content": "..."}'
        )

        try:
            result = await self._client.generate_json(
                prompt,
                model=model,
                temperature=0.0,
                max_tokens=4000,
            )
            content = (result.get("content") or "").strip()
            if not content:
                return text

            # If model output regressed to hashtag-only while input was richer, keep input.
            if _is_mostly_hashtags(content) and not _is_mostly_hashtags(text):
                return text
            return content
        except Exception:
            return text
