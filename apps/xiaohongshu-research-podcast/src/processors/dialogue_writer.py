"""
播客对话脚本生成器
使用 Gemini 2.5 Pro 将小红书话题分析转化为双人对谈脚本
"""
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import google.generativeai as genai

from ..models.topic import TopicAnalysisResult, AIInsight, XHSTopic
from ..utils.logger import get_logger

logger = get_logger()


@dataclass
class DialogueLine:
    """对话行"""

    speaker: str  # "小雅" or "植萌"
    text: str  # 对话内容
    emotion: str = "neutral"  # 情绪: excited, thoughtful, curious, neutral

    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)


@dataclass
class PodcastScript:
    """播客脚本"""

    title: str  # 播客标题
    date: str  # 日期
    episode_number: Optional[int] = None  # 集数（可选）
    lines: list[DialogueLine] = None  # 对话行列表
    duration_estimate: int = 600  # 预计时长（秒）

    def __post_init__(self):
        if self.lines is None:
            self.lines = []

    def to_json(self) -> str:
        """转换为JSON字符串"""
        data = {
            "title": self.title,
            "date": self.date,
            "episode_number": self.episode_number,
            "duration_estimate": self.duration_estimate,
            "lines": [line.to_dict() for line in self.lines],
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    def save_to_file(self, output_dir: Path) -> tuple[Path, Path]:
        """
        保存脚本到文件

        Args:
            output_dir: 输出目录

        Returns:
            (JSON路径, Markdown路径)
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 保存JSON（用于TTS处理）
        json_path = output_dir / f"script-{self.date}.json"
        json_path.write_text(self.to_json(), encoding="utf-8")

        # 保存Markdown（便于人类阅读）
        md_path = output_dir / f"script-{self.date}.md"
        md_content = self._to_markdown()
        md_path.write_text(md_content, encoding="utf-8")

        return json_path, md_path

    def _to_markdown(self) -> str:
        """转换为Markdown格式"""
        lines_md = []

        # 标题
        lines_md.append(f"# {self.title}\n")
        lines_md.append(f"**日期**: {self.date}")

        if self.episode_number:
            lines_md.append(f"**第{self.episode_number}期**")

        lines_md.append(f"**预计时长**: {self.duration_estimate // 60}分钟\n")
        lines_md.append("---\n")

        # 对话内容
        for line in self.lines:
            # 使用emoji区分说话者
            speaker_icon = "🎙️" if line.speaker == "小雅" else "💡"
            emotion_tag = f" ({line.emotion})" if line.emotion != "neutral" else ""

            lines_md.append(
                f"**{speaker_icon} {line.speaker}**{emotion_tag}: {line.text}\n"
            )

        # 页脚
        lines_md.append("\n---\n")
        lines_md.append(
            f"*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        )

        return "\n".join(lines_md)


class DialogueWriter:
    """播客脚本生成器（使用Gemini API）"""

    def __init__(
        self,
        model_name: str = "gemini-2.0-flash-exp",
        temperature: float = 0.9,
        max_output_tokens: int = 8192,
    ):
        """
        初始化

        Args:
            model_name: Gemini模型名称
            temperature: 生成温度（0-1，越高越随机）
            max_output_tokens: 最大输出token数
        """
        # 从环境变量读取API Key
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("需要设置 GOOGLE_API_KEY 或 GEMINI_API_KEY 环境变量")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens

        logger.info(f"DialogueWriter 初始化完成 (model={model_name})")

    def generate(
        self,
        analysis_result: TopicAnalysisResult,
        ai_insight: Optional[AIInsight] = None,
        target_duration: int = 600,
    ) -> PodcastScript:
        """
        生成播客对话脚本

        Args:
            analysis_result: 话题分析结果
            ai_insight: AI洞察（可选）
            target_duration: 目标时长（秒），默认10分钟

        Returns:
            播客脚本对象
        """
        logger.info("开始生成播客对话脚本...")

        # 1. 准备输入上下文
        context = self._build_context(analysis_result, ai_insight)

        # 2. 构建Prompt
        prompt = self._build_prompt(analysis_result, target_duration)

        # 3. 调用Gemini API
        try:
            logger.info("  调用 Gemini API...")
            response = self.model.generate_content(
                [prompt, context],
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_output_tokens,
                    "response_mime_type": "application/json",
                },
            )

            # 4. 解析结果
            dialogue_data = json.loads(response.text)
            lines = [
                DialogueLine(
                    speaker=item.get("speaker", "小雅"),
                    text=item.get("text", ""),
                    emotion=item.get("emotion", "neutral"),
                )
                for item in dialogue_data
            ]

            script = PodcastScript(
                title=f"小红书热门话题研究 - {analysis_result.date}",
                date=analysis_result.date,
                lines=lines,
                duration_estimate=target_duration,
            )

            logger.info(f"  ✓ 脚本生成完成，共{len(lines)}行对话")
            return script

        except json.JSONDecodeError as e:
            logger.error(f"  ✗ JSON解析失败: {e}")
            logger.error(f"  原始输出: {response.text[:500]}...")
            # 返回错误脚本
            return self._create_error_script(analysis_result.date)

        except Exception as e:
            logger.error(f"  ✗ 脚本生成失败: {e}")
            return self._create_error_script(analysis_result.date)

    def _build_context(
        self, analysis_result: TopicAnalysisResult, ai_insight: Optional[AIInsight]
    ) -> str:
        """构建输入上下文"""
        context_parts = []

        # 基础信息
        context_parts.append(f"**分析日期**: {analysis_result.date}")
        context_parts.append(f"**话题总数**: {analysis_result.total_topics}")
        context_parts.append(
            f"**总热度**: {analysis_result.total_heat / 10000:.1f}万\n"
        )

        # Top话题
        context_parts.append("## Top 10 热门话题\n")
        for topic in analysis_result.top_topics[:10]:
            heat = topic.heat_score_formatted
            read = self._format_number(topic.read_count)
            notes = self._format_number(topic.note_count)
            trend = topic.rank_change_text

            context_parts.append(
                f"{topic.rank}. **{topic.title}** "
                f"(热度: {heat}, 阅读: {read}, 笔记: {notes}, 趋势: {trend})"
            )

        context_parts.append("")

        # 热词
        if analysis_result.top_keywords:
            keywords_text = "、".join(analysis_result.top_keywords[:15])
            context_parts.append(f"## 热词Top 15\n{keywords_text}\n")

        # 分类统计
        if analysis_result.category_stats:
            context_parts.append("## 分类分布\n")
            for category, stats in list(analysis_result.category_stats.items())[:5]:
                count = stats.get("count", 0)
                context_parts.append(f"- {category}: {count}个话题")
            context_parts.append("")

        # AI洞察
        if ai_insight:
            context_parts.append("## AI洞察\n")

            if ai_insight.user_behavior:
                context_parts.append("**用户行为**:")
                for item in ai_insight.user_behavior[:3]:
                    context_parts.append(f"- {item}")
                context_parts.append("")

            if ai_insight.trend_predictions:
                context_parts.append("**趋势预测**:")
                for item in ai_insight.trend_predictions[:3]:
                    context_parts.append(f"- {item}")
                context_parts.append("")

        return "\n".join(context_parts)

    def _build_prompt(
        self, analysis_result: TopicAnalysisResult, target_duration: int
    ) -> str:
        """构建Gemini Prompt"""
        target_minutes = target_duration // 60

        return f"""
你是一位专业的播客制作人，负责为"小红书数据观察"播客撰写对话脚本。

## 节目定位
- **节目名称**: 小红书数据观察
- **播出频率**: 每日
- **时长**: {target_minutes}分钟左右
- **受众**: 内容创作者、品牌方、数据分析师

## 主持人设定

**小雅** (女性，数据分析师):
- 性格：理性、专业、善于发现数据背后的规律
- 角色：主导数据解读，提供深度分析
- 语言风格：简洁专业，善用数据对比
- 典型表达："从数据来看..."、"这个趋势值得关注..."

**植萌** (男性，内容创作者):
- 性格：好奇、活跃、代表创作者视角
- 角色：提出问题，关注实操建议
- 语言风格：轻松活泼，接地气
- 典型表达："这个有意思..."、"创作者该怎么做..."

## 脚本要求

1. **自然对话**：
   - 使用口语化表达，避免书面语
   - 加入语气词（"诶"、"对"、"嗯"、"是吧"）
   - 适当打断和补充（模拟真实对话）

2. **结构清晰**：
   - 开场：简短有力的Hook（30秒内吸引注意）
   - 主体：3-4个话题板块，每个2-3分钟
   - 结尾：总结要点 + 行动建议

3. **内容深度**：
   - 不只是播报数据，要解释"为什么"
   - 连接不同话题，发现关联
   - 提供可落地的创作者建议

4. **节奏把控**：
   - 快慢结合：数据部分快速，洞察部分放慢
   - 适时制造悬念："那你猜接下来会怎样？"
   - 避免单人长篇大论（每轮对话控制在50字内）

5. **语言风格**：
   - 使用中文，保留"小红书"、"互动量"等平台术语
   - 数字用中文表达：150万、5000万（不要用1.5M）
   - 适当使用网络流行语，但不过度

## 输出格式（JSON Array）

```json
[
  {{"speaker": "小雅", "text": "...", "emotion": "excited"}},
  {{"speaker": "植萌", "text": "...", "emotion": "curious"}}
]
```

**emotion可选值**: neutral, excited, thoughtful, curious, surprised, concerned

## 脚本示例

小雅: 大家好，欢迎来到小红书数据观察，我是小雅。
植萌: 我是植萌。今天的数据有点意思啊！
小雅: 对，今天抓取了50个热门话题，总热度达到5000万，比昨天涨了15%。
植萌: 哇，这个增长幅度不小。那都是哪些话题在带动增长呢？
小雅: 你看排名第一的是"春节出游攻略"，热度150万，而且排名比昨天上升了2位。
植萌: 春节嘛，这个时间点确实是出游规划的高峰期。那这个话题的数据表现怎么样？
小雅: 阅读量5000万，笔记数2万，互动率算是比较高的。

---

请基于提供的数据生成完整的{target_minutes}分钟对话脚本。
"""

    def _build_context(
        self, analysis_result: TopicAnalysisResult, ai_insight: Optional[AIInsight]
    ) -> str:
        """构建数据上下文（已在上面实现）"""
        # 此方法在上面已实现
        pass

    def _create_error_script(self, date: str) -> PodcastScript:
        """创建错误处理脚本"""
        return PodcastScript(
            title=f"小红书热门话题研究 - {date}",
            date=date,
            lines=[
                DialogueLine(
                    speaker="小雅",
                    text="抱歉，今天的播客脚本生成遇到了一些技术问题。",
                    emotion="concerned",
                ),
                DialogueLine(
                    speaker="植萌",
                    text="我们正在努力修复，请稍后再来收听。感谢你的理解！",
                    emotion="neutral",
                ),
            ],
            duration_estimate=30,
        )

    @staticmethod
    def _format_number(num: int) -> str:
        """格式化数字（万、亿）"""
        if num >= 100_000_000:
            return f"{num / 100_000_000:.1f}亿"
        elif num >= 10_000:
            return f"{num / 10_000:.1f}万"
        else:
            return str(num)


# 示例用法
if __name__ == "__main__":
    # 创建测试数据
    from models.topic import XHSTopic, TopicAnalysisResult, AIInsight

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

    test_analysis = TopicAnalysisResult(
        date="2026-01-15",
        total_topics=50,
        total_heat=50000000,
        top_keywords=["春节", "旅游", "年货", "美食", "攻略"],
        category_stats={
            "旅游": {"count": 15, "total_heat": 20000000},
            "美食": {"count": 12, "total_heat": 15000000},
        },
        top_topics=test_topics,
    )

    test_insight = AIInsight(
        user_behavior=["用户对春节相关内容关注度显著上升"],
        trend_predictions=["预计未来一周，春节旅游话题将持续升温"],
        creator_tips=["建议创作者提前布局春节相关内容"],
    )

    # 生成脚本
    generator = DialogueWriter()
    script = generator.generate(
        analysis_result=test_analysis,
        ai_insight=test_insight,
        target_duration=600,  # 10分钟
    )

    # 保存
    json_path, md_path = script.save_to_file(Path("output/test"))

    print(f"✓ 脚本已生成:")
    print(f"  JSON: {json_path}")
    print(f"  Markdown: {md_path}")
    print(f"  对话行数: {len(script.lines)}")
