"""桌面整理任务

每晚凌晨 4 点执行，自动整理桌面和下载目录。

整理规则：
1. 按文件类型分类（文档/图片/视频/音频/压缩包/代码/安装包等）
2. 移动到归档目录的日期子文件夹
3. 生成整理报告同步到 Obsidian
"""

import os
import sys
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tasks.config import config
from tasks.sync_utils import create_syncer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# 跳过的文件/文件夹
SKIP_PATTERNS = [
    ".DS_Store",
    ".localized",
    "Thumbs.db",
    "desktop.ini",
    ".Spotlight-V100",
    ".Trashes",
    ".fseventsd",
]

# 跳过的文件夹（桌面上的常驻文件夹）
SKIP_FOLDERS = [
    "Screenshots",
    "Workspace",
    "Temp",
]

# 文件年龄阈值（天数），超过此天数的文件才会被整理
FILE_AGE_THRESHOLD_DAYS = 1


@dataclass
class FileInfo:
    """文件信息"""
    path: Path
    name: str
    extension: str
    size: int
    modified_time: datetime
    category: str = "Others"


@dataclass
class OrganizeStats:
    """整理统计"""
    total_scanned: int = 0
    files_moved: int = 0
    folders_skipped: int = 0
    size_freed: int = 0  # bytes
    by_category: Dict[str, int] = field(default_factory=dict)
    by_source: Dict[str, int] = field(default_factory=dict)  # Desktop/Downloads
    errors: List[str] = field(default_factory=list)


class DesktopOrganizer:
    """桌面和下载目录整理器"""

    def __init__(self, dry_run: bool = False, include_downloads: bool = True):
        """
        Args:
            dry_run: 如果为 True，只分析不实际移动
            include_downloads: 是否同时整理下载目录
        """
        self.dry_run = dry_run
        self.include_downloads = include_downloads
        self.stats = OrganizeStats()
        self.file_categories = config.FILE_CATEGORIES

    def get_category(self, extension: str) -> str:
        """根据扩展名获取文件分类"""
        ext_lower = extension.lower()
        for category, extensions in self.file_categories.items():
            if ext_lower in extensions:
                return category
        return "Others"

    def should_skip(self, path: Path) -> bool:
        """判断是否应该跳过此文件/文件夹"""
        name = path.name

        # 跳过隐藏文件和系统文件
        if name.startswith(".") and name not in [".env", ".gitignore"]:
            return True

        # 跳过特定模式
        if name in SKIP_PATTERNS:
            return True

        # 跳过常驻文件夹
        if path.is_dir() and name in SKIP_FOLDERS:
            return True

        return False

    def is_old_enough(self, path: Path) -> bool:
        """检查文件是否足够旧（超过阈值天数未修改）"""
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            age = datetime.now() - mtime
            return age.days >= FILE_AGE_THRESHOLD_DAYS
        except Exception:
            return False

    def scan_directory(self, directory: Path) -> List[FileInfo]:
        """扫描目录获取文件列表"""
        files = []

        if not directory.exists():
            logger.warning(f"目录不存在: {directory}")
            return files

        try:
            for item in directory.iterdir():
                # 跳过特定文件/文件夹
                if self.should_skip(item):
                    if item.is_dir():
                        self.stats.folders_skipped += 1
                    continue

                self.stats.total_scanned += 1

                # 只处理文件，跳过文件夹（文件夹需要特殊处理）
                if item.is_dir():
                    # 对于旧文件夹，也可以整理
                    if self.is_old_enough(item):
                        files.append(FileInfo(
                            path=item,
                            name=item.name,
                            extension="",
                            size=self._get_folder_size(item),
                            modified_time=datetime.fromtimestamp(item.stat().st_mtime),
                            category="Folders",
                        ))
                    continue

                # 检查文件年龄
                if not self.is_old_enough(item):
                    continue

                # 获取文件信息
                stat = item.stat()
                extension = item.suffix
                category = self.get_category(extension)

                files.append(FileInfo(
                    path=item,
                    name=item.name,
                    extension=extension,
                    size=stat.st_size,
                    modified_time=datetime.fromtimestamp(stat.st_mtime),
                    category=category,
                ))

        except Exception as e:
            logger.error(f"扫描目录 {directory} 失败: {e}")
            self.stats.errors.append(f"扫描 {directory}: {e}")

        return files

    def _get_folder_size(self, folder: Path) -> int:
        """计算文件夹大小"""
        total = 0
        try:
            for item in folder.rglob("*"):
                if item.is_file():
                    total += item.stat().st_size
        except Exception:
            pass
        return total

    def get_archive_path(self, file_info: FileInfo, source: str) -> Path:
        """获取归档目标路径"""
        # 按日期和来源组织
        date_str = datetime.now().strftime("%Y/%m")
        archive_dir = config.ARCHIVE_PATH / date_str / source / file_info.category

        return archive_dir / file_info.name

    def move_file(self, file_info: FileInfo, source: str) -> bool:
        """移动文件到归档目录"""
        dest_path = self.get_archive_path(file_info, source)

        if self.dry_run:
            logger.info(f"[DRY RUN] 将移动: {file_info.path} -> {dest_path}")
            return True

        try:
            # 创建目标目录
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # 处理同名文件
            if dest_path.exists():
                base = dest_path.stem
                ext = dest_path.suffix
                counter = 1
                while dest_path.exists():
                    dest_path = dest_path.parent / f"{base}_{counter}{ext}"
                    counter += 1

            # 移动文件
            shutil.move(str(file_info.path), str(dest_path))
            logger.info(f"已移动: {file_info.name} -> {dest_path.parent}")
            return True

        except Exception as e:
            logger.error(f"移动文件 {file_info.path} 失败: {e}")
            self.stats.errors.append(f"移动 {file_info.name}: {e}")
            return False

    def organize_directory(self, directory: Path, source_name: str):
        """整理单个目录"""
        logger.info(f"开始整理: {directory}")

        files = self.scan_directory(directory)
        logger.info(f"发现 {len(files)} 个待整理文件")

        for file_info in files:
            if self.move_file(file_info, source_name):
                self.stats.files_moved += 1
                self.stats.size_freed += file_info.size

                # 统计分类
                if file_info.category not in self.stats.by_category:
                    self.stats.by_category[file_info.category] = 0
                self.stats.by_category[file_info.category] += 1

                # 统计来源
                if source_name not in self.stats.by_source:
                    self.stats.by_source[source_name] = 0
                self.stats.by_source[source_name] += 1

    def organize(self) -> OrganizeStats:
        """执行整理"""
        logger.info("开始桌面和下载目录整理...")

        # 整理桌面
        self.organize_directory(config.DESKTOP_PATH, "Desktop")

        # 整理下载目录
        if self.include_downloads:
            self.organize_directory(config.DOWNLOADS_PATH, "Downloads")

        logger.info(
            f"整理完成: 扫描 {self.stats.total_scanned}, "
            f"移动 {self.stats.files_moved}, "
            f"释放 {self._format_size(self.stats.size_freed)}"
        )
        return self.stats

    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def generate_report(self) -> str:
        """生成整理报告 Markdown"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")

        lines = [
            f"# {date_str} 桌面整理报告",
            "",
            f"> 自动生成于 {now.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 概览",
            "",
            f"- 扫描文件: {self.stats.total_scanned} 个",
            f"- 整理文件: {self.stats.files_moved} 个",
            f"- 跳过文件夹: {self.stats.folders_skipped} 个",
            f"- 释放空间: {self._format_size(self.stats.size_freed)}",
            f"- 模式: {'模拟运行' if self.dry_run else '实际执行'}",
            "",
        ]

        if self.stats.by_source:
            lines.extend([
                "## 按来源统计",
                "",
            ])
            for source, count in sorted(self.stats.by_source.items()):
                lines.append(f"- {source}: {count} 个文件")
            lines.append("")

        if self.stats.by_category:
            lines.extend([
                "## 按类型统计",
                "",
            ])
            # 按数量排序
            sorted_categories = sorted(
                self.stats.by_category.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            for category, count in sorted_categories:
                lines.append(f"- {category}: {count} 个")
            lines.append("")

        if self.stats.errors:
            lines.extend([
                "## 错误日志",
                "",
            ])
            for error in self.stats.errors[:10]:  # 最多显示10条
                lines.append(f"- {error}")
            lines.append("")

        if not self.stats.files_moved and not self.stats.errors:
            lines.extend([
                "## 结果",
                "",
                "_今日无需整理的文件_",
                "",
            ])

        # 归档目录提示
        if self.stats.files_moved > 0:
            archive_path = config.ARCHIVE_PATH / datetime.now().strftime("%Y/%m")
            lines.extend([
                "## 归档位置",
                "",
                f"文件已移动到: `{archive_path}`",
                "",
            ])

        return "\n".join(lines)

    def run(self) -> Dict[str, bool]:
        """执行整理和同步"""
        # 执行整理
        self.organize()

        # 生成报告
        report = self.generate_report()
        date_str = datetime.now().strftime("%Y%m%d")
        report_title = f"desktop-organize-{date_str}"

        # 同步到 Obsidian（桌面整理报告仅本地保存）
        syncer = create_syncer()
        results = syncer.sync_content(
            title=report_title,
            content=report,
            targets=["obsidian"],  # 仅同步到 Obsidian
            obsidian_folder="Journal/Desktop",
        )

        logger.info(f"桌面整理报告同步结果: {results}")
        return results


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="桌面和下载目录整理任务")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅分析，不实际移动文件",
    )
    parser.add_argument(
        "--desktop-only",
        action="store_true",
        help="仅整理桌面，不整理下载目录",
    )

    args = parser.parse_args()

    organizer = DesktopOrganizer(
        dry_run=args.dry_run,
        include_downloads=not args.desktop_only,
    )

    if args.dry_run:
        organizer.organize()
        report = organizer.generate_report()
        print(report)
    else:
        results = organizer.run()
        success = all(results.values()) if results else False
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
