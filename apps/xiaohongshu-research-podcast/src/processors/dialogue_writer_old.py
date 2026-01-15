"""对话脚本生成器"""
import json
import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import google.generativeai as genai

from ..models.topic import AIInsight
from ..utils.logger import get_logger

logger = get_logger()


@dataclass
class DialogueLine:
    """对话行"""

    speaker: str  # "Host A" or "Host B"
    text: str  # 对话内容
    emotion: str = "neutral"  # excited/thoughtful/curious/neutral


@dataclass
class DialogueScript:
    """完整对话脚本"""

    title: str
    date: str
    lines: list[DialogueLine]

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "title": self.title,
            "date": self.date,
            "lines": [
                {"speaker": line.speaker, "text": line.text, "emotion": line.emotion}
                for line in self.lines
            ],
        }

    def save_to_file(self, filepath: str):
        """保存到JSON文件"""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)


class DialogueWriter:
    """对话脚本生成器"""

    def __init__(self, voice_config_path: str = "config/voice.yaml"):
        """
        初始化

        Args:
            voice_config_path: 语音配置文件路径
        """
        # 加载配置
        with open(voice_config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.hosts = self.config.get("hosts", {})
        self.template = self.config.get("script_template", {})
        self.podcast_config = self.config.get("podcast", {})

        # 初始化Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")

    def generate_xhs_dialogue(
        self, insights: AIInsight, analysis: dict, date: datetime
    ) -> DialogueScript:
        """
        生成小红书研究播客对话脚本

        Args:
            insights: AI洞察
            analysis: 分析结果
            date: 日期

        Returns:
            对话脚本
        """
        logger.info("开始生成对话脚本...")

        # 构建Prompt
        prompt = self._build_dialogue_prompt(insights, analysis)

        # 调用Gemini生成对话
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.8,  # 稍高温度增加创造性
                    "max_output_tokens": 4096,
                },
            )

            dialogue_data = json.loads(response.text)
            logger.info(f"  生成 {len(dialogue_data)} 句对话")

            # 构建对话脚本
            lines = [
                DialogueLine(
                    speaker=item["speaker"],
                    text=item["text"],
                    emotion=item.get("emotion", "neutral"),
                )
                for item in dialogue_data
            ]

            script = DialogueScript(
                title=f"每日小红书研究 - {date.strftime('%Y年%m月%d日')}",
                date=date.strftime("%Y-%m-%d"),
                lines=lines,
            )

            logger.info("对话脚本生成成功")
            return script

        except Exception as e:
            logger.error(f"对话生成失败: {e}")
            # 返回基础脚本
            return self._create_fallback_script(insights, date)

    def _build_dialogue_prompt(self, insights: AIInsight, analysis: dict) -> str:
        """
        构建对话生成Prompt

        Args:
            insights: AI洞察
            analysis: 分析结果

        Returns:
            Prompt字符串
        """
        host_a_name = self.hosts.get("host_a", {}).get("name", "小雅")
        host_b_name = self.hosts.get("host_b", {}).get("name", "植萌")

        # 提取Top话题
        top_topics = analysis.get("top_topics", [])[:10]
        topics_text = "\n".join(
            [
                f"{i + 1}. {t.title} (热度: {t.heat_score_formatted}, 分类: {t.category})"
                for i, t in enumerate(top_topics)
            ]
        )

        # 提取分类统计
        category_stats = analysis.get("category_stats", {})
        categories_text = "\n".join(
            [
                f"- {cat}: {stats['count']}个话题, 占比{stats['percentage']}%"
                for cat, stats in list(category_stats.items())[:5]
            ]
        )

        prompt = f"""
你是《每日小红书研究》播客的专业脚本编剧。请将以下数据转化为9分钟的双人对话脚本。

【主持人设定】
- {host_a_name} (Host A): 活泼、好奇、善于提问，代表普通用户视角
- {host_b_name} (Host B): 分析型、专业、数据驱动，行业专家视角

【数据输入】
Top 10 话题:
{topics_text}

分类统计:
{categories_text}

AI洞察:
- 用户行为: {', '.join(insights.user_behavior)}
- 趋势预测: {', '.join(insights.trend_predictions)}
- 创作者建议: {', '.join(insights.creator_tips)}

【脚本结构】总时长 9分钟

**第1部分 [00:00-01:00] 开场**
- Cold Open (30秒): 用最热话题吸引注意力
- 正式开场 (30秒): 介绍播客和今日主题

**第2部分 [01:00-03:00] Top话题盘点**
- 快速盘点前3个最热话题
- 每个话题用1-2轮对话讲清楚
- 小雅提问，植萌解读数据

**第3部分 [03:00-06:00] 深度分析**
- 趋势分析 (1.5分钟): 讨论热度变化和新兴话题
- 用户洞察 (1.5分钟): 分析用户行为模式

**第4部分 [06:00-08:00] 创作者建议**
- 给小红书创作者的3条具体建议
- 结合真实话题举例

**第5部分 [08:00-09:00] 结尾**
- 总结今日要点
- 预告明天内容
- 感谢收听

【对话要求】
1. 口语化，自然流畅，避免书面语
2. 每人每次发言控制在2-3句话，避免长篇大论
3. 使用类比和例子让数据易懂（如"相当于...""就像..."）
4. 在关键数据前制造悬念（"你猜猜看..."）
5. 两人要有互动（"确实是这样""有意思"等回应）
6. 引用具体话题标题时要自然

【情绪标签】
- excited: 兴奋、惊讶
- thoughtful: 深思、分析
- curious: 好奇、疑问
- neutral: 中性、陈述

【输出JSON格式】
[
  {{"speaker": "Host A", "text": "大家好，欢迎收听每日小红书研究！", "emotion": "excited"}},
  {{"speaker": "Host B", "text": "今天我们发现了一个特别有意思的现象...", "emotion": "thoughtful"}},
  ...
]

请生成完整的9分钟对话脚本（约30-40句对话）。
"""
        return prompt

    def _create_fallback_script(
        self, insights: AIInsight, date: datetime
    ) -> DialogueScript:
        """
        创建回退脚本（当AI生成失败时）

        Args:
            insights: AI洞察
            date: 日期

        Returns:
            基础对话脚本
        """
        logger.warning("使用回退脚本")

        host_a = self.hosts.get("host_a", {}).get("name", "小雅")
        host_b = self.hosts.get("host_b", {}).get("name", "植萌")

        lines = [
            DialogueLine("Host A", f"大家好，欢迎收听每日小红书研究。我是{host_a}。", "excited"),
            DialogueLine("Host B", f"大家好，我是{host_b}。今天我们来分析小红书平台的最新热点。", "neutral"),
            DialogueLine("Host A", "那我们开始吧！", "excited"),
        ]

        # 添加洞察内容
        if insights.user_behavior:
            lines.append(
                DialogueLine("Host B", f"今天的一个重要发现是：{insights.user_behavior[0]}", "thoughtful")
            )

        # 结尾
        lines.extend(
            [
                DialogueLine("Host A", "好的，以上就是今天的小红书数据分析。", "neutral"),
                DialogueLine("Host B", "感谢大家的收听，我们明天再见！", "neutral"),
            ]
        )

        return DialogueScript(
            title=f"每日小红书研究 - {date.strftime('%Y年%m月%d日')}",
            date=date.strftime("%Y-%m-%d"),
            lines=lines,
        )
