"""
创意生成器测试

测试每日创意生成功能的核心逻辑
"""
from __future__ import annotations

import pytest
from pathlib import Path

from src.services.idea_generator import DailyIdeaGenerator
from src.models.idea import ProductIdea, DailyIdeaBatch


@pytest.mark.asyncio
async def test_generate_daily_ideas():
    """测试创意生成完整流程"""
    generator = DailyIdeaGenerator()
    batch = await generator.generate_daily_ideas()

    # 验证批次结构
    assert isinstance(batch, DailyIdeaBatch)
    assert batch.date is not None
    assert len(batch.ideas) == 5

    # 验证每个创意
    for idea in batch.ideas:
        assert isinstance(idea, ProductIdea)
        assert idea.id.startswith("idea_")
        assert idea.title
        assert idea.category in ["feature", "performance", "ux", "architecture", "security"]
        assert idea.priority in ["P0", "P1", "P2", "P3"]
        assert idea.estimated_effort in ["S", "M", "L", "XL"]
        assert idea.description
        assert idea.expected_impact


@pytest.mark.asyncio
async def test_context_collection():
    """测试上下文收集"""
    generator = DailyIdeaGenerator()
    context = await generator._collect_context()

    # 验证上下文包含必要字段
    assert "recent_changes" in context
    assert "prd_summary" in context
    assert "design_summary" in context
    assert "historical_ideas" in context
    assert "code_stats" in context
    assert "metadata" in context

    # 验证元数据
    metadata = context["metadata"]
    assert "context_sources" in metadata
    assert "generated_at" in metadata


def test_extract_idea_titles():
    """测试从 Markdown 提取创意标题"""
    generator = DailyIdeaGenerator()

    markdown_content = """
# TeamVenture 每日创意 - 2026-01-15

## 🚀 功能增强

### 方案对比智能排序

**优先级**: P1

### 新增活动类型

**优先级**: P2
"""

    titles = generator._extract_idea_titles(markdown_content)

    assert len(titles) == 2
    assert "方案对比智能排序" in titles
    assert "新增活动类型" in titles


def test_analyze_code_quality():
    """测试代码质量分析"""
    generator = DailyIdeaGenerator()
    stats = generator._analyze_code_quality()

    # 验证返回的统计字段
    assert isinstance(stats, dict)

    # 如果成功（无错误），应包含统计字段
    if "error" not in stats:
        assert "total_todos" in stats
        assert "total_fixmes" in stats
        assert isinstance(stats["total_todos"], int)
        assert isinstance(stats["total_fixmes"], int)


def test_build_prompt():
    """测试 Prompt 构建"""
    generator = DailyIdeaGenerator()

    mock_context = {
        "recent_changes": "最近无代码变更",
        "prd_summary": "PRD 摘要内容...",
        "design_summary": "设计文档摘要...",
        "qa_summary": "QA 报告摘要...",
        "historical_ideas": "（暂无历史创意）",
        "code_stats": {"total_todos": 5, "total_fixmes": 2},
        "metadata": {},
    }

    prompt = generator._build_prompt(mock_context)

    # 验证 Prompt 包含关键元素
    assert "TeamVenture" in prompt
    assert "5个高质量的功能改进创意" in prompt
    assert "feature|performance|ux|architecture|security" in prompt
    assert "P0|P1|P2|P3" in prompt
    assert mock_context["recent_changes"] in prompt
    assert mock_context["prd_summary"] in prompt


@pytest.mark.asyncio
async def test_parse_ideas():
    """测试创意解析"""
    generator = DailyIdeaGenerator()

    # Mock OpenAI 响应
    raw_response = {
        "ideas": [
            {
                "title": "测试创意1",
                "category": "feature",
                "description": "这是一个测试创意的详细描述",
                "priority": "P0",
                "estimated_effort": "S",
                "expected_impact": "提升10%",
                "context": "基于测试需求",
            },
            {
                "title": "测试创意2",
                "category": "performance",
                "description": "性能优化测试",
                "priority": "P1",
                "estimated_effort": "M",
                "expected_impact": "减少响应时间50%",
                "context": "性能测试发现",
            },
            {
                "title": "测试创意3",
                "category": "ux",
                "description": "用户体验改进",
                "priority": "P1",
                "estimated_effort": "M",
                "expected_impact": "提升满意度15%",
                "context": "用户反馈",
            },
            {
                "title": "测试创意4",
                "category": "architecture",
                "description": "架构重构",
                "priority": "P2",
                "estimated_effort": "L",
                "expected_impact": "降低维护成本",
                "context": "技术债务清理",
            },
            {
                "title": "测试创意5",
                "category": "security",
                "description": "安全加固",
                "priority": "P2",
                "estimated_effort": "S",
                "expected_impact": "消除安全隐患",
                "context": "安全审计",
            },
        ]
    }

    ideas = generator._parse_ideas(raw_response)

    assert len(ideas) == 5
    assert all(isinstance(idea, ProductIdea) for idea in ideas)
    assert ideas[0].title == "测试创意1"
    assert ideas[0].category == "feature"


@pytest.mark.asyncio
async def test_parse_ideas_invalid_count():
    """测试创意数量错误时的异常处理"""
    generator = DailyIdeaGenerator()

    # 只有4个创意（应该是5个）
    invalid_response = {
        "ideas": [
            {
                "title": "创意1",
                "category": "feature",
                "description": "描述",
                "priority": "P0",
                "estimated_effort": "S",
                "expected_impact": "收益",
                "context": "上下文",
            },
            # ... 只有4个
        ]
        * 4
    }

    with pytest.raises(ValueError, match="Expected 5 ideas"):
        generator._parse_ideas(invalid_response)
