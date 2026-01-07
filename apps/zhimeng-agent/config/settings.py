"""应用配置"""

import os
from pathlib import Path
from typing import List, Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""

    # LLM API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # 知识库路径
    obsidian_vault_path: str = "~/Documents/Obsidian Vault/"

    # ChromaDB 持久化路径
    chroma_persist_dir: str = "./data/chroma"

    # LLM 配置
    llm_provider: Literal["anthropic", "openai"] = "anthropic"
    llm_model: str = "claude-3-5-sonnet-20241022"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 2000

    # Embedding 配置
    embedding_model: str = "text-embedding-3-small"

    # 索引配置
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # 检索配置
    retrieval_top_k: int = 5

    # 排除的文件/目录
    exclude_patterns: List[str] = [
        "_attachments",
        "_Inbox",
        "*.docx",
        "*.pdf",
        ".obsidian",
        ".trash",
    ]

    # 飞书配置
    feishu_app_id: str = ""
    feishu_app_secret: str = ""
    feishu_verification_token: str = ""
    feishu_encrypt_key: str = ""

    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = True

    class Config:
        env_file = "config/.env"
        env_file_encoding = "utf-8"

    @property
    def vault_path(self) -> Path:
        """获取 Obsidian Vault 的绝对路径"""
        return Path(self.obsidian_vault_path).expanduser().resolve()

    @property
    def chroma_path(self) -> Path:
        """获取 ChromaDB 的绝对路径"""
        path = Path(self.chroma_persist_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path.resolve()


# 全局配置实例
settings = Settings()
