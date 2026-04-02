from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import uuid

from api.dependencies import get_db, get_current_active_user
from api.schemas.slice import (
    SliceCreate,
    SliceUpdate,
    SliceResponse,
    SliceListResponse,
    SliceCreateResponse
)
from domain.entities.user import User
from domain.entities.slice import Slice
from domain.entities.task import Task
from infrastructure.database.repositories.video_repo import VideoRepository
from infrastructure.database.repositories.slice_repo import SliceRepository
from infrastructure.database.repositories.task_repo import TaskRepository
from infrastructure.storage.file_storage import FileStorage
from celery_app.tasks.video_tasks import create_video_slices
from celery_app.tasks.ai_tasks import generate_ai_content_for_video_slices
from config.settings import get_settings

settings = get_settings()
router = APIRouter(prefix="/api", tags=["slices"])


@router.post("/videos/{video_id}/slices", response_model=SliceCreateResponse)
async def create_slices(
    video_id: int,
    slice_data: SliceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    为视频创建切片
    """
    # 验证视频存在且属于当前用户
    video_repo = VideoRepository(db)
    video = video_repo.get_by_id(video_id)
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    if video.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to slice this video"
        )
    
    # 移除视频状态限制，允许用户在任何状态下创建切片
    # 即使视频未处理完成，也可以尝试创建切片
    
    # 创建任务记录
    import uuid
    from domain.entities.task import Task
    from infrastructure.database.repositories.task_repo import TaskRepository
    task_repo = TaskRepository(db)
    task = Task(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        task_type="video_slicing",
        status="pending",
        progress=0
    )
    task = task_repo.create(task)
    
    # 异步创建切片
    from celery_app.tasks.video_tasks import create_video_slices
    create_video_slices.delay(
        video_id,
        method=slice_data.method,
        duration=slice_data.duration,
        scene_threshold=slice_data.scene_threshold,
        task_id=task.id
    )
    
    return {
        "message": "Slice creation started. Processing in background.",
        "task_id": task.id,
        "video_id": video_id
    }


@router.get("/videos/{video_id}/slices", response_model=SliceListResponse)
async def get_video_slices(
    video_id: int,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取视频的切片列表
    """
    # 验证视频存在且属于当前用户
    video_repo = VideoRepository(db)
    video = video_repo.get_by_id(video_id)
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    if video.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this video's slices"
        )
    
    # 获取切片列表
    slice_repo = SliceRepository(db)
    slices = slice_repo.get_by_video_id(video_id, skip=skip, limit=limit)
    
    # 获取总数
    all_slices = slice_repo.get_by_video_id(video_id)
    total = len(all_slices)
    
    return {
        "total": total,
        "items": slices
    }


@router.get("/slices/{slice_id}", response_model=SliceResponse)
async def get_slice(
    slice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取切片详情
    """
    slice_repo = SliceRepository(db)
    slice_entity = slice_repo.get_by_id(slice_id)
    
    if not slice_entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slice not found"
        )
    
    # 验证视频属于当前用户
    video_repo = VideoRepository(db)
    video = video_repo.get_by_id(slice_entity.video_id)
    
    if not video or video.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this slice"
        )
    
    return slice_entity


@router.put("/slices/{slice_id}", response_model=SliceResponse)
async def update_slice(
    slice_id: int,
    slice_data: SliceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新切片信息
    """
    slice_repo = SliceRepository(db)
    slice_entity = slice_repo.get_by_id(slice_id)
    
    if not slice_entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slice not found"
        )
    
    # 验证视频属于当前用户
    video_repo = VideoRepository(db)
    video = video_repo.get_by_id(slice_entity.video_id)
    
    if not video or video.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this slice"
        )
    
    # 更新切片信息
    if slice_data.title is not None:
        slice_entity.title = slice_data.title
    if slice_data.description is not None:
        slice_entity.description = slice_data.description
    if slice_data.tags is not None:
        slice_entity.tags = slice_data.tags
    
    updated_slice = slice_repo.update(slice_entity)
    return updated_slice


@router.delete("/slices/{slice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_slice(
    slice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除切片
    """
    slice_repo = SliceRepository(db)
    slice_entity = slice_repo.get_by_id(slice_id)
    
    if not slice_entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slice not found"
        )
    
    # 验证视频属于当前用户
    video_repo = VideoRepository(db)
    video = video_repo.get_by_id(slice_entity.video_id)
    
    if not video or video.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this slice"
        )
    
    # 删除文件
    file_storage = FileStorage(settings.upload_dir)
    if file_storage.file_exists(slice_entity.filepath):
        file_storage.delete_file(slice_entity.filepath)
    
    # 删除切片记录
    slice_repo.delete(slice_id)
    
    return None


@router.post("/videos/{video_id}/slices/generate-ai")
async def generate_ai_content(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    为视频的所有切片生成AI内容
    """
    # 验证视频存在且属于当前用户
    video_repo = VideoRepository(db)
    video = video_repo.get_by_id(video_id)
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    if video.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to process this video"
        )
    
    # 检查是否有切片
    slice_repo = SliceRepository(db)
    slices = slice_repo.get_by_video_id(video_id)
    
    if not slices:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No slices found for this video"
        )
    
    # 创建任务记录
    task_repo = TaskRepository(db)
    task = Task(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        task_type="batch_ai_content_generation",
        status="pending",
        progress=0
    )
    task = task_repo.create(task)
    
    # 异步生成AI内容，传入任务ID
    generate_ai_content_for_video_slices.delay(video_id, task.id)
    
    return {
        "message": "AI content generation started. Processing in background.",
        "task_id": task.id,
        "video_id": video_id
    }