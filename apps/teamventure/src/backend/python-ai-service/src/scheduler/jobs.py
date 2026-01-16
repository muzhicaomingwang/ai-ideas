"""
定时任务定义

包含所有定时任务的具体执行逻辑

@author TeamVenture Team
@version 1.0.0
@since 2026-01-15
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from src.models.config import settings
from src.services.feishu_publisher import FeishuPublisher
# TEMP: 临时禁用idea_generator和idea_storage（Git依赖问题），专注测试Markdown方案生成功能
# from src.services.idea_generator import DailyIdeaGenerator
# from src.services.idea_storage import IdeaStorage
from src.services.notion_publisher import NotionPublisher

logger = logging.getLogger(__name__)


async def daily_idea_generation_job():
    """
    每日创意生成任务

    TEMP: 临时禁用（Git依赖问题），专注测试Markdown方案生成功能
    """
    logger.info("⏭️ 每日创意生成任务已临时禁用（Git依赖问题）")
    return

    # start_time = datetime.now()
    # logger.info(f"🎯 开始执行每日创意生成任务 - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    #
    # try:
    #     # ========== 1. 生成创意 ==========
    #     generator = DailyIdeaGenerator()
    #     batch = await generator.generate_daily_ideas()
    #     logger.info(f"✅ 创意生成成功: {len(batch.ideas)} 个")
    #
    #     # 打印创意摘要
    #     for i, idea in enumerate(batch.ideas, 1):
    #         logger.info(f"   {i}. [{idea.priority}/{idea.category}] {idea.title}")
    #
    #     # ========== 2. 保存到本地 & Git 提交 ==========
    #     storage = IdeaStorage(generator.repo_root)
    #     file_path = storage.save_to_markdown(batch)
    #     logger.info(f"✅ 文件保存成功: {file_path}")
    #
    #     # Git 自动提交
    #     git_success = storage.git_commit_and_push(file_path, batch.date)
    #     if git_success:
    #         logger.info(f"✅ Git 提交成功")
    #     else:
    #         logger.warning(f"⚠️ Git 提交失败，但文件已保存到本地")
    #
    #     # ========== 3. 同步到 Notion（如果配置了）==========
    #     if settings.notion_page_id:
    #         try:
    #             notion = NotionPublisher(settings.notion_page_id)
    #             await notion.publish_to_notion(batch)
    #         except Exception as e:
    #             logger.error(f"⚠️ Notion 同步失败（不影响主流程）: {e}")
    #     else:
    #         logger.info("⏭️ 跳过 Notion 同步（未配置 NOTION_PAGE_ID）")
    #
    #     # ========== 4. 推送到飞书（如果配置了）==========
    #     if settings.feishu_doc_token and settings.feishu_chat_id:
    #         try:
    #             feishu = FeishuPublisher(settings.feishu_doc_token, settings.feishu_chat_id)
    #             await feishu.publish_to_feishu(batch)
    #         except Exception as e:
    #             logger.error(f"⚠️ 飞书推送失败（不影响主流程）: {e}")
    #     else:
    #         logger.info("⏭️ 跳过飞书推送（未配置 FEISHU_DOC_TOKEN/FEISHU_CHAT_ID）")
    #
    #     # ========== 5. 记录执行时长 ==========
    #     duration = (datetime.now() - start_time).total_seconds()
    #     logger.info(f"✅ 任务执行完成，耗时 {duration:.2f} 秒")
    #
    #     # 返回结果摘要
    #     return {
    #         "status": "success",
    #         "date": batch.date,
    #         "ideas_count": len(batch.ideas),
    #         "file_path": str(file_path),
    #         "git_committed": git_success,
    #         "duration_seconds": duration,
    #     }
    #
    # except Exception as e:
    #     logger.error(f"❌ 任务执行失败: {e}", exc_info=True)
    #
    #     # 可选：发送告警通知（邮件/Slack/飞书等）
    #     # await send_alert(f"每日创意生成任务失败: {e}")
    #
    #     return {
    #         "status": "failure",
    #         "error": str(e),
    #         "duration_seconds": (datetime.now() - start_time).total_seconds(),
    #     }


# ========== 手动触发入口（用于测试）==========
# TEMP: 临时禁用
# if __name__ == "__main__":
#     """手动触发任务（调试用）"""
#     import asyncio
#
#     logging.basicConfig(
#         level=logging.INFO,
#         format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
#     )
#
#     asyncio.run(daily_idea_generation_job())
