from __future__ import annotations

import json
import logging
from typing import Any

from src.integrations.openai_client import OpenAIClient
from src.services.id_generator import new_prefixed_id

logger = logging.getLogger(__name__)


def _budget_targets(inputs: dict[str, Any]) -> dict[str, float]:
    budget_min = float(inputs["budget_min"])
    budget_max = float(inputs["budget_max"])
    return {
        "budget": budget_min,
        "standard": (budget_min + budget_max) / 2.0,
        "premium": budget_max,
    }


def _normalize_generated_plans(
    *,
    raw: dict[str, Any],
    plan_request_id: str,
    user_id: str,
    duration_days: int,
) -> list[dict[str, Any]]:
    plans = raw.get("plans")
    if not isinstance(plans, list) or len(plans) != 3:
        raise ValueError("LLM response must include plans: [..3 items..]")

    normalized: list[dict[str, Any]] = []
    for plan in plans:
        if not isinstance(plan, dict):
            raise ValueError("Each plan must be an object")
        normalized.append(
            {
                "plan_id": new_prefixed_id("plan"),
                "plan_request_id": plan_request_id,
                "user_id": user_id,
                "plan_type": str(plan.get("plan_type", "")),
                "plan_name": str(plan.get("plan_name", "")),
                "summary": str(plan.get("summary", "")),
                "highlights": plan.get("highlights", []),
                "itinerary": plan.get("itinerary", {}),
                "budget_breakdown": plan.get("budget_breakdown", {}),
                "supplier_snapshots": plan.get("supplier_snapshots", []),
                "budget_total": float(plan.get("budget_total", 0.0) or 0.0),
                "budget_per_person": float(plan.get("budget_per_person", 0.0) or 0.0),
                "duration_days": duration_days,
                "departure_city": plan.get("departure_city"),
                "status": "draft",
            }
        )
    return normalized


async def _generate_three_plans_stub(
    *,
    plan_request_id: str,
    user_id: str,
    inputs: dict[str, Any],
    matched_suppliers: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Deterministic plan generation fallback.

    Keeps the Java → MQ → Python → Java path usable without LLM credentials.
    """
    people = int(inputs["people_count"])
    duration_days = int(inputs["duration_days"])
    city = inputs.get("departure_city") or "目的地"
    targets = _budget_targets(inputs)

    def make_plan(plan_type: str, budget_total: float) -> dict[str, Any]:
        plan_id = new_prefixed_id("plan")
        per_person = round(budget_total / max(people, 1), 2)
        supplier_snapshots = matched_suppliers[:]
        return {
            "plan_id": plan_id,
            "plan_request_id": plan_request_id,
            "user_id": user_id,
            "plan_type": plan_type,
            "plan_name": f"{plan_type.upper()}·{city}{duration_days}天团建",
            "summary": f"人均¥{per_person}，{duration_days}天行程，含住宿/活动/餐饮",
            "highlights": [f"人均¥{per_person}", "可对比三套方案", "供应商信息透明"],
            "itinerary": {
                "days": [
                    {
                        "day": 1,
                        "items": [
                            {"time_start": "09:00", "time_end": "11:00", "activity": "出发前往目的地"},
                            {"time_start": "11:30", "time_end": "13:00", "activity": "午餐"},
                            {"time_start": "14:00", "time_end": "17:00", "activity": "团队活动"},
                        ],
                    }
                ]
            },
            "budget_breakdown": {
                "total": round(budget_total, 2),
                "per_person": per_person,
                "categories": [
                    {"category": "交通", "subtotal": round(budget_total * 0.25, 2)},
                    {"category": "住宿", "subtotal": round(budget_total * 0.35, 2)},
                    {"category": "餐饮", "subtotal": round(budget_total * 0.25, 2)},
                    {"category": "活动", "subtotal": round(budget_total * 0.15, 2)},
                ],
            },
            "supplier_snapshots": supplier_snapshots,
            "budget_total": round(budget_total, 2),
            "budget_per_person": per_person,
            "duration_days": duration_days,
            "departure_city": city,
            "status": "draft",
        }

    plans: list[dict[str, Any]] = []
    for plan_type in ["budget", "standard", "premium"]:
        plans.append(make_plan(plan_type, targets[plan_type]))
    return plans


async def generate_three_plans(
    *,
    plan_request_id: str,
    user_id: str,
    inputs: dict[str, Any],
    matched_suppliers: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Generate 3 plans via LLM (preferred) with deterministic fallback.
    """
    people = int(inputs["people_count"])
    duration_days = int(inputs["duration_days"])
    city = inputs.get("departure_city") or "目的地"
    targets = _budget_targets(inputs)

    client = OpenAIClient()
    if not client.is_configured():
        logger.warning("OPENAI_API_KEY not configured; using stub plan generation")
        return await _generate_three_plans_stub(
            plan_request_id=plan_request_id,
            user_id=user_id,
            inputs=inputs,
            matched_suppliers=matched_suppliers,
        )

    prompt_payload = {
        "plan_request_id": plan_request_id,
        "user_id": user_id,
        "inputs": inputs,
        "matched_suppliers": matched_suppliers,
        "constraints": {
            "people_count": people,
            "duration_days": duration_days,
            "departure_city": city,
            "budget_targets_total": targets,
        },
        "output_contract": {
            "plans_length": 3,
            "plan_types": ["budget", "standard", "premium"],
        },
    }

    prompt = (
        "Generate exactly 3 corporate team-building plans in Chinese.\n"
        "Return JSON ONLY with this shape:\n"
        "{\n"
        '  "plans": [\n'
        "    {\n"
        '      "plan_type": "budget|standard|premium",\n'
        '      "plan_name": "string",\n'
        '      "summary": "string",\n'
        '      "highlights": ["string"],\n'
        '      "itinerary": {"days": [{"day": 1, "items": [{"time_start":"HH:MM","time_end":"HH:MM","activity":"string"}]}]},\n'
        '      "budget_breakdown": {"total": number, "per_person": number, "categories": [{"category":"string","subtotal": number}]},\n'
        '      "supplier_snapshots": [{"supplier_id":"string","name":"string","type":"string","price_range":"string"}],\n'
        '      "budget_total": number,\n'
        '      "budget_per_person": number,\n'
        '      "departure_city": "string"\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "Rules:\n"
        "- plans must match plan_types budget/standard/premium in order.\n"
        "- budget_total must be close to constraints.budget_targets_total for each plan.\n"
        "- budget_per_person = budget_total / people_count.\n"
        "- Keep itinerary duration_days days.\n"
        "\n"
        "Input JSON:\n"
        f"{json.dumps(prompt_payload, ensure_ascii=False)}"
    )

    raw = await client.generate_json(prompt)
    return _normalize_generated_plans(
        raw=raw,
        plan_request_id=plan_request_id,
        user_id=user_id,
        duration_days=duration_days,
    )
