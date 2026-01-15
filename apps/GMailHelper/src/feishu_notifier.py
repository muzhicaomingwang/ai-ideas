"""
飞书通知模块

负责发送处理报告到飞书
"""

import json
import time
import requests
from typing import Dict


class FeishuNotifier:
    """飞书通知器"""

    def __init__(self, app_id: str, app_secret: str, user_open_id: str):
        """
        初始化飞书通知器

        Args:
            app_id: 飞书应用ID
            app_secret: 飞书应用密钥
            user_open_id: 接收人的open_id
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.user_open_id = user_open_id
        self.tenant_access_token = None
        self.token_expires_at = 0

    def _get_tenant_access_token(self) -> str:
        """
        获取tenant_access_token

        Returns:
            访问令牌
        """
        # 检查缓存是否过期
        if self.tenant_access_token and time.time() < self.token_expires_at:
            return self.tenant_access_token

        # 请求新token
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()

        if result.get("code") != 0:
            raise RuntimeError(f"获取飞书token失败: {result.get('msg')}")

        self.tenant_access_token = result["tenant_access_token"]
        self.token_expires_at = time.time() + result.get("expire", 7200) - 300  # 提前5分钟过期

        return self.tenant_access_token

    def send_daily_report(self, stats: Dict, details: Dict):
        """
        发送每日处理报告（卡片消息）

        Args:
            stats: 统计数据
            details: 详细信息
        """
        # 构造卡片内容
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        card_content = {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"📧 Gmail清理报告 - {today}"
                },
                "template": "blue"
            },
            "elements": [
                # 统计摘要
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**总邮件数**\n{stats['total']}"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**已处理**\n{stats['processed']}"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**清理率**\n{stats['processed']/max(stats['total'],1)*100:.1f}%"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**模式**\n{'模拟' if stats.get('dry_run') else '实际'}"
                            }
                        }
                    ]
                },
                {"tag": "hr"},
                # 处理详情
                {
                    "tag": "markdown",
                    "content": self._build_details_markdown(details)
                }
            ]
        }

        # 添加错误信息（如果有）
        if stats.get('errors', 0) > 0:
            card_content["elements"].append({"tag": "hr"})
            card_content["elements"].append({
                "tag": "markdown",
                "content": f"⚠️ **处理失败**: {stats['errors']} 封邮件"
            })

        # 发送消息
        self._send_card_message(card_content)

    def _build_details_markdown(self, details: Dict) -> str:
        """构造详细信息的Markdown"""
        lines = []

        # 营销邮件
        marketing_count = details.get('marketing', {}).get('count', 0)
        if marketing_count > 0:
            lines.append(f"**营销邮件**: {marketing_count}封（归档）")

        # 通知邮件
        notification_count = details.get('notification', {}).get('count', 0)
        if notification_count > 0:
            lines.append(f"**通知邮件**: {notification_count}封（归档）")

        # 论坛邮件
        forum_count = details.get('forum', {}).get('count', 0)
        if forum_count > 0:
            lines.append(f"**论坛邮件**: {forum_count}封（归档）")

        # AI分类
        ai_count = details.get('ai_classification', {})
        if ai_count:
            ai_total = sum(ai_count.values())
            lines.append(f"**AI分类**: {ai_total}封")

        return "\n".join(lines) if lines else "无邮件处理"

    def _send_card_message(self, card_content: Dict):
        """
        发送卡片消息

        Args:
            card_content: 卡片内容
        """
        token = self._get_tenant_access_token()

        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        data = {
            "receive_id": self.user_open_id,
            "msg_type": "interactive",
            "content": json.dumps(card_content)
        }

        params = {"receive_id_type": "open_id"}

        response = requests.post(url, headers=headers, json=data, params=params)
        response.raise_for_status()

        result = response.json()

        if result.get("code") != 0:
            raise RuntimeError(f"发送飞书消息失败: {result.get('msg')}")

        print(f"✅ 飞书通知已发送（message_id: {result.get('data', {}).get('message_id')}）")

    def send_error_notification(self, error_message: str):
        """
        发送错误通知

        Args:
            error_message: 错误信息
        """
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        card_content = {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "❌ GMailHelper 执行失败"
                },
                "template": "red"
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": f"**时间**: {today}\n\n**错误信息**:\n```\n{error_message}\n```"
                }
            ]
        }

        try:
            self._send_card_message(card_content)
        except Exception as e:
            print(f"❌ 发送错误通知失败: {e}")
