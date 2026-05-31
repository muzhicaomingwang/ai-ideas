"""飞书个人域 Claude Code Bot

通过个人域飞书应用的 WebSocket 长连接接收消息，
调用本地 claude CLI 处理后回复。

启动方式:
    cd /Users/qitmac001395/workspace/QAL/ideas/apps/zhimeng-agent
    poetry run python src/claude_code_bot.py
"""

import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

# 设置工作目录
os.chdir(Path(__file__).parent.parent)
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("claude_code_bot")

# 个人域凭证
PERSONAL_APP_ID = os.environ.get("PERSONAL_FEISHU_APP_ID", "cli_aa969cb71db85cc8")
PERSONAL_APP_SECRET = os.environ.get(
    "PERSONAL_FEISHU_APP_SECRET", "JmXLj9PgyDlUGb9TlqtA0bz6ePbxiUz3"
)

# Claude Code 工作目录
CLAUDE_CWD = "/Users/qitmac001395/Documents/Obsidian Vault"

# 飞书消息长度限制（保守值）
MAX_REPLY_LENGTH = 4000

# Claude CLI 超时（秒）
CLAUDE_TIMEOUT = 120


def call_claude_code(question: str, timeout: int = CLAUDE_TIMEOUT) -> str:
    """调用本地 claude CLI 处理问题"""
    logger.info(f"调用 claude -p，问题: {question[:80]}...")
    try:
        # 清除嵌套检测环境变量，确保 claude CLI 可正常启动
        env = os.environ.copy()
        env.pop("CLAUDE_CODE_ENTRYPOINT", None)
        env.pop("CLAUDECODE", None)

        result = subprocess.run(
            ["claude", "-p", question],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=CLAUDE_CWD,
            env=env,
        )
        output = result.stdout.strip()
        if not output:
            output = result.stderr.strip()
        if not output:
            output = "(claude 未返回内容)"
        return output
    except subprocess.TimeoutExpired:
        return f"(claude 执行超时，已超过 {timeout} 秒)"
    except FileNotFoundError:
        return "(未找到 claude 命令，请确认已安装 Claude Code CLI)"
    except Exception as e:
        return f"(claude 调用失败: {e})"


def truncate_reply(text: str, max_length: int = MAX_REPLY_LENGTH) -> str:
    """截断超长回复"""
    if len(text) <= max_length:
        return text
    return text[: max_length - 20] + "\n\n...(回复已截断)"


def create_claude_code_handler():
    """创建 Claude Code 消息处理器"""
    import lark_oapi as lark
    from lark_oapi.api.im.v1 import CreateMessageRequest, CreateMessageRequestBody

    # 消息去重
    processed_messages = {}
    MAX_CACHE_SIZE = 1000

    # 构建 lark 客户端（复用）
    lark_client = (
        lark.Client.builder().app_id(PERSONAL_APP_ID).app_secret(PERSONAL_APP_SECRET).build()
    )

    def handle_message(event_data):
        nonlocal processed_messages

        try:
            message = event_data.message
            sender = event_data.sender

            # 去重
            message_id = message.message_id
            if message_id in processed_messages:
                logger.info(f"跳过重复消息: {message_id}")
                return
            processed_messages[message_id] = time.time()

            # 清理缓存
            if len(processed_messages) > MAX_CACHE_SIZE:
                cutoff = time.time() - 3600
                processed_messages = {
                    k: v for k, v in processed_messages.items() if v > cutoff
                }

            # 仅处理文本消息
            if message.message_type != "text":
                logger.info(f"跳过非文本消息: {message.message_type}")
                return

            # 解析文本
            try:
                text_content = json.loads(message.content)
                question = text_content.get("text", "").strip()
            except json.JSONDecodeError:
                question = message.content.strip()

            if not question:
                return

            open_id = sender.sender_id.open_id
            logger.info(f"收到问题 (from {open_id}): {question}")

            # 调用 Claude Code
            answer = call_claude_code(question)
            reply_text = truncate_reply(answer)

            logger.info(f"Claude Code 回复 ({len(reply_text)} 字): {reply_text[:100]}...")

            # 发送回复
            request = (
                CreateMessageRequest.builder()
                .receive_id_type("open_id")
                .request_body(
                    CreateMessageRequestBody.builder()
                    .receive_id(open_id)
                    .msg_type("text")
                    .content(json.dumps({"text": reply_text}))
                    .build()
                )
                .build()
            )

            response = lark_client.im.v1.message.create(request)

            if response.success():
                logger.info(f"已回复用户: {open_id}")
            else:
                logger.error(f"发送回复失败: {response.code} - {response.msg}")

        except Exception as e:
            logger.error(f"处理消息失败: {e}", exc_info=True)

    return handle_message


def main():
    """启动个人域 Claude Code Bot"""
    import lark_oapi as lark
    from lark_oapi.ws import Client as WsClient

    logger.info(f"个人域 App ID: {PERSONAL_APP_ID}")
    logger.info(f"Claude CWD: {CLAUDE_CWD}")

    handler = create_claude_code_handler()

    # 注册消息事件
    event_handler = (
        lark.EventDispatcherHandler.builder("", "")
        .register_p2_im_message_receive_v1(
            lambda data: handler(data.event)
        )
        .build()
    )

    # WebSocket 客户端
    ws_client = WsClient(
        PERSONAL_APP_ID,
        PERSONAL_APP_SECRET,
        event_handler=event_handler,
        log_level=lark.LogLevel.INFO,
    )

    logger.info("启动飞书个人域长连接...")
    try:
        ws_client.start()
    except KeyboardInterrupt:
        logger.info("已停止")


if __name__ == "__main__":
    main()
