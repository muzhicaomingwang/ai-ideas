"""
团建方案生成服务

字段语义说明：
- departure_city: 出发城市，团队从哪里出发（如公司所在地：上海市）
- destination: 目的地，团建活动举办地点（如：杭州千岛湖）
- destination_city: 目的地所属行政城市（如：杭州）

前端显示格式："{departure_city} → {destination}"
示例：上海市 → 杭州千岛湖
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from src.integrations.openai_client import OpenAIClient
from src.integrations.amap_client import AmapClient
from src.services.id_generator import new_prefixed_id

logger = logging.getLogger(__name__)


# ============ 偏好翻译映射 ============

ACTIVITY_TYPE_NAMES = {
    "team_building": "团队拓展",
    "leisure": "休闲度假",
    "culture": "文化体验",
    "sports": "运动挑战",
}

ACCOMMODATION_LEVEL_NAMES = {
    "budget": "经济型（快捷酒店）",
    "standard": "舒适型（三星/四星酒店）",
    "premium": "品质型（五星酒店/度假村）",
}

# ============ 季节配置 ============

SEASON_CONFIG = {
    "winter": {
        "months": [12, 1, 2],
        "description": "冬季（12-2月），气温较低",
        "forbidden_activities": ["游艇出海", "水上活动", "漂流", "户外露营"],
        "recommended": ["温泉", "室内拓展", "滑雪", "火锅聚餐"],
    },
    "spring": {
        "months": [3, 4, 5],
        "description": "春季（3-5月），气候温和",
        "forbidden_activities": [],
        "recommended": ["踏青", "户外拓展", "骑行", "登山"],
    },
    "summer": {
        "months": [6, 7, 8],
        "description": "夏季（6-8月），天气炎热",
        "forbidden_activities": ["高强度户外暴晒活动"],
        "recommended": ["水上活动", "漂流", "避暑山庄", "夜间活动"],
    },
    "autumn": {
        "months": [9, 10, 11],
        "description": "秋季（9-11月），气候宜人",
        "forbidden_activities": [],
        "recommended": ["登山", "户外拓展", "采摘", "露营"],
    },
}


def _get_season_info(start_date: str, city: str) -> dict[str, Any]:
    """根据日期和城市获取季节信息"""
    try:
        date = datetime.strptime(start_date, "%Y-%m-%d")
        month = date.month
    except (ValueError, TypeError):
        month = datetime.now().month

    for season, config in SEASON_CONFIG.items():
        if month in config["months"]:
            return {
                "season": season,
                "description": config["description"],
                "forbidden_activities": config["forbidden_activities"],
                "recommended": config["recommended"],
            }

    return {
        "season": "unknown",
        "description": "请根据实际天气安排活动",
        "forbidden_activities": [],
        "recommended": [],
    }


def _translate_activity_types(types: list[str]) -> list[str]:
    """翻译活动类型"""
    return [ACTIVITY_TYPE_NAMES.get(t, t) for t in types]


def _translate_accommodation_level(level: str) -> str:
    """翻译住宿标准"""
    return ACCOMMODATION_LEVEL_NAMES.get(level, "舒适型酒店")


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
    departure_city: str,
    destination: str,
    destination_city: str,
) -> list[dict[str, Any]]:
    """
    规范化 LLM 生成的方案数据

    Args:
        departure_city: 出发城市（团队从哪里出发，如：上海市）
        destination: 目的地（团建活动举办地点，如：杭州千岛湖）
        destination_city: 目的地所属行政城市（如：杭州）
    """
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
                # MVP 不输出供应商信息，但数据库字段仍为 NOT NULL，统一写空数组
                "supplier_snapshots": [],
                "budget_total": float(plan.get("budget_total", 0.0) or 0.0),
                "budget_per_person": float(plan.get("budget_per_person", 0.0) or 0.0),
                "duration_days": duration_days,
                "departure_city": departure_city,  # 出发城市（从输入获取，非LLM生成）
                "destination": destination,        # 目的地（从输入获取，非LLM生成）
                "destination_city": destination_city,  # 目的地城市（可由上游/高德补全）
                "status": "draft",
            }
        )
    return normalized


# ============ 预算合理性校验 ============

# 各城市住宿参考价格（元/人/晚）
CITY_ACCOMMODATION_PRICES = {
    "default": {"budget": 80, "standard": 150, "premium": 300},
    "杭州": {"budget": 100, "standard": 180, "premium": 350},
    "上海": {"budget": 120, "standard": 220, "premium": 450},
    "北京": {"budget": 120, "standard": 220, "premium": 450},
    "深圳": {"budget": 110, "standard": 200, "premium": 400},
    "广州": {"budget": 100, "standard": 180, "premium": 350},
}

# 预算分配合理区间
BUDGET_RATIO_RANGES = {
    "accommodation": (0.20, 0.40),  # 住宿 20-40%
    "activities": (0.25, 0.45),     # 活动 25-45%
    "dining": (0.15, 0.30),         # 餐饮 15-30%
    "transport": (0.05, 0.20),      # 交通 5-20%
}


def _validate_and_fix_budget(
    plans: list[dict[str, Any]],
    people_count: int,
    duration_days: int,
    city: str,
    accommodation_level: str,
) -> list[dict[str, Any]]:
    """
    校验并修正预算分配的合理性
    """
    city_prices = CITY_ACCOMMODATION_PRICES.get(city, CITY_ACCOMMODATION_PRICES["default"])

    validated_plans = []
    for plan in plans:
        plan_type = plan.get("plan_type", "standard")
        budget_total = plan.get("budget_total", 0)
        breakdown = plan.get("budget_breakdown", {})

        if not breakdown or not isinstance(breakdown.get("categories"), list):
            # 如果没有分解，创建合理的默认分解
            breakdown = _create_reasonable_breakdown(
                budget_total, people_count, duration_days, city, plan_type
            )
            plan["budget_breakdown"] = breakdown
        else:
            # 校验现有分解是否合理
            breakdown = _fix_budget_breakdown(
                breakdown, budget_total, people_count, duration_days, city, plan_type
            )
            plan["budget_breakdown"] = breakdown

        # 添加校验标记
        plan["budget_validated"] = True
        validated_plans.append(plan)

    return validated_plans


def _create_reasonable_breakdown(
    budget_total: float,
    people_count: int,
    duration_days: int,
    city: str,
    plan_type: str,
) -> dict[str, Any]:
    """创建合理的预算分解"""
    # 根据方案类型调整比例
    if plan_type == "budget":
        ratios = {"accommodation": 0.25, "activities": 0.35, "dining": 0.25, "transport": 0.15}
    elif plan_type == "premium":
        ratios = {"accommodation": 0.35, "activities": 0.35, "dining": 0.20, "transport": 0.10}
    else:  # standard
        ratios = {"accommodation": 0.30, "activities": 0.35, "dining": 0.25, "transport": 0.10}

    categories = []
    for category, ratio in ratios.items():
        category_names = {
            "accommodation": "住宿",
            "activities": "活动",
            "dining": "餐饮",
            "transport": "交通",
        }
        categories.append({
            "category": category_names.get(category, category),
            "subtotal": round(budget_total * ratio, 2),
        })

    return {
        "total": budget_total,
        "per_person": round(budget_total / max(people_count, 1), 2),
        "categories": categories,
    }


def _fix_budget_breakdown(
    breakdown: dict[str, Any],
    budget_total: float,
    people_count: int,
    duration_days: int,
    city: str,
    plan_type: str,
) -> dict[str, Any]:
    """修正不合理的预算分解"""
    categories = breakdown.get("categories", [])
    if not categories:
        return _create_reasonable_breakdown(budget_total, people_count, duration_days, city, plan_type)

    # 计算各项占比并检查
    category_map = {c.get("category", ""): c.get("subtotal", 0) for c in categories}
    total_allocated = sum(category_map.values())

    # 如果总和与预算差异过大，重新分配
    if abs(total_allocated - budget_total) > budget_total * 0.1:
        return _create_reasonable_breakdown(budget_total, people_count, duration_days, city, plan_type)

    # 检查住宿是否合理（最常见的问题）
    accommodation_cost = category_map.get("住宿", 0) or category_map.get("accommodation", 0)
    city_prices = CITY_ACCOMMODATION_PRICES.get(city, CITY_ACCOMMODATION_PRICES["default"])
    min_accommodation = city_prices.get(plan_type, 100) * duration_days

    if accommodation_cost < min_accommodation * 0.5:
        # 住宿费用过低，记录警告并调整
        logger.warning(
            f"住宿预算过低: {accommodation_cost} < 最低参考 {min_accommodation}, "
            f"城市={city}, 类型={plan_type}, 天数={duration_days}"
        )
        # 这里可以选择修正或仅记录警告

    return breakdown


async def _generate_three_plans_stub(
    *,
    plan_request_id: str,
    user_id: str,
    inputs: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    确定性方案生成回退（无 LLM 凭证时使用）

    字段说明：
    - departure_city: 出发城市（团队从哪里出发，如：上海市）
    - destination: 目的地（团建活动举办地点，如：杭州千岛湖）
    - destination_city: 目的地所属行政城市（如：杭州）
    """
    people = int(inputs["people_count"])
    duration_days = int(inputs["duration_days"])
    # 正确区分出发城市和目的地
    departure_city = inputs.get("departure_city") or "出发地"  # 出发城市
    destination = inputs.get("destination") or "目的地"        # 团建活动举办地点
    destination_city = inputs.get("destination_city") or ""   # 目的地所属城市（可选）
    targets = _budget_targets(inputs)

    def make_plan(plan_type: str, budget_total: float) -> dict[str, Any]:
        plan_id = new_prefixed_id("plan")
        per_person = round(budget_total / max(people, 1), 2)
        return {
            "plan_id": plan_id,
            "plan_request_id": plan_request_id,
            "user_id": user_id,
            "plan_type": plan_type,
            "plan_name": f"{plan_type.upper()}·{destination}{duration_days}天团建",  # 使用目的地命名
            "summary": f"从{departure_city}出发，前往{destination}，人均¥{per_person}，{duration_days}天行程",
            "highlights": [f"人均¥{per_person}", f"{departure_city} → {destination}", "可对比三套方案"],
            "itinerary": {
                "days": [
                    {
                        "day": 1,
                        "items": [
                            {"time_start": "09:00", "time_end": "11:00", "activity": f"从{departure_city}出发前往{destination}"},
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
            "supplier_snapshots": [],
            "budget_total": round(budget_total, 2),
            "budget_per_person": per_person,
            "duration_days": duration_days,
            "departure_city": departure_city,  # 出发城市
            "destination": destination,        # 目的地
            "destination_city": destination_city,
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
) -> list[dict[str, Any]]:
    """
    通过 LLM 生成3套方案（优先），或使用确定性回退

    字段说明：
    - departure_city: 出发城市（团队从哪里出发，如：上海市）
    - destination: 目的地（团建活动举办地点，如：杭州千岛湖）
    - destination_city: 目的地所属行政城市（如：杭州）
    """
    people = int(inputs["people_count"])
    duration_days = int(inputs["duration_days"])
    # 正确区分出发城市和目的地
    departure_city = inputs.get("departure_city") or "出发地"  # 出发城市
    destination = inputs.get("destination") or "目的地"        # 团建活动举办地点
    destination_city = inputs.get("destination_city") or ""   # 目的地所属城市（用于季节/价格配置）
    targets = _budget_targets(inputs)

    client = OpenAIClient()
    if not client.is_configured():
        logger.warning("OPENAI_API_KEY not configured; using stub plan generation")
        return await _generate_three_plans_stub(
            plan_request_id=plan_request_id,
            user_id=user_id,
            inputs=inputs,
        )

    # 提取用户偏好
    preferences = inputs.get("preferences", {}) or {}
    activity_types = preferences.get("activity_types", [])
    accommodation_level = preferences.get("accommodation_level", "standard")
    special_requirements = preferences.get("special_requirements", "")
    start_date = inputs.get("start_date", "")
    end_date = inputs.get("end_date", "")

    destination_context = None
    amap = AmapClient()
    if amap.is_enabled():
        destination_context = await amap.enrich_destination(
            destination=destination,
            activity_types=activity_types if isinstance(activity_types, list) else [],
            accommodation_level=str(accommodation_level),
        )
        if not destination_city and isinstance(destination_context, dict):
            destination_city = str(destination_context.get("destination_city") or "")

    # 季节适配（基于目的地城市而非出发城市）
    city_for_context = destination_city or destination
    season_info = _get_season_info(start_date, city_for_context)

    prompt_payload = {
        "plan_request_id": plan_request_id,
        "user_id": user_id,
        "inputs": inputs,
        "constraints": {
            "people_count": people,
            "duration_days": duration_days,
            "departure_city": departure_city,  # 出发城市
            "destination": destination,        # 目的地（活动举办地点）
            "destination_city": destination_city,  # 目的地所属城市（行政区）
            "budget_targets_total": targets,
        },
        "user_preferences": {
            "activity_types": activity_types,
            "accommodation_level": accommodation_level,
            "special_requirements": special_requirements,
        },
        "season_context": season_info,
        "destination_context": destination_context,
        "output_contract": {
            "plans_length": 3,
            "plan_types": ["budget", "standard", "premium"],
        },
    }

    # 构建偏好约束描述
    activity_desc = "、".join(_translate_activity_types(activity_types)) if activity_types else "团队拓展活动"
    accommodation_desc = _translate_accommodation_level(accommodation_level)

    destination_hint = ""
    if destination_context and isinstance(destination_context, dict):
        destination_hint = (
            "\n=== 目的地真实信息（尽量引用）===\n"
            "- destination_context 已提供高德 POI 列表（按类别），请在行程中尽量使用其中的真实地点名称。\n"
            "- 每天至少包含 2 个带具体地点名的活动/用餐点（例如：某景区/某农家乐/某拓展基地）。\n"
        )

    extra_constraints = ""
    if special_requirements:
        extra_constraints += f"- 特殊需求（必须考虑）：{special_requirements}\n"
    extra_constraints += destination_hint

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
        '      "budget_total": number,\n'
        '      "budget_per_person": number\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "\n"
        "=== 严格约束（必须遵守）===\n"
        f"1. 活动类型必须包含: {activity_desc}\n"
        f"2. 住宿标准: {accommodation_desc}\n"
        f"3. 季节注意: {season_info['description']}，禁止安排: {', '.join(season_info['forbidden_activities'])}\n"
        "\n"
        "=== 预算约束 ===\n"
        "- plans must match plan_types budget/standard/premium in order.\n"
        "- budget_total must be close to constraints.budget_targets_total for each plan.\n"
        "- budget_per_person = budget_total / people_count.\n"
        f"- 住宿预算占比应为25-35%（{accommodation_desc}标准）\n"
        "- 活动预算占比应为30-40%\n"
        "- 餐饮预算占比应为20-25%\n"
        "- 交通预算占比应为10-15%\n"
        "\n"
        "=== 行程约束 ===\n"
        "- Keep itinerary duration_days days.\n"
        f"- 出发城市: {departure_city}（团队从这里出发）\n"
        f"- 目的地: {destination}（团建活动举办地点）\n"
        f"- 目的地城市: {destination_city or '（未知）'}（用于季节/价格参考）\n"
        f"- 活动应在{destination}或周边（车程2小时内）\n"
        f"{extra_constraints}"
        "\n"
        "Input JSON:\n"
        f"{json.dumps(prompt_payload, ensure_ascii=False)}"
    )

    raw = await client.generate_json(prompt)
    normalized_plans = _normalize_generated_plans(
        raw=raw,
        plan_request_id=plan_request_id,
        user_id=user_id,
        duration_days=duration_days,
        departure_city=departure_city,  # 出发城市
        destination=destination,        # 目的地
        destination_city=destination_city,
    )

    # 预算合理性校验（基于目的地，因为住宿/活动在目的地）
    validated_plans = _validate_and_fix_budget(
        plans=normalized_plans,
        people_count=people,
        duration_days=duration_days,
        city=city_for_context,  # 优先使用目的地城市（行政区）进行预算校验
        accommodation_level=accommodation_level,
    )

    return validated_plans
