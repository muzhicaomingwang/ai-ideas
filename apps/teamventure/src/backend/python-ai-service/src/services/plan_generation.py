from __future__ import annotations

from typing import Any

from src.services.id_generator import new_prefixed_id


def _budget_targets(inputs: dict[str, Any]) -> dict[str, float]:
    budget_min = float(inputs["budget_min"])
    budget_max = float(inputs["budget_max"])
    return {
        "budget": budget_min,
        "standard": (budget_min + budget_max) / 2.0,
        "premium": budget_max,
    }


async def generate_three_plans(
    *,
    plan_request_id: str,
    user_id: str,
    inputs: dict[str, Any],
    matched_suppliers: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Deterministic plan generation stub.

    This provides a stable end-to-end path (Java → MQ → Python → Java) without requiring
    an LLM key. Replace with LLM-backed generation when ready.
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

