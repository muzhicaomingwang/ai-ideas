from __future__ import annotations

import logging
from typing import Any

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
        """
        Placeholder for real OpenAI call.

        We intentionally keep this as a stub here to avoid introducing network usage
        and to keep local dev deterministic. Integrate `openai` SDK when ready.
        """
        raise RuntimeError("OpenAI client not configured in this skeleton")

