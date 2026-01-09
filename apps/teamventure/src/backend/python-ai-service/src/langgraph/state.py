from __future__ import annotations

from typing import Any, Optional, TypedDict


class GenerationState(TypedDict, total=False):
    plan_request_id: str
    user_id: str
    user_inputs: dict[str, Any]
    parsed_requirements: dict[str, Any]
    generated_plans: list[dict[str, Any]]
    error: Optional[str]
