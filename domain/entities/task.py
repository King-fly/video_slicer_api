from datetime import datetime
from typing import Optional, Dict, Any


class Task:
    """任务实体"""
    
    def __init__(
        self,
        id: str,
        user_id: int,
        task_type: str,
        status: str = "pending",
        progress: int = 0,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.user_id = user_id
        self.task_type = task_type
        self.status = status
        self.progress = progress
        self.result = result or {}
        self.error = error
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def __repr__(self):
        return f"<Task(id='{self.id}', type='{self.task_type}', status='{self.status}', progress={self.progress}%)>"