#!/usr/bin/env python3
"""测试报告生成器"""
import sys
from pathlib import Path
from datetime import datetime

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.topic import XHSTopic, TopicAnalysisResult, AIInsight
from generators.report_generator import ReportGenerator


def main():
    """测试报告生成"""
    print("测试Markdown报告生成器...")

    # 创建测试数据
    test_topics = [
        XHSTopic(
            topic_id="t1",
            title="春节出游攻略",
            heat_score=1500000,
            read_count=50000000,
            note_count=20000,
            rank=1,
            rank_change=2,
            trend_icon="↑",
            category="旅游",
        ),
        XHSTopic(
            topic_id="t2",
            title="年货清单推荐",
            heat_score=1200000,
            read_count=40000000,
            note_count=18000,
            rank=2,
            rank_change=-1,
            trend_icon="↓",
            category="美食",
        ),
        XHSTopic(
            topic_id="t3",
            title="居家健身指南",
            heat_score=980000,
            read_count=35000000,
            note_count=15000,
            rank=3,
            rank_change=0,
            trend_icon="→",
            category="运动",
        ),
    ]

    test_result = TopicAnalysisResult(
        date="2026-01-15",
        total_topics=50,
        total_heat=50000000,
        top_keywords=["春节", "旅游", "年货", "美食", "攻略", "健身", "居家", "推荐"],
        category_stats={
            "旅游": {"count": 15, "total_heat": 20000000},
            "美食": {"count": 12, "total_heat": 15000000},
            "运动": {"count": 10, "total_heat": 8000000},
            "时尚": {"count": 8, "total_heat": 5000000},
            "美妆": {"count": 5, "total_heat": 2000000},
        },
        top_topics=test_topics,
        rising_topics=[
            {"title": "春节出游攻略", "rank": 1, "rank_change": 2},
            {"title": "居家健身指南", "rank": 3, "rank_change": 5},
        ],
        new_topics=["春节礼盒推荐", "年味装饰DIY", "红包封面设计"],
    )

    test_insight = AIInsight(
        user_behavior=[
            "用户对春节相关内容关注度显著上升，特别是旅游和年货类别",
            "短视频形式的攻略类内容互动率提升30%",
            "地域性美食话题在三四线城市表现突出",
        ],
        trend_predictions=[
            "预计未来一周，春节旅游相关话题将持续升温",
            "国潮元素结合传统文化的内容可能成为新热点",
            "健康养生类话题在节后可能迎来小高峰",
        ],
        creator_tips=[
            "建议创作者提前布局春节相关内容，抓住流量红利期",
            "可以尝试结合地域特色和传统文化打造差异化内容",
            "图文+短视频组合形式更容易获得平台推荐",
        ],
        platform_insights=[
            "平台正在加大对传统文化内容的推荐权重",
            "图文+短视频混合形式的笔记获得更多曝光",
            "用户停留时长成为新的核心推荐指标",
        ],
    )

    # 生成报告
    output_dir = Path("output") / "test"
    output_dir.mkdir(parents=True, exist_ok=True)

    generator = ReportGenerator()
    report_content = generator.generate(
        analysis_result=test_result,
        ai_insight=test_insight,
        output_path=output_dir / "test_report.md",
    )

    print("\n" + "=" * 50)
    print("✓ 测试报告已生成")
    print("=" * 50)
    print(f"  文件路径: {output_dir / 'test_report.md'}")
    print(f"  字符数: {len(report_content)}")
    print(f"  行数: {len(report_content.splitlines())}")
    print()
    print("报告预览（前30行）:")
    print("-" * 50)
    for i, line in enumerate(report_content.splitlines()[:30], 1):
        print(line)
    print("-" * 50)


if __name__ == "__main__":
    main()
