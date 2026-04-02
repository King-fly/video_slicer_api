from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class VideoBase(BaseModel):
    """视频基础模型"""
    title: str = Field(..., min_length=1, max_length=255, description="视频标题")


class VideoCreate(VideoBase):
    """视频创建模型"""
    pass  # 文件通过multipart/form-data上传


class VideoUpdate(VideoBase):
    """视频更新模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="视频标题")


class VideoResponse(VideoBase):
    """视频响应模型"""
    id: int
    user_id: int
    filename: str
    filepath: str
    duration: int
    size: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    """视频列表响应模型"""
    total: int
    items: List[VideoResponse]


class VideoUploadResponse(BaseModel):
    """视频上传响应模型"""
    video_id: int
    message: str
    task_id: Optional[str] = None