"""话题分析器"""
from collections import Counter
from typing import Optional
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer

from ..models.topic import XHSTopic, TopicAnalysisResult
from ..utils.logger import get_logger

logger = get_logger()


class TopicAnalyzer:
    """话题数据分析器"""

    def __init__(self):
        """初始化"""
        # 加载jieba词典（可选：添加自定义词典）
        jieba.setLogLevel(20)  # 降低日志级别

    def analyze(self, topics: list[XHSTopic], date: str) -> TopicAnalysisResult:
        """
        分析话题数据

        Args:
            topics: 话题列表
            date: 分析日期

        Returns:
            分析结果
        """
        logger.info("开始话题分析...")

        if not topics:
            logger.warning("话题列表为空，返回空分析结果")
            return TopicAnalysisResult(
                date=date, total_topics=0, total_heat=0
            )

        # 1. 热词提取
        top_keywords = self._extract_keywords(topics, top_n=20)
        logger.info(f"  提取热词: {len(top_keywords)}个")

        # 2. 分类统计
        category_stats = self._analyze_categories(topics)
        logger.info(f"  分类统计: {len(category_stats)}个分类")

        # 3. 计算总热度
        total_heat = sum(t.heat_score for t in topics)

        # 4. 构建结果
        result = TopicAnalysisResult(
            date=date,
            total_topics=len(topics),
            total_heat=total_heat,
            top_keywords=top_keywords,
            category_stats=category_stats,
            top_topics=topics[:10],  # Top 10
        )

        logger.info("话题分析完成")
        return result

    def _extract_keywords(
        self, topics: list[XHSTopic], top_n: int = 20
    ) -> list[str]:
        """
        提取热词（基于TF-IDF）

        Args:
            topics: 话题列表
            top_n: 返回前N个热词

        Returns:
            热词列表
        """
        if not topics:
            return []

        # 合并所有标题
        texts = [t.title for t in topics if t.title]

        if not texts:
            return []

        # 中文分词
        tokenized_texts = []
        for text in texts:
            # 分词
            words = jieba.cut(text)
            # 过滤停用词和单字
            filtered_words = [w for w in words if len(w) > 1 and w.strip()]
            tokenized_texts.append(" ".join(filtered_words))

        if not tokenized_texts:
            return []

        # TF-IDF提取
        try:
            vectorizer = TfidfVectorizer(max_features=top_n)
            vectorizer.fit(tokenized_texts)
            keywords = vectorizer.get_feature_names_out().tolist()
            return keywords
        except Exception as e:
            logger.warning(f"TF-IDF提取失败: {e}")
            # 回退到简单词频统计
            return self._fallback_keyword_extraction(tokenized_texts, top_n)

    def _fallback_keyword_extraction(
        self, tokenized_texts: list[str], top_n: int
    ) -> list[str]:
        """
        回退方案：简单词频统计

        Args:
            tokenized_texts: 已分词的文本列表
            top_n: 返回前N个

        Returns:
            高频词列表
        """
        all_words = []
        for text in tokenized_texts:
            all_words.extend(text.split())

        word_counts = Counter(all_words)
        top_words = [word for word, _ in word_counts.most_common(top_n)]
        return top_words

    def _analyze_categories(self, topics: list[XHSTopic]) -> dict[str, dict]:
        """
        分析分类统计

        Args:
            topics: 话题列表

        Returns:
            分类统计字典，格式:
            {
                "美妆": {
                    "count": 12,
                    "avg_heat": 45000,
                    "total_heat": 540000,
                    "top_topic": "早八人的护肤routine",
                    "percentage": 24.0
                }
            }
        """
        if not topics:
            return {}

        # 按分类分组
        category_topics = {}
        for topic in topics:
            cat = topic.category or "未分类"
            if cat not in category_topics:
                category_topics[cat] = []
            category_topics[cat].append(topic)

        # 计算统计信息
        total_topics = len(topics)
        total_heat = sum(t.heat_score for t in topics)

        stats = {}
        for cat, topic_list in category_topics.items():
            cat_heat = sum(t.heat_score for t in topic_list)
            stats[cat] = {
                "count": len(topic_list),
                "avg_heat": int(cat_heat / len(topic_list)) if topic_list else 0,
                "total_heat": cat_heat,
                "top_topic": topic_list[0].title if topic_list else "",
                "percentage": round((len(topic_list) / total_topics) * 100, 1),
                "heat_percentage": round((cat_heat / total_heat) * 100, 1) if total_heat > 0 else 0,
            }

        # 按话题数量降序排序
        sorted_stats = dict(
            sorted(stats.items(), key=lambda x: x[1]["count"], reverse=True)
        )

        return sorted_stats
