from __future__ import annotations

import re

from src.integrations.openai_client import OpenAIClient


def _looks_like_standard_itinerary_markdown(md: str) -> bool:
    t = (md or "").strip()
    if not t:
        return False
    return "# 行程安排" in t and "> 版本:" in t and "## Day" in t and " | " in t


_ITINERARY_LINE_RE = re.compile(
    r"(?m)^\s*-\s*(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*$"
)


def _looks_like_low_quality_itinerary_markdown(md: str) -> bool:
    """
    Heuristic guardrail: reject "valid-looking" v2 markdown that contains almost no usable rows.

    We consider it low-quality when:
    - It has <2 rows with a non-empty "地点" column; OR
    - Most rows have empty columns or are generic placeholders (e.g. 自由安排).
    """
    t = (md or "").strip()
    if not t:
        return True

    matches = list(_ITINERARY_LINE_RE.finditer(t))
    if not matches:
        return True

    usable_rows = 0
    bad_rows = 0
    for m in matches:
        activity = (m.group(3) or "").strip()
        place = (m.group(4) or "").strip()
        if not place:
            bad_rows += 1
            continue
        if activity in {"自由安排", "自由活动", "待定"}:
            bad_rows += 1
            continue
        usable_rows += 1

    if usable_rows < 2:
        return True
    if bad_rows >= max(2, len(matches) - 1):
        return True
    return False


_DAY_HEADER_RE = re.compile(r"(?im)^\s*(第\s*[一二三四五六七八九十\d]+\s*天|d\s*\d+|day\s*\d+)\s*[:：]?\s*(.*)$")
_TIME_RANGE_RE = re.compile(r"[（(]\s*(\d{1,2})\s*[:：]\s*(\d{2})\s*[-~–—]\s*(\d{1,2})\s*[:：]\s*(\d{2})\s*[)）]")
_TIME_HINT_RE = re.compile(r"(早上|上午|中午|下午|傍晚|晚上|夜间)")
_DATE_HEADER_RE = re.compile(
    r"""(?ix)^\s*
    (?:
        (?P<y>19\d{2}|20\d{2})\s*(?:[./-]|年)\s*(?P<m1>\d{1,2})\s*(?:[./-]|月)\s*(?P<d1>\d{1,2})\s*(?:日)?
        |
        (?P<m2>\d{1,2})\s*月\s*(?P<d2>\d{1,2})\s*日
        |
        (?P<m3>\d{1,2})\s*[/-]\s*(?P<d3>\d{1,2})
        |
        (?P<m4>\d{1,2})\s*[.]\s*(?P<d4>\d{1,2})
    )
    (?=$|[\s：:（(])
    \s*(?:[:：]\s*)?
    (?P<rest>.*)$
    """
)


def _pad_time(hour: str, minute: str) -> str:
    h = int(hour)
    m = int(minute)
    return f"{h:02d}:{m:02d}"


def _sanitize_cell(s: str) -> str:
    # Prevent breaking the " | " table-like rows.
    return (s or "").replace("|", " ").replace("\n", " ").strip()


def _parse_day_index(marker: str) -> int | None:
    s = (marker or "").strip().lower()
    if not s:
        return None

    m = re.search(r"\bd\s*(\d{1,2})\b", s)
    if not m:
        m = re.search(r"\bday\s*(\d{1,2})\b", s)
    if m:
        n = int(m.group(1))
        return max(0, n - 1)

    m = re.search(r"第\s*([一二三四五六七八九十两\d]{1,3})\s*天", marker)
    if not m:
        return None

    token = m.group(1).strip()
    if token.isdigit():
        return max(0, int(token) - 1)

    mapping = {"一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
    if token in mapping:
        return mapping[token] - 1

    # Minimal support for "十一"/"十二"... up to "二十".
    if token.startswith("十") and len(token) == 2 and token[1] in mapping:
        return 10 + mapping[token[1]] - 1
    if len(token) == 2 and token[0] in mapping and token[1] == "十":
        return mapping[token[0]] * 10 - 1
    if len(token) == 3 and token[0] in mapping and token[1] == "十" and token[2] in mapping:
        return mapping[token[0]] * 10 + mapping[token[2]] - 1

    return None


def _guess_time_range_from_hint(hint: str) -> tuple[str, str]:
    mapping = {
        "早上": ("08:30", "10:30"),
        "上午": ("09:00", "11:00"),
        "中午": ("11:00", "12:30"),
        "下午": ("13:00", "15:30"),
        "傍晚": ("15:30", "17:30"),
        "晚上": ("18:30", "20:00"),
        "夜间": ("20:00", "21:30"),
    }
    return mapping.get(hint, ("09:00", "11:00"))


def _normalize_date_token(year: str | None, month: str, day: str) -> str | None:
    try:
        m = int(month)
        d = int(day)
        if m < 1 or m > 12 or d < 1 or d > 31:
            return None
        if year is None:
            return f"{m:02d}-{d:02d}"
        y = int(year)
        if y < 1900 or y > 2100:
            return None
        return f"{y:04d}-{m:02d}-{d:02d}"
    except Exception:
        return None


def _extract_date_header(line: str) -> tuple[str, str] | None:
    """
    Detect a date header at the beginning of a line and return (normalized_date, remainder_text).

    Notes:
    - Does not guess the year. If the year is missing, returns MM-DD.
    - Guards against false positives like "提前1-7天预约" by requiring a delimiter after the token.
    """
    m = _DATE_HEADER_RE.match(line or "")
    if not m:
        return None

    year = m.group("y")
    month = m.group("m1") or m.group("m2") or m.group("m3") or m.group("m4")
    day = m.group("d1") or m.group("d2") or m.group("d3") or m.group("d4")
    if not month or not day:
        return None

    normalized = _normalize_date_token(year, month, day)
    if not normalized:
        return None

    rest = (m.group("rest") or "").strip()
    return normalized, rest


def _fallback_convert_to_itinerary_markdown_v2(parsed_content: str) -> str:
    """
    Deterministic fallback for common XHS "攻略/行程" text.

    Goal: generate usable v2 markdown without hallucinating facts.
    """
    text = (parsed_content or "").strip()
    if not text:
        return ""

    lines = [ln.rstrip() for ln in text.splitlines()]
    days: list[list[dict[str, str]]] = []
    day_dates: list[str] = []
    date_to_day: dict[str, int] = {}
    current_day_idx = 0

    def ensure_day(i: int) -> None:
        while len(days) <= i:
            days.append([])
        while len(day_dates) <= i:
            day_dates.append("")

    ensure_day(0)

    def start_new_entry(day_index: int, start: str, end: str, activity: str, place: str, remark: str) -> None:
        ensure_day(day_index)
        days[day_index].append(
            {
                "start": start,
                "end": end,
                "activity": _sanitize_cell(activity),
                "place": _sanitize_cell(place),
                "remark": _sanitize_cell(remark),
            }
        )

    def append_remark(day_index: int, extra: str) -> None:
        if not days[day_index]:
            return
        extra_clean = _sanitize_cell(extra)
        if not extra_clean:
            return
        existing = days[day_index][-1]["remark"]
        combined = (existing + " " + extra_clean).strip() if existing else extra_clean
        if len(combined) > 400:
            combined = combined[:400].rstrip() + "..."
        days[day_index][-1]["remark"] = combined

    def _split_inline_route_pois(s: str) -> list[str]:
        """
        Split "A→B→C" / "A->B->C" style inline route text into POI tokens.

        Keep it conservative: only split when there are 2+ tokens and each token
        looks like a short place name (avoid splitting long sentences).
        """
        t = (s or "").strip()
        if not t:
            return []
        parts = [p.strip() for p in re.split(r"\s*(?:->|→|➡️|—|–|－|＞|>)+\s*", t) if p.strip()]
        if len(parts) < 2:
            return []
        cleaned: list[str] = []
        for p in parts[:12]:
            if len(p) > 80:
                return []
            cleaned.append(p)
        return cleaned

    for raw in lines:
        line = (raw or "").strip()
        if not line:
            continue

        m_day = _DAY_HEADER_RE.match(line)
        if m_day:
            marker = (m_day.group(1) or "").strip()
            parsed_idx = _parse_day_index(marker)
            current_day_idx = parsed_idx if parsed_idx is not None else len(days)
            ensure_day(current_day_idx)
            remainder = (m_day.group(2) or "").strip()
            if not remainder:
                continue
            # Handle cases like "D1：中央大街→圣索菲亚教堂→..." without explicit times:
            # emit deterministic rows to preserve POIs.
            if not _TIME_RANGE_RE.search(remainder) and not _TIME_HINT_RE.search(remainder):
                pois = _split_inline_route_pois(remainder)
                if pois:
                    start_hour = 9
                    for idx, poi in enumerate(pois):
                        start = f"{min(start_hour + idx, 23):02d}:00"
                        start_new_entry(current_day_idx, start, "", "游览", poi, "")
                    continue
                start_new_entry(current_day_idx, "09:00", "", "游览", remainder, "")
                continue

            # Handle cases like "第二天：上午：寒山寺（9:00-11:00）" in one line.
            line = remainder

        date_header = _extract_date_header(line)
        if date_header:
            date_str, remainder = date_header
            if date_str in date_to_day:
                current_day_idx = date_to_day[date_str]
            else:
                # If we haven't started anything yet, reuse Day 1 instead of creating a blank leading day.
                if len(days) == 1 and not days[0] and not day_dates[0]:
                    current_day_idx = 0
                else:
                    current_day_idx = len(days)
                ensure_day(current_day_idx)
                day_dates[current_day_idx] = date_str
                date_to_day[date_str] = current_day_idx
            if not remainder:
                continue
            line = remainder

        m_time = _TIME_RANGE_RE.search(line)
        if m_time:
            start = _pad_time(m_time.group(1), m_time.group(2))
            end = _pad_time(m_time.group(3), m_time.group(4))
            title_part = _TIME_RANGE_RE.sub("", line).strip()
            # e.g. "上午：拙政园" / "观前街午餐"
            if "：" in title_part:
                _, title_part = title_part.split("：", 1)
                title_part = title_part.strip()
            title_part = title_part.strip("：:（()） ")

            activity = "游览"
            place = title_part
            if re.search(r"(午餐|晚餐|早餐|用餐|餐)", title_part):
                activity = "用餐"
                place = re.sub(r"(午餐|晚餐|早餐|用餐|餐)\\s*$", "", title_part).strip() or title_part
            elif "购物" in title_part:
                activity = "购物"
                if place.startswith("购物"):
                    place = place[len("购物") :].strip(" ：:，,.-—") or title_part
            elif re.search(r"(酒店|民宿|住宿|入住|休息)", title_part):
                activity = "住宿"
                for prefix in ("住宿", "入住"):
                    if place.startswith(prefix):
                        place = place[len(prefix) :].strip(" ：:，,.-—") or title_part

            remainder = line[m_time.end() :].strip(" ；;，,。.")
            start_new_entry(current_day_idx, start, end, activity, place, remainder)
            continue

        m_hint = _TIME_HINT_RE.search(line)
        if m_hint and ("：" in line or "：" in raw):
            hint = m_hint.group(1)
            start, end = _guess_time_range_from_hint(hint)
            title_part = line
            if "：" in title_part:
                _, title_part = title_part.split("：", 1)
            title_part = title_part.strip("：: ")

            activity = "游览"
            place = title_part
            if re.search(r"(午餐|晚餐|早餐|用餐|餐)", title_part):
                activity = "用餐"
                place = re.sub(r"(午餐|晚餐|早餐|用餐|餐)\\s*$", "", title_part).strip() or title_part
            elif "购物" in title_part:
                activity = "购物"
                if place.startswith("购物"):
                    place = place[len("购物") :].strip(" ：:，,.-—") or title_part
            elif re.search(r"(酒店|民宿|住宿|入住|休息)", title_part):
                activity = "住宿"
                for prefix in ("住宿", "入住"):
                    if place.startswith(prefix):
                        place = place[len(prefix) :].strip(" ：:，,.-—") or title_part
            start_new_entry(current_day_idx, start, end, activity, place, "")
            continue

        # Description line; attach to the last entry if possible.
        append_remark(current_day_idx, line)

    # If parsing found nothing usable, keep content as a single day note (still v2-compatible).
    has_any_row = any(len(d) > 0 for d in days)
    if not has_any_row:
        days = [[{"start": "09:00", "end": "11:00", "activity": "行程整理", "place": "", "remark": _sanitize_cell(text[:400])}]]

    out: list[str] = []
    out.append("# 行程安排")
    out.append("> 版本: v2")
    out.append("")

    has_any_explicit_date = any(d.strip() for d in day_dates)
    for i, entries in enumerate(days, start=1):
        if not entries:
            continue
        if has_any_explicit_date:
            day_date = day_dates[i - 1] or "今天"
        else:
            day_date = "今天"
        out.append(f"## Day {i}（{day_date}）")
        for e in entries:
            out.append(f"- {e['start']} - {e['end']} | {e['activity']} | {e['place']} | {e['remark']}")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


class MarkdownConverter:
    def __init__(self) -> None:
        self._client = OpenAIClient()

    @staticmethod
    def _introduces_extra_days(original_text: str, converted_md: str) -> bool:
        """
        Guardrail: if the original text explicitly contains D1/D2/... or Day1/Day2...
        markers, the converted markdown must not introduce additional days.
        """
        original_markers = _extract_explicit_day_markers(original_text)
        if not original_markers:
            return False

        output_days = _extract_day_numbers_from_v2(converted_md)
        if not output_days:
            return False

        return max(output_days) > max(original_markers)

    async def convert_parsed_text_to_markdown(
        self,
        *,
        parsed_content: str,
        model: str | None = None,
    ) -> str:
        text = (parsed_content or "").strip()
        if not text:
            return ""

        if not self._client.is_configured():
            raise RuntimeError("OPENAI_API_KEY is not configured")

        prompt = (
            "你将获得一段“小红书笔记解析原文”（纯文本）。\n"
            "任务：把它转成 TeamVenture 应用的“标准行程 Markdown（v2）”，用于后续 /plans/generate。\n"
            "\n"
            "强约束（非常重要）：\n"
            "- 不能编造任何事实（地点/天数/预算/交通/酒店/价格等）。\n"
            "- 大量去除无效信息：分享包装、口令、emoji堆砌、无关标签等；只保留能用于行程安排的核心内容。\n"
            "- 不要丢失任何在原文中出现的景点/POI 名称；如需合并到同一条行程，也必须在“地点”列完整保留名称。\n"
            "- 不要输出“解释/分析/总结”，只输出最终 Markdown。\n"
            "- 如果原文出现多个不同日期（如 2024-06-01 / 6月2日 / 06-03）：必须“按日期分 Day”，每个日期对应一个 Day；不得把多天合并成一天。\n"
            "- Day 标题里的日期：能确定年份则用 YYYY-MM-DD；缺少年份则用原文日期或 MM-DD（不要猜年份）。\n"
            "- 如果原文没有明确日期：Day 标题里的日期请用“今天”为 Day1 起始日（仅用于展示占位，用户后续会确认）。\n"
            "- 如果原文包含 day1/day2/D1/第1天 等分天信息：必须输出对应的 Day1/Day2/Day3…\n"
            "- 如果原文出现明确时间（例如 7:30-10:30）：必须保留并使用该时间范围；不要强行改成整天或统一时间段。\n"
            "- 每天输出多条行程条目，每条严格使用格式：\n"
            "  - HH:MM - HH:MM | 活动 | 地点 | 备注\n"
            "- 禁止输出“09:00-20:00 自由安排”这类占位；如果无法解析，宁可把原文拆分为多条条目并保留地点。\n"
            "- 交通/住宿允许没有具体时间（可留空或用大致范围），但不要编造航班/高铁等跨城交通。\n"
            "\n"
            "标准 Markdown 输出格式（必须严格遵守）：\n"
            "# 行程安排\n"
            "> 版本: v2\n"
            "\n"
            "## Day N（YYYY-MM-DD）\n"
            "- 09:00 - 10:30 | 活动 | 地点 | \n"
            "- 11:00 - 12:00 | 活动 | 地点 | \n"
            "\n"
            "\n"
            "输入 parsed_content：\n"
            f"{text}\n"
            "\n"
            '返回 JSON：{"markdown_content":"..."}'
        )

        try:
            result = await self._client.generate_json(
                prompt,
                model=model,
                temperature=0.0,
                max_tokens=4000,
            )
            content = (result.get("markdown_content") or "").strip()
            if (
                content
                and _looks_like_standard_itinerary_markdown(content)
                and not _looks_like_low_quality_itinerary_markdown(content)
                and not self._introduces_extra_days(text, content)
            ):
                return _rationalize_itinerary_markdown_v2(content)
            # Fall back to deterministic conversion for better UX.
            return _rationalize_itinerary_markdown_v2(_fallback_convert_to_itinerary_markdown_v2(text))
        except Exception:
            raise


_V2_DAY_HEADING_RE = re.compile(r"(?im)^\s*##\s*Day\s*(\d+)\b")


def _extract_day_numbers_from_v2(md: str) -> set[int]:
    out: set[int] = set()
    for m in _V2_DAY_HEADING_RE.finditer(md or ""):
        try:
            out.add(int(m.group(1)))
        except Exception:
            continue
    return out


def _extract_explicit_day_markers(text: str) -> set[int]:
    """
    Extract day numbers explicitly stated by the user (D1/D2, Day1/Day2, 第1天...).

    Only uses line-start markers to avoid false positives in long paragraphs.
    """
    out: set[int] = set()
    for raw in (text or "").splitlines():
        line = (raw or "").strip()
        if not line:
            continue
        m_day = _DAY_HEADER_RE.match(line)
        if not m_day:
            continue
        marker = (m_day.group(1) or "").strip()
        idx = _parse_day_index(marker)
        if idx is None:
            continue
        out.add(idx + 1)
    return out


def _rationalize_itinerary_markdown_v2(md: str) -> str:
    """
    Deterministic post-processor to make v2 itinerary markdown more reasonable
    WITHOUT adding new POIs/facts.

    Allowed supplements:
    - Insert generic "交通/转场" between POIs
    - Insert "午餐/晚餐" if missing (generic, no invented restaurant)
    - Normalize times to be sequential within 09:00-20:00 window
    - If items overflow after 20:00, keep POI as "备选" at 20:00
    """
    parsed = _parse_itinerary_markdown_v2(md)
    if not parsed:
        return md

    out_lines: list[str] = []
    out_lines.append("# 行程安排")
    out_lines.append("> 版本: v2")
    out_lines.append("")

    for day in parsed:
        day_no = day["day"]
        heading_suffix = day.get("heading_suffix") or ""
        if heading_suffix:
            out_lines.append(f"## Day {day_no}{heading_suffix}")
        else:
            out_lines.append(f"## Day {day_no}")

        items = day.get("items") or []
        rational = _rationalize_day_items(items)
        for it in rational:
            out_lines.append(
                f"- {it['time_start']} - {it['time_end']} | {it['activity']} | {it['location']} | {it['note']}"
            )
        out_lines.append("")

    return "\n".join(out_lines).rstrip() + "\n"


def _parse_itinerary_markdown_v2(md: str) -> list[dict[str, object]]:
    text = (md or "").replace("\r", "").strip()
    if not text:
        return []

    days: list[dict[str, object]] = []
    current: dict[str, object] | None = None

    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# "):
            continue
        if line.startswith(">"):
            continue

        m_day = re.match(r"^##\s*Day\s*(\d+)(.*)$", line, flags=re.IGNORECASE)
        if m_day:
            day_no = int(m_day.group(1))
            suffix = (m_day.group(2) or "").rstrip()
            current = {"day": day_no, "heading_suffix": suffix, "items": []}
            days.append(current)
            continue

        if line.startswith("- ") and current is not None:
            body = line[2:].strip()
            cols = [c.strip() for c in body.split("|")]
            while len(cols) < 4:
                cols.append("")
            time_range = cols[0]
            activity = cols[1]
            location = cols[2]
            note = cols[3]

            m_tr = re.match(r"^\s*(\d{1,2}:\d{2})\s*-\s*(\d{0,2}:?\d{0,2})\s*$", time_range)
            if not m_tr:
                continue
            start = _pad_hhmm(m_tr.group(1))
            end = _pad_hhmm(m_tr.group(2))
            current["items"].append(
                {
                    "time_start": start,
                    "time_end": end,
                    "activity": activity,
                    "location": location,
                    "note": note,
                }
            )

    return days


def _pad_hhmm(v: str) -> str:
    s = (v or "").strip()
    if not s:
        return ""
    m = re.match(r"^(\d{1,2}):(\d{2})$", s)
    if not m:
        return ""
    return f"{int(m.group(1)):02d}:{int(m.group(2)):02d}"


def _hhmm_to_minutes(v: str) -> int | None:
    m = re.match(r"^(\d{2}):(\d{2})$", (v or "").strip())
    if not m:
        return None
    h = int(m.group(1))
    mi = int(m.group(2))
    if h < 0 or h > 23 or mi < 0 or mi > 59:
        return None
    return h * 60 + mi


def _minutes_to_hhmm(m: int) -> str:
    m = max(0, min(int(m), 23 * 60 + 59))
    return f"{m // 60:02d}:{m % 60:02d}"


def _guess_duration_minutes(activity: str, location: str, explicit_duration: int | None) -> int:
    if explicit_duration is not None:
        return max(30, min(explicit_duration, 6 * 60))

    a = (activity or "").strip()
    loc = (location or "").strip()

    if "用餐" in a or a in {"午餐", "晚餐", "早餐"}:
        return 60
    if "交通" in a or "转场" in a or "接驳" in a:
        return 30

    heavy = ("冰雪大世界", "雪博会", "虎林园", "极地公园", "海洋馆", "滑雪")
    medium = ("公园", "博物馆", "教堂", "街区", "大街", "码头", "塔", "桥", "市场")
    if any(k in loc for k in heavy):
        return 180
    if any(k in loc for k in medium):
        return 90
    return 75


def _rationalize_day_items(items: list[dict[str, str]]) -> list[dict[str, str]]:
    if not items:
        return [{"time_start": "09:00", "time_end": "", "activity": "自由活动/机动安排", "location": "", "note": ""}]

    # Keep original order; rebuild a sequential schedule.
    day_start = 9 * 60
    day_end = 20 * 60
    transfer_buffer = 15

    normalized: list[dict[str, str]] = []
    has_meal = any("用餐" in (it.get("activity") or "") for it in items)

    current = day_start
    inserted_lunch = False
    inserted_dinner = False

    def maybe_insert_meal(window_start: int, window_end: int, meal_name: str) -> None:
        nonlocal current, inserted_lunch, inserted_dinner
        if has_meal:
            return
        if meal_name == "午餐" and inserted_lunch:
            return
        if meal_name == "晚餐" and inserted_dinner:
            return
        if current < window_start or current > window_end:
            return
        start = current
        end = min(start + 60, day_end)
        if end <= start:
            return
        normalized.append(
            {"time_start": _minutes_to_hhmm(start), "time_end": _minutes_to_hhmm(end), "activity": "用餐", "location": "", "note": meal_name}
        )
        current = end
        if meal_name == "午餐":
            inserted_lunch = True
        if meal_name == "晚餐":
            inserted_dinner = True

    for idx, it in enumerate(items):
        activity = (it.get("activity") or "").strip()
        location = (it.get("location") or "").strip()
        note = (it.get("note") or "").strip()
        if not activity and not location and not note:
            continue

        # Insert lunch/dinner around typical windows if missing.
        maybe_insert_meal(11 * 60 + 30, 13 * 60, "午餐")
        maybe_insert_meal(17 * 60 + 30, 19 * 60, "晚餐")

        # Transfer buffer before each non-first item.
        if idx > 0:
            next_hint = f"前往{location}" if location else ""
            start = current
            end = min(start + transfer_buffer, day_end)
            if end > start:
                normalized.append(
                    {
                        "time_start": _minutes_to_hhmm(start),
                        "time_end": _minutes_to_hhmm(end),
                        "activity": "交通/转场",
                        "location": "",
                        "note": next_hint,
                    }
                )
                current = end

        start_min = current
        if start_min >= day_end:
            # Keep POI as a "backup" item instead of dropping it.
            normalized.append(
                {
                    "time_start": _minutes_to_hhmm(day_end),
                    "time_end": "",
                    "activity": f"备选：{activity or '行程'}",
                    "location": location,
                    "note": (note + " " if note else "") + "超出当天时间，建议调整到白天或下次",
                }
            )
            continue

        explicit_start = _hhmm_to_minutes(it.get("time_start") or "")
        explicit_end = _hhmm_to_minutes(it.get("time_end") or "")
        explicit_duration = None
        if explicit_start is not None and explicit_end is not None and explicit_end > explicit_start:
            explicit_duration = explicit_end - explicit_start

        duration = _guess_duration_minutes(activity, location, explicit_duration)
        end_min = min(start_min + duration, day_end)
        end_str = _minutes_to_hhmm(end_min)
        normalized.append(
            {
                "time_start": _minutes_to_hhmm(start_min),
                "time_end": end_str,
                "activity": activity or "游览",
                "location": location,
                "note": note,
            }
        )
        current = end_min

    return normalized
