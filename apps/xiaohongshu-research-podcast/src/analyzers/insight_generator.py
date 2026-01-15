"""AI洞察生成器"""
import json
import os
from typing import Optional

import google.generativeai as genai

from ..models.topic import XHSTopic, AIInsight
from ..utils.logger import get_logger

logger = get_logger()


class InsightGenerator:
    """AI洞察生成器 - 使用LLM生成深度洞察"""

    def __init__(self, provider: str = "gemini"):
        """
        初始化

        Args:
            provider: AI提供商（gemini/openai）
        """
        self.provider = provider

        if provider == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not set")

            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
            logger.info("使用 Google Gemini 2.0 Flash")

        elif provider == "openai":
            from openai import OpenAI

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set")

            self.client = OpenAI(api_key=api_key)
            self.model_name = "gpt-4o-mini"
            logger.info(f"使用 OpenAI {self.model_name}")

        else:
            raise ValueError(f"不支持的AI提供商: {provider}")

    def generate_insights(
        self, topics: list[XHSTopic], analysis: dict
    ) -> AIInsight:
        """
        生成AI洞察

        Args:
            topics: 话题列表
            analysis: 话题分析结果

        Returns:
            AI洞察对象
        """
        logger.info("开始生成AI洞察...")

        # 构建Prompt
        prompt = self._build_prompt(topics, analysis)

        # 调用AI
        try:
            if self.provider == "gemini":
                insights_json = self._call_gemini(prompt)
            elif self.provider == "openai":
                insights_json = self._call_openai(prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

            # 解析结果
            insights = AIInsight(**insights_json)
            logger.info("AI洞察生成成功")
            return insights

        except Exception as e:
            logger.error(f"AI洞察生成失败: {e}")
            # 返回空洞察
            return AIInsight()

    def _build_prompt(self, topics: list[XHSTopic], analysis: dict) -> str:
        """
        构建Prompt

        Args:
            topics: 话题列表
            analysis: 分析结果

        Returns:
            Prompt字符串
        """
        # 只传Top 20话题（节省token）
        top_topics = topics[:20]

        # 构建分类信息
        category_info = []
        for cat, stats in list(analysis.get("category_stats", {}).items())[:10]:
            category_info.append(
                f"  - {cat}: {stats['count']}个话题, 占比{stats['percentage']}%, "
                f"平均热度{stats['avg_heat']:,}, Top话题《{stats['top_topic']}》"
            )

        prompt = f"""
你是一位资深的小红书平台数据分析师，拥有5年以上的内容运营和用户行为研究经验。
请基于以下小红书热门话题数据，生成深度洞察和专业建议。

【数据概览】
- 话题总数: {len(topics)}
- 总热度: {analysis.get('total_heat', 0):,}
- Top热词: {', '.join(analysis.get('top_keywords', [])[:15])}

【Top 20 话题】
{self._format_topics(top_topics)}

【分类分布】
{chr(10).join(category_info)}

【分析任务】
请从以下4个维度生成洞察：

1. **用户行为模式**（user_behavior）
   - 分析用户关注的内容类型
   - 识别用户活跃时段或人群特征
   - 发现用户需求变化
   请提供2-3条洞察

2. **趋势预测**（trend_predictions）
   - 预测未来3-7天可能持续热门的话题类型
   - 识别潜在的新兴趋势
   - 判断当前热点的生命周期
   请提供2-3条预测

3. **创作者建议**（creator_tips）
   - 为小红书创作者提供选题建议
   - 建议内容创作策略
   - 推荐最佳发布时机
   请提供3条具体建议

4. **平台洞察**（platform_insights，可选）
   - 分析平台内容生态变化
   - 识别平台推荐算法偏好
   请提供1-2条洞察

【输出要求】
1. 必须返回严格的JSON格式
2. 每条洞察控制在50字以内
3. 洞察要具体、可执行，避免空泛
4. 数据驱动，引用具体话题或分类

【JSON格式】
{{
  "user_behavior": ["洞察1", "洞察2", "洞察3"],
  "trend_predictions": ["预测1", "预测2", "预测3"],
  "creator_tips": ["建议1", "建议2", "建议3"],
  "platform_insights": ["平台洞察1", "平台洞察2"]
}}
"""
        return prompt

    def _format_topics(self, topics: list[XHSTopic]) -> str:
        """
        格式化话题列表

        Args:
            topics: 话题列表

        Returns:
            格式化的文本
        """
        lines = []
        for topic in topics:
            lines.append(
                f"{topic.rank}. {topic.title} "
                f"(热度: {topic.heat_score_formatted}, 分类: {topic.category})"
            )
        return "\n".join(lines)

    def _call_gemini(self, prompt: str) -> dict:
        """
        调用 Google Gemini API

        Args:
            prompt: 提示词

        Returns:
            解析后的JSON字典
        """
        logger.info("调用 Gemini API...")

        response = self.model.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.7,
                "max_output_tokens": 2048,
            },
        )

        # 解析JSON
        result_text = response.text
        logger.info(f"  Gemini响应长度: {len(result_text)} 字符")

        try:
            result = json.loads(result_text)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            logger.error(f"原始响应: {result_text[:500]}...")
            raise

    def _call_openai(self, prompt: str) -> dict:
        """
        调用 OpenAI API

        Args:
            prompt: 提示词

        Returns:
            解析后的JSON字典
        """
        logger.info("调用 OpenAI API...")

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "你是专业的小红书数据分析师。必须返回严格的JSON格式。",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=2048,
        )

        result_text = response.choices[0].message.content
        logger.info(f"  OpenAI响应长度: {len(result_text)} 字符")

        try:
            result = json.loads(result_text)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            logger.error(f"原始响应: {result_text[:500]}...")
            raise
