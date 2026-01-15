"""
AI 邮件分类器

使用 Claude API 进行智能邮件分类
"""

from typing import Dict
from anthropic import Anthropic


class AIEmailClassifier:
    """AI邮件分类器（使用Claude API）"""

    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-20241022"):
        """
        初始化AI分类器

        Args:
            api_key: Anthropic API Key
            model: Claude模型（默认Haiku，成本低）
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def classify(self, email: Dict, prompt_template: str = None) -> str:
        """
        分类邮件

        Args:
            email: 邮件对象（包含from, subject, snippet）
            prompt_template: 自定义提示词模板（可选）

        Returns:
            分类结果（marketing/notification/forum/important/spam）
        """
        sender = email.get("from", "")
        subject = email.get("subject", "")
        snippet = email.get("snippet", "")[:200]  # 限制长度

        # 使用默认提示词或自定义提示词
        if prompt_template is None:
            prompt = f"""分析以下邮件类型，仅返回类型名称（不要解释）：

发件人: {sender}
主题: {subject}
摘要: {snippet}

类型选项：
- marketing: 营销邮件
- notification: 通知邮件
- forum: 论坛邮件
- important: 重要邮件
- spam: 垃圾邮件

请仅返回类型名称（如：marketing）"""
        else:
            prompt = prompt_template.format(
                sender=sender,
                subject=subject,
                snippet=snippet
            )

        try:
            # 调用Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=20,
                temperature=0,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # 提取分类结果
            category = response.content[0].text.strip().lower()

            # 验证分类结果
            valid_categories = ["marketing", "notification", "forum", "important", "spam"]
            if category not in valid_categories:
                # 如果返回的不是有效分类，默认为important
                return "important"

            return category

        except Exception as e:
            # AI分类失败，默认标记为important（人工处理）
            print(f"⚠️ AI分类失败: {e}")
            return "important"
