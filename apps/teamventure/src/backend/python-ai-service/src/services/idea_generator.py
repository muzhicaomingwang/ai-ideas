"""
每日创意生成服务

功能：
- 收集代码/文档上下文
- 调用 OpenAI GPT-4 生成改进创意
- 规范化输出为结构化数据

@author TeamVenture Team
@version 1.0.0
@since 2026-01-15
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from git import Repo

from src.integrations.openai_client import OpenAIClient
from src.models.idea import DailyIdeaBatch, ProductIdea
from src.services.id_generator import new_prefixed_id

logger = logging.getLogger(__name__)


class DailyIdeaGenerator:
    """每日创意生成器"""

    def __init__(self):
        self.openai_client = OpenAIClient()
        # 仓库根目录：从 python-ai-service 向上6级到达 ideas/apps/teamventure
        self.repo_root = Path(__file__).parent.parent.parent.parent.parent.parent
        self.ideas_dir = self.repo_root / "docs" / "ideas"
        self.repo = Repo(self.repo_root)

    async def generate_daily_ideas(self) -> DailyIdeaBatch:
        """
        生成今日创意

        Returns:
            DailyIdeaBatch: 包含5个创意的批次对象
        """
        today = datetime.now().strftime("%Y-%m-%d")
        logger.info(f"🎯 开始生成 {today} 的创意...")

        # 1. 收集上下文
        context = await self._collect_context()
        logger.info(f"✅ 上下文收集完成: {len(context)} 项")

        # 2. 构建 Prompt
        prompt = self._build_prompt(context)

        # 3. 调用 GPT-4 生成
        logger.info("🤖 调用 OpenAI API 生成创意...")
        raw_response = await self.openai_client.generate_json(prompt)

        # 4. 解析并规范化
        ideas = self._parse_ideas(raw_response)
        logger.info(f"✅ 创意解析完成: {len(ideas)} 个")

        return DailyIdeaBatch(date=today, ideas=ideas, metadata=context["metadata"])

    async def _collect_context(self) -> dict[str, Any]:
        """
        收集上下文信息

        包括：代码变更、关键文档、历史创意、代码质量指标
        """
        logger.info("📚 收集上下文信息...")

        # 1. 扫描最近代码变更（最近7天的commits）
        recent_changes = self._get_recent_changes(days=7)

        # 2. 读取关键文档
        prd_content = self._read_doc("docs/requirements/prd.md")
        design_content = self._read_doc("docs/design/detailed-design.md")
        qa_summary = self._read_doc("docs/qa/QUALITY_IMPROVEMENT_SUMMARY_2026-01-08.md")

        # 3. 获取历史创意（避免重复）
        historical_ideas = self._get_historical_ideas(days=30)

        # 4. 统计代码质量指标
        code_stats = self._analyze_code_quality()

        return {
            "recent_changes": recent_changes,
            "prd_summary": prd_content[:2000],  # 截取关键部分，避免 token 超限
            "design_summary": design_content[:2000],
            "qa_summary": qa_summary[:1000],
            "historical_ideas": historical_ideas,
            "code_stats": code_stats,
            "metadata": {
                "context_sources": ["git_commits", "prd", "design_docs", "qa_reports", "historical_ideas"],
                "generated_at": datetime.now().isoformat(),
                "repo_root": str(self.repo_root),
            },
        }

    def _get_recent_changes(self, days: int = 7) -> str:
        """
        获取最近代码变更

        Args:
            days: 回溯天数

        Returns:
            str: Git 提交记录摘要
        """
        try:
            since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            commits = list(self.repo.iter_commits(f"--since={since_date}", max_count=20))

            if not commits:
                return "最近无代码变更"

            lines = [f"最近 {days} 天的代码变更（{len(commits)} 次提交）：", ""]
            for commit in commits[:10]:  # 只取前10条
                short_hash = commit.hexsha[:7]
                message = commit.message.split("\n")[0][:60]  # 只取第一行，截断过长消息
                lines.append(f"- [{short_hash}] {message}")

            return "\n".join(lines)

        except Exception as e:
            logger.warning(f"⚠️ 获取 Git 提交记录失败: {e}")
            return "（无法获取 Git 历史）"

    def _read_doc(self, relative_path: str) -> str:
        """
        读取文档内容

        Args:
            relative_path: 相对于仓库根目录的路径

        Returns:
            str: 文档内容（最多读取前5000字符）
        """
        try:
            doc_path = self.repo_root / relative_path
            if not doc_path.exists():
                logger.warning(f"⚠️ 文档不存在: {relative_path}")
                return f"（文档 {relative_path} 不存在）"

            content = doc_path.read_text(encoding="utf-8")
            # 截取前5000字符，避免 Prompt 过长
            if len(content) > 5000:
                content = content[:5000] + "\n\n（文档较长，已截断）"

            return content

        except Exception as e:
            logger.warning(f"⚠️ 读取文档失败 {relative_path}: {e}")
            return f"（无法读取 {relative_path}）"

    def _get_historical_ideas(self, days: int = 30) -> str:
        """
        获取历史创意（避免重复）

        Args:
            days: 回溯天数

        Returns:
            str: 历史创意标题列表
        """
        try:
            if not self.ideas_dir.exists():
                return "（暂无历史创意）"

            # 扫描最近30天的创意文件
            since_date = datetime.now() - timedelta(days=days)
            historical_titles = []

            # 遍历 YYYY/MM/*.md 文件
            for year_dir in self.ideas_dir.glob("*"):
                if not year_dir.is_dir():
                    continue
                for month_dir in year_dir.glob("*"):
                    if not month_dir.is_dir():
                        continue
                    for idea_file in month_dir.glob("*.md"):
                        # 从文件名提取日期（YYYY-MM-DD.md）
                        try:
                            file_date_str = idea_file.stem  # 去掉 .md 后缀
                            file_date = datetime.strptime(file_date_str, "%Y-%m-%d")

                            if file_date >= since_date:
                                # 读取文件，提取创意标题
                                content = idea_file.read_text(encoding="utf-8")
                                titles = self._extract_idea_titles(content)
                                historical_titles.extend(titles)

                        except ValueError:
                            continue  # 跳过格式不匹配的文件

            if not historical_titles:
                return "（近30天暂无历史创意）"

            return "近30天已生成的创意标题（避免重复）：\n- " + "\n- ".join(historical_titles[:20])

        except Exception as e:
            logger.warning(f"⚠️ 获取历史创意失败: {e}")
            return "（无法获取历史创意）"

    def _extract_idea_titles(self, markdown_content: str) -> list[str]:
        """
        从 Markdown 文件中提取创意标题

        Args:
            markdown_content: Markdown 文本

        Returns:
            list[str]: 创意标题列表
        """
        titles = []
        for line in markdown_content.split("\n"):
            # 匹配三级标题（### 创意标题）
            if line.startswith("### ") and not line.startswith("### 功能"):
                title = line.replace("### ", "").strip()
                titles.append(title)
        return titles

    def _analyze_code_quality(self) -> dict:
        """
        分析代码质量指标

        Returns:
            dict: 代码质量统计
        """
        try:
            java_dir = self.repo_root / "src" / "backend" / "java-business-service" / "src"
            python_dir = self.repo_root / "src" / "backend" / "python-ai-service" / "src"

            # 统计 TODO/FIXME 注释数量
            def count_todos(directory: Path, pattern: str) -> int:
                count = 0
                for file in directory.rglob("*.java") if "java" in str(directory) else directory.rglob("*.py"):
                    try:
                        content = file.read_text(encoding="utf-8")
                        count += content.upper().count(pattern.upper())
                    except Exception:
                        pass
                return count

            java_todos = count_todos(java_dir, "TODO") if java_dir.exists() else 0
            java_fixmes = count_todos(java_dir, "FIXME") if java_dir.exists() else 0
            python_todos = count_todos(python_dir, "TODO") if python_dir.exists() else 0
            python_fixmes = count_todos(python_dir, "FIXME") if python_dir.exists() else 0

            return {
                "java_todos": java_todos,
                "java_fixmes": java_fixmes,
                "python_todos": python_todos,
                "python_fixmes": python_fixmes,
                "total_todos": java_todos + python_todos,
                "total_fixmes": java_fixmes + python_fixmes,
            }

        except Exception as e:
            logger.warning(f"⚠️ 代码质量分析失败: {e}")
            return {"error": str(e)}

    def _build_prompt(self, context: dict[str, Any]) -> str:
        """
        构建 GPT-4 Prompt

        Args:
            context: 上下文信息字典

        Returns:
            str: 完整的 Prompt 文本
        """
        code_stats = context.get("code_stats", {})
        todo_info = ""
        if code_stats.get("total_todos", 0) > 0 or code_stats.get("total_fixmes", 0) > 0:
            todo_info = f"\n代码中有 {code_stats.get('total_todos', 0)} 个 TODO 和 {code_stats.get('total_fixmes', 0)} 个 FIXME，可考虑技术债清理相关创意。"

        return f"""你是 TeamVenture AI 团建策划助手的产品经理，负责提出功能改进建议。

**任务**：生成5个高质量的功能改进创意。

**上下文信息**：

1. 最近代码变更（最近7天）：
{context['recent_changes']}

2. 产品核心定位（PRD摘要）：
{context['prd_summary']}

3. 技术架构概要（设计文档摘要）：
{context['design_summary']}

4. QA 质量改进总结：
{context.get('qa_summary', '（暂无）')}

5. 代码质量指标：
{json.dumps(code_stats, ensure_ascii=False)}{todo_info}

6. 近30天已生成创意（避免重复）：
{context['historical_ideas']}

**严格要求**：
1. ✅ 聚焦 TeamVenture 功能改进（不要全新产品想法）
2. ✅ 覆盖5个分类：功能增强、性能优化、体验改进、架构优化、安全加固（各1个）
3. ✅ 优先级分布：1个P0，2个P1，2个P2
4. ✅ 工作量分布：2个S，2个M，1个L（避免全是小改进或全是大工程）
5. ✅ 必须具体可落地：
   - ❌ 错误示例："提升用户体验"（太空泛）
   - ✅ 正确示例："在方案对比页增加左右滑动切换功能，减少用户点击次数"
6. ✅ 描述中包含实现要点：
   - 涉及哪个文件/模块
   - 具体改动点（如"在 PlanService.java 第320行添加缓存逻辑"）
   - 关键技术选型（如"使用 Redis Sorted Set"）
7. ✅ 预期收益需量化：
   - ❌ 错误示例："提升性能"
   - ✅ 正确示例："减少响应时间 50%（从 2秒 降至 1秒）"
8. ✅ 避免重复历史创意（检查上下文中的历史标题）

**输出格式**（严格 JSON，不要 Markdown 代码块）：
{{
  "ideas": [
    {{
      "title": "创意标题（10字以内）",
      "category": "feature|performance|ux|architecture|security",
      "description": "详细描述（100-200字，包含：背景、具体方案、实现要点、技术细节）",
      "priority": "P0|P1|P2|P3",
      "estimated_effort": "S|M|L|XL",
      "expected_impact": "预期收益（必须量化，如：提升XX%、减少YY秒、增加ZZ用户）",
      "context": "为什么现在提这个创意（基于上下文的合理性，如：根据XX报告、用户反馈、代码分析等）"
    }},
    ... 共5个
  ]
}}

**示例创意**（仅作格式参考）：
{{
  "title": "方案对比智能排序",
  "category": "ux",
  "description": "当前方案对比页按 budget/standard/premium 固定顺序展示。建议根据用户历史偏好智能排序（如重视性价比则 budget 优先，重视品质则 premium 优先）。实现方式：在 PlanService.java 第580行的 listPlans() 方法中，基于用户画像（从 Redis 缓存读取历史选择记录）调整返回顺序。前端保持现有UI，仅调整数据顺序。技术细节：Redis key 设计为 user:{{user_id}}:plan_preference，TTL 90天。",
  "priority": "P1",
  "estimated_effort": "M",
  "expected_impact": "提升方案点击率 15%，减少用户比较时长 20%（从平均40秒降至32秒），降低首屏跳出率 10%",
  "context": "根据 QA 报告（QUALITY_IMPROVEMENT_SUMMARY_2026-01-08.md），用户在对比页平均停留40秒，存在选择困难。智能排序可降低认知负担。"
}}

现在请生成5个高质量创意（仅返回 JSON，不要其他文字）：
"""

    def _parse_ideas(self, raw: dict[str, Any]) -> list[ProductIdea]:
        """
        解析并规范化创意数据

        Args:
            raw: OpenAI 返回的 JSON 数据

        Returns:
            list[ProductIdea]: 创意对象列表

        Raises:
            ValueError: 如果创意数量不等于5
        """
        ideas_raw = raw.get("ideas", [])
        if len(ideas_raw) != 5:
            logger.error(f"❌ 创意数量错误: 期望5个，实际{len(ideas_raw)}个")
            raise ValueError(f"Expected 5 ideas, got {len(ideas_raw)}")

        ideas = []
        for idea_raw in ideas_raw:
            try:
                idea = ProductIdea(
                    id=new_prefixed_id("idea"),
                    title=str(idea_raw["title"]),
                    category=str(idea_raw["category"]),
                    description=str(idea_raw["description"]),
                    priority=str(idea_raw["priority"]),
                    estimated_effort=str(idea_raw["estimated_effort"]),
                    expected_impact=str(idea_raw["expected_impact"]),
                    context=str(idea_raw.get("context", "")),
                )
                ideas.append(idea)

            except (KeyError, ValueError) as e:
                logger.error(f"❌ 创意解析失败: {e}, 原始数据: {idea_raw}")
                raise ValueError(f"Failed to parse idea: {e}")

        # 验证分类和优先级分布
        self._validate_distribution(ideas)

        return ideas

    def _validate_distribution(self, ideas: list[ProductIdea]):
        """
        验证创意的分类和优先级分布

        Args:
            ideas: 创意列表

        Raises:
            ValueError: 如果分布不符合要求
        """
        # 检查分类（应各1个）
        categories = [idea.category for idea in ideas]
        expected_categories = {"feature", "performance", "ux", "architecture", "security"}
        if set(categories) != expected_categories:
            logger.warning(
                f"⚠️ 分类分布不均: {categories}，期望 {expected_categories}"
            )
            # 不抛异常，仅记录警告

        # 检查优先级分布（应有1个P0，2个P1，2个P2）
        priorities = [idea.priority for idea in ideas]
        priority_counts = {p: priorities.count(p) for p in set(priorities)}
        logger.info(f"📊 优先级分布: {priority_counts}")

    def _get_historical_ideas(self, days: int = 30) -> str:
        """获取历史创意实现"""
        try:
            if not self.ideas_dir.exists():
                return "（暂无历史创意）"

            since_date = datetime.now() - timedelta(days=days)
            historical_titles = []

            # 遍历 YYYY/MM/*.md 文件
            for year_dir in sorted(self.ideas_dir.glob("*"), reverse=True):
                if not year_dir.is_dir() or not year_dir.name.isdigit():
                    continue

                for month_dir in sorted(year_dir.glob("*"), reverse=True):
                    if not month_dir.is_dir() or not month_dir.name.isdigit():
                        continue

                    for idea_file in sorted(month_dir.glob("*.md"), reverse=True):
                        try:
                            file_date_str = idea_file.stem
                            file_date = datetime.strptime(file_date_str, "%Y-%m-%d")

                            if file_date >= since_date:
                                content = idea_file.read_text(encoding="utf-8")
                                titles = self._extract_idea_titles(content)
                                historical_titles.extend(titles)

                        except ValueError:
                            continue

            if not historical_titles:
                return "（近30天暂无历史创意）"

            return "近30天已生成的创意标题（避免重复）：\n- " + "\n- ".join(historical_titles[:20])

        except Exception as e:
            logger.warning(f"⚠️ 获取历史创意失败: {e}")
            return "（无法获取历史创意）"

    def _analyze_code_quality(self) -> dict:
        """（实现见上方）"""
        # 已在 _analyze_code_quality 方法中实现
        try:
            java_dir = self.repo_root / "src" / "backend" / "java-business-service" / "src"
            python_dir = self.repo_root / "src" / "backend" / "python-ai-service" / "src"

            def count_pattern(directory: Path, pattern: str, extensions: list[str]) -> int:
                count = 0
                for ext in extensions:
                    for file in directory.rglob(f"*{ext}"):
                        try:
                            content = file.read_text(encoding="utf-8")
                            count += content.upper().count(pattern.upper())
                        except Exception:
                            pass
                return count

            java_todos = count_pattern(java_dir, "TODO", [".java"]) if java_dir.exists() else 0
            java_fixmes = count_pattern(java_dir, "FIXME", [".java"]) if java_dir.exists() else 0
            python_todos = count_pattern(python_dir, "TODO", [".py"]) if python_dir.exists() else 0
            python_fixmes = count_pattern(python_dir, "FIXME", [".py"]) if python_dir.exists() else 0

            return {
                "java_todos": java_todos,
                "java_fixmes": java_fixmes,
                "python_todos": python_todos,
                "python_fixmes": python_fixmes,
                "total_todos": java_todos + python_todos,
                "total_fixmes": java_fixmes + python_fixmes,
            }

        except Exception as e:
            logger.warning(f"⚠️ 代码质量分析失败: {e}")
            return {"error": str(e)}
