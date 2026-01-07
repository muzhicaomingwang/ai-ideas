"""FastAPI 主入口

提供问答 API 和飞书 Webhook。
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import settings
from src.retriever import get_retriever
from src.llm_client import get_llm_client
from src.indexer import ObsidianIndexer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 全局实例
retriever = None
llm_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global retriever, llm_client

    logger.info("正在初始化服务...")

    # 初始化检索器
    retriever = get_retriever()

    # 初始化 LLM 客户端
    llm_client = get_llm_client()

    logger.info("服务初始化完成")

    yield

    logger.info("服务关闭")


app = FastAPI(
    title="zhimeng's Agent",
    description="基于 Obsidian 知识库的智能问答助手",
    version="0.1.0",
    lifespan=lifespan,
)


# ==================== 数据模型 ====================


class AskRequest(BaseModel):
    """问答请求"""
    question: str = Field(..., description="用户问题")
    top_k: int = Field(default=5, description="检索文档数量", ge=1, le=20)
    include_sources: bool = Field(default=True, description="是否包含来源")
    filter_folder: Optional[str] = Field(default=None, description="限定搜索的文件夹")
    user_id: Optional[str] = Field(default=None, description="用户唯一标识（用于对话记忆）")


class SourceInfo(BaseModel):
    """来源信息"""
    file: str
    folder: str
    relevance: float


class AskResponse(BaseModel):
    """问答响应"""
    answer: str
    sources: Optional[List[SourceInfo]] = None
    tokens_used: Optional[int] = None


class IndexRequest(BaseModel):
    """索引请求"""
    paths: Optional[List[str]] = Field(default=None, description="要索引的子目录")
    force: bool = Field(default=False, description="是否强制重建")


class IndexResponse(BaseModel):
    """索引响应"""
    status: str
    chunks_indexed: int


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    vectorstore_loaded: bool
    document_count: int


# ==================== API 路由 ====================


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    if retriever and retriever.vectorstore:
        count = retriever.vectorstore._collection.count()
        return HealthResponse(
            status="healthy",
            vectorstore_loaded=True,
            document_count=count,
        )
    return HealthResponse(
        status="degraded",
        vectorstore_loaded=False,
        document_count=0,
    )


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    """问答接口 - 使用智能 Agent"""
    from src.smart_agent import get_smart_agent

    try:
        agent = get_smart_agent()
        result = agent.answer(
            question=request.question,
            top_k=request.top_k,
            user_id=request.user_id,
        )

        sources = None
        if request.include_sources and result.get("sources"):
            sources = [
                SourceInfo(
                    file=s["file"],
                    folder=s["folder"],
                    relevance=s["relevance"],
                )
                for s in result["sources"]
            ]

        return AskResponse(
            answer=result["answer"],
            sources=sources,
        )
    except Exception as e:
        logger.error(f"问答失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index", response_model=IndexResponse)
async def build_index(request: IndexRequest):
    """重建索引"""
    try:
        indexer = ObsidianIndexer()
        count = indexer.build_index(
            paths=request.paths,
            force=request.force,
        )

        # 重新加载检索器
        global retriever
        retriever = get_retriever()

        return IndexResponse(
            status="success",
            chunks_indexed=count,
        )
    except Exception as e:
        logger.error(f"索引构建失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 飞书 Webhook ====================


class FeishuEvent(BaseModel):
    """飞书事件"""
    challenge: Optional[str] = None
    token: Optional[str] = None
    type: Optional[str] = None
    event: Optional[dict] = None


@app.post("/webhook/feishu")
async def feishu_webhook(event: FeishuEvent):
    """飞书 Webhook 处理"""
    # URL 验证
    if event.challenge:
        return {"challenge": event.challenge}

    # 处理消息事件
    if event.type == "event_callback" and event.event:
        event_type = event.event.get("type")

        if event_type == "message":
            # 处理消息
            msg = event.event.get("message", {})
            content = msg.get("content", "")
            sender = event.event.get("sender", {}).get("sender_id", {})
            open_id = sender.get("open_id")

            if content and open_id:
                # TODO: 解析消息内容，调用问答接口，回复消息
                logger.info(f"收到消息: {content}, from: {open_id}")

    return {"code": 0}


# ==================== 主入口 ====================


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
