"""
邮件处理器模块

负责执行邮件处理动作（归档、标签、删除等）
"""

from typing import List, Dict
from gmail_client import GmailMCPClient


class EmailProcessor:
    """邮件处理器"""

    def __init__(self, gmail_client: GmailMCPClient, dry_run: bool = True):
        """
        初始化处理器

        Args:
            gmail_client: Gmail MCP客户端
            dry_run: 是否为模拟模式
        """
        self.gmail = gmail_client
        self.dry_run = dry_run

    def execute_actions(self, message_id: str, actions: List, logger):
        """
        执行邮件处理动作

        Args:
            message_id: 邮件ID
            actions: 动作列表
            logger: 日志记录器
        """
        add_labels = []
        remove_labels = []
        should_delete = False

        # 收集所有动作
        for action in actions:
            action_type = action.type if hasattr(action, 'type') else action.get('type')
            action_value = action.value if hasattr(action, 'value') else action.get('value')

            if action_type == "add_label":
                # 获取或创建标签
                label_id = self.gmail.get_or_create_label(action_value)
                add_labels.append(label_id)

            elif action_type == "archive":
                # 归档 = 移除INBOX标签
                remove_labels.append("INBOX")

            elif action_type == "mark_read":
                # 标记已读 = 移除UNREAD标签
                remove_labels.append("UNREAD")

            elif action_type == "delete":
                should_delete = True

        # 执行修改操作
        if add_labels or remove_labels:
            if self.dry_run:
                logger.info(
                    f"  [模拟] 修改邮件 {message_id}: "
                    f"添加标签={add_labels}, 移除标签={remove_labels}"
                )
            else:
                try:
                    self.gmail.modify_email(
                        message_id=message_id,
                        add_label_ids=add_labels,
                        remove_label_ids=remove_labels
                    )
                    logger.info(
                        f"  ✅ 已修改邮件 {message_id}: "
                        f"添加标签={add_labels}, 移除标签={remove_labels}"
                    )
                except Exception as e:
                    logger.error(f"  ❌ 修改邮件失败 {message_id}: {e}")
                    raise

        # 执行删除操作
        if should_delete:
            if self.dry_run:
                logger.info(f"  [模拟] 删除邮件 {message_id}")
            else:
                try:
                    self.gmail.delete_email(message_id)
                    logger.info(f"  ✅ 已删除邮件 {message_id}")
                except Exception as e:
                    logger.error(f"  ❌ 删除邮件失败 {message_id}: {e}")
                    raise

    def batch_execute_actions(
        self,
        message_ids: List[str],
        actions: List,
        logger,
        batch_size: int = 50
    ):
        """
        批量执行邮件处理动作

        Args:
            message_ids: 邮件ID列表
            actions: 动作列表
            logger: 日志记录器
            batch_size: 批次大小
        """
        if not message_ids:
            return

        add_labels = []
        remove_labels = []

        # 收集所有动作（批量操作不支持delete）
        for action in actions:
            action_type = action.type if hasattr(action, 'type') else action.get('type')
            action_value = action.value if hasattr(action, 'value') else action.get('value')

            if action_type == "add_label":
                label_id = self.gmail.get_or_create_label(action_value)
                add_labels.append(label_id)

            elif action_type == "archive":
                remove_labels.append("INBOX")

            elif action_type == "mark_read":
                remove_labels.append("UNREAD")

        # 分批执行
        for i in range(0, len(message_ids), batch_size):
            batch = message_ids[i:i + batch_size]

            if self.dry_run:
                logger.info(
                    f"  [模拟] 批量修改 {len(batch)} 封邮件: "
                    f"添加标签={add_labels}, 移除标签={remove_labels}"
                )
            else:
                try:
                    self.gmail.batch_modify_emails(
                        message_ids=batch,
                        add_label_ids=add_labels if add_labels else None,
                        remove_label_ids=remove_labels if remove_labels else None
                    )
                    logger.info(
                        f"  ✅ 批量修改 {len(batch)} 封邮件成功"
                    )
                except Exception as e:
                    logger.error(f"  ❌ 批量修改失败: {e}")
                    # 降级为逐封处理
                    logger.info("  ⚠️ 降级为逐封处理...")
                    for msg_id in batch:
                        try:
                            self.execute_actions(msg_id, actions, logger)
                        except Exception:
                            pass  # 单封失败不影响其他邮件
