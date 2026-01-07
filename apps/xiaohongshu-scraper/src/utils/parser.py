"""
小红书 URL 解析工具
"""
import re
from typing import Optional
from urllib.parse import urlparse, parse_qs


class XHSUrlParser:
    """小红书 URL 解析器"""

    # 支持的 URL 模式（注意：更具体的模式必须放在前面）
    PATTERNS = [
        # Web 端详情页: https://www.xiaohongshu.com/explore/xxxxx
        r"xiaohongshu\.com/explore/([a-zA-Z0-9]+)",
        # Web 端详情页（带参数）: https://www.xiaohongshu.com/discovery/item/xxxxx
        r"xiaohongshu\.com/discovery/item/([a-zA-Z0-9]+)",
        # App 分享链接: http://xhslink.com/a/xxxxx（必须在通用短链接之前）
        r"xhslink\.com/a/([a-zA-Z0-9]+)",
        # 短链接: https://xhslink.com/xxxxx
        r"xhslink\.com/([a-zA-Z0-9]+)",
    ]

    @classmethod
    def extract_note_id(cls, url: str) -> Optional[str]:
        """
        从 URL 中提取笔记 ID

        Args:
            url: 小红书链接

        Returns:
            笔记 ID 或 None
        """
        if not url:
            return None

        # 清理 URL
        url = url.strip()

        # 尝试匹配各种模式
        for pattern in cls.PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    @classmethod
    def is_valid_xhs_url(cls, url: str) -> bool:
        """
        检查是否为有效的小红书 URL

        Args:
            url: 待检查的 URL

        Returns:
            是否有效
        """
        if not url:
            return False

        # 检查域名
        try:
            parsed = urlparse(url)
            valid_domains = ["xiaohongshu.com", "www.xiaohongshu.com", "xhslink.com"]
            return parsed.netloc in valid_domains
        except Exception:
            return False

    @classmethod
    def normalize_url(cls, url: str) -> str:
        """
        标准化 URL

        Args:
            url: 原始 URL

        Returns:
            标准化后的 URL
        """
        note_id = cls.extract_note_id(url)
        if note_id:
            return f"https://www.xiaohongshu.com/explore/{note_id}"
        return url

    @classmethod
    def parse(cls, url: str) -> dict:
        """
        解析 URL 并返回详细信息

        Args:
            url: 小红书链接

        Returns:
            解析结果字典
        """
        note_id = cls.extract_note_id(url)
        return {
            "original_url": url,
            "note_id": note_id,
            "normalized_url": cls.normalize_url(url) if note_id else None,
            "is_valid": note_id is not None,
        }
