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

    async def generate_json(
        self,
        prompt: str,
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError("OPENAI_API_KEY is not configured")

        client = AsyncOpenAI(api_key=self._api_key)
        start_time = time.perf_counter()

        model_to_use = model or self._model
        temperature_to_use = self._temperature if temperature is None else temperature
        max_tokens_to_use = self._max_tokens if max_tokens is None else max_tokens

        try:
            kwargs: dict[str, Any] = {
                "model": model_to_use,
                "temperature": temperature_to_use,
                "response_format": {"type": "json_object"},
                "messages": [
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
            }

            # Some newer models (e.g. gpt-5.*) reject `max_tokens` and require `max_completion_tokens`.
            if isinstance(model_to_use, str) and model_to_use.startswith(("gpt-5", "o")):
                kwargs["max_completion_tokens"] = max_tokens_to_use
            else:
                kwargs["max_tokens"] = max_tokens_to_use

            response = await client.chat.completions.create(**kwargs)
            duration = time.perf_counter() - start_time

            # Record metrics
            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0

            record_llm_call(
                model=model_to_use,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_seconds=duration,
                status="success",
            )

            logger.info(
                "OpenAI call completed: model=%s, input_tokens=%d, output_tokens=%d, duration=%.2fs",
                model_to_use,
                input_tokens,
                output_tokens,
                duration,
            )

        except Exception:
            duration = time.perf_counter() - start_time
            record_llm_call(
                model=model_to_use,
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
