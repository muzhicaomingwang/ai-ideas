"""
对话式脚本生成器 (NotebookLM Style)
使用 Gemini Pro 将新闻转化为双人对谈脚本
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import google.generativeai as genai
from .summarizer import SummarizedArticle


@dataclass
class DialogueLine:
    speaker: str  # "Host A" or "Host B"
    text: str
    emotion: str = "neutral"  # excited, thoughtful, curious, etc.


@dataclass
class DialogueScript:
    title: str
    date: str
    lines: List[DialogueLine]
    total_duration_estimate: int  # seconds

    def save_to_file(self, output_dir: str = "output/scripts") -> str:
        """保存对话脚本到 JSON 和 Markdown"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存 Markdown (便于阅读)
        md_path = f"{output_dir}/dialogue-{self.date}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# {self.title}\n\n")
            f.write(f"**Date**: {self.date}\n")
            f.write(f"**Format**: Deep Dive Dialogue\n\n")
            f.write("---\n\n")
            
            for line in self.lines:
                speaker_icon = "🎙️" if line.speaker == "Host A" else "💡"
                f.write(f"**{speaker_icon} {line.speaker}** ({line.emotion}): {line.text}\n\n")
        
        # 保存 JSON (便于程序处理)
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


class DialogueWriter:
    """基于 Gemini Pro 的对话生成器"""

    def __init__(self, model_name: str = "gemini-2.5-pro"):
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("需要设置 GOOGLE_API_KEY 环境变量")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_dialogue(self, articles: List[SummarizedArticle], date: Optional[datetime] = None) -> DialogueScript:
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        
        # 1. 准备输入上下文
        context_text = f"Today's Date: {date_str}\n\nHere are the top news stories to discuss:\n\n"
        for i, article in enumerate(articles, 1):
            context_text += f"Story {i}: {article.title}\n"
            context_text += f"Summary: {article.summary}\n"
            context_text += f"Key Points: {article.podcast_text}\n"
            context_text += f"Category: {article.category}\n\n"

        # 2. 构建 Prompt
        prompt = """
        You are the producer of a high-quality tech podcast called "Tech Morning Deep Dive".
        Your task is to convert the provided news stories into a lively, natural, and insightful conversation between two hosts:
        
        **Host A (Alex)**: Energetic, leads the conversation, asks the "dumb" questions for the audience, often uses analogies.
        **Host B (Jamie)**: Analytical, an industry expert, provides depth, context, and skepticism.
        
        **Instructions:**
        1. Do NOT just read the news. Banter about it. Connect the dots between stories.
        2. Start with a catchy "Cold Open" (a hook before the intro music).
        3. Have a standard Intro ("Welcome back to Deep Dive...").
        4. Discuss the stories in a logical flow (group related topics).
        5. Use natural speech patterns (short sentences, interjections like "Right?", "Exactly.", "Wait, really?").
        6. End with a fun or thought-provoking Outro.
        7. The output MUST be valid JSON. 
        
        **Output Format (JSON Array of objects):**
        [
            {"speaker": "Host A", "text": "...", "emotion": "excited"},
            {"speaker": "Host B", "text": "...", "emotion": "neutral"}
        ]
        
        Language: Chinese (Mandarin), but use English technical terms where appropriate.
        Tone: Professional yet conversational (like a high-quality NPR or Gimlet Media show).
        Length: Aim for about 10-15 minutes of spoken content (approx 2000-2500 chars).
        """

        # 3. 调用 Gemini Pro
        print("🤖 正在调用 Gemini Pro 生成深度对话脚本...")
        response = self.model.generate_content(
            [prompt, context_text],
            generation_config={"response_mime_type": "application/json"}
        )

        # 4. 解析结果
        try:
            raw_json = response.text
            dialogue_data = json.loads(raw_json)
            
            lines = []
            for item in dialogue_data:
                lines.append(DialogueLine(
                    speaker=item.get("speaker", "Host A"),
                    text=item.get("text", ""),
                    emotion=item.get("emotion", "neutral")
                ))
            
            return DialogueScript(
                title=f"Tech Deep Dive - {date_str}",
                date=date_str,
                lines=lines,
                total_duration_estimate=len(lines) * 5  # 粗略估计
            )
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败: {e}")
            print(f"Raw output: {response.text[:500]}...")
            # Fallback simple script
            return DialogueScript(
                title="Error Generating Script",
                date=date_str,
                lines=[DialogueLine("Host A", "抱歉，今天的脚本生成出了一点小问题，请检查日志。")],
                total_duration_estimate=10
            )

def main():
    """测试对话生成"""
    from .summarizer import SummarizedArticle
    
    # Mock data
    articles = [
        SummarizedArticle(
            title="OpenAI发布GPT-5预览版",
            summary="OpenAI突袭发布新模型，推理能力大幅提升。",
            podcast_text="GPT-5在数学和编程测试中得分为98%，远超GPT-4。",
            url="http://example.com",
            category="AI",
            publish_date=datetime.now()
        ),
        SummarizedArticle(
            title="苹果宣布放弃Vision Pro产品线",
            summary="由于销量不佳，苹果决定暂停MR头显开发。",
            podcast_text="供应链消息确认，Vision Pro 2已取消生产计划。",
            url="http://example.com",
            category="Hardware",
            publish_date=datetime.now()
        )
    ]
    
    writer = DialogueWriter()
    script = writer.generate_dialogue(articles)
    
    saved_path = script.save_to_file("output/test_dialogue")
    print(f"✅ 脚本已生成: {saved_path}")
    
    # 打印前几行预览
    print("\n--- Preview ---")
    for line in script.lines[:5]:
        print(f"{line.speaker}: {line.text}")

if __name__ == "__main__":
    main()
