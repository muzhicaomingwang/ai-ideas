"""日报生成任务

每晚 0 点执行，生成前一天的工作日报。
数据来源：
1. ideas 项目的 git 提交记录
2. Claude Code 会话日志
3. Obsidian 当日笔记

输出目标：
- Obsidian Journal 文件夹
- Git 自动提交
- 飞书消息推送
- Notion 页面（可选）
"""

import os
import sys
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tasks.config import config
from tasks.sync_utils import create_syncer, MultiPlatformSync

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class DailyReportGenerator:
    """日报生成器"""

    def __init__(self, target_date: Optional[datetime] = None):
        """
        Args:
            target_date: 目标日期，默认为昨天
        """
        if target_date is None:
            target_date = datetime.now() - timedelta(days=1)
        self.target_date = target_date
        self.date_str = target_date.strftime("%Y%m%d")
        self.date_display = target_date.strftime("%Y-%m-%d")

    def collect_git_commits(self) -> List[Dict[str, str]]:
        """收集 ideas 项目的 git 提交记录"""
        commits = []
        try:
            # 获取指定日期的提交
            since = self.target_date.strftime("%Y-%m-%d 00:00:00")
            until = (self.target_date + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")

            result = subprocess.run(
                [
                    "git", "log",
                    f"--since={since}",
                    f"--until={until}",
                    "--pretty=format:%H|%s|%an|%ai",
                    "--all",
                ],
                cwd=config.IDEAS_ROOT,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().split("\n"):
                    parts = line.split("|", 3)
                    if len(parts) >= 4:
                        commits.append({
                            "hash": parts[0][:8],
                            "message": parts[1],
                            "author": parts[2],
                            "date": parts[3],
                        })

            logger.info(f"收集到 {len(commits)} 条 git 提交")

        except Exception as e:
            logger.error(f"收集 git 提交失败: {e}")

        return commits

    def collect_git_stats(self) -> Dict[str, int]:
        """收集 git 变更统计"""
        stats = {"files_changed": 0, "insertions": 0, "deletions": 0}
        try:
            since = self.target_date.strftime("%Y-%m-%d 00:00:00")
            until = (self.target_date + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")

            result = subprocess.run(
                [
                    "git", "log",
                    f"--since={since}",
                    f"--until={until}",
                    "--shortstat",
                    "--all",
                ],
                cwd=config.IDEAS_ROOT,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "file" in line and "changed" in line:
                        # 解析 "X files changed, Y insertions(+), Z deletions(-)"
                        parts = line.strip().split(",")
                        for part in parts:
                            part = part.strip()
                            if "file" in part:
                                stats["files_changed"] += int(part.split()[0])
                            elif "insertion" in part:
                                stats["insertions"] += int(part.split()[0])
                            elif "deletion" in part:
                                stats["deletions"] += int(part.split()[0])

            logger.info(f"Git 统计: {stats}")

        except Exception as e:
            logger.error(f"收集 git 统计失败: {e}")

        return stats

    def collect_claude_sessions(self) -> List[Dict[str, Any]]:
        """收集 Claude Code 会话记录"""
        sessions = []
        try:
            # Claude Code 会话日志路径
            claude_dir = Path.home() / ".claude" / "projects"
            if not claude_dir.exists():
                logger.info("未找到 Claude Code 会话目录")
                return sessions

            # 搜索当日的会话
            target_date_str = self.target_date.strftime("%Y-%m-%d")

            for project_dir in claude_dir.iterdir():
                if not project_dir.is_dir():
                    continue

                # 检查会话文件
                sessions_dir = project_dir / "sessions"
                if sessions_dir.exists():
                    for session_file in sessions_dir.glob("*.json"):
                        # 检查文件修改时间
                        mtime = datetime.fromtimestamp(session_file.stat().st_mtime)
                        if mtime.strftime("%Y-%m-%d") == target_date_str:
                            sessions.append({
                                "project": project_dir.name,
                                "session": session_file.stem,
                                "time": mtime.strftime("%H:%M"),
                            })

            logger.info(f"收集到 {len(sessions)} 个 Claude 会话")

        except Exception as e:
            logger.error(f"收集 Claude 会话失败: {e}")

        return sessions

    def collect_obsidian_notes(self) -> List[Dict[str, str]]:
        """收集当日 Obsidian 笔记"""
        notes = []
        try:
            # 检查日报文件
            journal_file = config.JOURNAL_DIR / f"{self.date_str}.md"
            if journal_file.exists():
                content = journal_file.read_text(encoding="utf-8")
                notes.append({
                    "type": "journal",
                    "path": str(journal_file.relative_to(config.OBSIDIAN_VAULT)),
                    "preview": content[:200] + "..." if len(content) > 200 else content,
                })

            # 扫描其他文件夹的当日新增/修改文件
            target_date_str = self.target_date.strftime("%Y-%m-%d")
            for folder in ["Projects", "Notes", "Ideas"]:
                folder_path = config.OBSIDIAN_VAULT / folder
                if folder_path.exists():
                    for md_file in folder_path.rglob("*.md"):
                        mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                        if mtime.strftime("%Y-%m-%d") == target_date_str:
                            notes.append({
                                "type": folder.lower(),
                                "path": str(md_file.relative_to(config.OBSIDIAN_VAULT)),
                                "time": mtime.strftime("%H:%M"),
                            })

            logger.info(f"收集到 {len(notes)} 个 Obsidian 笔记")

        except Exception as e:
            logger.error(f"收集 Obsidian 笔记失败: {e}")

        return notes

    def generate_report(self) -> str:
        """生成日报 Markdown 内容"""
        # 收集数据
        commits = self.collect_git_commits()
        git_stats = self.collect_git_stats()
        claude_sessions = self.collect_claude_sessions()
        obsidian_notes = self.collect_obsidian_notes()

        # 构建 Markdown
        lines = [
            f"# {self.date_display} 工作日报",
            "",
            f"> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]

        # 概览
        lines.extend([
            "## 概览",
            "",
            f"- Git 提交: {len(commits)} 次",
            f"- 代码变更: {git_stats['files_changed']} 文件, +{git_stats['insertions']}/-{git_stats['deletions']} 行",
            f"- Claude 会话: {len(claude_sessions)} 个",
            f"- 笔记更新: {len(obsidian_notes)} 篇",
            "",
        ])

        # Git 提交详情
        if commits:
            lines.extend([
                "## Git 提交",
                "",
            ])
            for commit in commits:
                lines.append(f"- `{commit['hash']}` {commit['message']}")
            lines.append("")

        # Claude 会话
        if claude_sessions:
            lines.extend([
                "## Claude Code 会话",
                "",
            ])
            for session in claude_sessions:
                lines.append(f"- {session['time']} - {session['project']}")
            lines.append("")

        # Obsidian 笔记
        if obsidian_notes:
            lines.extend([
                "## Obsidian 笔记",
                "",
            ])
            for note in obsidian_notes:
                if note["type"] == "journal":
                    lines.append(f"- 日报: [[{note['path']}]]")
                else:
                    lines.append(f"- [{note['type']}] [[{note['path']}]] @ {note.get('time', '')}")
            lines.append("")

        # 如果没有任何活动
        if not commits and not claude_sessions and not obsidian_notes:
            lines.extend([
                "## 活动记录",
                "",
                "_今日暂无记录_",
                "",
            ])

        return "\n".join(lines)

    def run(self) -> Dict[str, bool]:
        """执行日报生成和同步"""
        logger.info(f"开始生成 {self.date_display} 日报")

        # 生成报告
        report_content = self.generate_report()
        report_title = f"{self.date_str}"

        # 创建同步器
        syncer = create_syncer()

        # 同步到各平台
        results = syncer.sync_content(
            title=report_title,
            content=report_content,
            targets=["obsidian", "git", "feishu"],
            obsidian_folder="Journal",
            feishu_receive_id=config.FEISHU_RECIPIENT_OPEN_ID,
            git_message=f"auto: daily report {self.date_display}",
        )

        logger.info(f"日报同步结果: {results}")
        return results


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="生成工作日报")
    parser.add_argument(
        "--date",
        type=str,
        help="目标日期 (YYYYMMDD 格式)，默认为昨天",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅生成报告，不同步",
    )

    args = parser.parse_args()

    # 解析日期
    target_date = None
    if args.date:
        target_date = datetime.strptime(args.date, "%Y%m%d")

    # 生成日报
    generator = DailyReportGenerator(target_date)

    if args.dry_run:
        report = generator.generate_report()
        print(report)
    else:
        results = generator.run()
        success = all(results.values())
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
