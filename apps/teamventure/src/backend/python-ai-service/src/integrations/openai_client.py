from __future__ import annotations

import json
import logging
import time
from typing import Any

from openai import AsyncOpenAI

from src.models.config import settings
from src.utils.llm_metrics import record_llm_call

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
        start_time = time.perf_counter()

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
            duration = time.perf_counter() - start_time

            # Record metrics
            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0

            record_llm_call(
                model=self._model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_seconds=duration,
                status="success",
            )

            logger.info(
                "OpenAI call completed: model=%s, input_tokens=%d, output_tokens=%d, duration=%.2fs",
                self._model,
                input_tokens,
                output_tokens,
                duration,
            )

        except Exception:
            duration = time.perf_counter() - start_time
            record_llm_call(
                model=self._model,
                input_tokens=0,
                output_tokens=0,
                duration_seconds=duration,
                status="error",
            )
            logger.exception("OpenAI call failed after %.2fs", duration)
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
