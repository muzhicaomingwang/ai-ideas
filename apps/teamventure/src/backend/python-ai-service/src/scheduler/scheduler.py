"""
定时任务调度器

使用 APScheduler 实现定时任务调度
- 每天上午10点触发创意生成

@author TeamVenture Team
@version 1.0.0
@since 2026-01-15
"""
from __future__ import annotations

import logging

from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.models.config import settings
from src.scheduler.jobs import daily_idea_generation_job

logger = logging.getLogger(__name__)

# 全局调度器实例（单例模式）
_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    """
    获取调度器实例（单例）

    Returns:
        AsyncIOScheduler: 调度器实例
    """
    global _scheduler
    if _scheduler is None:
        executors = {
            "default": AsyncIOExecutor(),
        }
        job_defaults = {
            "coalesce": True,  # 合并多个积压任务（避免服务重启后执行多次）
            "max_instances": 1,  # 同一任务最多1个实例（避免并发执行）
            "misfire_grace_time": 300,  # 容错5分钟（服务重启时的补偿机制）
        }
        _scheduler = AsyncIOScheduler(
            executors=executors,
            job_defaults=job_defaults,
            timezone="Asia/Shanghai",  # 中国时区
        )
    return _scheduler


async def start_scheduler():
    """
    启动调度器

    注册所有定时任务并启动调度器
    """
    if not settings.daily_idea_enabled:
        logger.info("⏸️ 每日创意生成已禁用（DAILY_IDEA_ENABLED=false）")
        return

    scheduler = get_scheduler()

    # 添加每日创意生成任务
    scheduler.add_job(
        daily_idea_generation_job,
        trigger=CronTrigger(
            hour=settings.daily_idea_cron_hour,
            minute=settings.daily_idea_cron_minute,
        ),
        id="daily_idea_generation",
        name="每日创意生成",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("✅ 定时任务调度器已启动")
    logger.info(
        f"📅 每日创意生成任务: 每天 {settings.daily_idea_cron_hour:02d}:{settings.daily_idea_cron_minute:02d}"
    )

    # 列出所有已注册的任务
    jobs = scheduler.get_jobs()
    logger.info(f"📋 已注册任务数: {len(jobs)}")
    for job in jobs:
        logger.info(f"   - {job.name} (ID: {job.id})")


async def stop_scheduler():
    """
    停止调度器

    优雅关闭，等待正在执行的任务完成
    """
    scheduler = get_scheduler()
    scheduler.shutdown(wait=True)
    logger.info("🛑 定时任务调度器已停止")
