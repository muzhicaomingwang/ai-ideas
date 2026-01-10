"""
高质量对话脚本生成器 (使用 Anthropic Claude)
生成 NotebookLM 风格的双人深度对话播客
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from anthropic import Anthropic

from .summarizer import SummarizedArticle


@dataclass
class DialogueLine:
    speaker: str  # "Host A" or "Host B" or "Sound"
    text: str
    emotion: str = "neutral"


@dataclass
class DialogueScript:
    title: str
    date: str
    lines: List[DialogueLine]
    total_duration_estimate: int  # seconds

    def save_to_file(self, output_dir: str = "output/scripts") -> str:
        """保存对话脚本到 JSON 和 Markdown"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存 Markdown
        md_path = f"{output_dir}/dialogue-{self.date}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# {self.title}\n\n")
            f.write(f"**日期**: {self.date}\n")
            f.write(f"**格式**: Deep Dive 双人对话\n\n")
            f.write("---\n\n")
            
            for line in self.lines:
                if line.speaker == "Sound":
                    f.write(f"**🎵 {line.speaker}**: {line.text}\n\n")
                else:
                    speaker_icon = "🎙️" if line.speaker == "Host A" else "💬"
                    f.write(f"**{speaker_icon} {line.speaker}** ({line.emotion}): {line.text}\n\n")
        
        # 保存 JSON
        json_path = f"{output_dir}/dialogue-{self.date}.json"
        data = {
            "title": self.title,
            "date": self.date,
            "lines": [
                {"speaker": l.speaker, "text": l.text, "emotion": l.emotion}
                for l in self.lines
            ]
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return md_path


class ClaudeDialogueWriter:
    """基于 Anthropic Claude 的高质量对话生成器"""

    def __init__(self, model_name: str = "claude-sonnet-4-20250514"):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("需要设置 ANTHROPIC_API_KEY 环境变量")
        
        self.client = Anthropic(api_key=api_key)
        self.model = model_name

    def filter_quality_news(self, articles: List[SummarizedArticle]) -> List[SummarizedArticle]:
        """
        过滤低质量新闻
        
        排除：
        - 股票减持/增持公告
        - 纯财务数据披露
        - 晚报/早报聚合类
        """
        low_quality_keywords = [
            "减持", "增持", "股份", "ST", "*ST",
            "晚报", "早报", "盘前", "盘后",
            "涨停", "跌停", "连板",
            "召回", "公告", "公司股份"
        ]
        
        filtered = []
        for article in articles:
            title = article.title.lower() if hasattr(article, 'title') else ""
            
            # 检查是否包含低质量关键词
            is_low_quality = any(kw in title for kw in low_quality_keywords)
            
            if not is_low_quality:
                filtered.append(article)
        
        print(f"  📋 过滤新闻: {len(articles)} → {len(filtered)} 篇 (移除 {len(articles) - len(filtered)} 篇低质量内容)")
        return filtered

    def generate_dialogue(
        self, 
        articles: List[SummarizedArticle], 
        date: Optional[datetime] = None,
        host_a_name: str = "植萌",
        host_b_name: str = "小雅"
    ) -> DialogueScript:
        """
        生成高质量双人对话脚本
        
        Args:
            articles: 新闻文章列表
            date: 日期
            host_a_name: 主持人A名称
            host_b_name: 主持人B名称
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        
        # 过滤低质量新闻
        quality_articles = self.filter_quality_news(articles)
        
        if not quality_articles:
            print("  ⚠️ 过滤后没有剩余新闻，使用原始列表")
            quality_articles = articles[:5]  # 最多取5条
        
        # 准备新闻上下文
        news_context = self._prepare_news_context(quality_articles)
        
        # 构建高质量 Prompt
        system_prompt = f"""你是一位资深播客制作人，擅长制作 NotebookLM 风格的深度科技对话节目。

你的任务是将今日科技新闻转化为一段自然、专业、有洞察力的双人对话。

## 主持人设定

**{host_a_name}** (Host A): 
- 角色：主理人，负责引导对话
- 风格：充满好奇心，善于用通俗比喻解释复杂概念
- 语言：自然亲切，会用"诶""哇""真的假的"等口语化表达

**{host_b_name}** (Host B):
- 角色：技术专家，提供深度分析
- 风格：理性专业，但不呆板，会适时幽默
- 语言：有条理，善于总结要点

## 对话要求

1. **开场白 (Cold Open)**: 用一个吸引人的话题切入，不要说"大家好"
2. **自然过渡**: 话题之间要有逻辑连接，不要生硬切换
3. **深度分析**: 不是念新闻，而是讨论新闻背后的意义
4. **互动感强**: 两人要有真实的对话感，包括:
   - 追问："等等，你是说...?"
   - 认同："对对对，这个很关键"
   - 质疑："但是我觉得..."
   - 补充："而且你注意到没有..."
5. **结尾**: 留一个思考问题给听众，然后自然收尾

## 输出格式

必须输出合法的 JSON 数组:
```json
[
  {{"speaker": "Sound", "text": "[片头音乐渐入]", "emotion": "energetic"}},
  {{"speaker": "Host A", "text": "对话内容...", "emotion": "curious"}},
  {{"speaker": "Host B", "text": "对话内容...", "emotion": "thoughtful"}}
]
```

emotion 可选值: excited, curious, thoughtful, surprised, amused, serious, calm, energetic

## 重要提醒
- 语言：中文（专业术语可保留英文）
- 长度：约 15-20 轮对话，预计 8-12 分钟音频
- 只输出 JSON，不要其他任何文字"""

        user_prompt = f"""今天是 {date_str}。

请将以下科技新闻转化为 {host_a_name} 和 {host_b_name} 之间的深度对话：

{news_context}

要求：
1. 选择 2-3 个最有讨论价值的话题深入展开
2. 找到新闻之间的关联性
3. 加入行业背景和个人见解
4. 让对话听起来像两个朋友在聊天，而不是在播报新闻

请直接输出 JSON 数组。"""

        print(f"  🤖 正在使用 Claude ({self.model}) 生成深度对话...")
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                system=system_prompt
            )
            
            # 提取 JSON
            raw_text = response.content[0].text.strip()
            
            # 尝试解析 JSON
            dialogue_data = self._parse_json_response(raw_text)
            
            lines = []
            for item in dialogue_data:
                lines.append(DialogueLine(
                    speaker=item.get("speaker", "Host A"),
                    text=item.get("text", ""),
                    emotion=item.get("emotion", "neutral")
                ))
            
            print(f"  ✅ 生成 {len(lines)} 句对话")
            
            return DialogueScript(
                title=f"科技早报 Deep Dive - {date_str}",
                date=date_str,
                lines=lines,
                total_duration_estimate=len(lines) * 8  # 每句约8秒
            )
            
        except Exception as e:
            print(f"  ❌ 对话生成失败: {e}")
            return self._create_fallback_script(date_str, quality_articles)

    def _prepare_news_context(self, articles: List[SummarizedArticle]) -> str:
        """准备新闻上下文"""
        lines = []
        for i, article in enumerate(articles, 1):
            title = article.title if hasattr(article, 'title') else str(article)
            summary = article.summary if hasattr(article, 'summary') else ""
            podcast_text = article.podcast_text if hasattr(article, 'podcast_text') else ""
            category = article.category if hasattr(article, 'category') else "科技"
            
            lines.append(f"### 新闻 {i}: {title}")
            lines.append(f"**分类**: {category}")
            lines.append(f"**摘要**: {summary}")
            if podcast_text:
                lines.append(f"**要点**: {podcast_text}")
            lines.append("")
        
        return "\n".join(lines)

    def _parse_json_response(self, text: str) -> list:
        """解析 JSON 响应，处理可能的格式问题"""
        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # 尝试提取 JSON 块
        import re
        json_match = re.search(r'\[[\s\S]*\]', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # 尝试移除 markdown 代码块标记
        cleaned = text.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)

    def _create_fallback_script(self, date_str: str, articles: list) -> DialogueScript:
        """创建备用脚本"""
        lines = [
            DialogueLine("Sound", "[片头音乐]", "energetic"),
            DialogueLine("Host A", f"大家好，欢迎收听今日科技早报，今天是{date_str}。", "calm"),
            DialogueLine("Host B", "今天我们为大家准备了一些有趣的科技资讯。", "calm"),
        ]
        
        for article in articles[:3]:
            title = article.title if hasattr(article, 'title') else str(article)
            lines.append(DialogueLine("Host A", f"我们来聊聊这条新闻：{title}", "curious"))
            lines.append(DialogueLine("Host B", "这确实是一个值得关注的话题。", "thoughtful"))
        
        lines.extend([
            DialogueLine("Host A", "好的，今天的节目就到这里。", "calm"),
            DialogueLine("Host B", "感谢收听，我们下期再见！", "energetic"),
            DialogueLine("Sound", "[片尾音乐]", "calm"),
        ])
        
        return DialogueScript(
            title=f"科技早报 - {date_str}",
            date=date_str,
            lines=lines,
            total_duration_estimate=len(lines) * 5
        )


def main():
    """测试入口"""
    from dotenv import load_dotenv
    load_dotenv()
    
    from .summarizer import SummarizedArticle
    
    # Mock 测试数据
    articles = [
        SummarizedArticle(
            title="吉利发布全域AI2.0架构和世界行为模型",
            summary="吉利在CES发布WAM世界行为模型，采用分层设计，实现从理解-规划到预演-判断-修正的闭环。",
            podcast_text="这是自动驾驶领域的重要突破，与VLA路线形成差异化竞争。",
            url="http://example.com",
            category="汽车科技",
            publish_date=datetime.now()
        ),
        SummarizedArticle(
            title="欧洲转向中国卫星技术合作",
            summary="中国卫星技术成为欧洲打破僵局的选择，标志着技术平权时代到来。",
            podcast_text="这反映了全球科技格局的重大变化。",
            url="http://example.com",
            category="航天",
            publish_date=datetime.now()
        )
    ]
    
    writer = ClaudeDialogueWriter()
    script = writer.generate_dialogue(articles)
    
    saved_path = script.save_to_file("output/test_claude_dialogue")
    print(f"✅ 脚本已生成: {saved_path}")
    
    print("\n--- 预览 ---")
    for line in script.lines[:8]:
        print(f"{line.speaker}: {line.text[:50]}...")


if __name__ == "__main__":
    main()
