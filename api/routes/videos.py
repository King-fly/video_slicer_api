from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import os
import uuid

from api.dependencies import get_db, get_current_active_user
from api.schemas.video import (
    VideoCreate,
    VideoUpdate,
    VideoResponse,
    VideoListResponse,
    VideoUploadResponse
)
from domain.entities.user import User
from domain.entities.video import Video
from infrastructure.database.repositories.video_repo import VideoRepository
from infrastructure.storage.file_storage import FileStorage
from config.settings import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.post("", response_model=VideoUploadResponse)
async def upload_video(
    title: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    上传视频文件
    """
    # 验证文件类型
    if not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a video"
        )
    
    # 验证文件大小
    file_size = 0
    content = await file.read()
    file_size = len(content)
    await file.seek(0)  # 重置文件指针
    
    if file_size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {settings.max_file_size / (1024 * 1024 * 1024):.1f}GB"
        )
    
    # 保存文件
    file_storage = FileStorage(settings.upload_dir)
    video_dir = f"user_{current_user.id}_videos"
    file_path = file_storage.save_file_from_stream(
        file.file,
        file.filename,
        video_dir
    )
    
    # 创建视频记录
    video_repo = VideoRepository(db)
    video = Video(
        user_id=current_user.id,
        title=title,
        filename=file.filename,
        filepath=file_path,
        duration=0,  # 将在处理任务中更新
        size=file_size,
        status="uploading"
    )
    video = video_repo.create(video)
    
    # 创建任务记录
    from domain.entities.task import Task
    from infrastructure.database.repositories.task_repo import TaskRepository
    task_repo = TaskRepository(db)
    task = Task(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        task_type="video_processing",
        status="pending",
        progress=0
    )
    task = task_repo.create(task)
    
    # 异步处理视频
    from celery_app.tasks.video_tasks import process_video_upload
    process_video_upload.delay(video.id, file_path, task.id)
    
    return {
        "video_id": video.id,
        "message": "Video uploaded successfully. Processing in background.",
        "task_id": task.id
    }


@router.get("", response_model=VideoListResponse)
async def get_videos(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的视频列表
    """
    video_repo = VideoRepository(db)
    videos = video_repo.get_by_user_id(current_user.id, skip=skip, limit=limit)
    
    # 获取总数
    all_videos = video_repo.get_by_user_id(current_user.id)
    total = len(all_videos)
    
    return {
        "total": total,
        "items": videos
    }


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取视频详情
    """
    video_repo = VideoRepository(db)
    video = video_repo.get_by_id(video_id)
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # 检查权限
    if video.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this video"
        )
    
    return video


@router.put("/{video_id}", response_model=VideoResponse)
async def update_video(
    video_id: int,
    video_data: VideoUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新视频信息
    """
    video_repo = VideoRepository(db)
    video = video_repo.get_by_id(video_id)
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # 检查权限
    if video.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this video"
        )
    
    # 更新视频信息
    if video_data.title is not None:
        video.title = video_data.title
    
    updated_video = video_repo.update(video)
    return updated_video


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除视频
    """
    video_repo = VideoRepository(db)
    video = video_repo.get_by_id(video_id)
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # 检查权限
    if video.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this video"
        )
    
    # 删除文件
    file_storage = FileStorage(settings.upload_dir)
    if file_storage.file_exists(video.filepath):
        file_storage.delete_file(video.filepath)
    
    # 删除视频记录
    video_repo.delete(video_id)
    
    return None