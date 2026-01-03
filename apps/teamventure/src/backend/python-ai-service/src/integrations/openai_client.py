from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI

from src.models.config import settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    """
    Minimal OpenAI client wrapper.

    Note: This repo may run without valid OPENAI_API_KEY in local dev; callers should
    gracefully fall back to deterministic stub generation when keys are missing.
    """

    def __init__(self) -> None:
        self._api_key = settings.openai_api_key
        self._model = settings.openai_model
        self._temperature = settings.openai_temperature
        self._max_tokens = settings.openai_max_tokens

    def is_configured(self) -> bool:
        return bool(self._api_key and not self._api_key.startswith("sk-xxxx"))

    async def generate_json(self, prompt: str) -> dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError("OPENAI_API_KEY is not configured")

        client = AsyncOpenAI(api_key=self._api_key)

        try:
            response = await client.chat.completions.create(
                model=self._model,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a careful assistant. "
                            "Return ONLY valid JSON that matches the user's requested shape. "
                            "Do not wrap in markdown."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )
        except Exception:
            logger.exception("OpenAI call failed")
            raise

        content = (response.choices[0].message.content or "").strip()
        if not content:
            raise RuntimeError("OpenAI returned empty content")

        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            logger.error("OpenAI returned non-JSON content: %r", content[:500])
            raise RuntimeError("OpenAI returned invalid JSON") from exc

        if not isinstance(parsed, dict):
            raise RuntimeError("OpenAI JSON root must be an object")
        return parsed
