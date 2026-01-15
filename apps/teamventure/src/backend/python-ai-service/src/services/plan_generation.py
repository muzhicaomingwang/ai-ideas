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

import hashlib
import json
import logging
from datetime import datetime
from typing import Any

from src.integrations.openai_client import OpenAIClient
from src.integrations.amap_client import AmapClient
from src.services.id_generator import new_prefixed_id
from src.models.config import settings

logger = logging.getLogger(__name__)

# ============ Redis缓存客户端（懒加载）============
_redis_client = None


def _get_redis_client():
    """获取Redis客户端（懒加载）"""
    global _redis_client
    if _redis_client is None and settings.ai_cache_enabled:
        try:
            import redis
            _redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                db=settings.redis_db,
                decode_responses=True,
            )
            # 测试连接
            _redis_client.ping()
            logger.info("Redis AI cache connected successfully")
        except Exception as exc:
            logger.warning(f"Failed to connect to Redis for AI cache: {exc}")
            _redis_client = False  # 标记为不可用
    return _redis_client if _redis_client is not False else None


def _generate_cache_key(inputs: dict[str, Any]) -> str:
    """生成缓存key（基于输入hash）"""
    # 只用影响方案生成的关键字段计算hash
    cache_payload = {
        "people_count": inputs.get("people_count"),
        "duration_days": inputs.get("duration_days"),
        "departure_city": inputs.get("departure_city"),
        "destination": inputs.get("destination"),
        "budget_min": inputs.get("budget_min"),
        "budget_max": inputs.get("budget_max"),
        "preferences": inputs.get("preferences"),
    }
    payload_str = json.dumps(cache_payload, sort_keys=True, ensure_ascii=False)
    hash_digest = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()[:16]
    return f"ai:plan:{hash_digest}"


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

    优化机制：
    1. Mock模式：ENABLE_AI_MOCK=true 时强制使用stub（节省token）
    2. 缓存机制：相同输入24小时内直接返回缓存结果
    3. Fallback：API key未配置时自动降级到stub
    """
    people = int(inputs["people_count"])
    duration_days = int(inputs["duration_days"])
    # 正确区分出发城市和目的地
    departure_city = inputs.get("departure_city") or "出发地"  # 出发城市
    destination = inputs.get("destination") or "目的地"        # 团建活动举办地点
    destination_city = inputs.get("destination_city") or ""   # 目的地所属城市（用于季节/价格配置）
    targets = _budget_targets(inputs)

    # === 1. Mock模式检查 ===
    if settings.enable_ai_mock:
        logger.info("AI Mock模式已启用，使用确定性stub生成（节省token）")
        return await _generate_three_plans_stub(
            plan_request_id=plan_request_id,
            user_id=user_id,
            inputs=inputs,
        )

    # === 2. 缓存检查 ===
    cache_key = _generate_cache_key(inputs)
    redis = _get_redis_client()
    if redis and settings.ai_cache_enabled:
        try:
            cached = redis.get(cache_key)
            if cached:
                logger.info(f"AI缓存命中 cache_key={cache_key}，跳过LLM调用")
                cached_plans = json.loads(cached)
                # 更新 plan_id 和 plan_request_id（避免ID重复）
                for plan in cached_plans:
                    plan["plan_id"] = new_prefixed_id("plan")
                    plan["plan_request_id"] = plan_request_id
                    plan["user_id"] = user_id
                return cached_plans
        except Exception as exc:
            logger.warning(f"读取AI缓存失败: {exc}")

    # === 3. API Key检查 ===
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

    # 优化后的Prompt（减少token消耗）
    prompt = (
        "生成3套团建方案（中文），返回纯JSON格式：\n"
        "{\n"
        '  "plans": [\n'
        '    {"plan_type":"budget|standard|premium","plan_name":"string","summary":"string",\n'
        '     "highlights":["string"],"itinerary":{"days":[{"day":1,"items":[{"time_start":"HH:MM","time_end":"HH:MM","activity":"string"}]}]},\n'
        '     "budget_breakdown":{"total":number,"per_person":number,"categories":[{"category":"string","subtotal":number}]},\n'
        '     "budget_total":number,"budget_per_person":number}\n'
        "  ]\n"
        "}\n"
        "\n"
        f"基本信息: {people}人, {duration_days}天, {departure_city}→{destination}\n"
        f"预算目标: 经济¥{targets['budget']:.0f}/标准¥{targets['standard']:.0f}/品质¥{targets['premium']:.0f}\n"
        f"活动偏好: {activity_desc} | 住宿: {accommodation_desc}\n"
        f"季节: {season_info['description']}, 禁止: {','.join(season_info['forbidden_activities']) or '无'}\n"
    )

    if special_requirements:
        prompt += f"特殊需求: {special_requirements}\n"

    if destination_context and isinstance(destination_context, dict):
        # 只附加POI名称列表，不传完整对象（减少token）
        poi_categories = destination_context.get("poi_categories", {})
        if poi_categories:
            prompt += "\n真实地点（优先使用）:\n"
            for cat, pois in list(poi_categories.items())[:3]:  # 只取前3类
                poi_names = [p.get("name", "") for p in pois[:3]]  # 每类只取3个
                if poi_names:
                    prompt += f"- {cat}: {', '.join(poi_names)}\n"

    prompt += (
        "\n约束:\n"
        "- 3套方案必须按budget/standard/premium顺序\n"
        "- budget_total必须接近预算目标（±10%）\n"
        "- 住宿25-35%，活动30-40%，餐饮20-25%，交通10-15%\n"
        "- 每天至少3个时间段，包含具体活动名称\n"
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

    # === 4. 写入缓存 ===
    if redis and settings.ai_cache_enabled:
        try:
            # 缓存清理ID后的plans（避免ID污染）
            cache_data = [
                {k: v for k, v in plan.items() if k not in ["plan_id", "plan_request_id", "user_id"]}
                for plan in validated_plans
            ]
            redis.setex(
                cache_key,
                settings.ai_cache_ttl_seconds,
                json.dumps(cache_data, ensure_ascii=False),
            )
            logger.info(f"AI响应已缓存 cache_key={cache_key}, ttl={settings.ai_cache_ttl_seconds}s")
        except Exception as exc:
            logger.warning(f"写入AI缓存失败: {exc}")

    return validated_plans
