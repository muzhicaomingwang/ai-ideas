"""
数据模型定义
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class NoteType(str, Enum):
    """笔记类型"""
    IMAGE = "image"  # 图文笔记
    VIDEO = "video"  # 视频笔记


class MediaItem(BaseModel):
    """媒体项"""
    url: str = Field(..., description="媒体URL")
    width: Optional[int] = Field(None, description="宽度")
    height: Optional[int] = Field(None, description="高度")
    local_path: Optional[str] = Field(None, description="本地保存路径")


class Author(BaseModel):
    """作者信息"""
    id: str = Field(..., description="作者ID")
    name: str = Field(..., description="作者昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    fans_count: Optional[int] = Field(None, description="粉丝数")


class Comment(BaseModel):
    """评论"""
    id: str = Field(..., description="评论ID")
    user_id: str = Field(..., description="用户ID")
    user_name: str = Field(..., description="用户昵称")
    user_avatar: Optional[str] = Field(None, description="用户头像")
    content: str = Field(..., description="评论内容")
    likes: int = Field(0, description="点赞数")
    time: Optional[datetime] = Field(None, description="评论时间")
    replies: list["Comment"] = Field(default_factory=list, description="回复列表")


class NoteStats(BaseModel):
    """笔记统计数据"""
    likes: int = Field(0, description="点赞数")
    collects: int = Field(0, description="收藏数")
    comments: int = Field(0, description="评论数")
    shares: int = Field(0, description="分享数")


class NoteContent(BaseModel):
    """笔记完整内容"""
    note_id: str = Field(..., description="笔记ID")
    url: str = Field(..., description="原始URL")
    type: NoteType = Field(..., description="笔记类型")
    title: str = Field(..., description="标题")
    content: str = Field("", description="正文内容")
    tags: list[str] = Field(default_factory=list, description="标签列表")
    author: Author = Field(..., description="作者信息")
    stats: NoteStats = Field(default_factory=NoteStats, description="统计数据")
    images: list[MediaItem] = Field(default_factory=list, description="图片列表")
    video: Optional[MediaItem] = Field(None, description="视频信息")
    comments: list[Comment] = Field(default_factory=list, description="评论列表")
    crawled_at: datetime = Field(default_factory=datetime.now, description="抓取时间")


class ScrapeRequest(BaseModel):
    """抓取请求"""
    url: str = Field(..., description="小红书链接", examples=["https://www.xiaohongshu.com/explore/xxx"])
    download_media: bool = Field(True, description="是否下载媒体文件")
    fetch_comments: bool = Field(True, description="是否抓取评论")
    comment_limit: int = Field(100, description="评论数量限制", ge=1, le=1000)


class ScrapeResponse(BaseModel):
    """抓取响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field("", description="消息")
    data: Optional[NoteContent] = Field(None, description="笔记内容")
    error: Optional[str] = Field(None, description="错误信息")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="服务版本")
    browser_ready: bool = Field(..., description="浏览器是否就绪")
    login_status: bool = Field(..., description="登录状态")
