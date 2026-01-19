from __future__ import annotations

from src.services.plan_generation import (
    _extract_pois_by_day_from_markdown,
    _ensure_itinerary_contains_all_pois,
    _sanitize_itinerary_times,
    _remove_speculative_intercity_transport,
    _remove_empty_placeholder_items,
    _create_fallback_plan_from_pois,
)


def test_extract_pois_by_day_from_teamventure_markdown_reference_itinerary():
    md = """
# 团建行程方案

## 行程路线
- **参考行程**:
  - Day1: 南京路步行街-上海邮政博物馆-外白渡桥-乍浦路桥
  - **Day2**：愚园路-安福路-乌鲁木齐路-五原路-武康路-武康大楼
  - 🏷️day3: 静安寺-马勒别墅-淮海中路-思南公馆-上海新天地-上海博物馆
"""
    pois = _extract_pois_by_day_from_markdown(md)
    assert pois[1][:4] == ["南京路步行街", "上海邮政博物馆", "外白渡桥", "乍浦路桥"]
    assert pois[2] == ["愚园路", "安福路", "乌鲁木齐路", "五原路", "武康路", "武康大楼"]
    assert pois[3] == ["静安寺", "马勒别墅", "淮海中路", "思南公馆", "上海新天地", "上海博物馆"]


def test_extract_pois_by_day_from_standard_v2_schedule_lines():
    md = """
# 行程安排
> 版本: v2

## Day 1（2026-01-19）
- 09:00 - 10:30 | 参观南京路步行街 | 南京路步行街 | 
- 11:00 - 12:00 | 游览上海邮政博物馆 | 上海邮政博物馆 | 
- 14:00 - 15:00 | 参观外白渡桥和乍浦路桥 | 外白渡桥、乍浦路桥 | 
"""
    pois = _extract_pois_by_day_from_markdown(md)
    assert pois[1] == ["南京路步行街", "上海邮政博物馆", "外白渡桥", "乍浦路桥"]


def test_extract_pois_by_day_from_bullet_list_after_day_header():
    md = """
## 行程路线
Day1:
- 南京路步行街
- 上海邮政博物馆
- 外白渡桥
Day2:
- 愚园路
- 安福路
"""
    pois = _extract_pois_by_day_from_markdown(md)
    assert pois == {1: ["南京路步行街", "上海邮政博物馆", "外白渡桥"], 2: ["愚园路", "安福路"]}


def test_guardrail_appends_missing_pois_instead_of_dropping():
    plan = {
        "itinerary": {
            "days": [
                {
                    "day": 1,
                    "date": "",
                    "items": [{"time_start": "09:00", "time_end": "10:00", "activity": "南京路步行街", "location": ""}],
                }
            ]
        }
    }

    pois_by_day = {
        1: ["南京路步行街", "上海邮政博物馆", "外白渡桥"],
        2: ["愚园路", "安福路"],
    }
    patched = _ensure_itinerary_contains_all_pois(plan, pois_by_day)

    days = patched["itinerary"]["days"]
    by_day = {d["day"]: d for d in days}

    day1_acts = "\n".join(i["activity"] for i in by_day[1]["items"])
    assert "南京路步行街" in day1_acts
    assert "上海邮政博物馆" in day1_acts
    assert "外白渡桥" in day1_acts

    day2_acts = "\n".join(i["activity"] for i in by_day[2]["items"])
    assert "愚园路" in day2_acts
    assert "安福路" in day2_acts


def test_guardrail_does_not_generate_impossible_times_after_day_end():
    plan = {
        "itinerary": {
            "days": [
                {
                    "day": 3,
                    "date": "",
                    "items": [{"time_start": "20:30", "time_end": "21:00", "activity": "晚餐", "location": ""}],
                }
            ]
        }
    }
    pois_by_day = {3: ["晚餐", "A", "B", "C", "D", "E", "F", "G"]}
    patched = _ensure_itinerary_contains_all_pois(plan, pois_by_day)
    day3 = next(d for d in patched["itinerary"]["days"] if d["day"] == 3)
    # Newly appended items should not have times beyond 21:00; overflow items should omit times.
    for it in day3["items"]:
        ts = str(it.get("time_start") or "")
        te = str(it.get("time_end") or "")
        if ts and te:
            assert ts <= "21:00"
            assert te <= "21:00"


def test_sanitize_itinerary_times_drops_invalid_2400_plus():
    plan = {
        "itinerary": {
            "days": [
                {
                    "day": 3,
                    "items": [
                        {"time_start": "24:00", "time_end": "25:00", "activity": "A"},
                        {"time_start": "20:00", "time_end": "19:00", "activity": "B"},
                        {"time_start": "09:00", "time_end": "10:00", "activity": "C"},
                    ],
                }
            ]
        }
    }
    out = _sanitize_itinerary_times(plan)
    items = out["itinerary"]["days"][0]["items"]
    assert "time_start" not in items[0] and "time_end" not in items[0]
    assert "time_start" not in items[1] and "time_end" not in items[1]
    assert items[2]["time_start"] == "09:00" and items[2]["time_end"] == "10:00"


def test_sanitize_itinerary_times_nearby_not_after_2000():
    plan = {
        "itinerary": {
            "days": [
                {
                    "day": 3,
                    "items": [
                        {"time_start": "19:30", "time_end": "20:30", "activity": "外滩", "location": ""},  # nearby crosses 20
                        {"time_start": "20:00", "time_end": "21:00", "activity": "上海新天地", "location": ""},  # nearby at 20+
                        {"time_start": "21:00", "time_end": "22:00", "activity": "返程到酒店", "location": ""},  # transport ok
                        {"time_start": "22:00", "time_end": "23:00", "activity": "入住酒店", "location": ""},  # accommodation ok
                    ],
                }
            ]
        }
    }
    out = _sanitize_itinerary_times(plan)
    items = out["itinerary"]["days"][0]["items"]
    assert items[0]["time_start"] == "19:30" and items[0]["time_end"] == "20:00"
    assert "time_start" not in items[1] and "time_end" not in items[1]
    assert "20:00" in str(items[1].get("note") or "")
    assert items[2]["time_start"] == "21:00" and items[2]["time_end"] == "22:00"
    assert items[3]["time_start"] == "22:00" and items[3]["time_end"] == "23:00"


def test_sanitize_itinerary_times_nearby_not_before_0900():
    plan = {
        "itinerary": {
            "days": [
                {
                    "day": 1,
                    "items": [
                        {"time_start": "08:30", "time_end": "09:30", "activity": "外滩", "location": ""},  # nearby too early
                        {"time_start": "07:30", "time_end": "08:30", "activity": "出发前往外滩", "location": ""},  # transport ok
                    ],
                }
            ]
        }
    }
    out = _sanitize_itinerary_times(plan)
    items = out["itinerary"]["days"][0]["items"]
    assert "time_start" not in items[0] and "time_end" not in items[0]
    assert "09:00" in str(items[0].get("note") or "")
    assert items[1]["time_start"] == "07:30" and items[1]["time_end"] == "08:30"


def test_remove_speculative_intercity_transport_when_not_mentioned():
    md = "# 团建行程方案\n\n## 行程\n- 上海 citywalk\n"
    plan = {
        "itinerary": {
            "days": [
                {
                    "day": 3,
                    "items": [
                        {"time_start": "18:00", "time_end": "19:00", "activity": "上海新天地", "location": ""},
                        {"time_start": "20:00", "time_end": "22:00", "activity": "乘高铁返程", "location": "虹桥火车站"},
                        {"time_start": "22:00", "time_end": "23:00", "activity": "前往机场乘机", "location": "浦东机场"},
                        {"activity": "无"},
                    ],
                }
            ]
        }
    }
    out = _remove_speculative_intercity_transport(plan, md)
    out = _remove_empty_placeholder_items(out)
    items = out["itinerary"]["days"][0]["items"]
    acts = [i.get("activity") for i in items]
    assert acts == ["上海新天地"]


def test_keep_intercity_transport_when_mentioned():
    md = "交通：高铁 G1234\n"
    plan = {
        "itinerary": {"days": [{"day": 1, "items": [{"activity": "乘高铁出发", "location": "虹桥火车站"}]}]}
    }
    out = _remove_speculative_intercity_transport(plan, md)
    assert len(out["itinerary"]["days"][0]["items"]) == 1


def test_fallback_plan_from_pois_keeps_day_count_and_pois():
    pois_by_day = {1: ["A", "B"], 2: ["C"], 3: ["D", "E", "F"]}
    plan = _create_fallback_plan_from_pois(plan_request_id="plan_req_x", user_id="user_x", pois_by_day=pois_by_day)
    days = plan["itinerary"]["days"]
    assert [d["day"] for d in days] == [1, 2, 3]
    day3 = next(d for d in days if d["day"] == 3)
    acts = [it["activity"] for it in day3["items"]]
    assert acts == ["D", "E", "F"]

