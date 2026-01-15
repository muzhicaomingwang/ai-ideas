# Markdown报告生成器使用说明

## 功能概述

`ReportGenerator` 用于将小红书热门话题分析结果转换为结构化的Markdown研究报告。

## 数据输入

报告生成器接收以下数据：

1. **TopicAnalysisResult** (必需)
   - 话题分析结果
   - 包含热词、分类统计、Top话题等

2. **AIInsight** (可选)
   - AI生成的深度洞察
   - 包含用户行为、趋势预测、创作者建议

## 使用示例

```python
from pathlib import Path
from generators.report_generator import ReportGenerator
from models.topic import TopicAnalysisResult, AIInsight

# 创建生成器
generator = ReportGenerator()

# 生成报告
report_content = generator.generate(
    analysis_result=analysis_result,  # TopicAnalysisResult对象
    ai_insight=ai_insight,             # AIInsight对象（可选）
    output_path=Path("output/2026-01-15/report.md")  # 输出路径（可选）
)

print(f"报告已生成，字符数: {len(report_content)}")
```

## 报告结构

生成的报告包含以下章节：

### 1. 报告头部
- 标题
- 日期
- 生成时间
- 数据来源

### 2. 数据摘要
- 话题总数
- 总热度
- 平均热度
- 分类数

### 3. Top话题榜单
表格展示Top 10话题：
- 排名
- 话题标题
- 热度值
- 阅读量
- 笔记数
- 趋势变化

### 4. 热词分析
提取的关键词（每行5个）

### 5. 分类统计
表格展示各分类数据：
- 话题数
- 总热度
- 平均热度
- 占比

### 6. 趋势分析（如有数据）
- 热度上升话题（Top 10）
- 新出现话题（Top 10）

### 7. AI洞察（如提供）
- 用户行为洞察
- 趋势预测
- 创作者建议
- 平台洞察

### 8. 页脚
- 报告说明
- 声明
- 生成时间戳

## 输出示例

```markdown
# 小红书热门话题研究报告

**日期**: 2026-01-15
**生成时间**: 2026-01-15 19:45:00
**数据来源**: 新榜小红书热门话题榜单

---

## 📊 数据摘要

- **话题总数**: 50
- **总热度**: 5000.0万
- **平均热度**: 100.0万
- **分类数**: 5

## 🔥 Top话题榜单

| 排名 | 话题标题 | 热度值 | 阅读量 | 笔记数 | 趋势 |
|------|----------|--------|--------|--------|------|
| 1 | 春节出游攻略 | 150.0万 | 5000.0万 | 2.0万 | ↑ ↑2 |
| 2 | 年货清单推荐 | 120.0万 | 4000.0万 | 1.8万 | ↓ ↓1 |
...
```

## 数字格式化

报告会自动格式化大数字：
- `>= 1亿`: 显示为 "1.5亿"
- `>= 1万`: 显示为 "150.0万"
- `< 1万`: 显示原数字

## 集成到主流程

在 `scripts/daily_generate.py` 中调用：

```python
from generators.report_generator import ReportGenerator

# 生成分析结果后
analysis_result = analyzer.analyze(topics, date_str)
ai_insight = insight_generator.generate(analysis_result)

# 生成报告
report_generator = ReportGenerator()
report_path = output_dir / f"report-{date_str}.md"
report_generator.generate(
    analysis_result=analysis_result,
    ai_insight=ai_insight,
    output_path=report_path
)
```

## 自定义扩展

如需添加新的报告章节，可以：

1. 在 `ReportGenerator` 类中添加新的 `_generate_xxx()` 方法
2. 在 `generate()` 方法中调用该方法
3. 确保返回Markdown格式的字符串

示例：

```python
def _generate_custom_section(self, result: TopicAnalysisResult) -> str:
    """生成自定义章节"""
    return """## 🎯 自定义分析

- 自定义内容1
- 自定义内容2

"""
```

## 注意事项

- 报告使用UTF-8编码保存
- 数字格式化遵循中文习惯（万、亿）
- 表格自动对齐，便于阅读
- 生成时间使用本地时区

## 测试

运行测试脚本验证：

```bash
python3 test_report_generator.py
```

输出文件: `output/test/test_report.md`
