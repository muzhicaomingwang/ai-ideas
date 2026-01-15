"""趋势分析器"""
from typing import Optional
from ..models.topic import XHSTopic
from ..utils.logger import get_logger

logger = get_logger()


class TrendAnalyzer:
    """趋势分析器 - 对比历史数据分析趋势"""

    def __init__(self):
        """初始化"""
        pass

    def analyze_trends(
        self, today_topics: list[XHSTopic], yesterday_topics: list[XHSTopic]
    ) -> dict:
        """
        分析趋势（对比昨日数据）

        Args:
            today_topics: 今日话题列表
            yesterday_topics: 昨日话题列表

        Returns:
            趋势分析结果字典
        """
        if not today_topics:
            logger.warning("今日话题列表为空")
            return self._empty_trend_result()

        if not yesterday_topics:
            logger.info("无昨日数据，所有话题标记为新话题")
            return {
                "rising_topics": [],
                "falling_topics": [],
                "new_topics": [t.title for t in today_topics[:10]],
                "disappeared_topics": [],
                "stable_topics": [],
            }

        logger.info("开始趋势分析...")

        # 构建昨日数据字典（标题 -> 话题）
        yesterday_map = {t.title: t for t in yesterday_topics}
        today_set = {t.title for t in today_topics}
        yesterday_set = {t.title for t in yesterday_topics}

        rising_topics = []
        falling_topics = []
        stable_topics = []
        new_topics = []

        # 分析今日话题
        for topic in today_topics:
            if topic.title in yesterday_map:
                yesterday_topic = yesterday_map[topic.title]

                # 计算热度变化
                heat_change = topic.heat_score - yesterday_topic.heat_score
                heat_change_percent = (
                    (heat_change / yesterday_topic.heat_score) * 100
                    if yesterday_topic.heat_score > 0
                    else 0
                )

                # 计算排名变化（排名下降=数值上升=变好）
                rank_change = yesterday_topic.rank - topic.rank

                topic_info = {
                    "title": topic.title,
                    "today_rank": topic.rank,
                    "yesterday_rank": yesterday_topic.rank,
                    "rank_change": rank_change,
                    "today_heat": topic.heat_score,
                    "yesterday_heat": yesterday_topic.heat_score,
                    "heat_change": heat_change,
                    "heat_change_percent": round(heat_change_percent, 1),
                    "category": topic.category,
                }

                # 分类
                if heat_change > 10000:  # 热度增长1万+
                    rising_topics.append(topic_info)
                elif heat_change < -10000:  # 热度下降1万+
                    falling_topics.append(topic_info)
                else:
                    stable_topics.append(topic_info)
            else:
                # 新出现的话题
                new_topics.append(topic.title)

        # 找出消失的话题
        disappeared_topics = list(yesterday_set - today_set)

        # 排序
        rising_topics = sorted(
            rising_topics, key=lambda x: x["heat_change"], reverse=True
        )[:10]
        falling_topics = sorted(falling_topics, key=lambda x: x["heat_change"])[:10]

        logger.info(f"  热度上升: {len(rising_topics)}个")
        logger.info(f"  热度下降: {len(falling_topics)}个")
        logger.info(f"  新出现: {len(new_topics)}个")
        logger.info(f"  消失: {len(disappeared_topics)}个")
        logger.info(f"  稳定: {len(stable_topics)}个")

        return {
            "rising_topics": rising_topics,
            "falling_topics": falling_topics,
            "new_topics": new_topics[:10],  # 只返回前10个
            "disappeared_topics": disappeared_topics[:10],
            "stable_topics": stable_topics[:5],  # 稳定话题返回少一些
        }

    def _empty_trend_result(self) -> dict:
        """返回空趋势结果"""
        return {
            "rising_topics": [],
            "falling_topics": [],
            "new_topics": [],
            "disappeared_topics": [],
            "stable_topics": [],
        }

    def generate_trend_summary(self, trends: dict) -> str:
        """
        生成趋势摘要文本

        Args:
            trends: 趋势分析结果

        Returns:
            摘要文本
        """
        lines = []

        # 热度上升
        if trends["rising_topics"]:
            lines.append("【热度上升】")
            for item in trends["rising_topics"][:5]:
                lines.append(
                    f"- {item['title']}: {item['heat_change_percent']:+.1f}% "
                    f"(排名 {item['yesterday_rank']}→{item['today_rank']})"
                )

        # 新话题
        if trends["new_topics"]:
            lines.append("\n【新出现话题】")
            for title in trends["new_topics"][:5]:
                lines.append(f"- {title}")

        # 消失话题
        if trends["disappeared_topics"]:
            lines.append("\n【消失话题】")
            for title in trends["disappeared_topics"][:3]:
                lines.append(f"- {title}")

        return "\n".join(lines) if lines else "暂无显著趋势变化"
