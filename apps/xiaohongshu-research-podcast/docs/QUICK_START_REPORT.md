# Markdown报告生成快速指南

## 一分钟快速体验

### 1. 查看示例报告

已生成的示例报告：
```bash
cat output/example-report-2026-01-15.md
```

### 2. 运行示例生成器

```bash
cd xiaohongshu-research-podcast

# 方式1：如果Poetry环境配置好
poetry run python examples/generate_complete_report.py

# 方式2：直接运行（需要安装依赖）
python3 examples/generate_complete_report.py
```

输出文件: `output/example/report-{日期}.md`

## 报告内容结构

生成的报告包含7个主要部分：

```
1. 📄 报告头部
   - 日期、生成时间、数据来源

2. 📊 数据摘要
   - 话题总数、总热度、平均热度、分类数

3. 🔥 Top话题榜单（表格）
   - 排名、标题、热度、阅读量、笔记数、趋势

4. 🏷️ 热词分析
   - 提取的关键词（每行5个）

5. 📂 分类统计（表格）
   - 各分类的话题数、热度、占比

6. 📊 趋势分析
   - 热度上升话题（Top 10）
   - 新出现话题（Top 10）

7. 🤖 AI洞察（如提供）
   - 用户行为洞察
   - 趋势预测
   - 创作者建议
   - 平台洞察
```

## API使用

### 基础用法

```python
from generators.report_generator import ReportGenerator
from models.topic import TopicAnalysisResult, AIInsight

# 创建生成器
generator = ReportGenerator()

# 生成报告（仅必需参数）
report = generator.generate(
    analysis_result=your_analysis_result
)
```

### 完整用法

```python
from pathlib import Path

# 生成报告并保存
report = generator.generate(
    analysis_result=your_analysis_result,  # 必需
    ai_insight=your_ai_insight,           # 可选
    output_path=Path("output/report.md")   # 可选
)

# report 包含完整的Markdown文本
print(f"报告字符数: {len(report)}")
```

## 数据格式要求

### TopicAnalysisResult

```python
TopicAnalysisResult(
    date="2026-01-15",              # 分析日期
    total_topics=50,                 # 话题总数
    total_heat=50000000,             # 总热度
    top_keywords=["春节", "旅游"],   # 热词列表
    category_stats={                 # 分类统计
        "旅游": {
            "count": 15,
            "total_heat": 20000000
        }
    },
    top_topics=[...],                # XHSTopic对象列表
    rising_topics=[...],             # 上升话题（可选）
    new_topics=[...]                 # 新话题（可选）
)
```

### AIInsight

```python
AIInsight(
    user_behavior=["洞察1", "洞察2"],        # 用户行为洞察
    trend_predictions=["预测1", "预测2"],    # 趋势预测
    creator_tips=["建议1", "建议2"],         # 创作者建议
    platform_insights=["洞察1", "洞察2"]     # 平台洞察
)
```

## 集成到主流程

在 `scripts/daily_generate.py` 中：

```python
# Step 1: 数据抓取
topics = scraper.fetch_topics()

# Step 2: 数据分析
analyzer = TopicAnalyzer()
analysis_result = analyzer.analyze(topics, date_str)

# Step 3: AI洞察（可选）
insight_generator = InsightGenerator()
ai_insight = insight_generator.generate(analysis_result)

# Step 4: 生成报告
report_generator = ReportGenerator()
report_path = output_dir / f"report-{date_str}.md"
report_generator.generate(
    analysis_result=analysis_result,
    ai_insight=ai_insight,
    output_path=report_path
)
```

## 自定义报告

### 修改报告章节

编辑 `src/generators/report_generator.py`:

```python
def generate(self, ...):
    """生成报告"""
    report = []

    # 添加/删除/重排章节
    report.append(self._generate_header(...))
    report.append(self._generate_summary(...))
    report.append(self._generate_custom_section(...))  # 新增
    # ...

    return "\n".join(report)
```

### 修改数字格式

修改 `_format_number()` 方法：

```python
@staticmethod
def _format_number(num: int) -> str:
    if num >= 100_000_000:
        return f"{num / 100_000_000:.2f}亿"  # 保留2位小数
    # ...
```

## 输出示例

查看生成的示例报告：
- `output/example-report-2026-01-15.md` - 手动创建的示例
- `output/example/report-{日期}.md` - 脚本生成的示例

## 故障排查

### 问题1：导入失败

```
ModuleNotFoundError: No module named 'pydantic'
```

**解决**: 安装依赖
```bash
poetry install
# 或
pip3 install pydantic
```

### 问题2：相对导入错误

```
ImportError: attempted relative import with no known parent package
```

**解决**: 使用正确的入口脚本（添加 `sys.path`）

### 问题3：输出目录不存在

报告生成器会自动创建目录，无需手动创建。

## 下一步

- 查看详细文档: `docs/REPORT_GENERATOR.md`
- 查看完整实现: `src/generators/report_generator.py`
- 运行示例: `examples/generate_complete_report.py`
