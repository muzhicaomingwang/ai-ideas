"""数据缓存管理"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from ..models.topic import XHSTopic, TopicAnalysisResult, AIInsight


class CacheManager:
    """数据缓存管理器"""

    def __init__(self, cache_dir: str = "cache"):
        """
        初始化

        Args:
            cache_dir: 缓存目录路径
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def save_topics(self, topics: list[XHSTopic], date: str):
        """
        保存话题数据到缓存

        Args:
            topics: 话题列表
            date: 日期字符串（YYYY-MM-DD）
        """
        cache_file = self.cache_dir / f"{date}-raw-data.json"

        data = {
            "date": date,
            "crawled_at": datetime.now().isoformat(),
            "total_topics": len(topics),
            "topics": [topic.to_dict() for topic in topics],
        }

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_topics(self, date: str) -> list[XHSTopic]:
        """
        从缓存加载话题数据

        Args:
            date: 日期字符串（YYYY-MM-DD）

        Returns:
            话题列表，不存在则返回空列表
        """
        cache_file = self.cache_dir / f"{date}-raw-data.json"

        if not cache_file.exists():
            return []

        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [XHSTopic(**topic) for topic in data["topics"]]

    def save_analysis(self, analysis: TopicAnalysisResult, date: str):
        """
        保存分析结果

        Args:
            analysis: 分析结果
            date: 日期字符串
        """
        cache_file = self.cache_dir / f"{date}-analysis.json"

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(analysis.to_dict(), f, ensure_ascii=False, indent=2)

    def load_analysis(self, date: str) -> Optional[TopicAnalysisResult]:
        """
        加载分析结果

        Args:
            date: 日期字符串

        Returns:
            分析结果，不存在则返回None
        """
        cache_file = self.cache_dir / f"{date}-analysis.json"

        if not cache_file.exists():
            return None

        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return TopicAnalysisResult(**data)

    def save_insights(self, insights: AIInsight, date: str):
        """
        保存AI洞察

        Args:
            insights: AI洞察
            date: 日期字符串
        """
        cache_file = self.cache_dir / f"{date}-insights.json"

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(insights.to_dict(), f, ensure_ascii=False, indent=2)

    def load_insights(self, date: str) -> Optional[AIInsight]:
        """
        加载AI洞察

        Args:
            date: 日期字符串

        Returns:
            AI洞察，不存在则返回None
        """
        cache_file = self.cache_dir / f"{date}-insights.json"

        if not cache_file.exists():
            return None

        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return AIInsight(**data)

    def has_cache(self, date: str, cache_type: str = "raw-data") -> bool:
        """
        检查缓存是否存在

        Args:
            date: 日期字符串
            cache_type: 缓存类型（raw-data/analysis/insights）

        Returns:
            是否存在
        """
        cache_file = self.cache_dir / f"{date}-{cache_type}.json"
        return cache_file.exists()

    def get_cache_age(self, date: str, cache_type: str = "raw-data") -> Optional[int]:
        """
        获取缓存年龄（小时）

        Args:
            date: 日期字符串
            cache_type: 缓存类型

        Returns:
            缓存年龄（小时），不存在则返回None
        """
        cache_file = self.cache_dir / f"{date}-{cache_type}.json"

        if not cache_file.exists():
            return None

        mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        age = datetime.now() - mtime
        return int(age.total_seconds() / 3600)

    def clean_old_cache(self, days: int = 7):
        """
        清理旧缓存文件

        Args:
            days: 保留最近N天的缓存
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        for cache_file in self.cache_dir.glob("*.json"):
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if mtime < cutoff_date:
                cache_file.unlink()
                print(f"Deleted old cache: {cache_file.name}")
