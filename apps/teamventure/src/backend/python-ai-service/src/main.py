"""
TeamVenture AI Service - 主应用入口

技术栈：
- FastAPI 0.109+
- LangGraph 0.0.40+
- OpenAI GPT-4
- Redis (缓存)
- RabbitMQ (消息队列)

主要功能：
- 接收方案生成请求（MQ消费）
- 多Agent协作生成团建方案
- 回调Java服务写入结果

@author TeamVenture Team
@version 1.0.0
@since 2025-12-30
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator

from src.models.config import settings
from src.langgraph.workflow import run_generation_workflow
from src.scheduler.scheduler import start_scheduler, stop_scheduler
from src.services.mq_consumer import start_mq_consumer, stop_mq_consumer
from src.services.markdown_converter import MarkdownConverter
from src.services.markdown_optimizer import MarkdownOptimizer
from src.services.xhs_normalizer import XhsNormalizer

# Import and initialize LLM metrics with Prometheus REGISTRY
from src.utils.llm_metrics import init_metrics as init_llm_metrics

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

# Avoid leaking query params (e.g., AMAP_API_KEY) via httpx INFO logs.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("🚀 Starting TeamVenture AI Service...")

    # 启动时初始化
    try:
        # Initialize LLM metrics (so they appear in /metrics even before first call)
        init_llm_metrics(default_model=settings.openai_model)
        logger.info("✅ LLM metrics initialized")

        # 启动MQ消费者
        await start_mq_consumer()
        logger.info("✅ MQ Consumer started")

        # 启动定时任务调度器
        await start_scheduler()
        logger.info("✅ Scheduler started")

        logger.info(f"🎯 AI Service running on: {settings.host}:{settings.port}")
        logger.info(f"📚 API Docs: http://{settings.host}:{settings.port}/docs")
        logger.info(f"💚 Health Check: http://{settings.host}:{settings.port}/health")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    yield

    # 关闭时清理
    logger.info("🛑 Shutting down TeamVenture AI Service...")
    try:
        await stop_mq_consumer()
        logger.info("✅ MQ Consumer stopped")

        await stop_scheduler()
        logger.info("✅ Scheduler stopped")
    except Exception as e:
        logger.error(f"⚠️ Shutdown warning: {e}")


# 创建FastAPI应用
app = FastAPI(
    title="TeamVenture AI Service",
    description="团建方案智能生成服务 - AI驱动的多Agent协作系统",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Instrument the app with default metrics
Instrumentator().instrument(app).expose(app)


# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 健康检查 ====================
@app.get("/health", tags=["Health"])
async def health_check():
    """健康检查接口"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "teamventure-ai-service",
            "version": "1.0.0",
        },
    )


@app.get("/", tags=["Root"])
async def root():
    """根路径"""
    return {
        "message": "Welcome to TeamVenture AI Service",
        "docs": "/docs",
        "health": "/health",
    }


# ==================== API路由 ====================
# 注意：一期主要通过MQ消费，HTTP接口作为备用/调试
@app.post("/api/v1/plans/generate", tags=["Plans"])
async def generate_plan_http(request: dict):
    """
    HTTP方式同步生成方案（备用/调试/同步链路）

    说明：
    - 该接口会同步调用 LangGraph 工作流生成方案，并直接返回 plans 列表。
    - 生产环境仍可继续使用MQ异步方式；Java侧如需同步链路，可调用此接口。
    """
    payload = request or {}
    state = await run_generation_workflow(payload)
    if state.get("error"):
        return JSONResponse(
            status_code=500,
            content={
                "error": state.get("error") or "generation failed",
                "plan_request_id": payload.get("plan_request_id"),
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "plan_request_id": state.get("plan_request_id"),
            "user_id": state.get("user_id"),
            "plans": state.get("generated_plans", []),
            "trace_id": payload.get("trace_id"),
        },
    )


class XhsNormalizeRequest(BaseModel):
    url: str = Field(default="", description="XHS share URL")
    title: str = Field(default="", description="Extracted title")
    extracted_text: str = Field(default="", description="Extracted note text")
    model: str | None = Field(default=None, description="Optional OpenAI model override (e.g. gpt-5.2)")


class XhsNormalizeResponse(BaseModel):
    content: str


@app.post("/api/v1/import/xiaohongshu/normalize", tags=["Import"])
async def normalize_xhs_text(req: XhsNormalizeRequest):
    """
    Normalize XHS extracted text via GPT (two-stage flow).

    Returns plain text content only; if OPENAI_API_KEY is missing, returns extracted_text as-is.
    """
    normalizer = XhsNormalizer()
    content = await normalizer.normalize_original_text(
        url=req.url,
        title=req.title,
        extracted_text=req.extracted_text,
        model=req.model,
    )
    return XhsNormalizeResponse(content=content)


class MarkdownOptimizeRequest(BaseModel):
    markdown_content: str = Field(default="", description="Markdown draft to optimize")
    model: str | None = Field(default=None, description="Optional OpenAI model override (e.g. gpt-5.2)")


class MarkdownOptimizeResponse(BaseModel):
    markdown_content: str


@app.post("/api/v1/markdown/optimize", tags=["Markdown"])
async def optimize_markdown(req: MarkdownOptimizeRequest):
    """
    Optimize markdown formatting via GPT.

    If OPENAI_API_KEY is missing, returns markdown_content as-is.
    """
    optimizer = MarkdownOptimizer()
    content = await optimizer.optimize_markdown(markdown_content=req.markdown_content, model=req.model)
    return MarkdownOptimizeResponse(markdown_content=content)


class MarkdownConvertRequest(BaseModel):
    parsed_content: str = Field(default="", description="Plain text parsed from XHS")
    model: str | None = Field(default=None, description="Optional OpenAI model override (e.g. gpt-5.2)")


class MarkdownConvertResponse(BaseModel):
    markdown_content: str


@app.post("/api/v1/markdown/convert", tags=["Markdown"])
async def convert_to_markdown(req: MarkdownConvertRequest):
    """
    Convert parsed plain text into markdown via GPT.

    This endpoint requires OPENAI_API_KEY; conversion is done by the LLM to handle free-form user text.
    """
    converter = MarkdownConverter()
    try:
        content = await converter.convert_parsed_text_to_markdown(parsed_content=req.parsed_content, model=req.model)
        return MarkdownConvertResponse(markdown_content=content)
    except RuntimeError as e:
        msg = str(e) or "Markdown convert failed"
        if "OPENAI_API_KEY" in msg:
            raise HTTPException(status_code=503, detail="AI is not configured (missing OPENAI_API_KEY)")
        raise HTTPException(status_code=502, detail=msg)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )
