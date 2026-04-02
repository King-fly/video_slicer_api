from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class TaskBase(BaseModel):
    """任务基础模型"""
    task_type: str = Field(..., description="任务类型")
    status: str = Field("pending", description="任务状态")
    progress: int = Field(0, ge=0, le=100, description="任务进度")


class TaskCreate(TaskBase):
    """任务创建模型"""
    user_id: int = Field(..., description="用户ID")
    result: Optional[Dict[str, Any]] = Field(None, description="任务结果")
    error: Optional[str] = Field(None, description="错误信息")


class TaskUpdate(BaseModel):
    """任务更新模型"""
    status: Optional[str] = Field(None, description="任务状态")
    progress: Optional[int] = Field(None, ge=0, le=100, description="任务进度")
    result: Optional[Dict[str, Any]] = Field(None, description="任务结果")
    error: Optional[str] = Field(None, description="错误信息")


class TaskResponse(TaskBase):
    """任务响应模型"""
    id: str
    user_id: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """任务列表响应模型"""
    total: int
    items: List[TaskResponse]


class TaskStatusUpdate(BaseModel):
    """任务状态更新模型"""
    status: str = Field(..., description="任务状态")
    progress: Optional[int] = Field(None, ge=0, le=100, description="任务进度")