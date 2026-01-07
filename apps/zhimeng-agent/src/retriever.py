"""知识库检索器

负责从向量数据库中检索相关文档。
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ObsidianRetriever:
    """Obsidian 知识库检索器"""

    def __init__(self, persist_dir: Optional[Path] = None):
        self.persist_dir = persist_dir or settings.chroma_path

        # 初始化 Embedding 模型
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
        )

        # 加载向量数据库
        self.vectorstore: Optional[Chroma] = None
        self._load_vectorstore()

    def _load_vectorstore(self):
        """加载向量数据库"""
        if not (self.persist_dir / "chroma.sqlite3").exists():
            logger.warning("向量数据库不存在，请先运行索引器")
            return

        self.vectorstore = Chroma(
            persist_directory=str(self.persist_dir),
            embedding_function=self.embeddings,
            collection_name="obsidian_vault",
        )
        logger.info("向量数据库加载完成")

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_folder: Optional[str] = None,
    ) -> List[Tuple[Document, float]]:
        """检索相关文档

        Args:
            query: 查询文本
            top_k: 返回的文档数量
            filter_folder: 限定搜索的文件夹

        Returns:
            文档和相似度分数的列表
        """
        if not self.vectorstore:
            logger.error("向量数据库未加载")
            return []

        # 构建过滤条件
        where_filter = None
        if filter_folder:
            where_filter = {"folder": {"$eq": filter_folder}}

        # 执行相似度搜索
        results = self.vectorstore.similarity_search_with_score(
            query=query,
            k=top_k,
            filter=where_filter,
        )

        # 按相似度排序（分数越低越相似）
        results.sort(key=lambda x: x[1])

        logger.info(f"检索到 {len(results)} 个相关文档")
        return results

    def retrieve_with_context(
        self,
        query: str,
        top_k: int = 5,
        context_window: int = 500,
    ) -> List[dict]:
        """检索并返回带上下文的结果

        Args:
            query: 查询文本
            top_k: 返回的文档数量
            context_window: 上下文窗口大小

        Returns:
            包含文档内容、来源和分数的字典列表
        """
        results = self.retrieve(query, top_k)

        formatted_results = []
        for doc, score in results:
            # 计算相关度分数（转换为 0-1 范围）
            relevance = max(0, 1 - score / 2)

            formatted_results.append({
                "content": doc.page_content[:context_window],
                "source": doc.metadata.get("source", "unknown"),
                "file_name": doc.metadata.get("file_name", "unknown"),
                "folder": doc.metadata.get("folder", ""),
                "relevance": round(relevance, 3),
            })

        return formatted_results

    def format_context(self, results: List[dict]) -> str:
        """将检索结果格式化为 LLM 可用的上下文

        Args:
            results: retrieve_with_context 的返回结果

        Returns:
            格式化的上下文字符串
        """
        if not results:
            return "未找到相关文档。"

        context_parts = []
        for i, r in enumerate(results, 1):
            context_parts.append(
                f"[文档 {i}] 来源: {r['source']} (相关度: {r['relevance']})\n"
                f"{r['content']}\n"
            )

        return "\n---\n".join(context_parts)


# 单例模式
_retriever_instance: Optional[ObsidianRetriever] = None


def get_retriever() -> ObsidianRetriever:
    """获取检索器单例"""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = ObsidianRetriever()
    return _retriever_instance
