import os
import logging

from celery_app.app import app

try:
    from celery_progress.backend import ProgressRecorder
except ImportError:
    ProgressRecorder = None

from domain.entities.slice import Slice
from domain.services.video_analyzer import VideoAnalyzer
from infrastructure.database.repositories.video_repo import VideoRepository
from infrastructure.database.repositories.slice_repo import SliceRepository
from infrastructure.database.repositories.task_repo import TaskRepository
from infrastructure.services.ffmpeg_service import FFmpegService
from infrastructure.storage.file_storage import FileStorage
from infrastructure.database.db import SessionLocal
from config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@app.task(bind=True)
def process_video_upload(self, video_id: int, file_path: str, task_id: str):
    """
    处理视频上传后的任务
    
    Args:
        video_id: 视频ID
        file_path: 视频文件路径
        task_id: 任务ID
    """
    # 只有当 ProgressRecorder 可用时才创建实例
    progress_recorder = ProgressRecorder(self) if ProgressRecorder else None
    db = SessionLocal()
    
    try:
        # 获取仓库
        video_repo = VideoRepository(db)
        task_repo = TaskRepository(db)
        
        # 获取任务记录
        task = task_repo.get_by_id(task_id)
        if not task:
            # 如果任务不存在，记录错误并抛出异常
            # 注意：任务应该由 API 在发送任务前创建好
            raise ValueError(f"Task {task_id} not found in database. Please ensure task is created before sending to worker.")
        
        # 获取视频信息
        video = video_repo.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video {video_id} not found")
        
        # 初始化服务
        ffmpeg_service = FFmpegService(settings.ffmpeg_path)
        video_analyzer = VideoAnalyzer(settings.ffmpeg_path)
        
        # 更新进度
        task_repo.update_status(task.id, "processing", 10)
        if progress_recorder:
            progress_recorder.set_progress(10, 100)
        
        # 分析视频
        logger.info(f"Analyzing video: {file_path}")
        
        # 初始化文件存储服务
        file_storage = FileStorage(settings.upload_dir)
        
        # 获取视频完整路径
        video_path = file_storage.get_file_path(file_path)
        logger.info(f"Using full path: {video_path}")
        
        # 检查文件是否存在
        if not os.path.exists(video_path):
            raise ValueError(f"Video file not found: {video_path}")
            
        # 确保使用绝对路径
        video_path = os.path.abspath(video_path)
        logger.info(f"Using absolute path: {video_path}")
        
        try:
            metadata = video_analyzer.get_video_metadata(video_path)
            
            if metadata:
                # 更新视频信息
                video.duration = int(metadata['duration'])
                video.size = metadata['size']
                video.status = "processed"
                video_repo.update(video)
                
                # 更新任务进度
                task_repo.update_status(task.id, "processing", 50)
                if progress_recorder:
                    progress_recorder.set_progress(50, 100)
                
                # 更新任务结果
                task_repo.update_result(task.id, {
                    "video_id": video.id,
                    "metadata": metadata,
                    "status": "success"
                })
                
                # 完成任务
                task_repo.update_status(task.id, "completed", 100)
                if progress_recorder:
                    progress_recorder.set_progress(100, 100)
                
                return {
                    "video_id": video.id,
                    "status": "success",
                    "metadata": metadata
                }
            else:
                # 即使无法获取元数据，也将视频状态设置为processed
                # 这样用户仍然可以创建切片
                video.status = "processed"
                video_repo.update(video)
                
                # 更新任务进度
                task_repo.update_status(task.id, "completed", 100)
                if progress_recorder:
                    progress_recorder.set_progress(100, 100)
                
                return {
                    "video_id": video.id,
                    "status": "success",
                    "message": "Video processed successfully (metadata extraction failed)"
                }
        except Exception as e:
            logger.error(f"Error analyzing video: {str(e)}")
            # 即使分析失败，也将视频状态设置为processed
            # 这样用户仍然可以创建切片
            video.status = "processed"
            video_repo.update(video)
            
            # 更新任务进度
            task_repo.update_status(task.id, "completed", 100)
            if progress_recorder:
                progress_recorder.set_progress(100, 100)
            
            return {
                "video_id": video.id,
                "status": "success",
                "message": f"Video processed successfully (analysis error: {str(e)})"
            }
            
    except Exception as e:
        logger.error(f"Error processing video {video_id}: {str(e)}")
        
        # 更新任务状态为失败（需要task不为None）
        if task is not None:
            try:
                task_repo.update_error(task.id, str(e))
            except Exception as update_error:
                logger.error(f"Failed to update task error status: {update_error}")
        
        # 更新视频状态
        if 'video' in locals() and video:
            video.status = "error"
            video_repo.update(video)
        
        raise
    finally:
        db.close()


@app.task(bind=True)
def create_video_slices(
    self,
    video_id: int,
    method: str = "fixed",
    duration: int = 60,
    scene_threshold: float = 0.3,
    task_id: str = None
):
    """
    创建视频切片
    
    Args:
        video_id: 视频ID
        method: 切片方法 ('fixed' 或 'scene')
        duration: 固定切片时长（秒）
        scene_threshold: 场景变化阈值
        task_id: 任务ID
    """
    # 只有当 ProgressRecorder 可用时才创建实例
    progress_recorder = ProgressRecorder(self) if ProgressRecorder else None
    db = SessionLocal()
    
    try:
        # 获取仓库
        video_repo = VideoRepository(db)
        slice_repo = SliceRepository(db)
        task_repo = TaskRepository(db)
        
        # 使用提供的任务ID或创建新的
        task_id = task_id or self.request.id
        
        # 获取任务记录
        task = task_repo.get_by_id(task_id)
        if not task:
            # 如果任务不存在，记录错误并抛出异常
            # 注意：任务应该由 API 在发送任务前创建好
            raise ValueError(f"Task {task_id} not found in database. Please ensure task is created before sending to worker.")
        
        # 获取视频信息
        video = video_repo.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video {video_id} not found")
        
        # 初始化服务
        file_storage = FileStorage(settings.upload_dir)
        ffmpeg_service = FFmpegService(settings.ffmpeg_path)
        video_analyzer = VideoAnalyzer(settings.ffmpeg_path)
        
        # 获取视频完整路径
        video_path = file_storage.get_file_path(video.filepath)
        
        # 更新进度
        task_repo.update_status(task.id, "processing", 10)
        if progress_recorder:
            progress_recorder.set_progress(10, 100)
        
        # 生成切片时间点
        logger.info(f"Generating slice points for video {video_id}")
        slice_points = video_analyzer.generate_slice_points(
            video_path,
            method=method,
            duration=duration,
            scene_threshold=scene_threshold
        )
        
        # 更新进度
        task_repo.update_status(task.id, "processing", 30)
        if progress_recorder:
            progress_recorder.set_progress(30, 100)
        
        # 创建切片目录
        slice_dir = f"video_{video_id}_slices"
        file_storage.create_subdirectory(slice_dir)
        
        # 创建切片
        slices = []
        total_slices = len(slice_points)
        
        for i, (start_time, end_time) in enumerate(slice_points):
            slice_duration = end_time - start_time
            
            # 生成切片文件名
            slice_filename = f"slice_{i+1}_{start_time}_{end_time}.mp4"
            slice_output_path = file_storage.get_file_path(
                os.path.join(slice_dir, slice_filename)
            )
            
            # 提取切片
            logger.info(f"Extracting slice {i+1}/{total_slices}: {start_time}-{end_time}s")
            success = ffmpeg_service.extract_slice(
                video_path,
                slice_output_path,
                start_time,
                slice_duration
            )
            
            if success:
                # 获取切片文件大小
                slice_size = os.path.getsize(slice_output_path)
                
                # 创建切片实体
                slice_entity = Slice(
                    video_id=video.id,
                    filename=slice_filename,
                    filepath=os.path.join(slice_dir, slice_filename),
                    start_time=start_time,
                    end_time=end_time,
                    duration=slice_duration,
                    size=slice_size,
                    status="created"
                )
                slices.append(slice_entity)
            
            # 更新进度
            current_progress = 30 + (i + 1) / total_slices * 60
            task_repo.update_status(task.id, "processing", int(current_progress))
            if progress_recorder:
                progress_recorder.set_progress(int(current_progress), 100)
        
        # 批量保存切片
        if slices:
            slices = slice_repo.bulk_create(slices)
            
            # 更新任务结果
            task_repo.update_result(task.id, {
                "video_id": video.id,
                "slice_count": len(slices),
                "method": method,
                "status": "success"
            })
            
            # 完成任务
            task_repo.update_status(task.id, "completed", 100)
            if progress_recorder:
                progress_recorder.set_progress(100, 100)
            
            return {
                "video_id": video.id,
                "slice_count": len(slices),
                "status": "success"
            }
        else:
            raise ValueError("Failed to create any slices")
            
    except Exception as e:
        logger.error(f"Error creating slices for video {video_id}: {str(e)}")
        
        # 更新任务状态为失败
        if 'task' in locals():
            task_repo.update_error(task.id, str(e))
        
        raise
    finally:
        db.close()