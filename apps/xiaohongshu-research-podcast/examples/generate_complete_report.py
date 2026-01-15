#!/usr/bin/env python3
"""
完整报告生成示例
展示如何从数据抓取到最终生成Markdown报告的完整流程
"""
import sys
from pathlib import Path
from datetime import datetime

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.topic import XHSTopic, TopicAnalysisResult, AIInsight
from generators.report_generator import ReportGenerator


def create_mock_analysis_result() -> TopicAnalysisResult:
    """创建模拟的分析结果数据"""
    # 模拟Top话题
    mock_topics = [
        XHSTopic(
            topic_id="t1",
            title="春节出游攻略",
            description="分享春节期间的旅游目的地推荐和出行攻略",
            heat_score=1500000,
            read_count=50000000,
            note_count=20000,
            rank=1,
            rank_change=2,
            trend_icon="↑",
            trend_direction="up",
            category="旅游",
            tags=["春节", "旅游", "攻略"],
        ),
        XHSTopic(
            topic_id="t2",
            title="年货清单推荐",
            description="精选年货好物，让你轻松置办年货",
            heat_score=1200000,
            read_count=40000000,
            note_count=18000,
            rank=2,
            rank_change=-1,
            trend_icon="↓",
            trend_direction="down",
            category="美食",
            tags=["年货", "春节", "美食"],
        ),
        XHSTopic(
            topic_id="t3",
            title="居家健身指南",
            description="适合在家练习的健身动作和计划",
            heat_score=980000,
            read_count=35000000,
            note_count=15000,
            rank=3,
            rank_change=0,
            trend_icon="→",
            trend_direction="stable",
            category="运动",
            tags=["健身", "居家", "运动"],
        ),
        XHSTopic(
            topic_id="t4",
            title="冬季穿搭灵感",
            description="时髦又保暖的冬季穿搭方案",
            heat_score=850000,
            read_count=30000000,
            note_count=12000,
            rank=4,
            rank_change=3,
            trend_icon="↑",
            trend_direction="up",
            category="时尚",
            tags=["穿搭", "冬季", "时尚"],
        ),
        XHSTopic(
            topic_id="t5",
            title="护肤品测评",
            description="真实用户体验的护肤品测评分享",
            heat_score=720000,
            read_count=25000000,
            note_count=10000,
            rank=5,
            rank_change=-2,
            trend_icon="↓",
            trend_direction="down",
            category="美妆",
            tags=["护肤", "测评", "美妆"],
        ),
    ]

    # 构建分析结果
    result = TopicAnalysisResult(
        date=datetime.now().strftime("%Y-%m-%d"),
        total_topics=50,
        total_heat=50000000,  # 5000万
        top_keywords=[
            "春节",
            "旅游",
            "年货",
            "美食",
            "攻略",
            "健身",
            "居家",
            "推荐",
            "穿搭",
            "冬季",
            "护肤",
            "测评",
            "美妆",
            "时尚",
            "运动",
        ],
        category_stats={
            "旅游": {"count": 15, "total_heat": 20000000, "avg_heat": 1333333},
            "美食": {"count": 12, "total_heat": 15000000, "avg_heat": 1250000},
            "运动": {"count": 10, "total_heat": 8000000, "avg_heat": 800000},
            "时尚": {"count": 8, "total_heat": 5000000, "avg_heat": 625000},
            "美妆": {"count": 5, "total_heat": 2000000, "avg_heat": 400000},
        },
        top_topics=mock_topics,
        rising_topics=[
            {"title": "春节出游攻略", "rank": 1, "rank_change": 2},
            {"title": "冬季穿搭灵感", "rank": 4, "rank_change": 3},
            {"title": "居家烹饪教程", "rank": 8, "rank_change": 4},
        ],
        new_topics=["春节礼盒推荐", "年味装饰DIY", "红包封面设计", "春联书法教程"],
    )

    return result


def create_mock_ai_insight() -> AIInsight:
    """创建模拟的AI洞察"""
    return AIInsight(
        user_behavior=[
            "用户对春节相关内容关注度显著上升，特别是旅游和年货类别",
            "短视频形式的攻略类内容互动率提升30%",
            "地域性美食话题在三四线城市表现突出",
            "图文并茂的测评类内容获得更高的收藏率",
        ],
        trend_predictions=[
            "预计未来一周，春节旅游相关话题将持续升温",
            "国潮元素结合传统文化的内容可能成为新热点",
            "健康养生类话题在节后可能迎来小高峰",
            "居家场景的生活方式内容需求增长明显",
        ],
        creator_tips=[
            "建议创作者提前布局春节相关内容，抓住流量红利期",
            "可以尝试结合地域特色和传统文化打造差异化内容",
            "图文+短视频组合形式更容易获得平台推荐",
            "测评类内容需注重真实性和细节展示",
            "攻略类内容建议增加互动性设计（如投票、问答）",
        ],
        platform_insights=[
            "平台正在加大对传统文化内容的推荐权重",
            "图文+短视频混合形式的笔记获得更多曝光",
            "用户停留时长成为新的核心推荐指标",
            "本地化和地域性内容获得更精准的流量分发",
        ],
    )


def main():
    """主流程"""
    print("\n" + "=" * 60)
    print("📝 完整报告生成示例")
    print("=" * 60)
    print()

    # 1. 创建模拟数据
    print("[1/3] 准备分析数据...")
    analysis_result = create_mock_analysis_result()
    ai_insight = create_mock_ai_insight()
    print(f"  ✓ 话题数: {analysis_result.total_topics}")
    print(f"  ✓ 热词数: {len(analysis_result.top_keywords)}")
    print(f"  ✓ 分类数: {len(analysis_result.category_stats)}")

    # 2. 生成报告
    print("\n[2/3] 生成Markdown报告...")
    generator = ReportGenerator()

    output_dir = Path(__file__).parent.parent / "output" / "example"
    output_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = output_dir / f"report-{date_str}.md"

    report_content = generator.generate(
        analysis_result=analysis_result,
        ai_insight=ai_insight,
        output_path=output_path,
    )

    # 3. 输出统计
    print("\n[3/3] 生成完成")
    print("-" * 60)
    print(f"  📄 文件路径: {output_path}")
    print(f"  📏 字符数: {len(report_content)}")
    print(f"  📝 行数: {len(report_content.splitlines())}")
    print(f"  📦 文件大小: {len(report_content.encode('utf-8')) / 1024:.1f} KB")

    # 4. 预览报告
    print("\n" + "=" * 60)
    print("📖 报告预览（前25行）")
    print("=" * 60)
    for i, line in enumerate(report_content.splitlines()[:25], 1):
        print(f"{i:3d} | {line}")

    print("\n" + "=" * 60)
    print("✓ 示例运行完成！")
    print(f"  查看完整报告: {output_path}")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
