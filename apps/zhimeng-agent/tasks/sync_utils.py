"""多平台同步工具

提供 Git、Notion、飞书、Obsidian 的同步功能。
"""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitSync:
    """Git 同步工具"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def commit_and_push(
        self,
        message: str,
        files: Optional[List[str]] = None,
        push: bool = True,
    ) -> bool:
        """提交并推送变更

        Args:
            message: 提交信息
            files: 要添加的文件列表，None 表示所有变更
            push: 是否推送到远程

        Returns:
            是否成功
        """
        try:
            # 添加文件
            if files:
                for f in files:
                    subprocess.run(
                        ["git", "add", f],
                        cwd=self.repo_path,
                        check=True,
                        capture_output=True,
                    )
            else:
                subprocess.run(
                    ["git", "add", "-A"],
                    cwd=self.repo_path,
                    check=True,
                    capture_output=True,
                )

            # 检查是否有变更
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )
            if not result.stdout.strip():
                logger.info("没有需要提交的变更")
                return True

            # 提交
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
            )
            logger.info(f"Git 提交成功: {message}")

            # 推送
            if push:
                subprocess.run(
                    ["git", "push"],
                    cwd=self.repo_path,
                    check=True,
                    capture_output=True,
                )
                logger.info("Git 推送成功")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Git 操作失败: {e.stderr.decode() if e.stderr else e}")
            return False


class ObsidianSync:
    """Obsidian 同步工具（基于文件系统）"""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path

    def write_note(
        self,
        folder: str,
        filename: str,
        content: str,
        frontmatter: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """写入笔记

        Args:
            folder: 目标文件夹（相对于 vault 根目录）
            filename: 文件名（不含 .md 后缀）
            content: Markdown 内容
            frontmatter: YAML frontmatter 数据

        Returns:
            写入的文件路径
        """
        # 确保目录存在
        target_dir = self.vault_path / folder
        target_dir.mkdir(parents=True, exist_ok=True)

        # 构建完整内容
        full_content = ""
        if frontmatter:
            import yaml
            full_content = "---\n"
            full_content += yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False)
            full_content += "---\n\n"
        full_content += content

        # 写入文件
        file_path = target_dir / f"{filename}.md"
        file_path.write_text(full_content, encoding="utf-8")
        logger.info(f"Obsidian 笔记已写入: {file_path}")

        return file_path

    def read_note(self, folder: str, filename: str) -> Optional[str]:
        """读取笔记内容

        Args:
            folder: 文件夹
            filename: 文件名（不含 .md 后缀）

        Returns:
            笔记内容，不存在返回 None
        """
        file_path = self.vault_path / folder / f"{filename}.md"
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return None


class FeishuSync:
    """飞书同步工具"""

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self._tenant_access_token: Optional[str] = None
        self._token_expires_at: float = 0

    def _get_tenant_access_token(self) -> str:
        """获取租户访问令牌"""
        import time

        # 检查缓存
        if self._tenant_access_token and time.time() < self._token_expires_at:
            return self._tenant_access_token

        # 请求新令牌
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        with httpx.Client() as client:
            response = client.post(
                url,
                json={
                    "app_id": self.app_id,
                    "app_secret": self.app_secret,
                },
            )
            data = response.json()

        if data.get("code") != 0:
            raise Exception(f"获取飞书令牌失败: {data}")

        self._tenant_access_token = data["tenant_access_token"]
        self._token_expires_at = time.time() + data.get("expire", 7200) - 300  # 提前5分钟过期
        return self._tenant_access_token

    def send_message(
        self,
        receive_id: str,
        content: str,
        msg_type: str = "text",
        receive_id_type: str = "open_id",
    ) -> bool:
        """发送消息

        Args:
            receive_id: 接收者 ID
            content: 消息内容（文本或 JSON 字符串）
            msg_type: 消息类型（text, post, interactive 等）
            receive_id_type: ID 类型（open_id, user_id, chat_id 等）

        Returns:
            是否成功
        """
        try:
            token = self._get_tenant_access_token()
            url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}"

            # 构建消息内容
            if msg_type == "text" and not content.startswith("{"):
                content = json.dumps({"text": content})

            with httpx.Client() as client:
                response = client.post(
                    url,
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "receive_id": receive_id,
                        "msg_type": msg_type,
                        "content": content,
                    },
                )
                data = response.json()

            if data.get("code") != 0:
                logger.error(f"飞书消息发送失败: {data}")
                return False

            logger.info(f"飞书消息发送成功: {receive_id}")
            return True

        except Exception as e:
            logger.error(f"飞书消息发送异常: {e}")
            return False

    def send_rich_text(
        self,
        receive_id: str,
        title: str,
        content_blocks: List[List[Dict]],
        receive_id_type: str = "open_id",
    ) -> bool:
        """发送富文本消息

        Args:
            receive_id: 接收者 ID
            title: 消息标题
            content_blocks: 富文本内容块
            receive_id_type: ID 类型

        Returns:
            是否成功
        """
        post_content = {
            "zh_cn": {
                "title": title,
                "content": content_blocks,
            }
        }
        return self.send_message(
            receive_id=receive_id,
            content=json.dumps(post_content),
            msg_type="post",
            receive_id_type=receive_id_type,
        )


class NotionSync:
    """Notion 同步工具"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化

        注意：优先使用 MCP 工具，API 直接调用作为备选
        """
        self.api_key = api_key
        self.base_url = "https://api.notion.com/v1"
        self.version = "2022-06-28"

    def _headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": self.version,
            "Content-Type": "application/json",
        }

    def create_page(
        self,
        parent_id: str,
        title: str,
        content_blocks: Optional[List[Dict]] = None,
        parent_type: str = "page_id",
    ) -> Optional[str]:
        """创建页面

        Args:
            parent_id: 父页面或数据库 ID
            title: 页面标题
            content_blocks: 内容块列表
            parent_type: 父级类型（page_id 或 database_id）

        Returns:
            新页面 ID，失败返回 None
        """
        if not self.api_key:
            logger.warning("Notion API Key 未配置，跳过同步")
            return None

        try:
            # 构建请求体
            body = {
                "parent": {parent_type: parent_id},
                "properties": {
                    "title": {
                        "title": [{"text": {"content": title}}]
                    }
                },
            }

            if content_blocks:
                body["children"] = content_blocks

            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/pages",
                    headers=self._headers(),
                    json=body,
                )
                data = response.json()

            if "id" in data:
                logger.info(f"Notion 页面创建成功: {data['id']}")
                return data["id"]
            else:
                logger.error(f"Notion 页面创建失败: {data}")
                return None

        except Exception as e:
            logger.error(f"Notion 页面创建异常: {e}")
            return None

    def append_blocks(
        self,
        page_id: str,
        blocks: List[Dict],
    ) -> bool:
        """追加内容块

        Args:
            page_id: 页面 ID
            blocks: 内容块列表

        Returns:
            是否成功
        """
        if not self.api_key:
            logger.warning("Notion API Key 未配置，跳过同步")
            return False

        try:
            with httpx.Client() as client:
                response = client.patch(
                    f"{self.base_url}/blocks/{page_id}/children",
                    headers=self._headers(),
                    json={"children": blocks},
                )
                data = response.json()

            if "results" in data:
                logger.info(f"Notion 内容追加成功: {page_id}")
                return True
            else:
                logger.error(f"Notion 内容追加失败: {data}")
                return False

        except Exception as e:
            logger.error(f"Notion 内容追加异常: {e}")
            return False

    @staticmethod
    def markdown_to_blocks(markdown: str) -> List[Dict]:
        """将 Markdown 转换为 Notion 块

        简单转换，支持标题、段落、列表
        """
        blocks = []
        lines = markdown.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if not line:
                i += 1
                continue

            # 标题
            if line.startswith("### "):
                blocks.append({
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": line[4:]}}]
                    }
                })
            elif line.startswith("## "):
                blocks.append({
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                    }
                })
            elif line.startswith("# "):
                blocks.append({
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                    }
                })
            # 无序列表
            elif line.startswith("- ") or line.startswith("* "):
                blocks.append({
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                    }
                })
            # 有序列表
            elif len(line) > 2 and line[0].isdigit() and line[1:3] in [". ", ") "]:
                blocks.append({
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                    }
                })
            # 代码块
            elif line.startswith("```"):
                code_lines = []
                lang = line[3:].strip() or "plain text"
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                blocks.append({
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": "\n".join(code_lines)}}],
                        "language": lang,
                    }
                })
            # 普通段落
            else:
                blocks.append({
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": line}}]
                    }
                })

            i += 1

        return blocks


class MultiPlatformSync:
    """多平台同步协调器"""

    def __init__(
        self,
        git_repo: Optional[Path] = None,
        obsidian_vault: Optional[Path] = None,
        feishu_app_id: Optional[str] = None,
        feishu_app_secret: Optional[str] = None,
        notion_api_key: Optional[str] = None,
    ):
        self.git = GitSync(git_repo) if git_repo else None
        self.obsidian = ObsidianSync(obsidian_vault) if obsidian_vault else None
        self.feishu = FeishuSync(feishu_app_id, feishu_app_secret) if feishu_app_id else None
        self.notion = NotionSync(notion_api_key) if notion_api_key else None

    def sync_content(
        self,
        title: str,
        content: str,
        targets: Optional[List[str]] = None,
        obsidian_folder: str = "Journal",
        feishu_receive_id: Optional[str] = None,
        notion_parent_id: Optional[str] = None,
        git_message: Optional[str] = None,
    ) -> Dict[str, bool]:
        """同步内容到多个平台

        Args:
            title: 标题（用于文件名和消息标题）
            content: Markdown 内容
            targets: 目标平台列表 ["git", "obsidian", "feishu", "notion"]
            obsidian_folder: Obsidian 目标文件夹
            feishu_receive_id: 飞书接收者 ID
            notion_parent_id: Notion 父页面 ID
            git_message: Git 提交信息

        Returns:
            各平台同步结果
        """
        if targets is None:
            targets = ["git", "obsidian", "feishu", "notion"]

        results = {}

        # 1. 写入 Obsidian
        if "obsidian" in targets and self.obsidian:
            try:
                self.obsidian.write_note(
                    folder=obsidian_folder,
                    filename=title,
                    content=content,
                    frontmatter={
                        "created": datetime.now().isoformat(),
                        "tags": ["auto-generated"],
                    },
                )
                results["obsidian"] = True
            except Exception as e:
                logger.error(f"Obsidian 同步失败: {e}")
                results["obsidian"] = False

        # 2. Git 提交
        if "git" in targets and self.git:
            try:
                message = git_message or f"auto: {title}"
                results["git"] = self.git.commit_and_push(message)
            except Exception as e:
                logger.error(f"Git 同步失败: {e}")
                results["git"] = False

        # 3. 飞书消息
        if "feishu" in targets and self.feishu and feishu_receive_id:
            try:
                # 截取摘要（飞书消息长度限制）
                summary = content[:2000] if len(content) > 2000 else content
                results["feishu"] = self.feishu.send_message(
                    receive_id=feishu_receive_id,
                    content=f"📝 {title}\n\n{summary}",
                )
            except Exception as e:
                logger.error(f"飞书同步失败: {e}")
                results["feishu"] = False

        # 4. Notion 页面
        if "notion" in targets and self.notion and notion_parent_id:
            try:
                blocks = NotionSync.markdown_to_blocks(content)
                page_id = self.notion.create_page(
                    parent_id=notion_parent_id,
                    title=title,
                    content_blocks=blocks,
                )
                results["notion"] = page_id is not None
            except Exception as e:
                logger.error(f"Notion 同步失败: {e}")
                results["notion"] = False

        return results


def create_syncer() -> MultiPlatformSync:
    """创建配置好的同步器实例"""
    from tasks.config import config

    return MultiPlatformSync(
        git_repo=config.IDEAS_ROOT,
        obsidian_vault=config.OBSIDIAN_VAULT,
        feishu_app_id=config.FEISHU_APP_ID,
        feishu_app_secret=config.FEISHU_APP_SECRET,
        notion_api_key=None,  # 使用 MCP 工具替代
    )
