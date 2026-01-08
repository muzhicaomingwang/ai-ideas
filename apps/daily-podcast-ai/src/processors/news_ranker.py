"""
新闻排序和优选模块
使用 AI 对新闻进行质量评分并排序
"""

import os
from typing import List

from openai import OpenAI


class NewsRanker:
    """新闻排序器 - 使用 AI 评估新闻质量"""

    def __init__(self):
        """初始化 OpenAI 客户端"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "未设置 OPENAI_API_KEY 环境变量。\n"
                "请在 .env 文件中配置: OPENAI_API_KEY=your_key_here"
            )
        self.client = OpenAI(api_key=api_key)

    def rank_articles(self, articles: list, max_count: int = 10) -> list:
        """
        对新闻进行评分和排序

        Args:
            articles: 文章列表（Article 对象或字典）
            max_count: 返回的最大数量

        Returns:
            排序后的文章列表（最优质的在前）
        """
        if not articles:
            return []

        if len(articles) <= max_count:
            return articles

        print(f"  🤖 使用 AI 评估 {len(articles)} 篇新闻质量...")

        # 准备文章列表文本
        articles_text = self._format_articles_for_ranking(articles)

        # 调用 AI 评分
        prompt = f"""你是一个新闻编辑，需要从以下 {len(articles)} 篇科技新闻中选出最值得播报的 {max_count} 篇。

评分标准：
1. 重要性：对科技行业或用户的影响程度
2. 新颖性：是否有新的进展或突破
3. 可理解性：是否容易向大众解释
4. 时效性：是否是最新发生的事件

新闻列表：
{articles_text}

请返回 JSON 格式，包含选中的新闻序号（从1开始）和简短理由：
{{
  "selected": [
    {{"index": 1, "reason": "重大技术突破"}},
    {{"index": 3, "reason": "影响广泛的政策变化"}},
    ...
  ]
}}

只返回 JSON，不要其他文字。"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是专业的科技新闻编辑。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            result_text = response.choices[0].message.content.strip()

            # 解析 JSON 结果
            import json
            result = json.loads(result_text)
            selected_indices = [item["index"] - 1 for item in result["selected"]]  # 转为0-based

            # 根据选中的索引返回文章
            selected_articles = [articles[i] for i in selected_indices if i < len(articles)]

            print(f"  ✅ AI 选出 {len(selected_articles)} 篇优质新闻")

            return selected_articles

        except Exception as e:
            print(f"  ⚠️ AI 评分失败: {e}")
            print(f"  📊 回退到按时间排序，返回前 {max_count} 篇")
            return articles[:max_count]

    def _format_articles_for_ranking(self, articles: list) -> str:
        """格式化文章列表用于 AI 评分"""
        lines = []
        for i, article in enumerate(articles, 1):
            if isinstance(article, dict):
                title = article["title"]
                summary = article["summary"][:150]
                source = article["source"]
            else:
                title = article.title
                summary = article.summary[:150]
                source = article.source

            lines.append(f"{i}. 【{source}】{title}")
            lines.append(f"   {summary}...")
            lines.append("")

        return "\n".join(lines)


def main():
    """测试入口"""
    # 示例测试
    from news_sources import RSSFetcher

    fetcher = RSSFetcher()
    articles = fetcher.fetch_all()

    print(f"📰 获取到 {len(articles)} 篇新闻")

    ranker = NewsRanker()
    top_articles = ranker.rank_articles(articles, max_count=5)

    print(f"\n⭐ Top {len(top_articles)} 新闻:")
    for i, article in enumerate(top_articles, 1):
        print(f"{i}. {article.title}")


if __name__ == "__main__":
    main()
