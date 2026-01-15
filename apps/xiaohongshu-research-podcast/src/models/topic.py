"""小红书话题数据模型"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class XHSTopic(BaseModel):
    """小红书话题数据模型"""

    topic_id: str = Field(..., description="话题唯一标识")
    title: str = Field(..., description="话题标题")
    description: str = Field(default="", description="话题描述")

    # 数据指标
    heat_score: int = Field(default=0, description="热度值")
    read_count: int = Field(default=0, description="阅读量")
    note_count: int = Field(default=0, description="笔记数量")
    interaction_count: int = Field(default=0, description="互动量")

    # 分类信息
    category: str = Field(default="未分类", description="话题分类")
    tags: list[str] = Field(default_factory=list, description="相关标签")

    # 排名信息
    rank: int = Field(default=0, description="当前排名（1-based）")
    rank_change: int = Field(default=0, description="排名变化（正数=上升）")
    rank_change_percent: Optional[float] = Field(default=None, description="排名变化百分比")

    # 趋势信息
    trend_direction: str = Field(
        default="stable", description="趋势方向（up/down/stable/new）"
    )
    trend_icon: str = Field(default="→", description="趋势图标（↑/↓/→/🆕）")

    # 时间信息
    crawled_at: datetime = Field(
        default_factory=datetime.now, description="抓取时间"
    )
    updated_at: Optional[datetime] = Field(default=None, description="话题更新时间")

    # 链接
    url: Optional[str] = Field(default=None, description="话题详情页URL")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    def to_dict(self) -> dict:
        """转换为字典"""
        return self.model_dump(mode="json")

    @property
    def heat_score_formatted(self) -> str:
        """格式化热度值（万、亿）"""
        if self.heat_score >= 100_000_000:
            return f"{self.heat_score / 100_000_000:.1f}亿"
        elif self.heat_score >= 10_000:
            return f"{self.heat_score / 10_000:.1f}万"
        else:
            return str(self.heat_score)

    @property
    def rank_change_text(self) -> str:
        """排名变化文本"""
        if self.rank_change > 0:
            return f"↑{self.rank_change}"
        elif self.rank_change < 0:
            return f"↓{abs(self.rank_change)}"
        else:
            return "-"


class TopicAnalysisResult(BaseModel):
    """话题分析结果"""

    date: str = Field(..., description="分析日期")
    total_topics: int = Field(..., description="话题总数")
    total_heat: int = Field(..., description="总热度")

    # 热词分析
    top_keywords: list[str] = Field(default_factory=list, description="Top热词")

    # 分类统计
    category_stats: dict[str, dict] = Field(
        default_factory=dict, description="分类统计信息"
    )

    # Top话题
    top_topics: list[XHSTopic] = Field(default_factory=list, description="Top话题列表")

    # 趋势数据
    rising_topics: list[dict] = Field(default_factory=list, description="热度上升话题")
    new_topics: list[str] = Field(default_factory=list, description="新出现话题")

    def to_dict(self) -> dict:
        """转换为字典"""
        return self.model_dump(mode="json")


class AIInsight(BaseModel):
    """AI生成的洞察"""

    # 用户行为洞察
    user_behavior: list[str] = Field(
        default_factory=list, description="用户行为模式洞察"
    )

    # 趋势预测
    trend_predictions: list[str] = Field(default_factory=list, description="未来趋势预测")

    # 创作者建议
    creator_tips: list[str] = Field(default_factory=list, description="给创作者的建议")

    # 其他洞察
    platform_insights: list[str] = Field(
        default_factory=list, description="平台层面的洞察"
    )

    def to_dict(self) -> dict:
        """转换为字典"""
        return self.model_dump(mode="json")
