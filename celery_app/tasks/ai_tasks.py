import os
import uuid
from typing import List, Optional
import logging

from celery_app.app import app

try:
    from celery_progress.backend import ProgressRecorder
except ImportError:
    ProgressRecorder = None

from domain.entities.task import Task
from infrastructure.database.repositories.slice_repo import SliceRepository
from infrastructure.database.repositories.task_repo import TaskRepository
from infrastructure.database.repositories.video_repo import VideoRepository
from infrastructure.services.ollama_service import OllamaService
from infrastructure.storage.file_storage import FileStorage
from infrastructure.database.db import SessionLocal
from config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@app.task(bind=True)
def generate_ai_content_for_slice(self, slice_id: int, task_id: str = None):
    """
    为单个切片生成AI内容
    
    Args:
        slice_id: 切片ID
        task_id: 可选的任务ID，如果提供则使用现有任务记录
    """
    # 只有当 ProgressRecorder 可用时才创建实例
    progress_recorder = ProgressRecorder(self) if ProgressRecorder else None
    db = SessionLocal()
    
    try:
        # 获取仓库
        slice_repo = SliceRepository(db)
        task_repo = TaskRepository(db)
        video_repo = VideoRepository(db)
        
        # 获取切片信息
        slice_entity = slice_repo.get_by_id(slice_id)
        if not slice_entity:
            raise ValueError(f"Slice {slice_id} not found")
        
        # 获取视频信息
        video = video_repo.get_by_id(slice_entity.video_id)
        if not video:
            raise ValueError(f"Video {slice_entity.video_id} not found")
        
        # 使用提供的任务ID或创建新的
        task_id = task_id or self.request.id
        task = task_repo.get_by_id(task_id)
        
        if not task:
            # 如果任务不存在，创建一个
            task = Task(
                id=task_id,
                user_id=video.user_id,
                task_type="ai_content_generation",
                status="processing",
                progress=0
            )
            task = task_repo.create(task)
        
        # 初始化服务
        file_storage = FileStorage(settings.upload_dir)
        ollama_service = OllamaService(settings.ollama_url, settings.ollama_model)
        
        # 更新进度
        task_repo.update_status(task.id, "processing", 10)
        if progress_recorder:
            progress_recorder.set_progress(10, 100)
        
        # 构建视频描述
        video_description = f"""
        这是视频"{video.title}"的一个片段，时长{slice_entity.duration}秒，
        从第{slice_entity.start_time}秒开始到第{slice_entity.end_time}秒结束。
        请为这个视频片段生成吸引人的标题、描述和标签。
        """
        
        # 更新进度
        task_repo.update_status(task.id, "processing", 30)
        if progress_recorder:
            progress_recorder.set_progress(30, 100)
        
        # 生成AI内容
        logger.info(f"Generating AI content for slice {slice_id}")
        
        # 生成标题
        title = ollama_service.generate_video_title_sync(video_description)
        if not title:
            raise ValueError("Failed to generate title")
        
        # 更新进度
        task_repo.update_status(task.id, "processing", 50)
        if progress_recorder:
            progress_recorder.set_progress(50, 100)
        
        # 生成描述
        description = ollama_service.generate_video_description_sync(video_description)
        if not description:
            raise ValueError("Failed to generate description")
        
        # 更新进度
        task_repo.update_status(task.id, "processing", 70)
        if progress_recorder:
            progress_recorder.set_progress(70, 100)
        
        # 生成标签
        tags = ollama_service.generate_video_tags_sync(video_description)
        if not tags:
            raise ValueError("Failed to generate tags")
        
        # 更新进度
        task_repo.update_status(task.id, "processing", 90)
        if progress_recorder:
            progress_recorder.set_progress(90, 100)
        
        # 更新切片信息
        slice_entity.title = title
        slice_entity.description = description
        slice_entity.tags = ",".join(tags)
        slice_entity.status = "completed"
        slice_repo.update(slice_entity)
        
        # 更新任务结果
        task_repo.update_result(task.id, {
            "slice_id": slice_entity.id,
            "title": title,
            "description": description,
            "tags": tags,
            "status": "success"
        })
        
        # 完成任务
        task_repo.update_status(task.id, "completed", 100)
        if progress_recorder:
            progress_recorder.set_progress(100, 100)
        
        return {
            "slice_id": slice_entity.id,
            "title": title,
            "description": description,
            "tags": tags,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error generating AI content for slice {slice_id}: {str(e)}")
        
        # 更新任务状态为失败
        if task is not None:
            try:
                task_repo.update_error(task.id, str(e))
            except Exception as update_error:
                logger.error(f"Failed to update task error status: {update_error}")
        
        # 更新切片状态
        if 'slice_entity' in locals() and slice_entity:
            slice_entity.status = "error"
            slice_repo.update(slice_entity)
        
        raise
    finally:
        db.close()


@app.task(bind=True)
def generate_ai_content_for_video_slices(self, video_id: int, task_id: str = None):
    """
    为视频的所有切片生成AI内容
    
    Args:
        video_id: 视频ID
        task_id: 可选的任务ID，如果提供则使用现有任务记录
    """
    # 只有当 ProgressRecorder 可用时才创建实例
    progress_recorder = ProgressRecorder(self) if ProgressRecorder else None
    db = SessionLocal()
    
    try:
        # 获取仓库
        slice_repo = SliceRepository(db)
        task_repo = TaskRepository(db)
        video_repo = VideoRepository(db)
        
        # 先获取视频信息
        video = video_repo.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video {video_id} not found")
        
        # 使用提供的任务ID或创建新的
        task_id = task_id or self.request.id
        task = task_repo.get_by_id(task_id)
        
        if not task:
            # 如果任务不存在，创建一个
            task = Task(
                id=task_id,
                user_id=video.user_id,
                task_type="batch_ai_content_generation",
                status="processing",
                progress=0
            )
            task = task_repo.create(task)
        
        # 获取视频的所有切片
        slices = slice_repo.get_by_video_id(video_id)
        if not slices:
            raise ValueError(f"No slices found for video {video_id}")
        
        # 更新进度
        task_repo.update_status(task.id, "processing", 10)
        if progress_recorder:
            progress_recorder.set_progress(10, 100)
        
        # 为每个切片生成AI内容
        total_slices = len(slices)
        completed_slices = 0
        failed_slices = 0
        
        for i, slice_entity in enumerate(slices):
            try:
                # 检查切片是否已完成
                if slice_entity.status == "completed" and slice_entity.title:
                    logger.info(f"Slice {slice_entity.id} already has AI content, skipping")
                    completed_slices += 1
                    continue
                
                # 异步调用单个切片的AI内容生成任务
                result = generate_ai_content_for_slice.delay(slice_entity.id)
                
                completed_slices += 1
                
            except Exception as e:
                logger.error(f"Error processing slice {slice_entity.id}: {str(e)}")
                failed_slices += 1
            
            # 更新进度
            current_progress = 10 + (i + 1) / total_slices * 80
            task_repo.update_status(task.id, "processing", int(current_progress))
            if progress_recorder:
                progress_recorder.set_progress(int(current_progress), 100)
        
        # 更新任务结果
        task_repo.update_result(task.id, {
            "video_id": video.id,
            "total_slices": total_slices,
            "completed_slices": completed_slices,
            "failed_slices": failed_slices,
            "status": "success"
        })
        
        # 完成任务
        task_repo.update_status(task.id, "completed", 100)
        if progress_recorder:
            progress_recorder.set_progress(100, 100)
        
        return {
            "video_id": video.id,
            "total_slices": total_slices,
            "completed_slices": completed_slices,
            "failed_slices": failed_slices,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error generating batch AI content for video {video_id}: {str(e)}")
        
        # 更新任务状态为失败
        if task is not None:
            try:
                task_repo.update_error(task.id, str(e))
            except Exception as update_error:
                logger.error(f"Failed to update task error status: {update_error}")
        
        raise
    finally:
        db.close()


@app.task
def cleanup_task_results():
    """清理过期的任务结果"""
    db = SessionLocal()
    
    try:
        task_repo = TaskRepository(db)
        
        # 获取所有已完成且超过1天的任务
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=1)
        
        # 这里简化处理，实际应该查询数据库中过期的任务
        logger.info("Cleaning up expired task results")
        
    except Exception as e:
        logger.error(f"Error cleaning up task results: {str(e)}")
    finally:
        db.close()