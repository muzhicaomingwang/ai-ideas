"""
小红书热点指南生成器
基于每日科技新闻，为小红书创作者提供蹭点建议和文案模板
"""

import json
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from anthropic import Anthropic

# 导入 Article 数据类
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from news_sources.rss_fetcher import Article


@dataclass
class TitleTemplate:
    """标题模板"""
    text: str                    # 标题文案（20-30字）
    style: str                   # 风格："第一人称"/"悬念式"/"数字式"
    target_audience: str         # 目标受众
    emoji_suggestion: str        # 表情符号建议


@dataclass
class ContentAngle:
    """内容角度建议"""
    angle: str                   # 角度名称（如"效率革命指南"）
    why_works: str              # 为什么有效（用户痛点）
    example_outline: str        # 内容大纲示例


@dataclass
class XiaohongshuHotspotGuide:
    """单条热点的完整创作指南"""

    # 原始新闻
    original_title: str
    original_summary: str
    source: str
    category: str
    published: Optional[str]
    link: str

    # 适配度评估
    adaptation_score: int        # 1-5星
    adaptation_reason: str       # 适配理由
    target_demographics: List[str]  # 目标人群

    # 创作资源
    title_templates: List[TitleTemplate]
    content_angles: List[ContentAngle]
    hashtag_suggestions: List[str]
    image_suggestions: str

    # 风险提示
    risk_warning: Optional[str] = None


@dataclass
class XiaohongshuGuideDocument:
    """完整指南文档"""
    date: str
    total_hotspots: int

    # 按适配度分组
    high_priority: List[XiaohongshuHotspotGuide] = field(default_factory=list)  # 4-5星
    medium_priority: List[XiaohongshuHotspotGuide] = field(default_factory=list)  # 3星
    low_priority: List[XiaohongshuHotspotGuide] = field(default_factory=list)  # 1-2星

    # 趋势分析
    trend_summary: str = ""
    hot_keywords: List[str] = field(default_factory=list)

    def save_to_markdown(self, output_path: str) -> str:
        """保存为 Markdown 文件"""
        lines = []

        # === 头部 ===
        lines.append("# 📱 小红书热点蹭榜指南")
        lines.append("")
        lines.append(f"**日期**：{self.date}")
        lines.append(f"**热点总数**：{self.total_hotspots} 条")
        if self.hot_keywords:
            lines.append(f"**趋势关键词**：{', '.join(self.hot_keywords[:10])}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # === 趋势洞察 ===
        lines.append("## 🔥 今日趋势洞察")
        lines.append("")
        lines.append(self.trend_summary if self.trend_summary else "今日科技热点多元化，涵盖AI、消费、科技等多个领域。")
        lines.append("")
        if self.hot_keywords:
            lines.append(f"**高频关键词**：{', '.join(self.hot_keywords)}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # === 高适配度热点 ===
        if self.high_priority:
            lines.append("## ⭐️⭐️⭐️⭐️⭐️ 高适配度热点（必做！）")
            lines.append("")
            for i, guide in enumerate(self.high_priority, 1):
                lines.extend(self._render_hotspot(guide, i))

        # === 中等适配度热点 ===
        if self.medium_priority:
            lines.append("## ⭐️⭐️⭐️ 中等适配度热点（可选）")
            lines.append("")
            for i, guide in enumerate(self.medium_priority, 1):
                lines.extend(self._render_hotspot(guide, i))

        # === 低适配度热点 ===
        if self.low_priority:
            lines.append("## ⭐️⭐️ 低适配度热点（转化思路）")
            lines.append("")
            for i, guide in enumerate(self.low_priority, 1):
                lines.extend(self._render_hotspot(guide, i, show_conversion_tips=True))

        # === 附录 ===
        lines.append("---")
        lines.append("")
        lines.append("## 📊 附录：创作优先级建议")
        lines.append("")
        lines.append(f"**本周建议选题数量**：2-3条")
        lines.append("")

        if self.high_priority:
            lines.append("**优先级排序**：")
            for i, guide in enumerate(self.high_priority[:3], 1):
                lines.append(f"{i}. {guide.original_title[:40]}...（{guide.adaptation_score}星）")
            lines.append("")

        lines.append("**时效性提示**：")
        lines.append("- 消费类话题建议3天内发布（热度衰减快）")
        lines.append("- AI工具类可长期发布（常青内容）")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 获取所有来源
        all_guides = self.high_priority + self.medium_priority + self.low_priority
        sources = list(set(g.source for g in all_guides))
        if sources:
            lines.append(f"**数据来源**：{', '.join(sources)}")
        lines.append("")

        # 写入文件
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return str(output_file)

    def _render_hotspot(self, guide: XiaohongshuHotspotGuide, index: int,
                        show_conversion_tips: bool = False) -> List[str]:
        """渲染单条热点的 Markdown"""

        lines = []

        # 标题
        stars = "⭐️" * guide.adaptation_score
        lines.append(f"### {index}. {guide.original_title[:50]}... {stars}")
        lines.append("")

        # 元信息
        lines.append(f"**原标题**：{guide.original_title}")
        lines.append(f"**来源**：{guide.source} | **分类**：{guide.category}")
        lines.append(f"**适配理由**：{guide.adaptation_reason}")
        lines.append("")

        # 风险提示
        if guide.risk_warning:
            lines.append(f"⚠️ **风险提示**：{guide.risk_warning}")
            lines.append("")

        # 目标人群
        if guide.target_demographics:
            lines.append("#### 🎯 目标人群")
            for demo in guide.target_demographics:
                lines.append(f"- {demo}")
            lines.append("")

        # 标题模板
        if guide.title_templates:
            lines.append("#### 📝 标题模板（可直接套用）")
            lines.append("")
            for i, template in enumerate(guide.title_templates, 1):
                lines.append(f"{i}. **{template.text}**")
                lines.append(f"   风格：{template.style} | 受众：{template.target_audience} | 表情：{template.emoji_suggestion}")
                lines.append("")

        # 内容角度
        if guide.content_angles:
            lines.append("#### 💡 内容角度建议")
            lines.append("")
            for angle in guide.content_angles:
                lines.append(f"**{angle.angle}**")
                lines.append(f"✅ 为什么有效：{angle.why_works}")
                lines.append(f"📋 内容大纲：")
                for outline_item in angle.example_outline.split("\n"):
                    if outline_item.strip():
                        lines.append(f"   {outline_item.strip()}")
                lines.append("")

        # 话题标签
        if guide.hashtag_suggestions:
            lines.append("#### 🏷️ 话题标签")
            hashtags = " ".join([f"`#{tag}`" for tag in guide.hashtag_suggestions])
            lines.append(hashtags)
            lines.append("")

        # 配图建议
        if guide.image_suggestions:
            lines.append("#### 📸 配图建议")
            lines.append(guide.image_suggestions)
            lines.append("")

        # 转化思路（仅低适配度热点显示）
        if show_conversion_tips and guide.adaptation_score <= 2:
            lines.append("#### 🔄 转化思路")
            lines.append("")
            lines.append("这是一个低适配度话题，建议从以下角度转化：")
            lines.append("- 从B端视角 → C端视角（如：这个技术如何影响普通人生活）")
            lines.append("- 从宏观趋势 → 个人应用（如：趋势下的个人机会）")
            lines.append("- 从专业术语 → 生活场景（如：用比喻解释技术）")
            lines.append("")
            lines.append("**转化难度**：⭐️⭐️⭐️⭐️（需深度二创）")
            lines.append("**建议**：除非你是该垂直领域博主，否则不建议做")
            lines.append("")

        lines.append("---")
        lines.append("")

        return lines


class XiaohongshuGuideWriter:
    """小红书热点指南生成器"""

    def __init__(self, model_name: str = "claude-sonnet-4-20250514"):
        """初始化生成器"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "未设置 ANTHROPIC_API_KEY 环境变量。\n"
                "请在 .env 文件中配置: ANTHROPIC_API_KEY=your_key_here"
            )

        self.client = Anthropic(api_key=api_key)
        self.model = model_name

    def generate_guide(
        self,
        articles: List[Article],
        date: Optional[datetime] = None,
        batch_size: int = 10
    ) -> XiaohongshuGuideDocument:
        """
        生成小红书热点指南

        Args:
            articles: 新闻文章列表
            date: 日期
            batch_size: 每批处理的新闻数量（避免输出过长）

        Returns:
            完整的指南文档
        """
        if date is None:
            date = datetime.now()

        date_str = date.strftime("%Y-%m-%d")

        print(f"  🤖 正在使用 Claude ({self.model}) 生成小红书热点指南...")
        print(f"  📊 输入新闻总数: {len(articles)}")

        # 如果新闻数量超过 batch_size，分批处理
        all_guides = []
        total_input_tokens = 0
        total_output_tokens = 0

        num_batches = (len(articles) + batch_size - 1) // batch_size  # 向上取整

        for batch_idx in range(num_batches):
            start_idx = batch_idx * batch_size
            end_idx = min((batch_idx + 1) * batch_size, len(articles))
            batch_articles = articles[start_idx:end_idx]

            if num_batches > 1:
                print(f"  📦 处理批次 {batch_idx + 1}/{num_batches}（第 {start_idx + 1}-{end_idx} 条）")

            # 1. 构建 Prompt
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(batch_articles, date_str)

            # 2. 调用 Claude API
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=16384,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ],
                    system=system_prompt,
                    temperature=0.7
                )

                # 累计 token 消耗
                total_input_tokens += response.usage.input_tokens
                total_output_tokens += response.usage.output_tokens

                # 3. 解析 JSON
                raw_text = response.content[0].text.strip()
                guides_data = self._parse_json_response(raw_text)

                # 4. 转换为数据类
                batch_guides = self._convert_to_dataclasses(guides_data)
                all_guides.extend(batch_guides)

            except Exception as e:
                print(f"  ⚠️ 批次 {batch_idx + 1} 失败: {e}")
                # 继续处理下一批
                continue

        # 记录总 token 消耗和成本
        print(f"  💰 总 Token 消耗: 输入 {total_input_tokens}, 输出 {total_output_tokens}")
        input_cost = total_input_tokens / 1_000_000 * 3  # $3/M
        output_cost = total_output_tokens / 1_000_000 * 15  # $15/M
        total_cost = input_cost + output_cost
        print(f"  💵 总成本: ${total_cost:.4f} (¥{total_cost * 7:.2f})")

        # 5. 生成趋势洞察
        trend_summary, hot_keywords = self._generate_trend_insights(articles)

        # 6. 按适配度分组
        high = [g for g in all_guides if g.adaptation_score >= 4]
        medium = [g for g in all_guides if g.adaptation_score == 3]
        low = [g for g in all_guides if g.adaptation_score <= 2]

        print(f"  ✅ 生成完成: {len(high)}条高适配 | {len(medium)}条中等 | {len(low)}条低适配")

        return XiaohongshuGuideDocument(
            date=date_str,
            total_hotspots=len(all_guides),
            high_priority=high,
            medium_priority=medium,
            low_priority=low,
            trend_summary=trend_summary,
            hot_keywords=hot_keywords
        )

    def _build_system_prompt(self) -> str:
        """构建 System Prompt"""
        return """你是一位资深的小红书内容策略专家，拥有3年以上小红书创作和运营经验。

## 你的专业领域
1. **平台洞察**：深刻理解小红书用户画像
   - 核心用户：18-35岁，70%女性
   - 兴趣领域：美妆、时尚、生活、职场、科技、母婴
   - 内容偏好：实用攻略、避坑指南、情绪共鸣、颜值至上

2. **爆款规律**：熟悉小红书算法机制
   - 标题要有"钩子"（悬念/利益/情绪）
   - 内容要有价值（干货/新知/共鸣）
   - 封面要有冲击力（对比/数字/人脸）

3. **情绪共鸣**：善于将硬核科技新闻转化为用户关心的话题
   - 科技新闻 → "这对我有什么用？"
   - B端产品 → "普通人能用上吗？"
   - 融资消息 → "背后的赚钱机会在哪？"

## 小红书标题写作准则（必须严格遵循）

### 长度控制
- 最佳：20-30字
- 禁止：超过30字或少于20字

### 必备元素（至少包含2个）
1. **第一人称**："我实测""我发现""我踩坑""亲测有效"
2. **悬念制造**："居然...""没想到...""震惊...""真相是..."
3. **利益承诺**："省了XXX""赚了XXX""效率提升XXX"
4. **情绪词汇**："emo了""绝了""爱了""上头""狠狠心动"
5. **数字化表达**："3个技巧""7天见效""月入5w"

### 表情符号使用规范
- 每条标题：1-3个表情
- 常用：✨💡🔥💰😭❤️📊🎯⚡️
- 禁止：过度堆砌（超过3个）

### 典型句式模板
1. **悬念+利益**："XX后我发现了XX，XXX直接翻倍✨"
2. **对比+情绪**："XX vs XX，看完我emo了😭"
3. **数字+承诺**："X天XXX，亲测有效！附教程📊"
4. **第一人称+惊讶**："我试了这个XX，没想到竟然XX🔥"

## 适配度评分标准（1-5星）

**⭐️⭐️⭐️⭐️⭐️（5星 - 必做）**
- 与小红书核心人群强相关（职场/消费/美妆/生活科技）
- 有明确用户痛点或情绪共鸣点
- 可直接转化为实操内容（教程/测评/攻略）
- 示例：AI创作工具、消费品测评、职场工具

**⭐️⭐️⭐️⭐️（4星 - 推荐）**
- 话题有一定热度，与用户生活相关
- 可转化为避坑指南或省钱攻略
- 示例：外卖大战、新品发布、行业变化

**⭐️⭐️⭐️（3星 - 可做）**
- 需要一定角度转化，但有潜在价值
- 可能只适合特定垂直领域
- 示例：科技公司融资、行业报告

**⭐️⭐️（2星 - 慎做）**
- 与目标人群关联较弱
- 需要大量加工和角度转化
- 示例：B端SaaS、供应链管理

**⭐️（1星 - 不建议）**
- 纯B端/政策/财经话题
- 难以适配小红书场景
- 示例：金融监管政策、宏观经济数据

## 输出格式要求

**重要**：必须输出合法的 JSON 数组。JSON 字符串中的引号、反斜杠等特殊字符必须转义：
- 双引号 " → \\"
- 反斜杠 \\ → \\\\
- 换行符 → \\n

每个元素包含以下字段：

```json
[
  {
    "original_title": "新闻原标题",
    "original_summary": "新闻摘要（前300字）",
    "source": "36氪",
    "category": "科技",
    "published": "2026-01-15T10:42:30",
    "link": "https://...",

    "adaptation_score": 5,
    "adaptation_reason": "AI创作工具与小红书用户（内容创作者）强相关，容易产生'我也要试试'的转化",
    "target_demographics": ["内容创作者", "设计爱好者", "副业探索者"],

    "title_templates": [
      {
        "text": "实测！这个AI工具让我10分钟做出爆款封面✨",
        "style": "第一人称实测",
        "target_audience": "内容创作者",
        "emoji_suggestion": "✨💡🔥"
      }
    ],

    "content_angles": [
      {
        "angle": "效率革命指南",
        "why_works": "职场人痛点：做图耗时、缺乏设计技能",
        "example_outline": "1. 传统做图vs AI做图时间对比\\n2. 3个实测案例展示\\n3. 保姆级使用教程\\n4. 踩坑避雷经验"
      }
    ],

    "hashtag_suggestions": ["AI工具", "设计神器", "效率提升", "副业赚钱"],
    "image_suggestions": "对比图：传统设计软件界面 vs AI工具生成效果，突出'简单''快速'",
    "risk_warning": null
  }
]
```

## 关键原则
- 保留所有热点（不筛选），但诚实标注适配度
- 为低适配度热点提供"转化思路"
- 标题必须可操作（用户看了能立刻动手）
- 避免生硬的品牌植入
- 识别敏感话题（政治/金融监管/负面），在 risk_warning 标注
"""

    def _build_user_prompt(self, articles: List[Article], date_str: str) -> str:
        """构建 User Prompt"""

        # 准备新闻上下文（精简版，避免超token限制和特殊字符）
        news_context = []
        for i, article in enumerate(articles, 1):
            # 摘要截断到150字（减少特殊字符问题）
            summary = article.summary[:150]
            if len(article.summary) > 150:
                summary += "..."

            # 清理可能导致 JSON 解析问题的字符
            summary = summary.replace('"', "'").replace('"', "'").replace('"', "'")  # 替换中文引号为英文单引号
            summary = summary.replace('\n', ' ').replace('\r', ' ')  # 移除换行符

            # 格式化发布时间
            published_str = ""
            if article.published:
                if isinstance(article.published, datetime):
                    published_str = article.published.isoformat()
                else:
                    published_str = str(article.published)

            news_context.append(f"""### 新闻 {i}: {article.title}
- **来源**: {article.source} | **分类**: {article.category}
- **发布时间**: {published_str}
- **摘要**: {summary}
- **链接**: {article.link}
""")

        user_prompt = f"""今天是 {date_str}。

请将以下 {len(articles)} 条科技/商业新闻转化为小红书创作者的热点选题指南。

{''.join(news_context)}

---

## 你的任务

**为每条新闻生成完整的创作指南**，包含：

1. **适配度评估**（1-5星）
   - 评估该热点与小红书用户的相关度
   - 给出评分理由（50-100字）
   - 标注目标人群

2. **标题模板**（恰好3个）
   - 每个标题20-30字
   - 必须符合小红书风格（第一人称、悬念、表情符号）
   - 标注风格类型和目标受众

3. **内容角度**（恰好2个）
   - 提供具体的创作角度（如"薅羊毛指南""避坑测评"）
   - 分析为什么这个角度有效（用户痛点/情绪共鸣点）
   - 给出内容大纲示例（简洁的3-4个要点）

4. **话题标签**（恰好5个）
   - 推荐相关的小红书话题标签
   - 优先选择热门标签

5. **配图建议**
   - 描述适合的配图风格或元素

6. **风险提示**（如有）
   - 识别敏感话题（政治、金融监管、负面事件）
   - 给出规避建议

## 特别强调

- ✅ **保留所有 {len(articles)} 条新闻**（即使适配度只有1星）
- ✅ **为低适配度热点提供转化思路**（如何从B端转化为C端视角）
- ✅ **标题必须可直接使用**（创作者复制粘贴即可发布）
- ❌ **避免生硬的品牌植入**（不要像广告文案）

**输出要求**：
- 直接输出 JSON 数组，不要 Markdown 代码块标记
- JSON 中的特殊字符必须转义：双引号 " → \\", 反斜杠 \\ → \\\\
- 确保输出是合法的 JSON 格式
"""

        return user_prompt

    def _parse_json_response(self, text: str) -> list:
        """
        解析 JSON 响应，处理可能的格式问题

        复用自 claude_dialogue_writer.py:255-274，增强容错能力

        容错策略：
        1. 尝试直接解析
        2. 正则提取 [...] 块
        3. 移除 Markdown 标记后解析
        4. 使用 json5 宽松解析（如果可用）
        """
        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试提取 JSON 块
        json_match = re.search(r'\[[\s\S]*\]', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # 移除 markdown 代码块标记
        cleaned = text.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # 尝试使用 json5（更宽松的JSON解析）
        try:
            import json5
            return json5.loads(text)
        except (ImportError, Exception):
            pass

        # 最后的尝试：使用 demjson3
        try:
            import demjson3
            return demjson3.decode(text)
        except (ImportError, Exception) as e:
            # 保存原始响应到日志
            error_log = f"logs/xiaohongshu_parse_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            Path("logs").mkdir(exist_ok=True)
            with open(error_log, "w", encoding="utf-8") as f:
                f.write(f"=== 解析失败 ===\n")
                f.write(f"时间: {datetime.now()}\n")
                f.write(f"错误: {e}\n\n")
                f.write(f"=== 原始响应 ===\n")
                f.write(text)

            print(f"  ⚠️ JSON 解析失败，原始响应已保存到: {error_log}")
            print(f"  💡 提示：可尝试安装 demjson3 库来提升解析容错性：pip install demjson3")
            raise

    def _convert_to_dataclasses(self, guides_data: list) -> List[XiaohongshuHotspotGuide]:
        """将 JSON 转换为数据类"""
        guides = []

        for item in guides_data:
            try:
                # 转换嵌套的 TitleTemplate
                title_templates = []
                for t in item.get("title_templates", []):
                    title_templates.append(TitleTemplate(
                        text=t["text"],
                        style=t.get("style", "未知"),
                        target_audience=t.get("target_audience", "通用"),
                        emoji_suggestion=t.get("emoji_suggestion", "")
                    ))

                # 转换嵌套的 ContentAngle
                content_angles = []
                for a in item.get("content_angles", []):
                    content_angles.append(ContentAngle(
                        angle=a["angle"],
                        why_works=a.get("why_works", ""),
                        example_outline=a.get("example_outline", "")
                    ))

                # 构建主对象
                guide = XiaohongshuHotspotGuide(
                    original_title=item["original_title"],
                    original_summary=item.get("original_summary", ""),
                    source=item.get("source", ""),
                    category=item.get("category", ""),
                    published=item.get("published"),
                    link=item.get("link", ""),
                    adaptation_score=item["adaptation_score"],
                    adaptation_reason=item["adaptation_reason"],
                    target_demographics=item.get("target_demographics", []),
                    title_templates=title_templates,
                    content_angles=content_angles,
                    hashtag_suggestions=item.get("hashtag_suggestions", []),
                    image_suggestions=item.get("image_suggestions", ""),
                    risk_warning=item.get("risk_warning")
                )
                guides.append(guide)

            except KeyError as e:
                print(f"  ⚠️ 跳过格式错误的热点: {e}")
                continue

        return guides

    def _generate_trend_insights(self, articles: List[Article]) -> tuple[str, List[str]]:
        """
        生成趋势洞察

        Returns:
            (趋势总结, 高频关键词列表)
        """
        # 预定义关键词库（科技/商业领域）
        tech_keywords = [
            # AI & 科技
            "AI", "人工智能", "大模型", "GPT", "Claude", "智能体",
            "芯片", "半导体", "RISC-V",
            "机器人", "自动驾驶", "新能源",

            # 商业 & 消费
            "融资", "IPO", "上市", "投资", "估值",
            "外卖", "消费", "供应链", "电商",
            "品牌", "出海", "营收",

            # 行业
            "汽车", "金融", "医疗", "教育", "房地产"
        ]

        keyword_counts = Counter()

        # 统计关键词出现次数
        for article in articles:
            text = f"{article.title} {article.summary}".lower()
            for kw in tech_keywords:
                if kw.lower() in text:
                    keyword_counts[kw] += 1

        # 提取 Top 10
        hot_keywords = [kw for kw, _ in keyword_counts.most_common(10)]

        # 简单的趋势总结
        if hot_keywords:
            top3 = ', '.join(hot_keywords[:3])
            trend_summary = (
                f"今日科技热点聚焦于 {top3} 等领域，"
                f"共收录 {len(articles)} 条新闻。"
                f"其中 AI 相关话题占比较高，适合小红书科技内容创作者重点关注。"
            )
        else:
            trend_summary = f"今日科技热点多元化，共收录 {len(articles)} 条新闻。"

        return trend_summary, hot_keywords


def main():
    """测试入口"""
    from dotenv import load_dotenv
    load_dotenv()

    # Mock 测试数据
    test_articles = [
        Article(
            title='AI时代的全球创作消费平台，出现了一家来自中国的"隐形冠军"',
            summary="SeaArt 月活用户突破2500万，年度经常性收入超过5000万美元...",
            link="https://36kr.com/p/3638895618739335",
            source="36氪",
            category="科技",
            published=datetime(2026, 1, 15, 10, 42, 30)
        ),
        Article(
            title="第二次外卖大战：平台资本和国家监管的博弈，谁输谁赢？",
            summary="美团、淘宝、京东的外卖大战，我们普通人看到的是三大平台互抢订单、狂撒红包...",
            link="http://www.huxiu.com/article/4826742.html",
            source="虎嗅",
            category="商业",
            published=datetime(2026, 1, 15, 10, 32, 58)
        )
    ]

    writer = XiaohongshuGuideWriter()
    guide = writer.generate_guide(test_articles, datetime.now())

    output_path = "output/test/xiaohongshu-guide-test.md"
    saved_path = guide.save_to_markdown(output_path)

    print(f"\n✅ 测试成功！指南已保存到: {saved_path}")
    print(f"📊 高适配: {len(guide.high_priority)}, 中适配: {len(guide.medium_priority)}, 低适配: {len(guide.low_priority)}")


if __name__ == "__main__":
    main()
