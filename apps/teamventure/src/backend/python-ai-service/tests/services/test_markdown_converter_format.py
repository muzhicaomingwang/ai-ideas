from __future__ import annotations

from src.services.markdown_converter import _looks_like_standard_itinerary_markdown


def test_looks_like_standard_itinerary_markdown_v2():
    md = """
# 行程安排
> 版本: v2

## Day 1（2026-01-19）
- 09:00 - 10:30 | 参观南京路步行街 | 南京路步行街 |
"""
    assert _looks_like_standard_itinerary_markdown(md) is True


def test_looks_like_standard_itinerary_markdown_rejects_empty():
    assert _looks_like_standard_itinerary_markdown("") is False

