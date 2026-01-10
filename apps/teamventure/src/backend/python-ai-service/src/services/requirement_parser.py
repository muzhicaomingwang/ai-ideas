from __future__ import annotations

from datetime import date
from typing import Any


def parse_requirements(message: dict[str, Any]) -> dict[str, Any]:
    """
    Rule-based parsing per detailed-design: no LLM call.
    """
    people_raw = message.get("people_count", message.get("group_size"))
    if people_raw is None:
        raise KeyError("people_count")
    people_count = int(people_raw)
    budget_min = float(message["budget_min"])
    budget_max = float(message["budget_max"])
    start_date = date.fromisoformat(message["start_date"])
    end_date = date.fromisoformat(message["end_date"])
    duration_days = (end_date - start_date).days + 1

    budget_per_person_min = budget_min / max(people_count, 1)
    budget_per_person_max = budget_max / max(people_count, 1)

    preferences = dict(message.get("preferences") or {})
    # Normalize preference keys to the ubiquitous language used in API contract.
    # Keep backward-compat with older clients/scripts.
    if "accommodation_level" not in preferences and "accommodation" in preferences:
        preferences["accommodation_level"] = preferences.get("accommodation")
    return {
        "people_count": people_count,
        "group_size": people_count,  # alias (UL v1.3): group_size
        "budget_min": budget_min,
        "budget_max": budget_max,
        "budget_per_person_range": [round(budget_per_person_min, 2), round(budget_per_person_max, 2)],
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "duration_days": duration_days,
        "departure_city": message.get("departure_city", ""),
        # Keep destination from upstream (miniapp/Java) so generated plans reflect real user input.
        # When empty, downstream may choose to recommend a destination; do not hardcode placeholder here.
        "destination": message.get("destination", "") or "",
        "destination_city": message.get("destination_city", "") or "",
        "preferences": preferences,
    }
