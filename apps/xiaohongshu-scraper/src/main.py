"""
小红书内容抓取服务 - FastAPI 主入口
"""
import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.browser import BrowserManager
from .core.scraper import XHSScraper
from .models.schemas import (
    HealthResponse,
    ScrapeRequest,
    ScrapeResponse,
    NoteContent,
)
from .utils.parser import XHSUrlParser

# 全局实例
browser_manager: Optional[BrowserManager] = None
scraper: Optional[XHSScraper] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global browser_manager, scraper

    # 启动时初始化
    print("[Service] Starting browser manager...")
    browser_manager = BrowserManager(headless=True)
    await browser_manager.start()

    scraper = XHSScraper(browser_manager)
    print("[Service] Service ready!")

    yield

    # 关闭时清理
    print("[Service] Shutting down...")
    if browser_manager:
        await browser_manager.stop()
    print("[Service] Goodbye!")


# 创建 FastAPI 应用
app = FastAPI(
    title="小红书内容抓取服务",
    description="抓取小红书笔记内容，包括图片、视频、文字和评论",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=dict)
async def root():
    """服务根路径"""
    return {
        "service": "XHS Scraper Service",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        browser_ready=browser_manager.is_ready if browser_manager else False,
        login_status=browser_manager.is_logged_in if browser_manager else False,
    )


@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_note(request: ScrapeRequest):
    """
    抓取小红书笔记内容

    - **url**: 小红书笔记链接
    - **download_media**: 是否下载媒体文件（默认 true）
    - **fetch_comments**: 是否抓取评论（默认 true）
    - **comment_limit**: 评论数量限制（默认 100）
    """
    if not scraper:
        raise HTTPException(status_code=503, detail="Service not ready")

    # 验证 URL
    if not XHSUrlParser.is_valid_xhs_url(request.url):
        return ScrapeResponse(
            success=False,
            message="Invalid URL",
            error=f"Not a valid XHS URL: {request.url}",
        )

    try:
        note = await scraper.scrape_note(
            url=request.url,
            download_media=request.download_media,
            fetch_comments=request.fetch_comments,
            comment_limit=request.comment_limit,
        )

        # 保存到 JSON
        await scraper.save_to_json(note)

        return ScrapeResponse(
            success=True,
            message=f"Successfully scraped note: {note.title}",
            data=note,
        )

    except PermissionError as e:
        return ScrapeResponse(
            success=False,
            message="Login required",
            error=str(e),
        )

    except ValueError as e:
        return ScrapeResponse(
            success=False,
            message="Invalid request",
            error=str(e),
        )

    except Exception as e:
        return ScrapeResponse(
            success=False,
            message="Scrape failed",
            error=str(e),
        )


@app.post("/login/qrcode", response_model=dict)
async def login_with_qrcode():
    """
    二维码登录

    调用此接口后，会在服务端打开浏览器显示登录二维码。
    使用小红书 App 扫描二维码完成登录。
    """
    if not browser_manager:
        raise HTTPException(status_code=503, detail="Service not ready")

    # 需要非 headless 模式才能扫码
    # 这里先返回提示信息
    return {
        "message": "QR code login requires non-headless mode",
        "instructions": [
            "1. Stop the service",
            "2. Set HEADLESS=false in environment",
            "3. Restart and call this endpoint",
            "4. Scan the QR code in browser window",
        ],
    }


@app.get("/login/status", response_model=dict)
async def check_login_status():
    """检查登录状态"""
    if not browser_manager:
        raise HTTPException(status_code=503, detail="Service not ready")

    is_logged_in = await browser_manager.check_login_status()

    return {
        "logged_in": is_logged_in,
        "message": "Logged in" if is_logged_in else "Not logged in",
    }


@app.post("/parse", response_model=dict)
async def parse_url(url: str):
    """
    解析小红书 URL

    支持多种格式:
    - https://www.xiaohongshu.com/explore/xxxxx
    - https://www.xiaohongshu.com/discovery/item/xxxxx
    - https://xhslink.com/xxxxx
    """
    result = XHSUrlParser.parse(url)
    return result


# CLI 入口
def main():
    """命令行启动"""
    import uvicorn
    import os

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8100"))

    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=True,
    )


if __name__ == "__main__":
    main()
