"""
Markdown 研究报告生成器
基于小红书话题数据生成结构化报告
"""
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models.topic import XHSTopic, TopicAnalysisResult, AIInsight
from ..utils.logger import get_logger

logger = get_logger()


class ReportGenerator:
    """Markdown报告生成器"""

    def __init__(self):
        """初始化"""
        pass

    def generate(
        self,
        analysis_result: TopicAnalysisResult,
        ai_insight: Optional[AIInsight] = None,
        output_path: Optional[Path] = None,
    ) -> str:
        """
        生成Markdown报告

        Args:
            analysis_result: 话题分析结果
            ai_insight: AI洞察（可选）
            output_path: 输出文件路径（可选）

        Returns:
            报告内容（Markdown格式）
        """
        logger.info("开始生成Markdown报告...")

        # 构建报告内容
        report = []

        # 1. 标题和元信息
        report.append(self._generate_header(analysis_result))

        # 2. 摘要
        report.append(self._generate_summary(analysis_result))

        # 3. Top话题
        report.append(self._generate_top_topics(analysis_result))

        # 4. 热词分析
        report.append(self._generate_keywords(analysis_result))

        # 5. 分类统计
        report.append(self._generate_category_stats(analysis_result))

        # 6. 趋势分析
        if analysis_result.rising_topics or analysis_result.new_topics:
            report.append(self._generate_trends(analysis_result))

        # 7. AI洞察
        if ai_insight:
            report.append(self._generate_ai_insights(ai_insight))

        # 8. 页脚
        report.append(self._generate_footer(analysis_result))

        # 拼接完整报告
        full_report = "\n".join(report)

        # 保存到文件
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(full_report, encoding="utf-8")
            logger.info(f"  ✓ 报告已保存: {output_path}")

        logger.info("Markdown报告生成完成")
        return full_report

    def _generate_header(self, result: TopicAnalysisResult) -> str:
        """生成报告头部"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f"""# 小红书热门话题研究报告

**日期**: {result.date}
**生成时间**: {now}
**数据来源**: 新榜小红书热门话题榜单

---
"""

    def _generate_summary(self, result: TopicAnalysisResult) -> str:
        """生成摘要部分"""
        avg_heat = (
            result.total_heat // result.total_topics if result.total_topics > 0 else 0
        )

        # 格式化总热度
        if result.total_heat >= 100_000_000:
            total_heat_text = f"{result.total_heat / 100_000_000:.1f}亿"
        elif result.total_heat >= 10_000:
            total_heat_text = f"{result.total_heat / 10_000:.1f}万"
        else:
            total_heat_text = str(result.total_heat)

        # 格式化平均热度
        if avg_heat >= 100_000_000:
            avg_heat_text = f"{avg_heat / 100_000_000:.1f}亿"
        elif avg_heat >= 10_000:
            avg_heat_text = f"{avg_heat / 10_000:.1f}万"
        else:
            avg_heat_text = str(avg_heat)

        return f"""## 📊 数据摘要

- **话题总数**: {result.total_topics}
- **总热度**: {total_heat_text}
- **平均热度**: {avg_heat_text}
- **分类数**: {len(result.category_stats)}

"""

    def _generate_top_topics(self, result: TopicAnalysisResult) -> str:
        """生成Top话题表格"""
        if not result.top_topics:
            return ""

        lines = [
            "## 🔥 Top话题榜单",
            "",
            "| 排名 | 话题标题 | 热度值 | 阅读量 | 笔记数 | 趋势 |",
            "|------|----------|--------|--------|--------|------|",
        ]

        for topic in result.top_topics:
            # 格式化数值
            heat = topic.heat_score_formatted
            read = self._format_number(topic.read_count)
            notes = self._format_number(topic.note_count)

            # 趋势显示
            trend = f"{topic.trend_icon} {topic.rank_change_text}"

            lines.append(
                f"| {topic.rank} | {topic.title} | {heat} | {read} | {notes} | {trend} |"
            )

        lines.append("")
        return "\n".join(lines)

    def _generate_keywords(self, result: TopicAnalysisResult) -> str:
        """生成热词分析"""
        if not result.top_keywords:
            return ""

        # 将热词分组显示（每行5个）
        keyword_lines = []
        for i in range(0, len(result.top_keywords), 5):
            chunk = result.top_keywords[i : i + 5]
            keyword_lines.append("- " + " · ".join([f"**{kw}**" for kw in chunk]))

        return f"""## 🏷️ 热词分析

{chr(10).join(keyword_lines)}

"""

    def _generate_category_stats(self, result: TopicAnalysisResult) -> str:
        """生成分类统计"""
        if not result.category_stats:
            return ""

        lines = [
            "## 📂 分类统计",
            "",
            "| 分类 | 话题数 | 总热度 | 平均热度 | 占比 |",
            "|------|--------|--------|----------|------|",
        ]

        # 按话题数排序
        sorted_categories = sorted(
            result.category_stats.items(),
            key=lambda x: x[1].get("count", 0),
            reverse=True,
        )

        for category, stats in sorted_categories:
            count = stats.get("count", 0)
            total_heat = stats.get("total_heat", 0)
            avg_heat = total_heat // count if count > 0 else 0
            percentage = (count / result.total_topics * 100) if result.total_topics > 0 else 0

            # 格式化
            total_heat_text = self._format_number(total_heat)
            avg_heat_text = self._format_number(avg_heat)

            lines.append(
                f"| {category} | {count} | {total_heat_text} | {avg_heat_text} | {percentage:.1f}% |"
            )

        lines.append("")
        return "\n".join(lines)

    def _generate_trends(self, result: TopicAnalysisResult) -> str:
        """生成趋势分析"""
        sections = []

        # 上升话题
        if result.rising_topics:
            sections.append("### 📈 热度上升")
            sections.append("")

            for item in result.rising_topics[:10]:  # 只显示前10个
                title = item.get("title", "未知话题")
                rank = item.get("rank", 0)
                change = item.get("rank_change", 0)

                if change > 0:
                    sections.append(f"- **{title}** (排名#{rank} ↑{change})")
                else:
                    sections.append(f"- **{title}** (排名#{rank})")

            sections.append("")

        # 新话题
        if result.new_topics:
            sections.append("### 🆕 新出现话题")
            sections.append("")

            for title in result.new_topics[:10]:  # 只显示前10个
                sections.append(f"- {title}")

            sections.append("")

        if not sections:
            return ""

        return "## 📊 趋势分析\n\n" + "\n".join(sections)

    def _generate_ai_insights(self, insight: AIInsight) -> str:
        """生成AI洞察部分"""
        sections = []

        # 用户行为洞察
        if insight.user_behavior:
            sections.append("### 👥 用户行为洞察")
            sections.append("")
            for item in insight.user_behavior:
                sections.append(f"- {item}")
            sections.append("")

        # 趋势预测
        if insight.trend_predictions:
            sections.append("### 🔮 趋势预测")
            sections.append("")
            for item in insight.trend_predictions:
                sections.append(f"- {item}")
            sections.append("")

        # 创作者建议
        if insight.creator_tips:
            sections.append("### 💡 创作者建议")
            sections.append("")
            for item in insight.creator_tips:
                sections.append(f"- {item}")
            sections.append("")

        # 平台洞察
        if insight.platform_insights:
            sections.append("### 🎯 平台洞察")
            sections.append("")
            for item in insight.platform_insights:
                sections.append(f"- {item}")
            sections.append("")

        if not sections:
            return ""

        return "## 🤖 AI洞察\n\n" + "\n".join(sections)

    def _generate_footer(self, result: TopicAnalysisResult) -> str:
        """生成页脚"""
        return f"""---

**报告说明**:
- 本报告基于新榜小红书热门话题榜单数据自动生成
- 分析日期: {result.date}
- 数据更新频率: 每日
- AI引擎: Google Gemini 2.5 Pro

**声明**:
- 本报告仅供研究学习使用，不构成任何投资建议
- 数据来源于公开平台，分析结果仅代表算法观点
- 如有疑问或建议，欢迎反馈

---

*自动生成于 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

    @staticmethod
    def _format_number(num: int) -> str:
        """
        格式化数字（万、亿）

        Args:
            num: 数字

        Returns:
            格式化后的字符串
        """
        if num >= 100_000_000:
            return f"{num / 100_000_000:.1f}亿"
        elif num >= 10_000:
            return f"{num / 10_000:.1f}万"
        else:
            return str(num)


# 示例用法
if __name__ == "__main__":
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
    ]

    test_result = TopicAnalysisResult(
        date="2026-01-15",
        total_topics=50,
        total_heat=50000000,
        top_keywords=["春节", "旅游", "年货", "美食", "攻略"],
        category_stats={
            "旅游": {"count": 15, "total_heat": 20000000},
            "美食": {"count": 12, "total_heat": 15000000},
            "时尚": {"count": 10, "total_heat": 8000000},
        },
        top_topics=test_topics,
        rising_topics=[
            {"title": "春节出游攻略", "rank": 1, "rank_change": 2},
        ],
        new_topics=["春节礼盒推荐", "年味装饰DIY"],
    )

    test_insight = AIInsight(
        user_behavior=[
            "用户对春节相关内容关注度显著上升，特别是旅游和年货类别",
            "短视频形式的攻略类内容互动率提升30%",
        ],
        trend_predictions=[
            "预计未来一周，春节旅游相关话题将持续升温",
            "国潮元素结合传统文化的内容可能成为新热点",
        ],
        creator_tips=[
            "建议创作者提前布局春节相关内容，抓住流量红利期",
            "可以尝试结合地域特色和传统文化打造差异化内容",
        ],
        platform_insights=[
            "平台正在加大对传统文化内容的推荐权重",
            "图文+短视频混合形式的笔记获得更多曝光",
        ],
    )

    # 生成报告
    generator = ReportGenerator()
    report_content = generator.generate(
        analysis_result=test_result,
        ai_insight=test_insight,
        output_path=Path("test_report.md"),
    )

    print("✓ 测试报告已生成: test_report.md")
    print(f"  字符数: {len(report_content)}")
