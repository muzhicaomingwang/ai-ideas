#!/usr/bin/env python3
"""
离线队列功能测试脚本
模拟网络失败场景并验证队列机制
"""

import json
import sys
from pathlib import Path

# 队列文件路径
QUEUE_FILE = Path(__file__).parent.parent / "logs" / "notification_queue" / "pending_messages.json"


def show_queue():
    """显示队列内容"""
    if not QUEUE_FILE.exists():
        print("📭 队列为空（文件不存在）")
        return

    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        queue = json.load(f)

    if not queue:
        print("📭 队列为空")
        return

    print(f"📬 队列中有 {len(queue)} 条消息:\n")
    for i, msg in enumerate(queue, 1):
        print(f"{i}. {msg.get('title')}")
        print(f"   日期: {msg.get('date')}")
        print(f"   入队时间: {msg.get('queued_at')}")
        print(f"   ID: {msg.get('id')}")
        print()


def add_test_message():
    """添加测试消息到队列"""
    from datetime import datetime

    test_msg = {
        "id": f"test_{int(datetime.now().timestamp())}",
        "title": "🧪 测试消息（可删除）",
        "content": "这是一条测试消息，用于验证队列功能",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "status": "success",
        "queued_at": datetime.now().isoformat(),
    }

    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)

    queue = []
    if QUEUE_FILE.exists():
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            queue = json.load(f)

    queue.append(test_msg)

    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

    print(f"✅ 已添加测试消息到队列")
    print(f"   当前队列: {len(queue)} 条")


def clear_queue():
    """清空队列"""
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)
    print("🗑️ 队列已清空")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="队列管理工具")
    parser.add_argument("--show", action="store_true", help="显示队列内容")
    parser.add_argument("--add-test", action="store_true", help="添加测试消息")
    parser.add_argument("--clear", action="store_true", help="清空队列")
    args = parser.parse_args()

    if args.clear:
        clear_queue()
    elif args.add_test:
        add_test_message()
    elif args.show:
        show_queue()
    else:
        # 默认显示队列
        show_queue()
