"""Obsidian 文档索引器

负责读取 Obsidian Vault 中的 Markdown 文件，分块并存入向量数据库。
"""

import fnmatch
import hashlib
import json
import logging
from pathlib import Path
from typing import List, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ObsidianIndexer:
    """Obsidian 知识库索引器"""

    def __init__(
        self,
        vault_path: Optional[Path] = None,
        persist_dir: Optional[Path] = None,
    ):
        self.vault_path = vault_path or settings.vault_path
        self.persist_dir = persist_dir or settings.chroma_path

        # 初始化 Embedding 模型
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
        )

        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " ", ""],
        )

        # 初始化或加载向量数据库
        self.vectorstore: Optional[Chroma] = None

    def _should_exclude(self, path: Path) -> bool:
        """检查文件是否应该被排除"""
        path_str = str(path)
        for pattern in settings.exclude_patterns:
            if fnmatch.fnmatch(path.name, pattern):
                return True
            if fnmatch.fnmatch(path_str, f"*/{pattern}/*"):
                return True
            if fnmatch.fnmatch(path_str, f"*/{pattern}"):
                return True
        return False

    def _get_file_hash(self, file_path: Path) -> str:
        """计算文件的 MD5 哈希值"""
        content = file_path.read_bytes()
        return hashlib.md5(content).hexdigest()

    def _load_documents(self, paths: Optional[List[str]] = None) -> List[Document]:
        """加载 Markdown 文档"""
        documents = []

        if paths:
            # 加载指定路径
            search_paths = [self.vault_path / p for p in paths]
        else:
            # 加载整个 Vault
            search_paths = [self.vault_path]

        for search_path in search_paths:
            if not search_path.exists():
                logger.warning(f"路径不存在: {search_path}")
                continue

            # 遍历所有 Markdown 文件
            for md_file in search_path.rglob("*.md"):
                if self._should_exclude(md_file):
                    continue

                try:
                    content = md_file.read_text(encoding="utf-8")

                    # 计算相对路径
                    rel_path = md_file.relative_to(self.vault_path)

                    # 提取文件元数据
                    metadata = {
                        "source": str(rel_path),
                        "file_name": md_file.name,
                        "file_hash": self._get_file_hash(md_file),
                        "folder": str(rel_path.parent),
                    }

                    # 尝试提取 Obsidian 元数据（YAML frontmatter）
                    if content.startswith("---"):
                        try:
                            end_idx = content.index("---", 3)
                            frontmatter = content[3:end_idx].strip()
                            # 简单解析 frontmatter
                            for line in frontmatter.split("\n"):
                                if ":" in line:
                                    key, value = line.split(":", 1)
                                    metadata[f"fm_{key.strip()}"] = value.strip()
                            content = content[end_idx + 3:].strip()
                        except ValueError:
                            pass

                    doc = Document(page_content=content, metadata=metadata)
                    documents.append(doc)

                except Exception as e:
                    logger.error(f"读取文件失败 {md_file}: {e}")

        logger.info(f"加载了 {len(documents)} 个文档")
        return documents

    def build_index(
        self,
        paths: Optional[List[str]] = None,
        force: bool = False,
        batch_size: int = 50,
    ) -> int:
        """构建或更新索引

        Args:
            paths: 要索引的子目录列表，None 表示整个 Vault
            force: 是否强制重建索引
            batch_size: 每批处理的文档块数量

        Returns:
            索引的文档块数量
        """
        logger.info(f"开始构建索引: vault={self.vault_path}, force={force}")

        # 加载文档
        documents = self._load_documents(paths)

        if not documents:
            logger.warning("没有找到可索引的文档")
            return 0

        # 分割文档
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"分割为 {len(chunks)} 个文档块")

        # 分批处理
        total_batches = (len(chunks) + batch_size - 1) // batch_size
        logger.info(f"将分 {total_batches} 批处理，每批 {batch_size} 个")

        # 创建或更新向量数据库
        if force or not (self.persist_dir / "chroma.sqlite3").exists():
            # 第一批创建数据库
            first_batch = chunks[:batch_size]
            self.vectorstore = Chroma.from_documents(
                documents=first_batch,
                embedding=self.embeddings,
                persist_directory=str(self.persist_dir),
                collection_name="obsidian_vault",
            )
            logger.info(f"批次 1/{total_batches} 完成")

            # 后续批次追加
            for i in range(1, total_batches):
                start_idx = i * batch_size
                end_idx = min((i + 1) * batch_size, len(chunks))
                batch = chunks[start_idx:end_idx]

                self.vectorstore.add_documents(batch)
                logger.info(f"批次 {i+1}/{total_batches} 完成")

            logger.info("索引构建完成")
        else:
            # 增量更新
            self.load_index()
            for i in range(total_batches):
                start_idx = i * batch_size
                end_idx = min((i + 1) * batch_size, len(chunks))
                batch = chunks[start_idx:end_idx]

                self.vectorstore.add_documents(batch)
                logger.info(f"批次 {i+1}/{total_batches} 完成")

            logger.info("索引更新完成")

        return len(chunks)

    def load_index(self) -> bool:
        """加载已有索引"""
        if not (self.persist_dir / "chroma.sqlite3").exists():
            logger.warning("索引不存在，请先运行 build_index()")
            return False

        self.vectorstore = Chroma(
            persist_directory=str(self.persist_dir),
            embedding_function=self.embeddings,
            collection_name="obsidian_vault",
        )
        logger.info("索引加载完成")
        return True

    def get_stats(self) -> dict:
        """获取索引统计信息"""
        if not self.vectorstore:
            return {"status": "not_loaded"}

        collection = self.vectorstore._collection
        return {
            "status": "loaded",
            "document_count": collection.count(),
            "persist_dir": str(self.persist_dir),
        }


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Obsidian 知识库索引器")
    parser.add_argument("--paths", nargs="+", help="要索引的子目录")
    parser.add_argument("--force", action="store_true", help="强制重建索引")
    parser.add_argument("--stats", action="store_true", help="显示索引统计")
    args = parser.parse_args()

    indexer = ObsidianIndexer()

    if args.stats:
        indexer.load_index()
        print(json.dumps(indexer.get_stats(), indent=2, ensure_ascii=False))
    else:
        count = indexer.build_index(paths=args.paths, force=args.force)
        print(f"索引完成，共 {count} 个文档块")


if __name__ == "__main__":
    main()
