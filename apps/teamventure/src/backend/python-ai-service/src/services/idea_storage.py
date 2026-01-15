"""
创意存储服务

功能：
- 保存创意为 Markdown 文件
- 自动 Git 提交和推送
- 更新 README 索引

@author TeamVenture Team
@version 1.0.0
@since 2026-01-15
"""
from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from datetime import datetime

from git import Repo

from src.models.idea import DailyIdeaBatch, ProductIdea

logger = logging.getLogger(__name__)


class IdeaStorage:
    """创意存储管理"""

    def __init__(self, repo_root: Path):
        """
        初始化存储服务

        Args:
            repo_root: Git 仓库根目录
        """
        self.repo_root = repo_root
        self.ideas_dir = repo_root / "docs" / "ideas"
        self.repo = Repo(repo_root)

    def save_to_markdown(self, batch: DailyIdeaBatch) -> Path:
        """
        保存创意批次为 Markdown 文件

        文件路径: docs/ideas/YYYY/MM/YYYY-MM-DD.md

        Args:
            batch: 创意批次对象

        Returns:
            Path: 保存的文件路径
        """
        # 提取年份和月份
        year, month = batch.date.split("-")[:2]
        year_dir = self.ideas_dir / year
        month_dir = year_dir / month

        # 创建目录（如果不存在）
        month_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 创建目录: {month_dir}")

        # 生成文件
        file_path = month_dir / f"{batch.date}.md"
        content = self._format_markdown(batch)
        file_path.write_text(content, encoding="utf-8")

        logger.info(f"✅ Markdown 文件已保存: {file_path}")

        # 更新索引
        self._update_readme_index(batch)

        return file_path

    def _format_markdown(self, batch: DailyIdeaBatch) -> str:
        """
        格式化为 Markdown 内容

        Args:
            batch: 创意批次

        Returns:
            str: Markdown 文本
        """
        lines = [
            f"# TeamVenture 每日创意 - {batch.date}",
            "",
            f"> 生成时间：{batch.ideas[0].generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"> 创意数量：{len(batch.ideas)}",
            "",
            "---",
            "",
        ]

        # 按分类分组
        categories = {
            "feature": "🚀 功能增强",
            "performance": "⚡ 性能优化",
            "ux": "🎨 体验改进",
            "architecture": "🏗️ 架构优化",
            "security": "🔒 安全加固",
        }

        for cat_key, cat_name in categories.items():
            cat_ideas = [i for i in batch.ideas if i.category == cat_key]
            if not cat_ideas:
                continue

            lines.append(f"## {cat_name}")
            lines.append("")

            for idea in cat_ideas:
                lines.extend(
                    [
                        f"### {idea.title}",
                        "",
                        f"**优先级**：{idea.priority} | **工作量**：{idea.estimated_effort}",
                        "",
                        f"**描述**：{idea.description}",
                        "",
                        f"**预期收益**：{idea.expected_impact}",
                        "",
                        f"**上下文**：{idea.context}",
                        "",
                        f"**创意ID**：`{idea.id}`",
                        "",
                        "---",
                        "",
                    ]
                )

        return "\n".join(lines)

    def git_commit_and_push(self, file_path: Path, date: str) -> bool:
        """
        Git 自动提交并推送

        Args:
            file_path: 创意文件路径
            date: 日期（YYYY-MM-DD）

        Returns:
            bool: 是否成功
        """
        try:
            # 相对路径（用于 git add）
            relative_path = file_path.relative_to(self.repo_root)
            readme_path = self.ideas_dir / "README.md"
            relative_readme = readme_path.relative_to(self.repo_root)

            logger.info(f"📝 准备 Git 提交: {relative_path}")

            # git add
            self.repo.index.add([str(relative_path), str(relative_readme)])
            logger.info(f"✅ git add 成功")

            # git commit
            commit_msg = (
                f"auto: daily ideas generation {date}\n\n"
                f"自动生成5个 TeamVenture 功能改进创意\n\n"
                f"文件: {relative_path}"
            )
            self.repo.index.commit(commit_msg)
            logger.info(f"✅ git commit 成功")

            # git push
            origin = self.repo.remote(name="origin")
            origin.push()
            logger.info(f"✅ git push 成功")

            return True

        except Exception as e:
            logger.error(f"❌ Git 操作失败: {e}", exc_info=True)
            return False

    def _update_readme_index(self, batch: DailyIdeaBatch):
        """
        更新创意索引（docs/ideas/README.md）

        Args:
            batch: 创意批次
        """
        try:
            readme_path = self.ideas_dir / "README.md"

            # 如果 README 不存在，创建初始版本
            if not readme_path.exists():
                self._create_initial_readme()

            # 读取现有内容
            content = readme_path.read_text(encoding="utf-8")

            # 在"最新创意"章节前插入新条目
            lines = content.split("\n")
            insert_index = -1

            for i, line in enumerate(lines):
                if line.strip() == "## 📅 最新创意":
                    # 找到空行后的插入位置
                    insert_index = i + 2
                    break

            if insert_index > 0:
                # 构造新条目（相对链接）
                year, month = batch.date.split("-")[:2]
                relative_link = f"{year}/{month}/{batch.date}.md"

                # 创意摘要（取每个分类的标题）
                summaries = []
                for idea in batch.ideas:
                    summaries.append(f"{idea.title}({idea.priority})")

                new_entry = f"- [{batch.date}]({relative_link}) - {', '.join(summaries[:3])}..."

                # 插入新条目
                lines.insert(insert_index, new_entry)

                # 写回文件
                updated_content = "\n".join(lines)
                readme_path.write_text(updated_content, encoding="utf-8")
                logger.info(f"✅ README 索引已更新")

        except Exception as e:
            logger.warning(f"⚠️ 更新 README 失败: {e}")

    def _create_initial_readme(self):
        """创建初始 README.md"""
        readme_path = self.ideas_dir / "README.md"
        readme_path.parent.mkdir(parents=True, exist_ok=True)

        content = """# TeamVenture 每日创意归档

> 本目录记录 AI 每日自动生成的功能改进创意

## 📊 统计概览

- **创意总数**: 待统计
- **已实现**: 待统计
- **待评估**: 待统计

## 📅 最新创意

（自动更新）

## 🎯 分类索引

### 功能增强（Feature）
（待统计）

### 性能优化（Performance）
（待统计）

### 体验改进（UX）
（待统计）

### 架构优化（Architecture）
（待统计）

### 安全加固（Security）
（待统计）

---

## 使用说明

1. **查看最新创意**: 点击上方"最新创意"章节的日期链接
2. **手动触发生成**: 在项目根目录运行 `make generate-ideas`
3. **查看生成历史**: 运行 `make ideas-status`

## 创意格式说明

每个创意包含以下字段：
- **标题**: 简明扼要的创意名称（10字以内）
- **分类**: feature/performance/ux/architecture/security
- **优先级**: P0（最高）~ P3（最低）
- **工作量**: S（1-2天）、M（3-5天）、L（1-2周）、XL（2周+）
- **描述**: 详细说明（包含背景、方案、实现要点）
- **预期收益**: 量化的用户价值或技术价值
- **上下文**: 为什么现在提这个创意
- **创意ID**: 唯一标识符（ULID格式）

## 相关链接

- [PRD](../requirements/prd.md)
- [详细设计](../design/detailed-design.md)
- [QA 报告](../qa/)
"""

        readme_path.write_text(content, encoding="utf-8")
        logger.info(f"✅ 初始 README 已创建: {readme_path}")
