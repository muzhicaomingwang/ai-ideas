"""飞书长连接客户端

用于本地开发，无需公网 IP。
通过 WebSocket 长连接实时接收飞书消息。
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Callable, Optional

import os
import sys

# 设置工作目录
os.chdir(Path(__file__).parent.parent)
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv("config/.env")

from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 消息处理回调类型
MessageHandler = Callable[[dict], None]


class FeishuWsClient:
    """飞书 WebSocket 长连接客户端"""

    def __init__(
        self,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        message_handler: Optional[MessageHandler] = None,
    ):
        self.app_id = app_id or settings.feishu_app_id
        self.app_secret = app_secret or settings.feishu_app_secret
        self.message_handler = message_handler
        self._client = None

    def set_message_handler(self, handler: MessageHandler):
        """设置消息处理回调"""
        self.message_handler = handler

    def start(self):
        """启动长连接客户端"""
        try:
            import lark_oapi as lark
            from lark_oapi.ws import Client as WsClient
        except ImportError as e:
            logger.error(f"导入 lark-oapi 失败: {e}")
            return

        # 定义消息处理器
        def handle_message(data):
            """处理消息事件"""
            try:
                logger.info(f"收到消息事件: {data}")

                # 解析事件数据
                if hasattr(data, 'event'):
                    event_data = data.event
                else:
                    event_data = data

                if self.message_handler:
                    self.message_handler(event_data)
            except Exception as e:
                logger.error(f"处理消息失败: {e}")

        # 创建事件处理器
        event_handler = lark.EventDispatcherHandler.builder("", "") \
            .register_p2_im_message_receive_v1(handle_message) \
            .build()

        # 创建 WebSocket 客户端
        self._client = WsClient(
            self.app_id,
            self.app_secret,
            event_handler=event_handler,
            log_level=lark.LogLevel.DEBUG if settings.debug else lark.LogLevel.INFO,
        )

        logger.info("启动飞书长连接...")
        self._client.start()

    def stop(self):
        """停止长连接"""
        if self._client:
            self._client.stop()
            logger.info("飞书长连接已断开")


def create_message_handler(ask_endpoint: str = "http://localhost:8001/ask"):
    """创建消息处理器

    Args:
        ask_endpoint: 问答接口地址

    Returns:
        消息处理回调函数
    """
    import httpx
    import lark_oapi as lark
    from lark_oapi.api.im.v1 import CreateMessageRequest, CreateMessageRequestBody

    # 消息去重缓存（message_id -> timestamp）
    processed_messages = {}
    MAX_CACHE_SIZE = 1000

    def handle_message(event_data):
        """处理消息并回复（同步版本）"""
        nonlocal processed_messages

        try:
            # event_data 是 P2ImMessageReceiveV1Data 对象，直接访问属性
            message = event_data.message
            sender = event_data.sender

            # 消息去重
            message_id = message.message_id
            if message_id in processed_messages:
                logger.info(f"跳过重复消息: {message_id}")
                return

            # 记录已处理的消息
            import time
            processed_messages[message_id] = time.time()

            # 清理过期缓存
            if len(processed_messages) > MAX_CACHE_SIZE:
                cutoff = time.time() - 3600  # 1小时前
                processed_messages = {k: v for k, v in processed_messages.items() if v > cutoff}

            # 提取消息内容
            content = message.content
            chat_id = message.chat_id
            message_type = message.message_type

            # 提取发送者
            sender_id = sender.sender_id
            open_id = sender_id.open_id

            # 解析消息内容
            if message_type == "text":
                try:
                    text_content = json.loads(content)
                    question = text_content.get("text", "")
                except json.JSONDecodeError:
                    question = content
            else:
                logger.info(f"跳过非文本消息: {message_type}")
                return

            if not question.strip():
                return

            logger.info(f"收到问题: {question} (from: {open_id})")

            # 调用问答接口（同步）
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    ask_endpoint,
                    json={"question": question, "top_k": 5, "user_id": open_id},
                )
                result = response.json()

            answer = result.get("answer", "抱歉，我无法回答这个问题。")
            sources = result.get("sources", [])

            logger.info(f"获得回答: {answer[:100]}...")

            # 构建回复内容
            reply_content = answer
            if sources:
                reply_content += "\n\n📚 参考来源："
                for src in sources[:3]:
                    reply_content += f"\n• {src.get('file', 'unknown')}"

            # 使用 lark-oapi 发送回复
            lark_client = lark.Client.builder() \
                .app_id(settings.feishu_app_id) \
                .app_secret(settings.feishu_app_secret) \
                .build()

            request = CreateMessageRequest.builder() \
                .receive_id_type("open_id") \
                .request_body(CreateMessageRequestBody.builder()
                    .receive_id(open_id)
                    .msg_type("text")
                    .content(json.dumps({"text": reply_content}))
                    .build()) \
                .build()

            response = lark_client.im.v1.message.create(request)

            if response.success():
                logger.info(f"已回复用户: {open_id}")
            else:
                logger.error(f"发送回复失败: {response.code} - {response.msg}")

        except Exception as e:
            logger.error(f"处理消息失败: {e}", exc_info=True)

    return handle_message


def main():
    """启动长连接客户端"""
    # 创建消息处理器
    handler = create_message_handler()

    # 创建客户端
    client = FeishuWsClient(message_handler=handler)

    try:
        client.start()
    except KeyboardInterrupt:
        client.stop()


if __name__ == "__main__":
    main()
