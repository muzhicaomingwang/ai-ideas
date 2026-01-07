"""
播客脚本生成模块
将摘要后的文章组织成完整的播客脚本
"""

import random
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

from .summarizer import SummarizedArticle


@dataclass
class PodcastScript:
    """播客脚本"""
    title: str  # 播客标题
    date: str  # 日期
    intro: str  # 开场白
    segments: list[dict]  # 新闻片段列表
    outro: str  # 结束语
    total_articles: int  # 文章总数
    categories: list[str]  # 涉及的分类

    def to_full_text(self) -> str:
        """生成完整的播报文本"""
        parts = [self.intro]

        for segment in self.segments:
            parts.append(segment["text"])
            if segment.get("transition"):
                parts.append(segment["transition"])

        parts.append(self.outro)

        return "\n\n".join(parts)

    def to_ssml(self) -> str:
        """生成 SSML 格式（用于更好的语音合成控制）"""
        ssml_parts = ['<speak>']

        # 开场白
        ssml_parts.append(f'<p>{self.intro}</p>')
        ssml_parts.append('<break time="1s"/>')

        # 新闻片段
        for i, segment in enumerate(self.segments):
            ssml_parts.append(f'<p>{segment["text"]}</p>')

            if segment.get("transition"):
                ssml_parts.append('<break time="500ms"/>')
                ssml_parts.append(f'<p>{segment["transition"]}</p>')

            if i < len(self.segments) - 1:
                ssml_parts.append('<break time="800ms"/>')

        # 结束语
        ssml_parts.append('<break time="1s"/>')
        ssml_parts.append(f'<p>{self.outro}</p>')

        ssml_parts.append('</speak>')

        return "\n".join(ssml_parts)

    def save_to_file(self, output_dir: str = "output") -> str:
        """保存脚本到文件"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        filename = f"script-{self.date}.md"
        filepath = output_path / filename

        content = f"""# {self.title}

**日期**: {self.date}
**文章数**: {self.total_articles}
**分类**: {", ".join(self.categories)}

---

## 开场白

{self.intro}

---

## 新闻内容

"""
        for i, segment in enumerate(self.segments, 1):
            content += f"""### {i}. {segment.get('title', '新闻' + str(i))}

{segment['text']}

"""

        content += f"""---

## 结束语

{self.outro}
"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return str(filepath)


class ScriptWriter:
    """播客脚本生成器"""

    def __init__(self, config_path: str = "config/voice.yaml"):
        """
        初始化脚本生成器

        Args:
            config_path: 语音配置文件路径
        """
        self.config = self._load_config(config_path)
        self.script_config = self.config.get("script", {})

    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        path = Path(config_path)
        if not path.exists():
            project_root = Path(__file__).parent.parent.parent
            path = project_root / config_path

        if not path.exists():
            # 使用默认配置
            return self._default_config()

        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _default_config(self) -> dict:
        """默认配置"""
        return {
            "script": {
                "intro_template": "大家好，欢迎收听今日科技早报。今天是{date}，我是你的AI播报员。接下来为大家带来今天的科技新闻。",
                "transitions": [
                    "接下来是下一条新闻。",
                    "让我们来看下一条消息。",
                    "继续关注今天的其他新闻。",
                    "下面是另一条值得关注的新闻。",
                    "接着来看这条新闻。"
                ],
                "outro_template": "以上就是今天的全部新闻内容。感谢收听今日科技早报，我们明天同一时间再见。"
            }
        }

    def _format_date(self, date: Optional[datetime] = None) -> str:
        """格式化日期为中文"""
        if date is None:
            date = datetime.now()

        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        weekday = weekdays[date.weekday()]

        return f"{date.year}年{date.month}月{date.day}日，{weekday}"

    def _generate_intro(self, date: Optional[datetime] = None) -> str:
        """生成开场白"""
        template = self.script_config.get(
            "intro_template",
            "大家好，今天是{date}，欢迎收听今日科技早报。"
        )
        return template.format(date=self._format_date(date))

    def _generate_outro(self) -> str:
        """生成结束语"""
        return self.script_config.get(
            "outro_template",
            "以上就是今天的全部内容，感谢收听，我们明天再见。"
        )

    def _get_transition(self) -> str:
        """随机获取过渡语"""
        transitions = self.script_config.get("transitions", [
            "接下来是下一条新闻。"
        ])
        return random.choice(transitions)

    def _group_by_category(self, articles: list[SummarizedArticle]) -> dict[str, list]:
        """按分类分组文章"""
        grouped = {}
        for article in articles:
            category = article.category
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(article)
        return grouped

    def generate_script(
        self,
        articles: list[SummarizedArticle],
        date: Optional[datetime] = None,
        group_by_category: bool = False
    ) -> PodcastScript:
        """
        生成播客脚本

        Args:
            articles: 摘要后的文章列表
            date: 播报日期
            group_by_category: 是否按分类分组

        Returns:
            PodcastScript 对象
        """
        if date is None:
            date = datetime.now()

        date_str = date.strftime("%Y-%m-%d")
        date_display = self._format_date(date)

        # 生成开场白
        intro = self._generate_intro(date)

        # 生成新闻片段
        segments = []
        categories = set()

        if group_by_category:
            # 按分类分组
            grouped = self._group_by_category(articles)
            for category, category_articles in grouped.items():
                categories.add(category)
                # 添加分类标题
                segments.append({
                    "title": f"{category}新闻",
                    "text": f"首先来看{category}领域的新闻。",
                    "transition": None
                })

                for i, article in enumerate(category_articles):
                    is_last = (i == len(category_articles) - 1)
                    segments.append({
                        "title": article.title,
                        "text": article.podcast_text,
                        "transition": None if is_last else self._get_transition()
                    })
        else:
            # 顺序排列
            for i, article in enumerate(articles):
                categories.add(article.category)
                is_last = (i == len(articles) - 1)
                segments.append({
                    "title": article.title,
                    "text": article.podcast_text,
                    "transition": None if is_last else self._get_transition()
                })

        # 生成结束语
        outro = self._generate_outro()

        return PodcastScript(
            title=f"今日科技早报 - {date_display}",
            date=date_str,
            intro=intro,
            segments=segments,
            outro=outro,
            total_articles=len(articles),
            categories=list(categories)
        )


def main():
    """测试入口"""
    from news_sources import RSSFetcher
    from .summarizer import SimpleSummarizer

    # 获取新闻
    print("📰 获取新闻...")
    fetcher = RSSFetcher()
    articles = fetcher.fetch_all()

    if not articles:
        print("没有获取到文章")
        return

    # 摘要处理
    print("\n📝 处理摘要...")
    summarizer = SimpleSummarizer()
    summarized = summarizer.summarize_batch(articles[:5])

    # 生成脚本
    print("\n📜 生成脚本...")
    writer = ScriptWriter()
    script = writer.generate_script(summarized)

    # 输出结果
    print("\n" + "=" * 50)
    print(f"📻 {script.title}")
    print("=" * 50)
    print(f"\n文章数: {script.total_articles}")
    print(f"分类: {', '.join(script.categories)}")

    print("\n--- 完整脚本 ---\n")
    print(script.to_full_text())

    # 保存脚本
    filepath = script.save_to_file()
    print(f"\n✅ 脚本已保存到: {filepath}")


if __name__ == "__main__":
    main()
