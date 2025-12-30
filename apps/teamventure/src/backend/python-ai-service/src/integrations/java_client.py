from __future__ import annotations

import logging
from typing import Any

import httpx

from src.models.config import settings

logger = logging.getLogger(__name__)


class JavaCallbackClient:
    def __init__(self) -> None:
        self._url = settings.java_callback_url
        self._secret = settings.java_internal_secret

    async def post_generated_plans(self, payload: dict[str, Any]) -> None:
        headers = {"X-Internal-Secret": self._secret}
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(self._url, json=payload, headers=headers)
            if resp.status_code >= 400:
                logger.error(
                    "Java callback failed: status=%s body=%s",
                    resp.status_code,
                    resp.text,
                )
                resp.raise_for_status()

