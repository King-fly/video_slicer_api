from datetime import datetime
from typing import Optional, List


class Slice:
    """视频切片实体"""
    
    def __init__(
        self,
        id: Optional[int] = None,
        video_id: int = 0,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[str] = None,
        filename: str = "",
        filepath: str = "",
        start_time: int = 0,
        end_time: int = 0,
        duration: int = 0,
        size: int = 0,
        status: str = "pending",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.video_id = video_id
        self.title = title
        self.description = description
        self.tags = tags
        self.filename = filename
        self.filepath = filepath
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.size = size
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def __repr__(self):
        return f"<Slice(id={self.id}, video_id={self.video_id}, {self.start_time}s-{self.end_time}s, status='{self.status}')>"