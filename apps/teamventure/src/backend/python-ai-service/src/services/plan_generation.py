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
import re
from datetime import datetime
from typing import Any

from src.integrations.openai_client import OpenAIClient
from src.integrations.amap_client import AmapClient
from src.services.id_generator import new_prefixed_id
from src.models.config import settings

logger = logging.getLogger(__name__)

# ============ Redis缓存客户端（懒加载）============
_redis_client = None
_MARKDOWN_PLAN_CACHE_VERSION = "v3_poi_guardrail_20260119_bold_day"


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


async def generate_plan_from_markdown(
    *,
    plan_request_id: str,
    user_id: str,
    markdown_content: str,
    plan_name: str | None = None,
) -> list[dict[str, Any]]:
    """
    V2: 从Markdown格式需求生成1套定制化方案

    输入：
    - markdown_content: 用户填写的Markdown格式需求（包含天数、人数、预算、路线、交通、住宿等）

    输出：
    - 返回1套完整方案（包含行程、预算明细、亮点等）

    优化机制：
    1. Mock模式：ENABLE_AI_MOCK=true 时返回确定性示例
    2. 缓存机制：相同输入24小时内直接返回缓存结果
    3. Fallback：API key未配置时返回简单示例
    """
    extracted_pois_by_day = _extract_pois_by_day_from_markdown(markdown_content or "")
    desired_plan_name = (plan_name or "").strip()

    # === 1. Mock模式检查 ===
    if settings.enable_ai_mock:
        logger.info("AI Mock模式已启用，返回示例方案")
        return [_create_mock_plan(plan_request_id, user_id)]

    # === 2. 缓存检查 ===
    markdown_hash = hashlib.sha256((markdown_content or "").encode("utf-8")).hexdigest()[:16]
    cache_key = f"markdown_plan:{_MARKDOWN_PLAN_CACHE_VERSION}:{markdown_hash}"
    redis = _get_redis_client()
    if redis and settings.ai_cache_enabled:
        try:
            cached = redis.get(cache_key)
            if cached:
                logger.info(f"AI缓存命中 cache_key={cache_key}")
                cached_plan = json.loads(cached)
                cached_plan["plan_id"] = new_prefixed_id("plan")
                cached_plan["plan_request_id"] = plan_request_id
                cached_plan["user_id"] = user_id
                return [cached_plan]
        except Exception as exc:
            logger.warning(f"读取AI缓存失败: {exc}")

    # === 3. API Key检查 ===
    client = OpenAIClient()
    if not client.is_configured():
        logger.warning("OPENAI_API_KEY not configured; using fallback plan from markdown")
        if extracted_pois_by_day:
            plan = _create_fallback_plan_from_pois(
                plan_request_id=plan_request_id,
                user_id=user_id,
                pois_by_day=extracted_pois_by_day,
                plan_name=desired_plan_name or None,
            )
            plan = _remove_speculative_intercity_transport(plan, markdown_content)
            plan = _remove_empty_placeholder_items(plan)
            plan = _sanitize_itinerary_times(plan)
            return [plan]
        return [_create_mock_plan(plan_request_id, user_id)]

    # === 4. LLM生成 ===
    poi_hint = ""
    if extracted_pois_by_day:
        lines: list[str] = []
        for day in sorted(extracted_pois_by_day.keys()):
            pois = extracted_pois_by_day[day]
            if not pois:
                continue
            lines.append(f"- Day{day}: " + "、".join(pois[:60]))
        if lines:
            poi_hint = "用户在 Markdown 中列出的景点清单（必须全部保留，不得丢失）：\n" + "\n".join(lines) + "\n\n"

    prompt = (
        "根据用户的Markdown需求描述，生成1套完整的团建方案。\n"
        "返回纯JSON格式（不要包含```json标记）：\n"
        "{\n"
        '  "plan_type": "standard",\n'
        '  "plan_name": "方案名称",\n'
        '  "summary": "方案简介",\n'
        '  "highlights": ["亮点1", "亮点2", "亮点3"],\n'
        '  "itinerary": {\n'
        '    "days": [\n'
        '      {\n'
        '        "day": 1,\n'
        '        "date": "YYYY-MM-DD",\n'
        '        "items": [\n'
        '          {"time_start": "HH:MM", "time_end": "HH:MM", "activity": "活动名称", "location": "地点"}\n'
        '        ]\n'
        '      }\n'
        '    ]\n'
        '  },\n'
        '  "budget_breakdown": {\n'
        '    "total": 总金额数字,\n'
        '    "per_person": 人均金额数字,\n'
        '    "categories": [\n'
        '      {"category": "类别", "subtotal": 金额数字}\n'
        '    ]\n'
        '  },\n'
        '  "transportation": "交通安排描述",\n'
        '  "accommodation": "住宿安排描述"\n'
        '}\n'
        '\n'
        + poi_hint +
        (f'用户指定的方案名称（如不为空必须使用，不要改写）：{desired_plan_name}\n' if desired_plan_name else '') +
        '用户需求（Markdown格式）：\n'
        f'{markdown_content}\n'
        '\n'
        '约束：\n'
        '- 严格按照用户提供的天数、人数、预算生成方案\n'
        '- 如用户指定了具体交通（航班/高铁），优先使用\n'
        '- 如用户指定了酒店，优先使用\n'
        '- 预算分配：住宿30%，活动35%，餐饮25%，交通10%\n'
        '- 每天至少安排3个时间段的活动（如果用户给了更多景点，必须全部列入，允许超过3个）\n'
        '- **用户Markdown里每一天列出的景点/地点/路线点，必须逐条出现在对应 day 的 itinerary.items.activity 中；可在 activity 中补充连贯描述，但不得丢掉任何一个名字**\n'
        '- 周边游/景点游玩类活动（非交通/非住宿）最晚结束到 20:00；20:00 后不要继续安排周边游时间段（可安排“自由活动/自行安排”之类占位，或留空）\n'
        '- 周边游/景点游玩类活动（非交通/非住宿）上午不早于 09:00 到第一个景点（不要安排 09:00 之前的景点时间段）\n'
        '- 若用户需求中没有明确提到“高铁/动车/航班/飞机/火车/机场/车次”等跨城交通信息，不要编造跨城交通（不要凭空安排乘机/高铁/到机场/到火车站等）\n'
        '- 时间必须是 00:00-23:59 范围内的 HH:MM，且 time_end > time_start；不要出现 24:00、25:00 这类不可能时间\n'
        '- 确保JSON格式完全正确，所有字段都必须存在\n'
    )

    try:
        raw = await client.generate_json(prompt)
        plan = _normalize_single_plan(raw, plan_request_id, user_id, markdown_content)
        if desired_plan_name:
            plan["plan_name"] = desired_plan_name
        plan = _remove_speculative_intercity_transport(plan, markdown_content)
        plan = _remove_empty_placeholder_items(plan)
        plan = _ensure_itinerary_contains_all_pois(plan, extracted_pois_by_day)
        plan = _sanitize_itinerary_times(plan)

        # 写入缓存
        if redis and settings.ai_cache_enabled:
            try:
                redis.setex(cache_key, settings.ai_cache_ttl_seconds, json.dumps(plan))
                logger.info(f"AI结果已缓存 cache_key={cache_key}")
            except Exception as exc:
                logger.warning(f"写入AI缓存失败: {exc}")

        return [plan]
    except Exception as exc:
        logger.exception("LLM生成失败，降级到mock方案")
        if extracted_pois_by_day:
            plan = _create_fallback_plan_from_pois(
                plan_request_id=plan_request_id,
                user_id=user_id,
                pois_by_day=extracted_pois_by_day,
                plan_name=desired_plan_name or None,
            )
            plan = _remove_speculative_intercity_transport(plan, markdown_content)
            plan = _remove_empty_placeholder_items(plan)
            plan = _sanitize_itinerary_times(plan)
            return [plan]
        return [_create_mock_plan(plan_request_id, user_id)]


def _extract_pois_by_day_from_markdown(markdown: str) -> dict[int, list[str]]:
    """
    Best-effort extractor for day sections and bullet POIs in user markdown.

    Used as a preservation guardrail: if the LLM drops user-listed POIs, we rebuild
    itinerary.items to include all of them (no new facts added).
    """
    text = (markdown or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        return {}

    def chinese_numeral_to_int(s: str) -> int | None:
        s = (s or "").strip()
        if not s:
            return None
        if s.isdigit():
            try:
                return int(s)
            except Exception:
                return None

        # 支持 1-10（足够覆盖大多数“第X天”场景）
        mapping = {
            "一": 1,
            "二": 2,
            "三": 3,
            "四": 4,
            "五": 5,
            "六": 6,
            "七": 7,
            "八": 8,
            "九": 9,
            "十": 10,
        }
        if s in mapping:
            return mapping[s]
        if s.startswith("十") and len(s) == 2 and s[1] in mapping:
            return 10 + mapping[s[1]]
        if s.endswith("十") and len(s) == 2 and s[0] in mapping:
            return mapping[s[0]] * 10
        if len(s) == 3 and s[1] == "十" and s[0] in mapping and s[2] in mapping:
            return mapping[s[0]] * 10 + mapping[s[2]]
        return None

    def normalize_poi_name(name: str) -> str | None:
        name = (name or "").strip()
        if not name:
            return None
        if len(name) > 120:
            return None
        if name.lower().startswith(("http://", "https://")):
            return None
        name = re.sub(r"[，,。.]$", "", name).strip()
        name = re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()
        name = re.sub(r"\s*（[^）]*）\s*$", "", name).strip()
        return name or None

    sep = re.compile(r"\s*(?:->|→|—|–|-|＞|>)+\s*")

    def split_pois_from_inline(rest: str) -> list[str]:
        rest = (rest or "").strip()
        if not rest:
            return []
        parts = [p.strip() for p in sep.split(rest) if p.strip()]
        if len(parts) >= 2:
            return parts
        # 如果只有一个片段，但整体看起来就是地点（短且无明显句式），也保留
        if len(rest) <= 60 and not re.search(r"[。！？!?:：]", rest):
            return [rest]
        return []

    day_header = re.compile(
        r"(?im)^\s*(?:[-*•·]\s*)?(?:🏷️\s*)?(?:#{1,6}\s*)?(?:\*\*)?"
        r"(?:day\s*(\d+)|d\s*(\d+)|第\s*([一二三四五六七八九十\d]+)\s*天)"
        r"(?:\*\*)?\s*[:：]?\s*(.*)$"
    )
    bullet = re.compile(r"^\s*[-*•·]\s+(.+?)\s*$")

    current_day: int | None = None
    pois: dict[int, list[str]] = {}

    for line in text.split("\n"):
        s = line.strip()
        if not s:
            continue

        m_day = day_header.match(s)
        if m_day:
            d_raw = m_day.group(1) or m_day.group(2) or m_day.group(3)
            if d_raw:
                current_day = chinese_numeral_to_int(d_raw)
            else:
                current_day = None
            if current_day is not None and current_day not in pois:
                pois[current_day] = []
            # Day 行尾可能直接带 “A-B-C” 的行程串
            if current_day is not None:
                inline_rest = (m_day.group(4) or "").strip()
                # Ignore standard date suffix like "（2026-01-19）"
                if re.match(r"^[（(]?\d{4}-\d{2}-\d{2}[）)]?$", inline_rest):
                    inline_rest = ""
                for p in split_pois_from_inline(inline_rest):
                    normalized_name = normalize_poi_name(p)
                    if normalized_name:
                        pois[current_day].append(normalized_name)
            continue

        if current_day is None:
            continue

        m_b = bullet.match(line)
        if not m_b:
            continue

        raw_name = m_b.group(1).strip()
        if not raw_name:
            continue
        # Standard v2 line: "HH:MM - HH:MM | 活动 | 地点 | 备注"
        if "|" in raw_name:
            cols = [c.strip() for c in raw_name.split("|")]
            # cols: [time-range, activity, location, note]
            candidate = ""
            if len(cols) >= 3 and cols[2]:
                candidate = cols[2]
            elif len(cols) >= 2 and cols[1]:
                candidate = cols[1]
            # location might be "A、B、C"
            if candidate:
                for p in [x.strip() for x in re.split(r"[、,，]\s*", candidate) if x.strip()]:
                    normalized_name = normalize_poi_name(p)
                    if normalized_name:
                        pois[current_day].append(normalized_name)
            continue

        parts = split_pois_from_inline(raw_name) or [raw_name]
        for p in parts:
            normalized_name = normalize_poi_name(p)
            if normalized_name:
                pois[current_day].append(normalized_name)

    normalized: dict[int, list[str]] = {}
    for day, items in pois.items():
        seen: set[str] = set()
        out: list[str] = []
        for it in items:
            key = it.strip()
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(key)
        if out:
            normalized[day] = out
    return normalized


def _ensure_itinerary_contains_all_pois(plan: dict[str, Any], pois_by_day: dict[int, list[str]]) -> dict[str, Any]:
    if not pois_by_day:
        return plan

    itinerary = plan.get("itinerary") if isinstance(plan, dict) else None
    if not isinstance(itinerary, dict):
        itinerary = {"days": []}

    days = itinerary.get("days")
    if not isinstance(days, list):
        days = []

    existing_by_day: dict[int, str] = {}
    for d in days:
        if not isinstance(d, dict):
            continue
        try:
            day_int = int(d.get("day"))
        except Exception:
            continue
        items = d.get("items")
        if not isinstance(items, list):
            continue
        blob = []
        for it in items:
            if isinstance(it, dict):
                a = str(it.get("activity") or "").strip()
                if a:
                    blob.append(a)
        existing_by_day[day_int] = "\n".join(blob)

    missing_by_day: dict[int, list[str]] = {}
    for day in sorted(pois_by_day.keys()):
        expected = pois_by_day.get(day) or []
        if not expected:
            continue
        blob = existing_by_day.get(day, "")
        missing = [p for p in expected if p not in blob]
        if missing:
            missing_by_day[day] = missing

    if not missing_by_day:
        return plan

    def parse_hhmm_to_minutes(v: str) -> int | None:
        v = (v or "").strip()
        m = re.match(r"^(\d{1,2}):(\d{2})$", v)
        if not m:
            return None
        h = int(m.group(1))
        mi = int(m.group(2))
        if h < 0 or h > 23 or mi < 0 or mi > 59:
            return None
        return h * 60 + mi

    def minutes_to_hhmm(m: int) -> str:
        m = max(0, int(m))
        # Avoid generating invalid times like 25:30
        m = min(m, 23 * 60 + 59)
        return f"{m // 60:02d}:{m % 60:02d}"

    # Map existing day objects for in-place patching
    day_objs: dict[int, dict[str, Any]] = {}
    for d in days:
        if not isinstance(d, dict):
            continue
        try:
            day_int = int(d.get("day"))
        except Exception:
            continue
        day_objs[day_int] = d

    for day, missing in missing_by_day.items():
        d = day_objs.get(day)
        if d is None:
            d = {"day": day, "date": "", "items": []}
            days.append(d)
            day_objs[day] = d

        items = d.get("items")
        if not isinstance(items, list):
            items = []
            d["items"] = items

        last_end = None
        for it in items:
            if isinstance(it, dict):
                last_end = parse_hhmm_to_minutes(str(it.get("time_end") or "")) or last_end

        # Keep appended POIs within a reasonable day window to avoid impossible timelines.
        # Product rule: "周边游" 最晚到 20:00，20:00 后由用户自行安排（交通/住宿除外）。
        day_start = 9 * 60
        day_end = 20 * 60  # last nearby activity ends by 20:00; overflow items omit time.
        start = last_end if last_end is not None else day_start

        available = max(day_end - start, 0)
        if len(missing) <= 0:
            continue
        # Evenly distribute; if too many items, later ones won't get explicit time.
        step = max(30, available // max(len(missing), 1))
        step = max(30, (step // 15) * 15)  # round down to 15-min blocks

        for i, poi in enumerate(missing):
            s = start + i * step
            e = min(s + step, day_end)
            if s >= day_end or e <= s:
                items.append({"activity": poi, "location": ""})
                continue
            items.append(
                {
                    "time_start": minutes_to_hhmm(s),
                    "time_end": minutes_to_hhmm(e),
                    "activity": poi,
                    "location": "",
                }
            )

    # Ensure stable order by day
    days_sorted = sorted(
        [d for d in days if isinstance(d, dict) and str(d.get("day") or "").isdigit()],
        key=lambda x: int(x.get("day")),
    )
    plan = dict(plan)
    plan["itinerary"] = dict(itinerary)
    plan["itinerary"]["days"] = days_sorted
    return plan


def _sanitize_itinerary_times(plan: dict[str, Any]) -> dict[str, Any]:
    """
    Hard guardrail: never return invalid times (e.g., 24:00, 25:30, end<=start).

    If an item's time_start/time_end are invalid, remove them so the UI won't show
    impossible timelines. This does not remove activities/POIs.
    """
    if not isinstance(plan, dict):
        return plan
    itinerary = plan.get("itinerary")
    if not isinstance(itinerary, dict):
        return plan
    days = itinerary.get("days")
    if not isinstance(days, list):
        return plan

    def classify_kind(it: dict[str, Any]) -> str:
        text = f"{it.get('activity') or ''} {it.get('location') or ''} {it.get('note') or ''}".strip()
        t = text.lower()
        accommodation_keywords = ["入住", "酒店", "民宿", "住宿", "休息", "退房", "办理入住", "checkin", "checkout"]
        transport_keywords = ["出发", "前往", "到达", "返程", "集合", "地铁", "公交", "打车", "网约车", "骑行", "自驾", "高铁", "动车", "航班", "飞机", "换乘", "步行", "接驳", "大巴"]
        if any(k in text or k in t for k in accommodation_keywords):
            return "accommodation"
        if any(k in text or k in t for k in transport_keywords):
            return "transport"
        return "nearby"

    def parse_minutes(v: Any) -> int | None:
        if not isinstance(v, str):
            return None
        s = v.strip()
        m = re.match(r"^(\d{1,2}):(\d{2})$", s)
        if not m:
            return None
        h = int(m.group(1))
        mi = int(m.group(2))
        if h < 0 or h > 23 or mi < 0 or mi > 59:
            return None
        return h * 60 + mi

    earliest_nearby_start = 9 * 60  # 09:00
    latest_nearby_end = 20 * 60  # 20:00

    for d in days:
        if not isinstance(d, dict):
            continue
        items = d.get("items")
        if not isinstance(items, list):
            continue
        for it in items:
            if not isinstance(it, dict):
                continue
            ts = it.get("time_start")
            te = it.get("time_end")
            ms = parse_minutes(ts)
            me = parse_minutes(te)
            # If either is invalid, drop both (avoid partial confusing timelines)
            if ms is None or me is None:
                it.pop("time_start", None)
                it.pop("time_end", None)
                continue
            if me <= ms:
                it.pop("time_start", None)
                it.pop("time_end", None)
                continue

            kind = classify_kind(it)
            if kind == "nearby":
                # Nearby activities should not start earlier than 09:00.
                if ms < earliest_nearby_start:
                    # Keep activity but remove times (user to adjust) to avoid incorrect "early" schedule.
                    it.pop("time_start", None)
                    it.pop("time_end", None)
                    if not str(it.get("note") or "").strip():
                        it["note"] = "09:00 后开始（时间待确认）"
                    continue
                # Nearby activities should not be scheduled after 20:00.
                # - If it crosses 20:00, truncate end to 20:00.
                # - If it starts at/after 20:00, remove times (user to arrange).
                if ms >= latest_nearby_end:
                    it.pop("time_start", None)
                    it.pop("time_end", None)
                    if not str(it.get("note") or "").strip():
                        it["note"] = "20:00 后自行安排"
                    continue
                if me > latest_nearby_end:
                    it["time_end"] = "20:00"
                    # If truncation makes it invalid, drop times.
                    if parse_minutes(it.get("time_end")) is None or parse_minutes(it.get("time_end")) <= ms:
                        it.pop("time_start", None)
                        it.pop("time_end", None)
                        if not str(it.get("note") or "").strip():
                            it["note"] = "20:00 后自行安排"
                    continue

    return plan


def _create_fallback_plan_from_pois(
    *,
    plan_request_id: str,
    user_id: str,
    pois_by_day: dict[int, list[str]],
    plan_name: str | None = None,
) -> dict[str, Any]:
    """
    Deterministic fallback when LLM is unavailable:
    - Preserve all POIs extracted from markdown by day
    - Keep times within nearby window (09:00-20:00); overflow items omit time
    """
    days_out: list[dict[str, Any]] = []
    for day in sorted(pois_by_day.keys()):
        pois = pois_by_day.get(day) or []
        items: list[dict[str, Any]] = []
        day_start = 9 * 60
        day_end = 20 * 60
        if pois:
            # Evenly spread in 09:00-20:00; round to 15min blocks.
            available = max(day_end - day_start, 0)
            step = max(30, available // max(len(pois), 1))
            step = max(30, (step // 15) * 15)
            for i, poi in enumerate(pois):
                s = day_start + i * step
                e = min(s + step, day_end)
                if s >= day_end or e <= s:
                    items.append({"activity": poi, "location": ""})
                    continue
                items.append({
                    "time_start": f"{s // 60:02d}:{s % 60:02d}",
                    "time_end": f"{e // 60:02d}:{e % 60:02d}",
                    "activity": poi,
                    "location": "",
                })
        days_out.append({"day": day, "date": "", "items": items})

    return {
        "plan_id": new_prefixed_id("plan"),
        "plan_request_id": plan_request_id,
        "user_id": user_id,
        "plan_type": "standard",
        "plan_name": (plan_name or "").strip() or "团建行程方案",
        "summary": "（自动生成草案，可继续完善）",
        "highlights": [],
        "itinerary": {"days": days_out},
        "budget_breakdown": {"total": 0, "per_person": 0, "categories": []},
        "budget_total": 0,
        "budget_per_person": 0,
        "transportation": "未提供",
        "accommodation": "未提供",
    }


def _remove_empty_placeholder_items(plan: dict[str, Any]) -> dict[str, Any]:
    """Drop obvious placeholders like '无' / empty activities from itinerary."""
    if not isinstance(plan, dict):
        return plan
    itinerary = plan.get("itinerary")
    if not isinstance(itinerary, dict):
        return plan
    days = itinerary.get("days")
    if not isinstance(days, list):
        return plan

    for d in days:
        if not isinstance(d, dict):
            continue
        items = d.get("items")
        if not isinstance(items, list):
            continue
        cleaned: list[dict[str, Any]] = []
        for it in items:
            if not isinstance(it, dict):
                continue
            a = str(it.get("activity") or "").strip()
            if not a:
                continue
            if a in {"无", "暂无", "待定", "空"}:
                continue
            cleaned.append(it)
        d["items"] = cleaned
    return plan


def _remove_speculative_intercity_transport(plan: dict[str, Any], markdown_content: str) -> dict[str, Any]:
    """
    If user markdown doesn't mention intercity transport, remove LLM-invented intercity items.

    We keep in-city transport (e.g., 地铁/打车) but remove items involving 飞机/航班/高铁/动车/火车等
    when the input markdown does not mention those concepts.
    """
    if not isinstance(plan, dict):
        return plan
    itinerary = plan.get("itinerary")
    if not isinstance(itinerary, dict):
        return plan
    days = itinerary.get("days")
    if not isinstance(days, list):
        return plan

    md = (markdown_content or "").strip()
    md_lower = md.lower()
    md_has_intercity = any(k in md for k in ["高铁", "动车", "航班", "飞机", "火车", "机票", "车次", "机场", "火车站"]) or any(
        k in md_lower for k in ["flight", "train", "airport"]
    )
    if md_has_intercity:
        return plan

    intercity_tokens = ["高铁", "动车", "航班", "飞机", "火车", "机票", "车次", "机场", "火车站", "虹桥", "浦东"]

    for d in days:
        if not isinstance(d, dict):
            continue
        items = d.get("items")
        if not isinstance(items, list):
            continue
        kept: list[dict[str, Any]] = []
        for it in items:
            if not isinstance(it, dict):
                continue
            text = f"{it.get('activity') or ''} {it.get('location') or ''} {it.get('note') or ''}".strip()
            if any(tok in text for tok in intercity_tokens):
                # Drop speculative intercity transport items entirely.
                continue
            kept.append(it)
        d["items"] = kept

    return plan


def _create_mock_plan(plan_request_id: str, user_id: str) -> dict[str, Any]:
    """创建Mock示例方案"""
    return {
        "plan_id": new_prefixed_id("plan"),
        "plan_request_id": plan_request_id,
        "user_id": user_id,
        "plan_type": "standard",
        "plan_name": "团建方案示例",
        "summary": "这是一个示例方案，请在生产环境配置OPENAI_API_KEY后重新生成",
        "highlights": ["示例亮点1", "示例亮点2", "示例亮点3"],
        "itinerary": {
            "days": [
                {
                    "day": 1,
                    "date": "2026-01-01",
                    "items": [
                        {"time_start": "09:00", "time_end": "12:00", "activity": "出发前往目的地", "location": "集合地点"},
                        {"time_start": "12:00", "time_end": "14:00", "activity": "午餐", "location": "当地餐厅"},
                        {"time_start": "14:00", "time_end": "17:00", "activity": "团队拓展活动", "location": "活动场地"}
                    ]
                }
            ]
        },
        "budget_breakdown": {
            "total": 25000,
            "per_person": 500,
            "categories": [
                {"category": "住宿", "subtotal": 7500},
                {"category": "活动", "subtotal": 8750},
                {"category": "餐饮", "subtotal": 6250},
                {"category": "交通", "subtotal": 2500}
            ]
        },
        "budget_total": 25000,
        "budget_per_person": 500,
        "transportation": "待定",
        "accommodation": "待定"
    }


def _normalize_single_plan(raw: dict[str, Any], plan_request_id: str, user_id: str, markdown_content: str) -> dict[str, Any]:
    """标准化单个方案的数据结构"""
    plan = raw if isinstance(raw, dict) else {}

    # 确保必需字段存在
    return {
        "plan_id": new_prefixed_id("plan"),
        "plan_request_id": plan_request_id,
        "user_id": user_id,
        "plan_type": plan.get("plan_type", "standard"),
        "plan_name": plan.get("plan_name", "团建方案"),
        "summary": plan.get("summary", ""),
        "highlights": plan.get("highlights", []),
        "itinerary": plan.get("itinerary", {"days": []}),
        "budget_breakdown": plan.get("budget_breakdown", {
            "total": 0,
            "per_person": 0,
            "categories": []
        }),
        "budget_total": plan.get("budget_total") or plan.get("budget_breakdown", {}).get("total", 0),
        "budget_per_person": plan.get("budget_per_person") or plan.get("budget_breakdown", {}).get("per_person", 0),
        "transportation": plan.get("transportation", "待定"),
        "accommodation": plan.get("accommodation", "待定")
    }


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
