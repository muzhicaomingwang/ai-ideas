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
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from src.models.config import settings
from src.scheduler.scheduler import start_scheduler, stop_scheduler
from src.services.mq_consumer import start_mq_consumer, stop_mq_consumer

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
    HTTP方式生成方案（调试用）

    生产环境主要使用MQ异步方式
    """
    return JSONResponse(
        status_code=200,
        content={
            "message": "Plan generation request received",
            "request_id": request.get("plan_request_id"),
            "note": "生产环境请使用MQ方式",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )
