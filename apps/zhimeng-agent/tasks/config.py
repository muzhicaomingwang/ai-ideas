"""定时任务共享配置

包含所有定时任务需要的路径、API配置等。
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# 加载环境变量
from dotenv import load_dotenv

# 尝试从多个位置加载 .env
env_paths = [
    Path(__file__).parent.parent / "config" / ".env",
    Path(__file__).parent / ".env",
    Path.home() / ".zhimeng-agent.env",
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break


@dataclass
class TaskConfig:
    """任务配置"""

    # ==================== 路径配置 ====================

    # 项目根目录
    IDEAS_ROOT: Path = Path("/Users/qitmac001395/workspace/QAL/ideas")

    # Obsidian 知识库路径
    OBSIDIAN_VAULT: Path = Path("/Users/qitmac001395/Documents/Obsidian Vault")

    # 日报输出目录
    JOURNAL_DIR: Path = OBSIDIAN_VAULT / "Journal"

    # 科技新闻输出目录
    NEWS_DIR: Path = OBSIDIAN_VAULT / "News"

    # 桌面路径
    DESKTOP_PATH: Path = Path.home() / "Desktop"

    # 下载目录
    DOWNLOADS_PATH: Path = Path.home() / "Downloads"

    # 文档目录
    DOCUMENTS_PATH: Path = Path.home() / "Documents"

    # 整理后的归档目录
    ARCHIVE_PATH: Path = Path.home() / "Documents" / "Archive"

    # ==================== API 配置 ====================

    # 飞书配置
    FEISHU_APP_ID: str = os.getenv("FEISHU_APP_ID", "")
    FEISHU_APP_SECRET: str = os.getenv("FEISHU_APP_SECRET", "")

    # 飞书接收人 open_id（王植萌）
    FEISHU_RECIPIENT_OPEN_ID: str = "ou_18b8063b232cbdec73ea1541dfb74890"

    # Anthropic API
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # OpenAI API
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # ==================== 服务配置 ====================

    # zhimeng-agent 服务地址
    AGENT_SERVICE_URL: str = "http://localhost:8001"

    # ==================== 定时任务时间 ====================

    # 日报生成时间（每晚0点）
    DAILY_REPORT_HOUR: int = 0
    DAILY_REPORT_MINUTE: int = 0

    # 邮箱整理时间（每晚2点）
    EMAIL_ORGANIZE_HOUR: int = 2
    EMAIL_ORGANIZE_MINUTE: int = 0

    # 桌面整理时间（每晚4点）
    DESKTOP_ORGANIZE_HOUR: int = 4
    DESKTOP_ORGANIZE_MINUTE: int = 0

    # 科技新闻时间（每早7点）
    TECH_NEWS_HOUR: int = 7
    TECH_NEWS_MINUTE: int = 0

    # ==================== 文件分类规则 ====================

    # 桌面/下载目录文件分类规则
    FILE_CATEGORIES: dict = None

    def __post_init__(self):
        # 确保目录存在
        self.JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
        self.NEWS_DIR.mkdir(parents=True, exist_ok=True)
        self.ARCHIVE_PATH.mkdir(parents=True, exist_ok=True)

        # 文件分类规则
        self.FILE_CATEGORIES = {
            # 文档类
            "Documents": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".rtf", ".odt"],
            # 图片类
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".heic", ".raw"],
            # 视频类
            "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
            # 音频类
            "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
            # 压缩包
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".dmg", ".iso"],
            # 代码类
            "Code": [".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".go", ".rs", ".swift", ".kt", ".rb", ".php", ".html", ".css", ".json", ".xml", ".yaml", ".yml", ".md", ".sh", ".sql"],
            # 安装包
            "Installers": [".pkg", ".app", ".exe", ".msi", ".deb", ".rpm"],
            # 数据文件
            "Data": [".csv", ".tsv", ".db", ".sqlite", ".parquet", ".arrow"],
            # 设计文件
            "Design": [".psd", ".ai", ".sketch", ".fig", ".xd", ".indd"],
            # 其他
            "Others": [],
        }


# 单例配置
config = TaskConfig()
