"""邮箱整理任务

每晚凌晨 2 点执行，自动归档和整理邮件。
支持 Gmail（通过 himalaya CLI）。

整理规则：
1. 归档通知类邮件（来自各平台的自动通知）
2. 按发件人分类整理
3. 生成整理报告同步到 Obsidian
"""

import os
import sys
import subprocess
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tasks.config import config
from tasks.sync_utils import create_syncer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# himalaya 配置路径
HIMALAYA_CONFIG = Path.home() / ".himalaya-config" / "himalaya" / "config.toml"

# Gmail 归档文件夹
GMAIL_ARCHIVE_FOLDER = "[Gmail]/所有邮件"

# 自动归档的发件人关键词（通知类）
AUTO_ARCHIVE_SENDERS = [
    # 社交平台
    "noreply", "no-reply", "donotreply", "notification",
    "newsletter", "digest", "update", "alert", "mailer",
    # 具体平台
    "Grok", "Reddit", "Twitter", "LinkedIn", "Instagram",
    "Facebook", "TikTok", "Discord", "Slack", "Medium",
    "Substack", "GitHub", "GitLab", "Bitbucket",
    "Coursera", "Udemy", "Kaggle", "Stack Overflow", "Quora",
    "KAYAK", "Booking", "Airbnb", "Uber", "Lyft",
    "DoorDash", "Grubhub", "Amazon", "eBay", "Alibaba",
    "Google", "Apple", "Microsoft", "Dropbox", "Notion",
    "Spotify", "Netflix", "YouTube", "Twitch",
    # 营销邮件
    "marketing", "promo", "promotions", "sales", "offer",
    "unsubscribe", "subscription",
]


@dataclass
class EmailStats:
    """邮件整理统计"""
    total_scanned: int = 0
    archived: int = 0
    by_sender: Dict[str, int] = None
    errors: List[str] = None

    def __post_init__(self):
        if self.by_sender is None:
            self.by_sender = {}
        if self.errors is None:
            self.errors = []


class EmailOrganizer:
    """邮箱整理器"""

    def __init__(self, dry_run: bool = False):
        """
        Args:
            dry_run: 如果为 True，只分析不实际操作
        """
        self.dry_run = dry_run
        self.stats = EmailStats()

    def check_himalaya(self) -> bool:
        """检查 himalaya 是否可用"""
        try:
            result = subprocess.run(
                ["himalaya", "-c", str(HIMALAYA_CONFIG), "folder", "list"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"himalaya 检查失败: {e}")
            return False

    def get_inbox_emails(self, limit: int = 500) -> List[Dict[str, str]]:
        """获取收件箱邮件列表"""
        emails = []
        try:
            result = subprocess.run(
                [
                    "himalaya", "-c", str(HIMALAYA_CONFIG),
                    "envelope", "list", "-s", str(limit),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                logger.error(f"获取邮件列表失败: {result.stderr}")
                return emails

            # 解析 himalaya 输出（表格格式）
            lines = result.stdout.strip().split("\n")
            for line in lines[2:]:  # 跳过表头
                if not line.strip() or line.startswith("─"):
                    continue
                # 解析格式: ID │ FLAGS │ SUBJECT │ FROM │ DATE
                parts = [p.strip() for p in line.split("│")]
                if len(parts) >= 4:
                    emails.append({
                        "id": parts[0].strip(),
                        "flags": parts[1].strip() if len(parts) > 1 else "",
                        "subject": parts[2].strip() if len(parts) > 2 else "",
                        "from": parts[3].strip() if len(parts) > 3 else "",
                        "date": parts[4].strip() if len(parts) > 4 else "",
                    })

            logger.info(f"获取到 {len(emails)} 封邮件")

        except Exception as e:
            logger.error(f"获取邮件列表异常: {e}")
            self.stats.errors.append(str(e))

        return emails

    def should_archive(self, email: Dict[str, str]) -> Tuple[bool, str]:
        """判断邮件是否应该归档

        Returns:
            (should_archive, reason)
        """
        sender = email.get("from", "").lower()
        subject = email.get("subject", "").lower()

        for keyword in AUTO_ARCHIVE_SENDERS:
            keyword_lower = keyword.lower()
            if keyword_lower in sender or keyword_lower in subject:
                return True, keyword

        return False, ""

    def archive_email(self, email_id: str) -> bool:
        """归档单封邮件"""
        if self.dry_run:
            logger.info(f"[DRY RUN] 将归档邮件: {email_id}")
            return True

        try:
            result = subprocess.run(
                [
                    "himalaya", "-c", str(HIMALAYA_CONFIG),
                    "message", "move", "-f", "INBOX",
                    GMAIL_ARCHIVE_FOLDER, email_id,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return True
            else:
                logger.warning(f"归档邮件 {email_id} 失败: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"归档邮件 {email_id} 异常: {e}")
            self.stats.errors.append(f"归档 {email_id}: {e}")
            return False

    def organize(self) -> EmailStats:
        """执行邮箱整理"""
        logger.info("开始邮箱整理...")

        # 检查 himalaya
        if not self.check_himalaya():
            logger.error("himalaya 不可用，跳过邮箱整理")
            self.stats.errors.append("himalaya 不可用")
            return self.stats

        # 获取收件箱邮件
        emails = self.get_inbox_emails()
        self.stats.total_scanned = len(emails)

        # 遍历并归档
        for email in emails:
            should_archive, reason = self.should_archive(email)
            if should_archive:
                sender = email.get("from", "unknown")
                if self.archive_email(email["id"]):
                    self.stats.archived += 1
                    # 统计发件人
                    if reason not in self.stats.by_sender:
                        self.stats.by_sender[reason] = 0
                    self.stats.by_sender[reason] += 1
                    logger.info(f"已归档: {email['subject'][:50]} (匹配: {reason})")

        logger.info(f"整理完成: 扫描 {self.stats.total_scanned}, 归档 {self.stats.archived}")
        return self.stats

    def generate_report(self) -> str:
        """生成整理报告 Markdown"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")

        lines = [
            f"# {date_str} 邮箱整理报告",
            "",
            f"> 自动生成于 {now.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 概览",
            "",
            f"- 扫描邮件: {self.stats.total_scanned} 封",
            f"- 归档邮件: {self.stats.archived} 封",
            f"- 模式: {'模拟运行' if self.dry_run else '实际执行'}",
            "",
        ]

        if self.stats.by_sender:
            lines.extend([
                "## 按发件人统计",
                "",
            ])
            # 按数量排序
            sorted_senders = sorted(
                self.stats.by_sender.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            for sender, count in sorted_senders:
                lines.append(f"- {sender}: {count} 封")
            lines.append("")

        if self.stats.errors:
            lines.extend([
                "## 错误日志",
                "",
            ])
            for error in self.stats.errors[:10]:  # 最多显示10条
                lines.append(f"- {error}")
            lines.append("")

        if not self.stats.archived and not self.stats.errors:
            lines.extend([
                "## 结果",
                "",
                "_今日无需整理的邮件_",
                "",
            ])

        return "\n".join(lines)

    def run(self) -> Dict[str, bool]:
        """执行整理和同步"""
        # 执行整理
        self.organize()

        # 生成报告
        report = self.generate_report()
        date_str = datetime.now().strftime("%Y%m%d")
        report_title = f"email-organize-{date_str}"

        # 同步到 Obsidian（不同步到其他平台，邮箱报告仅本地保存）
        syncer = create_syncer()
        results = syncer.sync_content(
            title=report_title,
            content=report,
            targets=["obsidian"],  # 仅同步到 Obsidian
            obsidian_folder="Journal/Email",
        )

        logger.info(f"邮箱整理报告同步结果: {results}")
        return results


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="邮箱整理任务")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅分析，不实际归档",
    )

    args = parser.parse_args()

    organizer = EmailOrganizer(dry_run=args.dry_run)

    if args.dry_run:
        organizer.organize()
        report = organizer.generate_report()
        print(report)
    else:
        results = organizer.run()
        success = all(results.values()) if results else False
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
