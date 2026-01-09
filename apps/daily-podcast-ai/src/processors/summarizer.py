"""
文章摘要生成模块
使用 AI 对新闻文章进行摘要和改写，使其适合播客播报
"""

import os
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI


@dataclass
class SummarizedArticle:
    """摘要后的文章"""
    title: str
    summary: str  # 原始摘要
    podcast_text: str  # 适合播报的文本
    source: str
    category: str


class ArticleSummarizer:
    """文章摘要生成器"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        初始化摘要生成器

        Args:
            api_key: OpenAI API 密钥（默认从环境变量读取）
            model: 使用的模型
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未设置 OPENAI_API_KEY 环境变量")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def _create_podcast_prompt(self, title: str, summary: str, source: str) -> str:
        """创建播客文本生成的 prompt"""
        return f"""你是一位专业的科技新闻播报员。请将以下新闻改写为适合播客播报的口语化文本。

要求：
1. 语言自然流畅，适合朗读
2. 保持信息准确，但用口语化表达
3. 控制在 100-150 字以内
4. 不要使用"据报道"、"根据消息"等书面语开头
5. 直接陈述事实，语气专业但亲切

新闻标题：{title}
来源：{source}
原文摘要：{summary}

请直接输出改写后的播报文本，不要添加任何前缀或说明："""

    def summarize_article(self, article) -> SummarizedArticle:
        """
        对单篇文章进行摘要和改写

        Args:
            article: Article 对象

        Returns:
            SummarizedArticle 对象
        """
        prompt = self._create_podcast_prompt(
            article.title,
            article.summary,
            article.source
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是专业的科技新闻播报员，擅长将书面新闻改写为口语化的播报文本。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            podcast_text = response.choices[0].message.content.strip()

            return SummarizedArticle(
                title=article.title,
                summary=article.summary,
                podcast_text=podcast_text,
                source=article.source,
                category=article.category
            )

        except Exception as e:
            print(f"  ❌ AI 摘要失败: {e}")
            # 降级处理：直接使用原摘要
            fallback_text = f"{article.title}。{article.summary[:100]}"
            return SummarizedArticle(
                title=article.title,
                summary=article.summary,
                podcast_text=fallback_text,
                source=article.source,
                category=article.category
            )

    def summarize_batch(self, articles: list, show_progress: bool = True) -> list[SummarizedArticle]:
        """
        批量处理文章摘要

        Args:
            articles: Article 对象列表
            show_progress: 是否显示进度

        Returns:
            SummarizedArticle 对象列表
        """
        if show_progress:
            print(f"\n🤖 开始 AI 内容处理，共 {len(articles)} 篇文章")
            print("-" * 40)

        summarized = []
        for i, article in enumerate(articles, 1):
            if show_progress:
                print(f"  [{i}/{len(articles)}] 处理: {article.title[:30]}...")

            result = self.summarize_article(article)
            summarized.append(result)

        if show_progress:
            print("-" * 40)
            print(f"✅ 内容处理完成，共 {len(summarized)} 篇")

        return summarized


class SimpleSummarizer:
    """简单摘要器（不使用 AI，仅做文本清理）"""

    def __init__(self, max_length: int = 150):
        self.max_length = max_length

    def summarize_article(self, article) -> SummarizedArticle:
        """简单处理文章，适合测试或无 API 场景"""
        # 简单的文本清理和截断
        podcast_text = f"{article.title}。{article.summary}"
        if len(podcast_text) > self.max_length:
            podcast_text = podcast_text[:self.max_length - 3] + "..."

        return SummarizedArticle(
            title=article.title,
            summary=article.summary,
            podcast_text=podcast_text,
            source=article.source,
            category=article.category
        )

    def summarize_batch(self, articles: list, show_progress: bool = True) -> list[SummarizedArticle]:
        """批量处理"""
        return [self.summarize_article(a) for a in articles]


def main():
    """测试入口"""
    from news_sources import RSSFetcher

    # 获取新闻
    fetcher = RSSFetcher()
    articles = fetcher.fetch_all()

    if not articles:
        print("没有获取到文章")
        return

    # 使用简单摘要器测试（不需要 API）
    print("\n" + "=" * 50)
    print("📝 使用简单摘要器测试")
    print("=" * 50)

    summarizer = SimpleSummarizer()
    summarized = summarizer.summarize_batch(articles[:3])

    for i, article in enumerate(summarized, 1):
        print(f"\n{i}. [{article.category}] {article.title}")
        print(f"   播报文本: {article.podcast_text}")


if __name__ == "__main__":
    main()
