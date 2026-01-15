"""
产品创意数据模型

用于每日创意生成任务的数据结构定义
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ProductIdea(BaseModel):
    """产品创意模型"""

    id: str = Field(..., description="创意ID（ULID格式，前缀 idea_）")
    title: str = Field(..., description="创意标题（建议10字以内）")
    category: Literal["feature", "performance", "ux", "architecture", "security"] = Field(
        ..., description="创意分类"
    )
    description: str = Field(..., description="详细描述（100-200字，包含背景、方案、实现要点）")
    priority: Literal["P0", "P1", "P2", "P3"] = Field(..., description="优先级（P0最高）")
    estimated_effort: Literal["S", "M", "L", "XL"] = Field(
        ..., description="工作量估算（S=1-2天，M=3-5天，L=1-2周，XL=2周+）"
    )
    expected_impact: str = Field(..., description="预期收益（量化指标或用户价值）")
    context: str = Field(default="", description="上下文/背景（为什么现在提这个创意）")
    generated_at: datetime = Field(default_factory=datetime.now, description="生成时间")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "idea_01kf7x8j9k2m3n4p5q6r7s8t9u",
                "title": "方案对比智能排序",
                "category": "ux",
                "description": "当前方案对比页按 budget/standard/premium 固定顺序展示。建议根据用户偏好智能排序...",
                "priority": "P1",
                "estimated_effort": "M",
                "expected_impact": "提升方案点击率15%，减少用户比较时长20%",
                "context": "根据 QA 报告，用户在对比页平均停留40秒，存在选择困难",
                "generated_at": "2026-01-15T10:00:00",
            }
        }


class DailyIdeaBatch(BaseModel):
    """每日创意批次"""

    date: str = Field(..., description="日期 YYYY-MM-DD")
    ideas: list[ProductIdea] = Field(..., min_length=5, max_length=5, description="创意列表（恒定5个）")
    metadata: dict = Field(
        default_factory=dict,
        description="元数据（生成时间、上下文来源等）",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2026-01-15",
                "ideas": [],  # 5个 ProductIdea 对象
                "metadata": {
                    "context_sources": ["git_commits", "prd", "design_docs", "historical_ideas"],
                    "generated_at": "2026-01-15T10:00:00",
                },
            }
        }
