from celery import Celery
from celery.schedules import crontab
from config.settings import get_settings
import os

settings = get_settings()

broker_url = os.environ.get('CELERY_BROKER_URL', settings.redis_url)
backend_url = os.environ.get('CELERY_RESULT_BACKEND', settings.redis_url)

# 创建Celery应用
app = Celery(
    'video_slicer',
    broker=broker_url,
    backend=backend_url
)

# 配置Celery
app.conf.update(
    broker_url=broker_url,
    result_backend=backend_url,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1小时
    task_soft_time_limit=3000,  # 50分钟
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    result_expires=3600,  # 1小时
    broker_connection_retry_on_startup=True,
    task_ignore_result=False,
)

# 自动发现任务
app.autodiscover_tasks(['celery_app.tasks'])

# 配置定时任务
app.conf.beat_schedule = {
    'cleanup-task-results': {
        'task': 'celery_app.tasks.ai_tasks.cleanup_task_results',
        'schedule': crontab(hour=0, minute=0),
    },
}