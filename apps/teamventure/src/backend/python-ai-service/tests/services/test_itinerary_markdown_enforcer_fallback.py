import pytest

from src.services.itinerary_markdown_enforcer import ensure_valid_itinerary_markdown
from src.services.itinerary_markdown_v2 import validate


@pytest.mark.asyncio
async def test_enforcer_fallback_is_always_valid_when_llm_not_configured():
    invalid = "# 行程安排\n## Day 1\n- - | 欧堡酒店 |\n"
    res = await ensure_valid_itinerary_markdown(
        initial_markdown=invalid,
        fallback_markdown="随便一段生成前输入（不一定是v2行程表）",
        max_attempts=5,
    )
    assert validate(res["markdown"])["valid"] is True
    assert res["fallback_used"] is True

