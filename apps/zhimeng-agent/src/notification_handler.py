"""
Claude Code 通知处理器

接收来自 Claude Code Hook 的通知请求，并通过飞书发送消息给用户。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal, Dict, Any
from datetime import datetime
from .feishu_bot import get_feishu_bot

router = APIRouter()

class NotificationRequest(BaseModel):
    """通知请求模型"""
    type: Literal["ask_user", "todo_complete", "session_complete", "error", "task_start"]
    session_id: str
    timestamp: str
    cwd: str
    data: Dict[str, Any]

# 王植萌的飞书 open_id
RECIPIENT_OPEN_ID = "ou_18b8063b232cbdec73ea1541dfb74890"


def format_options(options):
    """格式化选项列表"""
    if isinstance(options, list):
        return "\n".join([f"{i+1}️⃣ {opt}" for i, opt in enumerate(options)])
    return "N/A"


def format_files(files):
    """格式化文件列表"""
    if not files:
        return "  - 无"
    # 最多显示10个文件
    displayed = files[:10]
    result = "\n".join([f"  - {f}" for f in displayed])
    if len(files) > 10:
        result += f"\n  - ... 还有 {len(files) - 10} 个文件"
    return result


# 消息模板定义
TEMPLATES = {
    "ask_user": {
        "title": "🤔 Claude Code - 需要您的决策",
        "template": "blue",
        "format": lambda d: f"""❓ 问题：
{d.get('question', 'N/A')}

选项：
{format_options(d.get('options', []))}"""
    },
    "todo_complete": {
        "title": "✅ Claude Code - 任务完成",
        "template": "green",
        "format": lambda d: f"""📋 任务：{d.get('task', 'N/A')}
✓ 状态：已完成

📊 进度：{d.get('progress', 'N/A')} ({d.get('percent', 0)}%)"""
    },
    "session_complete": {
        "title": "🎉 Claude Code - 会话任务全部完成",
        "template": "green",
        "format": lambda d: f"""📊 总览：
  - 完成任务数：{d.get('total_tasks', 'N/A')}
  - 总耗时：{d.get('duration', 'N/A')}
  - 对话轮数：{d.get('conversation_turns', 'N/A')}

📁 生成文件：
{format_files(d.get('files_modified', []))}

💬 总结：{d.get('summary', 'N/A')}"""
    },
    "error": {
        "title": "⚠️ Claude Code - 需要人工介入",
        "template": "red",
        "format": lambda d: f"""❌ 错误类型：{d.get('error_type', 'N/A')}
📋 相关工具：{d.get('tool_name', 'N/A')}
📝 上下文：{d.get('context', 'N/A')}

详情：
{d.get('error_message', 'N/A')[:500]}

💡 建议：
{d.get('suggestion', '请检查日志并手动处理')}"""
    },
    "task_start": {
        "title": "🚀 Claude Code - 新任务启动",
        "template": "blue",
        "format": lambda d: f"""📋 任务：{d.get('task', 'N/A')}
📊 当前进度：{d.get('progress', 'N/A')}"""
    }
}


@router.post("/notify")
async def send_notification(req: NotificationRequest):
    """
    接收 Claude Code 通知并发送飞书消息

    Args:
        req: 通知请求，包含类型、数据等信息

    Returns:
        dict: 执行状态和类型

    注意：
        即使发送失败也返回成功状态，避免影响 Claude Code 正常运行
    """
    try:
        # 获取消息模板
        template = TEMPLATES.get(req.type)
        if not template:
            raise HTTPException(400, f"Unknown notification type: {req.type}")

        # 构建消息内容
        content = template["format"](req.data)

        # 添加通用信息（时间和工作目录）
        content += f"\n\n⏰ {req.timestamp}\n📂 {req.cwd}"

        # 发送飞书卡片消息
        bot = get_feishu_bot()
        await bot.send_card(
            receive_id=RECIPIENT_OPEN_ID,
            title=template["title"],
            content=content,
            template=template["template"]
        )

        print(f"[Notification] Sent {req.type} notification for session {req.session_id}")
        return {"status": "success", "type": req.type, "session_id": req.session_id}

    except Exception as e:
        # 记录错误但不抛出异常，避免影响 Claude Code
        print(f"[Notification Error] Failed to send {req.type} notification: {e}")
        # 仍然返回成功状态，因为通知失败不应该阻断 Claude Code 的正常运行
        return {"status": "error", "message": str(e), "type": req.type}


@router.get("/notify/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "claude-code-notifier",
        "recipient": RECIPIENT_OPEN_ID
    }
