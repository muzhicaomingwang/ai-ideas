from __future__ import annotations

import logging
from typing import Any

from src.langgraph.state import GenerationState
from src.services.plan_generation import generate_three_plans
from src.services.requirement_parser import parse_requirements
from src.services.supplier_matcher import match_suppliers

logger = logging.getLogger(__name__)


async def run_generation_workflow(message: dict[str, Any]) -> GenerationState:
    """
    Minimal workflow that matches the detailed design phases:
    parse requirements → match suppliers → generate plans.

    This is intentionally a lightweight implementation that can run without LLM keys.
    """
    state: GenerationState = {
        "plan_request_id": message["plan_request_id"],
        "user_id": message["user_id"],
        "user_inputs": message,
    }

    try:
        state["parsed_requirements"] = parse_requirements(message)
        state["matched_suppliers"] = await match_suppliers(state["parsed_requirements"])
        state["generated_plans"] = await generate_three_plans(
            plan_request_id=state["plan_request_id"],
            user_id=state["user_id"],
            inputs=state["parsed_requirements"],
            matched_suppliers=state["matched_suppliers"],
        )
        return state
    except Exception as exc:
        logger.exception("Generation workflow failed")
        state["error"] = str(exc)
        return state

