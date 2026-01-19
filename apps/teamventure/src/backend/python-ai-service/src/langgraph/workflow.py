from __future__ import annotations

import logging
from typing import Any

from src.langgraph.state import GenerationState
from src.services.plan_generation import generate_three_plans, generate_plan_from_markdown
from src.services.requirement_parser import parse_requirements

logger = logging.getLogger(__name__)


async def run_generation_workflow(message: dict[str, Any]) -> GenerationState:
    """
    方案生成工作流（支持V1结构化输入和V2 Markdown输入）

    V1: parse requirements → generate 3 plans（结构化字段输入）
    V2: markdown_content → generate 1 plan（Markdown格式输入）
    """
    state: GenerationState = {
        "plan_request_id": message["plan_request_id"],
        "user_id": message["user_id"],
        "user_inputs": message,
    }

    try:
        logger.info("workflow start plan_request_id=%s", state["plan_request_id"])

        # V2: 如果包含markdown_content，使用新的生成逻辑
        if "markdown_content" in message and message["markdown_content"]:
            logger.info("V2模式：使用Markdown输入生成1套方案")
            state["generated_plans"] = await generate_plan_from_markdown(
                plan_request_id=state["plan_request_id"],
                user_id=state["user_id"],
                markdown_content=message["markdown_content"],
                plan_name=message.get("plan_name"),
            )
        else:
            # V1: 旧版结构化输入，生成3套方案（向后兼容）
            logger.info("V1模式：使用结构化输入生成3套方案")
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
