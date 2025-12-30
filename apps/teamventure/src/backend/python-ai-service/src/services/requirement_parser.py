from __future__ import annotations

from datetime import date
from typing import Any


def parse_requirements(message: dict[str, Any]) -> dict[str, Any]:
    """
    Rule-based parsing per detailed-design: no LLM call.
    """
    people_count = int(message["people_count"])
    budget_min = float(message["budget_min"])
    budget_max = float(message["budget_max"])
    start_date = date.fromisoformat(message["start_date"])
    end_date = date.fromisoformat(message["end_date"])
    duration_days = (end_date - start_date).days + 1

    budget_per_person_min = budget_min / max(people_count, 1)
    budget_per_person_max = budget_max / max(people_count, 1)

    preferences = message.get("preferences") or {}
    return {
        "people_count": people_count,
        "budget_min": budget_min,
        "budget_max": budget_max,
        "budget_per_person_range": [round(budget_per_person_min, 2), round(budget_per_person_max, 2)],
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "duration_days": duration_days,
        "departure_city": message.get("departure_city", ""),
        "preferences": preferences,
    }

