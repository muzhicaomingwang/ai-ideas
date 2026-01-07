"""LLM 客户端

支持 Anthropic Claude 和 OpenAI GPT。
"""

import logging
from pathlib import Path
from typing import List, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 系统提示词（已弃用，改用 smart_agent 中的动态提示词）
SYSTEM_PROMPT = """你是 zhimeng 的 AI 分身，由 Claude Opus 4.5 驱动的全能智能助手。

**核心定位**：你既是知识库的门户，更是一个具备强大推理能力的 AI 助手。

**回答原则**：
1. **直接回答**：用你的知识和推理能力直接回答问题，不要拘泥于参考资料
2. **灵活参考**：如果提供了参考资料，可以引用，但这不是必须的
3. **结构化输出**：使用清晰的标题、列表组织回答
4. **实用导向**：提供可操作的建议和具体例子
5. **个人风格**：以 zhimeng 的视角回答，分享独到见解

**重要**：你是全能 AI 助手，可以回答任何问题。参考资料只是补充，不是限制。"""


class LLMClient:
    """LLM 客户端"""

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.provider = provider or settings.llm_provider
        self.model = model or settings.llm_model

        # 初始化 LLM
        if self.provider == "anthropic":
            self.llm = ChatAnthropic(
                model=self.model,
                anthropic_api_key=settings.anthropic_api_key,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
            )
        elif self.provider == "openai":
            self.llm = ChatOpenAI(
                model=self.model,
                openai_api_key=settings.openai_api_key,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
            )
        else:
            raise ValueError(f"不支持的 LLM 提供商: {self.provider}")

        logger.info(f"LLM 客户端初始化完成: {self.provider}/{self.model}")

    def generate(
        self,
        question: str,
        context: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """生成回答

        Args:
            question: 用户问题
            context: 检索到的文档上下文
            system_prompt: 自定义系统提示词

        Returns:
            生成的回答
        """
        system = system_prompt or SYSTEM_PROMPT

        # 构建用户消息 - 不再强制基于文档回答
        has_context = context and "没有找到相关信息" not in context

        if has_context:
            user_message = f"""用户问题：{question}

以下是可能相关的参考资料（仅供参考，可以直接用你的知识回答）：

{context}

请直接回答用户问题。参考资料只是辅助，优先用你的知识和推理能力。"""
        else:
            user_message = f"""用户问题：{question}

请直接用你的知识和推理能力回答这个问题。"""

        messages = [
            SystemMessage(content=system),
            HumanMessage(content=user_message),
        ]

        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"LLM 生成失败: {e}")
            raise

    def chat(
        self,
        messages: List[dict],
        system_prompt: Optional[str] = None,
    ) -> str:
        """多轮对话

        Args:
            messages: 对话历史 [{"role": "user/assistant", "content": "..."}]
            system_prompt: 系统提示词

        Returns:
            生成的回答
        """
        system = system_prompt or SYSTEM_PROMPT

        formatted_messages = [SystemMessage(content=system)]
        for msg in messages:
            if msg["role"] == "user":
                formatted_messages.append(HumanMessage(content=msg["content"]))
            # TODO: 支持 assistant 消息

        try:
            response = self.llm.invoke(formatted_messages)
            return response.content
        except Exception as e:
            logger.error(f"LLM 对话失败: {e}")
            raise


# 单例模式
_llm_instance: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """获取 LLM 客户端单例"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMClient()
    return _llm_instance
