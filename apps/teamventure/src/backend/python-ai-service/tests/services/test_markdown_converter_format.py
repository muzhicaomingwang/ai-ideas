from __future__ import annotations

from src.services.markdown_converter import (
    MarkdownConverter,
    _fallback_convert_to_itinerary_markdown_v2,
    _looks_like_low_quality_itinerary_markdown,
    _looks_like_standard_itinerary_markdown,
)


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


def test_looks_like_low_quality_itinerary_markdown_rejects_placeholder():
    md = """
# 行程安排
> 版本: v2

## Day 1（今天）
- 09:00 - 20:00 | 自由安排 | | 
"""
    assert _looks_like_standard_itinerary_markdown(md) is True
    assert _looks_like_low_quality_itinerary_markdown(md) is True


def test_fallback_convert_to_itinerary_markdown_v2_preserves_pois_and_times():
    text = """
苏州带娃老人两天一晚旅游攻略
行程安排
第一天：古典园林与文化体验
上午：拙政园（7:30-10:30）
中午：观前街午餐（11:00-12:30）
下午：苏州博物馆（13:00-15:00）
第二天：
上午：寒山寺（9:00-11:00）
"""
    md = _fallback_convert_to_itinerary_markdown_v2(text)
    assert _looks_like_standard_itinerary_markdown(md) is True
    assert "拙政园" in md
    assert "观前街" in md
    assert "苏州博物馆" in md
    assert "寒山寺" in md
    assert "07:30 - 10:30" in md


def test_fallback_convert_to_itinerary_markdown_v2_extracts_d1_route_lines():
    text = """
哈尔滨3天2夜路线：
D1：中央大街→圣索菲亚教堂→黑龙江省博物馆→防洪胜利纪念塔→松花江铁路桥
D2：东北虎林园→太阳岛雪博会→雪人码头→音乐公园→冰雪大世界
D3：七三一部队罪证陈列馆→果戈里大街→哈药六厂→兆麟公园→老道外中华巴洛克街区
"""
    md = _fallback_convert_to_itinerary_markdown_v2(text)
    assert _looks_like_standard_itinerary_markdown(md) is True
    assert "## Day 1" in md
    assert "## Day 2" in md
    assert "## Day 3" in md
    assert "中央大街" in md
    assert "冰雪大世界" in md
    assert "哈药六厂" in md


def test_llm_convert_guardrail_rejects_extra_days_when_input_has_d_markers():
    original = "哈尔滨3天2夜路线：\nD1：中央大街→索菲亚教堂\nD2：冰雪大世界\nD3：返程\n"
    llm_md_with_extra = """
# 行程安排
> 版本: v2

## Day 1（今天）
- 09:00 -  | 游览 | 中央大街 |  |

## Day 2（今天）
- 09:00 -  | 游览 | 冰雪大世界 |  |

## Day 3（今天）
- 09:00 -  | 返程 |  |  |

## Day 4（今天）
- 09:00 -  | 交通 | 哈尔滨太平国际机场 |  |
""".strip()
    assert MarkdownConverter._introduces_extra_days(original, llm_md_with_extra) is True


def test_rationalizer_inserts_transfer_and_meal_without_new_pois():
    md = """
# 行程安排
> 版本: v2

## Day 1（今天）
- 09:00 -  | 游览 | 中央大街 |  |
- 09:00 -  | 参观 | 圣索菲亚教堂 |  |
- 09:00 -  | 参观 | 黑龙江省博物馆 |  |
""".strip()
    from src.services.markdown_converter import _rationalize_itinerary_markdown_v2

    fixed = _rationalize_itinerary_markdown_v2(md)
    assert "交通/转场" in fixed
    assert "用餐" in fixed
    assert "中央大街" in fixed
    assert "圣索菲亚教堂" in fixed
    assert "黑龙江省博物馆" in fixed
