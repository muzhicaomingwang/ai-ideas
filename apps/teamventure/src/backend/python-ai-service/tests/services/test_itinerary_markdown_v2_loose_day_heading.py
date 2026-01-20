from src.services.itinerary_markdown_v2 import validate


def test_validate_accepts_day1_inline_route_lines():
    md = (
        "☃️3天2晚路线参考\n"
        "DAY1：巴洛克风情街→索菲亚教堂→道里菜市场→中央大街→防洪纪念塔→松花江铁路大桥\n"
        "DAY2：松花江索道→太阳岛·雪博会→极地公园&海洋馆→冰雪大世界→群力音乐公园·网红大雪人\n"
        "DAY3：七三一陈列馆→哈尔滨工业大学→黑龙江省博物馆→果戈里大街→哈药六厂→龙塔\n"
    )
    out = validate(md)
    assert out["valid"] is True
    assert out["days"] == 3
    assert out["items"] == 3


def test_validate_accepts_cn_day_heading_with_inline_text():
    md = "第1天：中央大街→索菲亚教堂\n"
    out = validate(md)
    assert out["valid"] is True
    assert out["days"] == 1
    assert out["items"] == 1


def test_validate_accepts_d1_d2_d3_headings():
    md = "D1：中央大街→索菲亚教堂\nD2：冰雪大世界\nD3：返程\n"
    out = validate(md)
    assert out["valid"] is True
    assert out["days"] == 3
    assert out["items"] == 3
