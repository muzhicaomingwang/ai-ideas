#!/usr/bin/env python3
"""
GMailHelper - 每日邮件清理主脚本

自动处理邮件：归档营销邮件、分类通知邮件、AI智能分类
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from gmail_client import GmailMCPClient
from rules_engine import RulesEngine
from ai_classifier import AIEmailClassifier
from processors import EmailProcessor
from feishu_notifier import FeishuNotifier
from utils import Logger, CacheManager, ReportGenerator


def main():
    """主执行函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="GMailHelper - 每日邮件清理")
    parser.add_argument("--dry-run", action="store_true", help="模拟模式（不实际修改邮件）")
    parser.add_argument("--max-emails", type=int, default=500, help="最大处理邮件数")
    parser.add_argument("--no-ai", action="store_true", help="禁用AI分类")
    parser.add_argument("--no-feishu", action="store_true", help="禁用飞书通知")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()

    # 项目根目录
    project_dir = Path(__file__).parent.parent
    os.chdir(project_dir)

    # 设置日志
    logger = Logger.setup(log_dir=str(project_dir / "logs"))
    logger.info("=" * 60)
    logger.info("GMailHelper 开始执行")
    logger.info("=" * 60)
    logger.info(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"执行模式: {'模拟模式' if args.dry_run else '实际执行'}")

    # 加载环境变量
    from dotenv import load_dotenv
    env_file = project_dir / ".env"
    if not env_file.exists():
        logger.error("❌ .env 文件不存在，请创建环境变量文件")
        sys.exit(1)

    load_dotenv(env_file)
    logger.info("✅ 环境变量已加载")

    # 初始化组件
    try:
        # Gmail客户端
        gmail = GmailMCPClient()
        logger.info("✅ Gmail MCP客户端初始化成功")

        # 规则引擎
        rules_engine = RulesEngine(str(project_dir / "config" / "rules.yaml"))
        config = rules_engine.get_config()
        logger.info(f"✅ 规则引擎加载成功（{len(rules_engine.rules)} 条规则）")

        # AI分类器（可选）
        ai_classifier = None
        if not args.no_ai and os.getenv("ANTHROPIC_API_KEY"):
            try:
                ai_classifier = AIEmailClassifier(
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    model="claude-3-5-haiku-20241022"
                )
                logger.info("✅ AI分类器初始化成功（Claude 3.5 Haiku）")
            except Exception as e:
                logger.warning(f"⚠️ AI分类器初始化失败: {e}")
                logger.info("将继续使用规则匹配，不使用AI分类")
        else:
            logger.info("ℹ️ AI分类器未启用")

        # 邮件处理器
        processor = EmailProcessor(gmail, dry_run=args.dry_run)
        logger.info("✅ 邮件处理器初始化成功")

        # 飞书通知器（可选）
        feishu_notifier = None
        if not args.no_feishu and os.getenv("FEISHU_APP_SECRET"):
            try:
                feishu_notifier = FeishuNotifier(
                    app_id=os.getenv("FEISHU_APP_ID"),
                    app_secret=os.getenv("FEISHU_APP_SECRET"),
                    user_open_id=os.getenv("FEISHU_USER_OPEN_ID")
                )
                logger.info("✅ 飞书通知器初始化成功")
            except Exception as e:
                logger.warning(f"⚠️ 飞书通知器初始化失败: {e}")
                feishu_notifier = None
        else:
            logger.info("ℹ️ 飞书通知未启用")

        # 缓存管理器
        cache_manager = CacheManager(str(project_dir / "cache"))

    except Exception as e:
        logger.error(f"❌ 初始化失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

    # 搜索未读邮件
    logger.info("")
    logger.info("📬 搜索未读邮件...")

    try:
        emails = gmail.search_emails(
            query="is:unread in:inbox",
            max_results=args.max_emails
        )
        logger.info(f"✅ 找到 {len(emails)} 封未读邮件")

    except Exception as e:
        logger.error(f"❌ 搜索邮件失败: {e}")
        if feishu_notifier:
            feishu_notifier.send_error_notification(str(e))
        sys.exit(1)

    # 加载缓存（幂等性）
    today = datetime.now().strftime("%Y-%m-%d")
    processed_cache = cache_manager.load_processed_ids(today)
    logger.info(f"📂 缓存加载：今日已处理 {len(processed_cache)} 封邮件")

    # 初始化统计
    stats = {
        "total": len(emails),
        "processed": 0,
        "whitelisted": 0,
        "matched": 0,
        "ai_classified": 0,
        "unmatched": 0,
        "errors": 0,
        "dry_run": args.dry_run
    }

    details = {
        "marketing": {"count": 0, "senders": defaultdict(int), "actions": ["归档", "标记已读"]},
        "notification": {"count": 0, "senders": defaultdict(int), "actions": ["归档"]},
        "forum": {"count": 0, "senders": defaultdict(int), "actions": ["归档", "标记已读"]},
        "ai_classification": defaultdict(int)
    }

    # 处理邮件
    logger.info("")
    logger.info("🔄 开始处理邮件...")
    logger.info("")

    for i, email in enumerate(emails, 1):
        message_id = email.get("id")
        sender = email.get("from", "")
        subject = email.get("subject", "")

        if args.verbose:
            logger.info(f"[{i}/{len(emails)}] {subject[:50]}...")

        # 检查是否已处理
        if message_id in processed_cache:
            if args.verbose:
                logger.info("  ⏭️ 已处理，跳过")
            continue

        # 白名单检查
        if rules_engine.is_whitelisted(email):
            stats["whitelisted"] += 1
            if args.verbose:
                logger.info("  ⭐ 白名单邮件，跳过")
            continue

        # 规则匹配
        matched_rule = rules_engine.match_rule(email)

        if matched_rule:
            # 匹配到规则
            stats["matched"] += 1

            if args.verbose:
                logger.info(f"  📌 匹配规则: {matched_rule.name}")

            try:
                processor.execute_actions(message_id, matched_rule.actions, logger)
                stats["processed"] += 1

                # 记录详细信息
                rule_category = matched_rule.name.lower()
                if "营销" in rule_category:
                    details["marketing"]["count"] += 1
                    details["marketing"]["senders"][sender] += 1
                elif "通知" in rule_category:
                    details["notification"]["count"] += 1
                    details["notification"]["senders"][sender] += 1
                elif "论坛" in rule_category:
                    details["forum"]["count"] += 1
                    details["forum"]["senders"][sender] += 1

            except Exception as e:
                logger.error(f"  ❌ 处理失败: {e}")
                stats["errors"] += 1

        else:
            # 未匹配规则，尝试AI分类
            if ai_classifier:
                stats["ai_classified"] += 1

                if args.verbose:
                    logger.info("  🤖 使用AI分类...")

                try:
                    # AI分类
                    category = ai_classifier.classify(email)

                    if args.verbose:
                        logger.info(f"  🎯 AI分类结果: {category}")

                    # 根据AI分类结果执行动作
                    # 从配置中获取动作映射
                    ai_config = config.get("rules", [])[-1] if config.get("rules") else {}
                    action_mapping = ai_config.get("ai_config", {}).get("action_mapping", {})

                    actions = action_mapping.get(category, [])

                    if actions:
                        processor.execute_actions(message_id, actions, logger)
                        stats["processed"] += 1
                        details["ai_classification"][category] += 1
                    else:
                        # 如果没有找到对应的动作，标记为未分类
                        stats["unmatched"] += 1

                except Exception as e:
                    logger.error(f"  ❌ AI分类失败: {e}")
                    stats["errors"] += 1
                    stats["unmatched"] += 1

            else:
                stats["unmatched"] += 1
                if args.verbose:
                    logger.info("  ℹ️ 未匹配规则，保留")

        # 添加到已处理缓存
        processed_cache.add(message_id)

    # 保存缓存
    logger.info("")
    logger.info("💾 保存处理缓存...")
    cache_manager.save_processed_ids(processed_cache, today)

    # 生成报告
    logger.info("")
    logger.info("📝 生成处理报告...")

    output_dir = project_dir / "output" / today
    output_dir.mkdir(parents=True, exist_ok=True)

    report = ReportGenerator.generate_markdown_report(stats, details)
    report_path = output_dir / f"report-{today}.md"
    ReportGenerator.save_report(report, str(report_path))

    logger.info(f"✅ 报告已保存: {report_path}")

    # 发送飞书通知
    if feishu_notifier and stats["processed"] > 0:
        logger.info("")
        logger.info("📱 发送飞书通知...")

        try:
            feishu_notifier.send_daily_report(stats, details)
            logger.info("✅ 飞书通知发送成功")
        except Exception as e:
            logger.error(f"❌ 飞书通知发送失败: {e}")

    # 输出摘要
    logger.info("")
    logger.info("=" * 60)
    logger.info("执行完成！")
    logger.info("=" * 60)
    logger.info(f"总邮件数: {stats['total']}")
    logger.info(f"已处理: {stats['processed']} ({stats['processed']/max(stats['total'],1)*100:.1f}%)")
    logger.info(f"白名单: {stats['whitelisted']}")
    logger.info(f"规则匹配: {stats['matched']}")
    logger.info(f"AI分类: {stats.get('ai_classified', 0)}")
    logger.info(f"未匹配: {stats['unmatched']}")
    logger.info(f"错误: {stats.get('errors', 0)}")
    logger.info("")


if __name__ == "__main__":
    main()
