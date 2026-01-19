from __future__ import annotations

from src.integrations.openai_client import OpenAIClient
from src.services.plan_generation import _extract_pois_by_day_from_markdown


class MarkdownOptimizer:
    def __init__(self) -> None:
        self._client = OpenAIClient()

    @staticmethod
    def _drops_user_pois(original_md: str, optimized_md: str) -> bool:
        """
        Guardrail: optimization must not drop any POI listed by day in the user's markdown.

        This is intentionally strict: if we cannot keep everything, we return original markdown.
        """
        original = (original_md or "").strip()
        optimized = (optimized_md or "").strip()
        if not original or not optimized:
            return False

        original_by_day = _extract_pois_by_day_from_markdown(original)
        if not original_by_day:
            return False

        optimized_by_day = _extract_pois_by_day_from_markdown(optimized)
        optimized_set = {p for ps in optimized_by_day.values() for p in ps}
        for day, pois in original_by_day.items():
            for p in pois:
                if p not in optimized_set:
                    return True
        return False

    async def optimize_markdown(
        self,
        *,
        markdown_content: str,
        model: str | None = None,
    ) -> str:
        text = (markdown_content or "").strip()
        if not text:
            return ""

        if not self._client.is_configured():
            return text

        prompt = (
            "You will be given a markdown draft describing a team travel/itinerary request.\n"
            "Task: Improve the markdown formatting and structure WITHOUT changing facts.\n"
            "- Do NOT invent places/times/budgets.\n"
            "- Keep all original information.\n"
            "- CRITICAL: If the markdown contains Day1/Day2/Day3... sections with POI bullet lists, you MUST keep every listed POI. Do not remove, shorten, or merge POIs.\n"
            "- If you are not sure how to improve, return the input markdown unchanged.\n"
            "- Prefer clear headings and bullet lists.\n"
            "- Preserve emojis and hashtags if present.\n"
            "- Output MUST be markdown.\n"
            "\n"
            "Return JSON: {\"markdown_content\": \"...\"}\n"
            "\n"
            "markdown_content:\n"
            f"{text}\n"
        )

        try:
            result = await self._client.generate_json(
                prompt,
                model=model,
                temperature=0.0,
                max_tokens=4000,
            )
            content = (result.get("markdown_content") or "").strip()
            if not content:
                return text
            if self._drops_user_pois(text, content):
                return text
            return content
        except Exception:
            return text
