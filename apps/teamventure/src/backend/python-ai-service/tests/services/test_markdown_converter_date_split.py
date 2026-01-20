from __future__ import annotations

from src.services.markdown_converter import _fallback_convert_to_itinerary_markdown_v2


def test_fallback_convert_splits_by_explicit_full_dates():
    text = """
2026-01-19：上午：南京路步行街（9:00-10:30）
2026-01-20：中午：外滩午餐（11:00-12:00）
"""
    md = _fallback_convert_to_itinerary_markdown_v2(text)
    assert "## Day 1（2026-01-19）" in md
    assert "## Day 2（2026-01-20）" in md
    assert "南京路步行街" in md
    assert "外滩" in md


def test_fallback_convert_splits_by_month_day_without_guessing_year():
    text = """
6月1日：上午：拙政园（7:30-10:30）
6月2日：上午：寒山寺（9:00-11:00）
"""
    md = _fallback_convert_to_itinerary_markdown_v2(text)
    assert "## Day 1（06-01）" in md
    assert "## Day 2（06-02）" in md


def test_fallback_convert_does_not_treat_booking_window_as_date_header():
    text = """
提前1-7天在公众号预约
第一天：上午：拙政园（7:30-10:30）
"""
    md = _fallback_convert_to_itinerary_markdown_v2(text)
    assert "## Day 1（今天）" in md
    assert "## Day 2（" not in md

