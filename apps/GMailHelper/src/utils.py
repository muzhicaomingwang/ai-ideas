"""
工具函数模块

提供日志、缓存、报告生成等通用功能
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Set, Dict


class Logger:
    """日志工具类"""

    @staticmethod
    def setup(log_dir: str, log_file: str = None) -> logging.Logger:
        """
        设置日志记录器

        Args:
            log_dir: 日志目录
            log_file: 日志文件名（默认使用当前日期）

        Returns:
            Logger对象
        """
        log_dir_path = Path(log_dir)
        log_dir_path.mkdir(parents=True, exist_ok=True)

        if log_file is None:
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = f"daily-{today}.log"

        log_path = log_dir_path / log_file

        # 配置日志格式
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.FileHandler(log_path, encoding="utf-8"),
                logging.StreamHandler()
            ]
        )

        return logging.getLogger("GMailHelper")


class CacheManager:
    """缓存管理类（用于幂等性保证）"""

    def __init__(self, cache_dir: str):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def load_processed_ids(self, date: str = None) -> Set[str]:
        """
        加载今日已处理的邮件ID

        Args:
            date: 日期（YYYY-MM-DD，默认今天）

        Returns:
            已处理邮件ID集合
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        cache_file = self.cache_dir / f"{date}-processed.json"

        if not cache_file.exists():
            return set()

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("processed_ids", []))
        except (json.JSONDecodeError, IOError):
            return set()

    def save_processed_ids(self, processed_ids: Set[str], date: str = None):
        """
        保存今日已处理的邮件ID

        Args:
            processed_ids: 已处理邮件ID集合
            date: 日期（YYYY-MM-DD，默认今天）
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        cache_file = self.cache_dir / f"{date}-processed.json"

        data = {
            "date": date,
            "processed_ids": list(processed_ids),
            "last_updated": datetime.now().isoformat()
        }

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


class ReportGenerator:
    """报告生成器"""

    @staticmethod
    def generate_markdown_report(stats: Dict, details: Dict) -> str:
        """
        生成Markdown格式的处理报告

        Args:
            stats: 统计数据
            details: 详细信息

        Returns:
            Markdown报告内容
        """
        today = datetime.now().strftime("%Y-%m-%d")
        time_now = datetime.now().strftime("%H:%M:%S")

        report = f"""# GMailHelper 执行报告

**执行日期**: {today}
**执行时间**: {time_now}
**执行模式**: {"模拟运行（Dry Run）" if stats.get('dry_run') else "实际执行"}

---

## 📊 统计摘要

| 指标 | 数量 | 占比 |
|------|------|------|
| 总邮件数 | {stats['total']} | 100% |
| 白名单邮件 | {stats['whitelisted']} | {stats['whitelisted']/max(stats['total'],1)*100:.1f}% |
| 匹配规则 | {stats['matched']} | {stats['matched']/max(stats['total'],1)*100:.1f}% |
| AI分类 | {stats.get('ai_classified', 0)} | {stats.get('ai_classified', 0)/max(stats['total'],1)*100:.1f}% |
| 已处理 | {stats['processed']} | {stats['processed']/max(stats['total'],1)*100:.1f}% |
| 处理失败 | {stats.get('errors', 0)} | {stats.get('errors', 0)/max(stats['total'],1)*100:.1f}% |

---

## 📋 处理详情

### 营销邮件（{details.get('marketing', {}).get('count', 0)}封）
"""

        marketing = details.get('marketing', {})
        if marketing.get('senders'):
            for sender, count in sorted(
                marketing['senders'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]:
                report += f"- {sender}: {count}封\n"

        report += f"\n**执行动作**: {', '.join(marketing.get('actions', []))}\n\n"

        report += f"""### 通知邮件（{details.get('notification', {}).get('count', 0)}封）
"""

        notification = details.get('notification', {})
        if notification.get('senders'):
            for sender, count in sorted(
                notification['senders'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]:
                report += f"- {sender}: {count}封\n"

        report += f"\n**执行动作**: {', '.join(notification.get('actions', []))}\n\n"

        report += f"""### 论坛邮件（{details.get('forum', {}).get('count', 0)}封）
"""

        forum = details.get('forum', {})
        if forum.get('senders'):
            for sender, count in sorted(
                forum['senders'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]:
                report += f"- {sender}: {count}封\n"

        report += f"\n**执行动作**: {', '.join(forum.get('actions', []))}\n\n"

        # AI分类结果
        if stats.get('ai_classified', 0) > 0:
            report += f"""### AI分类邮件（{stats.get('ai_classified', 0)}封）

"""
            ai_details = details.get('ai_classification', {})
            for category, count in ai_details.items():
                report += f"- {category}: {count}封\n"

            report += "\n"

        # 未匹配邮件
        if stats.get('unmatched', 0) > 0:
            report += f"""### 未匹配邮件（{stats['unmatched']}封）

保留在收件箱，建议人工处理

"""

        report += f"""---

## ✅ 执行结果

- **总处理数**: {stats['processed']} 封邮件
- **成功率**: {(stats['processed'] - stats.get('errors', 0)) / max(stats['processed'], 1) * 100:.1f}%
- **收件箱清理率**: {stats['processed'] / max(stats['total'], 1) * 100:.1f}%

---

## 📝 建议

"""

        if stats['processed'] / max(stats['total'], 1) > 0.7:
            report += "- ✅ 收件箱清理效果良好\n"
        else:
            report += "- ⚠️ 清理率较低，建议优化规则配置\n"

        if stats.get('unmatched', 0) > 10:
            report += f"- ℹ️ 有 {stats['unmatched']} 封未分类邮件，建议添加新规则\n"

        if stats.get('errors', 0) > 0:
            report += f"- ⚠️ 有 {stats['errors']} 个错误，请检查日志\n"

        report += "\n---\n\n*本报告由 GMailHelper 自动生成*\n"

        return report

    @staticmethod
    def save_report(content: str, output_path: str):
        """
        保存报告到文件

        Args:
            content: 报告内容
            output_path: 输出路径
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
