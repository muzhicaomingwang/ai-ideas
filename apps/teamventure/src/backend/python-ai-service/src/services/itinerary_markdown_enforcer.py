from __future__ import annotations

import re
from typing import Any

from src.integrations.openai_client import OpenAIClient
from src.services.itinerary_markdown_v2 import validate


async def ensure_valid_itinerary_markdown(
    *,
    initial_markdown: str,
    fallback_markdown: str,
    max_attempts: int = 5,
    model: str | None = None,
) -> dict[str, Any]:
    """
    Closed-loop: validate -> (LLM fix) -> validate, up to max_attempts.

    If still invalid after retries (or LLM not configured), fall back to fallback_markdown.
    """
    candidate = (initial_markdown or "").strip()
    fallback_source = (fallback_markdown or "").strip()
    fallback = _to_valid_itinerary_template(fallback_source or candidate)

    client = OpenAIClient()

    last_check = validate(candidate)
    if last_check["valid"]:
        return {"markdown": candidate, "check": last_check, "attempts": 0, "fallback_used": False}

    if not client.is_configured():
        return {"markdown": fallback, "check": validate(fallback), "attempts": 0, "fallback_used": True}

    for attempt in range(1, max_attempts + 1):
        errors = last_check.get("errors") or []
        errors_head = errors[:10]
        prompt = (
            "你将获得一段 TeamVenture 的行程 Markdown（v2），但它未通过格式校验。\n"
            "任务：仅修复格式/结构使其通过校验，不要编造事实，不要新增不存在的地点/活动/时间。\n"
            "\n"
            "必须满足（严格）：\n"
            "- Day 标题格式：## Day N（日期可选）\n"
            "- 行项目必须在某个 Day 下方\n"
            "- 行项目格式至少包含：- HH:MM - HH:MM | 活动\n"
            "- 允许更多列（如地点/备注），但用 | 分隔\n"
            "- 结束时间允许留空，但必须保留连字符：HH:MM - \n"
            "\n"
            "校验错误（供参考）：\n"
            + "\n".join(f"- {e}" for e in errors_head)
            + "\n\n"
            "待修复 Markdown：\n"
            + candidate
            + "\n\n"
            '返回 JSON：{"markdown_content":"..."}'
        )

        try:
            res = await client.generate_json(prompt, model=model, temperature=0.0, max_tokens=2000)
        except Exception:
            return {"markdown": fallback, "check": validate(fallback), "attempts": attempt, "fallback_used": True}

        fixed = (res.get("markdown_content") or "").strip()
        if not fixed:
            return {"markdown": fallback, "check": validate(fallback), "attempts": attempt, "fallback_used": True}

        candidate = fixed
        last_check = validate(candidate)
        if last_check["valid"]:
            return {"markdown": candidate, "check": last_check, "attempts": attempt, "fallback_used": False}

    return {"markdown": fallback, "check": validate(fallback), "attempts": max_attempts, "fallback_used": True}


_DAY_MARKER = re.compile(r"(?i)(?:^|\s)(?:D\s*\d+|day\s*\d+|第\s*\d+\s*天)(?:\b|\s|:|：)")


def _to_valid_itinerary_template(source_text: str) -> str:
    """
    Deterministic fallback that ALWAYS produces validator-passing v2 markdown,
    while preserving the original input as blockquote reference.
    """
    source = (source_text or "").replace("\r", "").strip()
    lines = _extract_activity_lines(source)
    if not lines:
        lines = ["自由活动/根据现场调整"]

    days = _infer_days(source, lines)
    days = max(1, min(days, 5))

    max_items_per_day = 8
    per_day = _split_into_days(lines, days, max_items_per_day)

    out: list[str] = []
    out.append("# 行程安排")
    out.append("> 版本: v2")
    out.append("")

    start_hour = 9
    for d in range(1, len(per_day) + 1):
        out.append(f"## Day {d}")
        items = per_day[d - 1] or ["自由活动/机动安排"]
        local_hour = start_hour
        for raw in items:
            activity = _sanitize_activity(raw)
            start = f"{local_hour:02d}:00"
            # Keep end time empty to avoid inventing durations.
            out.append(f"- {start} -  | {activity} |  | ")
            local_hour = min(local_hour + 1, 23)
        out.append("")
        start_hour = min(start_hour + 1, 12)

    out.append("> 原始输入（仅供参考）")
    if source:
        for raw in source.split("\n")[:24]:
            t = (raw or "").strip()
            if not t:
                continue
            if len(t) > 200:
                t = t[:200].rstrip() + "..."
            out.append("> " + t.replace("\t", " "))

    md = "\n".join(out).rstrip() + "\n"
    if validate(md)["valid"]:
        return md

    # Ultra-safe fallback (should be unreachable)
    return "# 行程安排\n> 版本: v2\n\n## Day 1\n- 09:00 -  | 行程整理 |  | \n"


def _extract_activity_lines(text: str) -> list[str]:
    s = (text or "").replace("\r", "")
    raw_lines = s.split("\n")
    out: list[str] = []

    for line in raw_lines:
        t = (line or "").strip()
        if not t:
            continue
        if t.startswith("#") or t.startswith(">"):
            continue
        if re.match(r"^\-\s*\-\s*\|.*$", t):
            continue
        if t.startswith("-"):
            t = re.sub(r"^\-+\s*", "", t).strip()
            parts = t.split("|")
            if len(parts) >= 2:
                activity = parts[1].strip()
                location = parts[2].strip() if len(parts) >= 3 else ""
                if location:
                    t = (activity + "（" + location + "）").strip()
                else:
                    t = activity
        if t.startswith("http"):
            continue
        if len(t) < 2:
            continue
        out.append(t)
        if len(out) >= 32:
            break

    if len(out) <= 1:
        compact = re.sub(r"\s+", " ", s).strip()
        parts = re.split(r"[。！!？?；;]|→|->|➡️|➜|—|–", compact)
        for p in parts:
            t = (p or "").strip()
            if len(t) < 3:
                continue
            out.append(t)
            if len(out) >= 32:
                break

    return out


def _infer_days(source: str, lines: list[str]) -> int:
    markers = len(_DAY_MARKER.findall(source or ""))
    if markers >= 2:
        return min(markers, 5)
    if len(lines) >= 16:
        return 3
    if len(lines) >= 10:
        return 2
    return 1


def _split_into_days(lines: list[str], days: int, max_items_per_day: int) -> list[list[str]]:
    out: list[list[str]] = [[] for _ in range(days)]
    if not lines:
        return out

    idx = 0
    for line in lines:
        out[min(idx // max_items_per_day, days - 1)].append(line)
        idx += 1
        if idx >= days * max_items_per_day:
            break
    return out


def _sanitize_activity(activity: str) -> str:
    s = (activity or "").strip()
    s = s.replace("|", " - ")
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        s = "自由活动/机动安排"
    if len(s) > 80:
        s = s[:80].rstrip() + "..."
    return s
