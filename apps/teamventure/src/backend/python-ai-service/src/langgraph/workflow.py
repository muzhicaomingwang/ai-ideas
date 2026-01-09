from __future__ import annotations

import logging
from typing import Any

from src.langgraph.state import GenerationState
from src.services.plan_generation import generate_three_plans
from src.services.requirement_parser import parse_requirements

logger = logging.getLogger(__name__)


async def run_generation_workflow(message: dict[str, Any]) -> GenerationState:
    """
    Minimal workflow that matches the detailed design phases:
    parse requirements → generate plans.

    This is intentionally a lightweight implementation that can run without LLM keys.
    """
    state: GenerationState = {
        "plan_request_id": message["plan_request_id"],
        "user_id": message["user_id"],
        "user_inputs": message,
    }

    try:
        logger.info("workflow start plan_request_id=%s", state["plan_request_id"])
        state["parsed_requirements"] = parse_requirements(message)
        logger.info("requirements parsed plan_request_id=%s", state["plan_request_id"])
        state["generated_plans"] = await generate_three_plans(
            plan_request_id=state["plan_request_id"],
            user_id=state["user_id"],
            inputs=state["parsed_requirements"],
        )
        logger.info(
            "plans generated plan_request_id=%s count=%s",
            state["plan_request_id"],
            len(state.get("generated_plans") or []),
        )
        return state
    except Exception as exc:
        logger.exception("Generation workflow failed")
        state["error"] = str(exc)
        return state
