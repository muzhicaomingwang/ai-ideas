"""检索器测试"""

import pytest
from pathlib import Path


class TestObsidianRetriever:
    """Obsidian 检索器测试"""

    def test_vault_path_exists(self):
        """测试知识库路径是否存在"""
        vault_path = Path.home() / "Documents" / "Obsidian Vault"
        assert vault_path.exists(), f"Obsidian Vault 不存在: {vault_path}"

    def test_vault_has_markdown_files(self):
        """测试知识库是否包含 Markdown 文件"""
        vault_path = Path.home() / "Documents" / "Obsidian Vault"
        md_files = list(vault_path.rglob("*.md"))
        assert len(md_files) > 0, "知识库中没有 Markdown 文件"
        print(f"找到 {len(md_files)} 个 Markdown 文件")


class TestIndexer:
    """索引器测试"""

    def test_exclude_patterns(self):
        """测试排除模式"""
        from src.indexer import ObsidianIndexer

        indexer = ObsidianIndexer()

        # 测试排除 _attachments
        assert indexer._should_exclude(Path("_attachments/image.png"))

        # 测试排除 .docx
        assert indexer._should_exclude(Path("notes/document.docx"))

        # 测试不排除普通 md 文件
        assert not indexer._should_exclude(Path("notes/readme.md"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
