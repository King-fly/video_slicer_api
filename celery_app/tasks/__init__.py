# 导入所有任务，以便 Celery 能够发现它们
from .video_tasks import process_video_upload, create_video_slices
from .ai_tasks import generate_ai_content_for_video_slices

__all__ = [
    'process_video_upload',
    'create_video_slices',
    'generate_ai_content_for_video_slices'
]