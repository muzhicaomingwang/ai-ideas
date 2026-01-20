from __future__ import annotations

import re
from typing import Any


_DAY_HEADING_STRICT = re.compile(r"^##\s*Day\s*(\d+)\s*(?:（(.*)）)?\s*$", re.IGNORECASE)
_DAY_HEADING_LOOSE = re.compile(
    r"^(?:#{1,6}\s*)?(?:\*\*)?\s*(?:day|d)\s*(\d+)\s*(?:\*\*)?\s*(?:（(.*)）|\((.*)\))?\s*(?:[:：]\s*(.*))?$",
    re.IGNORECASE,
)
_DAY_HEADING_CN = re.compile(
    r"^(?:#{1,6}\s*)?(?:\*\*)?\s*第\s*(\d+)\s*天\s*(?:\*\*)?\s*(?:[:：]\s*(.*))?$",
    re.IGNORECASE,
)
_TIME_RANGE = re.compile(r"^(\d{1,2}:\d{2})\s*-\s*(\d{0,2}:?\d{0,2})\s*$")


def normalize_markdown(markdown: str | None) -> str:
    if markdown is None:
        return ""
    s = str(markdown).replace("\r", "")
    s = s.replace("｜", "|")
    s = _strip_invisible(s)
    return s


def validate(markdown: str | None) -> dict[str, Any]:
    normalized = normalize_markdown(markdown)
    raw_lines = normalized.split("\n")

    errors: list[str] = []
    days = 0
    total_items = 0

    in_day = False
    current_day_has_item = False
    current_day_number: int | None = None

    for i, raw in enumerate(raw_lines):
        line = _normalize_line(raw)
        if not line:
            continue

        if line.startswith("# "):
            continue
        if line.startswith(">"):
            continue

        parsed = _parse_day_heading(line)
        if parsed is not None:
            day_number, inline_item = parsed
            if in_day and not current_day_has_item and current_day_number is not None:
                errors.append(f"Day {current_day_number} 下未找到任何行项目（以 \"-\" 开头）")
            in_day = True
            current_day_has_item = False
            current_day_number = day_number
            days += 1
            if inline_item:
                current_day_has_item = True
                total_items += 1
            continue

        if line.startswith("- "):
            if not in_day or current_day_number is None:
                errors.append(f"第 {i + 1} 行：行项目必须放在某个 Day 标题下方")
                continue
            err = _validate_item_line(line)
            if err:
                errors.append(f"第 {i + 1} 行：{err}")
                continue
            current_day_has_item = True
            total_items += 1
            continue

        if not in_day:
            continue

        errors.append(f"第 {i + 1} 行：无法识别的内容（请使用 Day 标题或 \"-\" 行项目）")

    if days == 0:
        errors.append("未找到任何 Day 标题（例如：## Day 1（日期））")
    elif in_day and not current_day_has_item and current_day_number is not None:
        errors.append(f"Day {current_day_number} 下未找到任何行项目（以 \"-\" 开头）")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "days": days,
        "items": total_items,
    }


def itinerary_to_markdown_v2(itinerary: dict[str, Any] | None) -> str:
    it = itinerary if isinstance(itinerary, dict) else {}
    days = it.get("days")
    if not isinstance(days, list):
        days = []

    out: list[str] = []
    out.append("# 行程安排")
    out.append("> 版本: v2")
    out.append("")

    for idx, day in enumerate(days, start=1):
        if not isinstance(day, dict):
            continue
        out.append(f"## Day {idx}")
        items = day.get("items")
        if not isinstance(items, list):
            items = []
        for item in items:
            if not isinstance(item, dict):
                continue
            start = str(item.get("time_start") or "").strip()
            end = str(item.get("time_end") or "").strip()
            activity = str(item.get("activity") or "").strip()
            out.append(f"- {start} - {end} | {activity} |  | ")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def _validate_item_line(line: str) -> str | None:
    trimmed = normalize_markdown(line).lstrip()
    trimmed = re.sub(r"^\-\s*", "", trimmed, count=1)
    parts = trimmed.split("|")
    if len(parts) < 2:
        return "行项目格式错误：需要至少包含「时间 | 活动」"

    time_range = _normalize_time_range(parts[0].strip())
    activity = _strip_invisible(parts[1]).strip()
    if not activity:
        return "活动不能为空"

    if not _TIME_RANGE.match(time_range):
        return "时间格式错误：应为「HH:MM - HH:MM」（结束时间可留空）"

    return None


def _normalize_line(line: str | None) -> str:
    return _strip_invisible("" if line is None else str(line)).strip()


def _parse_day_heading(line: str) -> tuple[int, str] | None:
    """
    Accepts strict v2 headings:
      - ## Day 1（可选日期）
    And also looser, user-authored headings:
      - DAY1：A→B→C
      - Day 2: ...
      - 第1天：...
    """
    m_strict = _DAY_HEADING_STRICT.match(line)
    if m_strict:
        day_number = _safe_int(m_strict.group(1))
        if day_number is None:
            return None
        return (day_number, "")

    m_loose = _DAY_HEADING_LOOSE.match(line)
    if m_loose:
        day_number = _safe_int(m_loose.group(1))
        if day_number is None:
            return None
        inline_item = (m_loose.group(4) or "").strip()
        return (day_number, inline_item)

    m_cn = _DAY_HEADING_CN.match(line)
    if m_cn:
        day_number = _safe_int(m_cn.group(1))
        if day_number is None:
            return None
        inline_item = (m_cn.group(2) or "").strip()
        return (day_number, inline_item)

    return None


def _normalize_time_range(time_range: str | None) -> str:
    if time_range is None:
        return ""
    s = _strip_invisible(str(time_range))
    s = s.replace("：", ":")
    s = re.sub(r"[—–－‐‑‒―−~〜～﹣]", "-", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _strip_invisible(s: str | None) -> str:
    if s is None:
        return ""
    return re.sub(r"[\u200B-\u200F\u202A-\u202E\u2060\uFEFF]", "", str(s))


def _safe_int(s: str | None) -> int | None:
    try:
        return int(str(s))
    except Exception:
        return None
