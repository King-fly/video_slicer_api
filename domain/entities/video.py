from datetime import datetime
from typing import Optional, List


class Video:
    """视频实体"""
    
    def __init__(
        self,
        id: Optional[int] = None,
        user_id: int = 0,
        title: str = "",
        filename: str = "",
        filepath: str = "",
        duration: int = 0,
        size: int = 0,
        status: str = "uploading",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.filename = filename
        self.filepath = filepath
        self.duration = duration
        self.size = size
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def __repr__(self):
        return f"<Video(id={self.id}, title='{self.title}', duration={self.duration}s, status='{self.status}')>"