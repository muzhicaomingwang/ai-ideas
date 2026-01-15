"""日志配置模块"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str = "xhs_podcast",
    level: str = "INFO",
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别（DEBUG/INFO/WARNING/ERROR）
        log_file: 日志文件路径（可选）

    Returns:
        配置好的Logger实例
    """
    logger = logging.getLogger(name)

    # 避免重复添加handler
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper()))

    # 日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件handler（如果指定）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "xhs_podcast") -> logging.Logger:
    """
    获取已配置的日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        Logger实例
    """
    return logging.getLogger(name)


class ProgressLogger:
    """进度日志记录器"""

    def __init__(self, logger: logging.Logger, total_steps: int):
        """
        初始化

        Args:
            logger: 日志记录器
            total_steps: 总步骤数
        """
        self.logger = logger
        self.total_steps = total_steps
        self.current_step = 0

    def log_step(self, message: str):
        """
        记录步骤进度

        Args:
            message: 步骤消息
        """
        self.current_step += 1
        progress = int((self.current_step / self.total_steps) * 100)
        self.logger.info(f"[进度: {progress}%] {message}")

    def log_info(self, message: str):
        """记录信息"""
        self.logger.info(f"  {message}")

    def log_error(self, message: str):
        """记录错误"""
        self.logger.error(f"  ❌ {message}")

    def log_success(self, message: str):
        """记录成功"""
        self.logger.info(f"  ✅ {message}")
