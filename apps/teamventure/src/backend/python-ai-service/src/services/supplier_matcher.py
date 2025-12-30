from __future__ import annotations

from typing import Any


async def match_suppliers(parsed_requirements: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Supplier matching stub.

    In the full implementation, this should read supplier catalog from MySQL (read-only)
    and optionally use an LLM to rank candidates.
    """
    city = parsed_requirements.get("departure_city") or "unknown"
    return [
        {
            "supplier_id": "sup_demo_accommodation",
            "name": f"{city}·示例民宿",
            "category": "accommodation",
            "rating": 4.5,
            "contact_phone": "13800000000",
            "contact_wechat": "demo_wechat",
        },
        {
            "supplier_id": "sup_demo_activity",
            "name": f"{city}·示例活动教练",
            "category": "activity",
            "rating": 4.6,
            "contact_phone": "13900000000",
            "contact_wechat": "demo_coach",
        },
        {
            "supplier_id": "sup_demo_dining",
            "name": f"{city}·示例餐饮",
            "category": "dining",
            "rating": 4.4,
            "contact_phone": "13700000000",
            "contact_wechat": "demo_food",
        },
    ]

