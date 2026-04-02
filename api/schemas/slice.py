from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SliceBase(BaseModel):
    """切片基础模型"""
    title: Optional[str] = Field(None, max_length=255, description="切片标题")
    description: Optional[str] = Field(None, description="切片描述")
    tags: Optional[List[str]] = Field(None, description="切片标签列表")


class SliceCreate(BaseModel):
    """切片创建模型"""
    method: str = Field("fixed", description="切片方法: fixed或scene")
    duration: int = Field(60, ge=5, le=300, description="切片时长（秒）")
    scene_threshold: float = Field(0.3, ge=0.1, le=0.9, description="场景变化阈值")


class SliceUpdate(SliceBase):
    """切片更新模型"""
    pass


class SliceResponse(SliceBase):
    """切片响应模型"""
    id: int
    video_id: int
    filename: str
    filepath: str
    start_time: int
    end_time: int
    duration: int
    size: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SliceListResponse(BaseModel):
    """切片列表响应模型"""
    total: int
    items: List[SliceResponse]


class SliceCreateResponse(BaseModel):
    """切片创建响应模型"""
    message: str
    task_id: str
    video_id: int