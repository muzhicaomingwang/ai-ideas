"""飞书机器人集成

处理飞书消息事件，调用问答接口并回复。
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional

import httpx

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeishuBot:
    """飞书机器人客户端"""

    BASE_URL = "https://open.feishu.cn/open-apis"

    def __init__(
        self,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
    ):
        self.app_id = app_id or settings.feishu_app_id
        self.app_secret = app_secret or settings.feishu_app_secret
        self._tenant_access_token: Optional[str] = None
        self._token_expires_at: float = 0

    async def _get_tenant_access_token(self) -> str:
        """获取 tenant_access_token"""
        import time

        # 检查缓存
        if self._tenant_access_token and time.time() < self._token_expires_at:
            return self._tenant_access_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/auth/v3/tenant_access_token/internal",
                json={
                    "app_id": self.app_id,
                    "app_secret": self.app_secret,
                },
            )
            data = response.json()

            if data.get("code") != 0:
                raise Exception(f"获取 token 失败: {data}")

            self._tenant_access_token = data["tenant_access_token"]
            self._token_expires_at = time.time() + data["expire"] - 60

            return self._tenant_access_token

    async def send_message(
        self,
        receive_id: str,
        content: str,
        msg_type: str = "text",
        receive_id_type: str = "open_id",
    ) -> dict:
        """发送消息

        Args:
            receive_id: 接收者 ID
            content: 消息内容（JSON 字符串）
            msg_type: 消息类型 (text/post/interactive)
            receive_id_type: ID 类型 (open_id/user_id/chat_id)

        Returns:
            API 响应
        """
        token = await self._get_tenant_access_token()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/im/v1/messages",
                params={"receive_id_type": receive_id_type},
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "receive_id": receive_id,
                    "msg_type": msg_type,
                    "content": content,
                },
            )
            return response.json()

    async def send_text(self, receive_id: str, text: str) -> dict:
        """发送文本消息"""
        content = json.dumps({"text": text})
        return await self.send_message(receive_id, content, "text")

    async def send_card(
        self,
        receive_id: str,
        title: str,
        content: str,
        template: str = "blue",
    ) -> dict:
        """发送卡片消息

        Args:
            receive_id: 接收者 open_id
            title: 卡片标题
            content: Markdown 内容
            template: 卡片颜色模板

        Returns:
            API 响应
        """
        card = {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": template,
            },
            "elements": [
                {"tag": "markdown", "content": content},
            ],
        }

        return await self.send_message(
            receive_id,
            json.dumps(card),
            "interactive",
        )

    async def send_answer(
        self,
        receive_id: str,
        question: str,
        answer: str,
        sources: Optional[list] = None,
    ) -> dict:
        """发送问答结果卡片

        Args:
            receive_id: 接收者 open_id
            question: 用户问题
            answer: AI 回答
            sources: 来源列表

        Returns:
            API 响应
        """
        # 构建来源引用
        sources_text = ""
        if sources:
            sources_text = "\n\n---\n**参考来源**:\n"
            for s in sources[:3]:  # 最多显示 3 个来源
                sources_text += f"- {s['file']} (相关度: {s['relevance']})\n"

        # 截断过长的回答
        max_length = 3000
        if len(answer) > max_length:
            answer = answer[:max_length] + "\n\n...(内容过长，已截断)"

        content = f"**Q: {question}**\n\n{answer}{sources_text}"

        return await self.send_card(
            receive_id=receive_id,
            title="💬 zhimeng's Agent",
            content=content,
        )


def parse_message_content(content: str) -> str:
    """解析飞书消息内容

    飞书消息内容是 JSON 格式，需要提取纯文本。
    """
    try:
        data = json.loads(content)
        # 文本消息
        if "text" in data:
            return data["text"]
        # 富文本消息
        if "content" in data:
            texts = []
            for line in data.get("content", []):
                for item in line:
                    if item.get("tag") == "text":
                        texts.append(item.get("text", ""))
            return " ".join(texts)
    except json.JSONDecodeError:
        pass
    return content


def verify_signature(
    timestamp: str,
    nonce: str,
    body: str,
    signature: str,
    encrypt_key: str,
) -> bool:
    """验证飞书请求签名"""
    content = timestamp + nonce + encrypt_key + body
    computed = hashlib.sha256(content.encode()).hexdigest()
    return computed == signature


# 单例
_bot_instance: Optional[FeishuBot] = None


def get_feishu_bot() -> FeishuBot:
    """获取飞书机器人单例"""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = FeishuBot()
    return _bot_instance
