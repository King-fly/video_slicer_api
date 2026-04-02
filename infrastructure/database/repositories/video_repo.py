from typing import Optional, List
from sqlalchemy.orm import Session

from domain.entities.video import Video
from infrastructure.database.models.video import VideoModel


class VideoRepository:
    """视频数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, video: Video) -> Video:
        """创建视频"""
        db_video = VideoModel(
            user_id=video.user_id,
            title=video.title,
            filename=video.filename,
            filepath=video.filepath,
            duration=video.duration,
            size=video.size,
            status=video.status
        )
        self.db.add(db_video)
        self.db.commit()
        self.db.refresh(db_video)
        
        return self._to_entity(db_video)
    
    def get_by_id(self, video_id: int) -> Optional[Video]:
        """根据ID获取视频"""
        db_video = self.db.query(VideoModel).filter(VideoModel.id == video_id).first()
        if db_video:
            return self._to_entity(db_video)
        return None
    
    def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Video]:
        """根据用户ID获取视频列表"""
        db_videos = self.db.query(VideoModel).filter(
            VideoModel.user_id == user_id
        ).offset(skip).limit(limit).all()
        return [self._to_entity(db_video) for db_video in db_videos]
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Video]:
        """获取所有视频"""
        db_videos = self.db.query(VideoModel).offset(skip).limit(limit).all()
        return [self._to_entity(db_video) for db_video in db_videos]
    
    def update(self, video: Video) -> Video:
        """更新视频"""
        db_video = self.db.query(VideoModel).filter(VideoModel.id == video.id).first()
        if db_video:
            db_video.title = video.title
            db_video.filename = video.filename
            db_video.filepath = video.filepath
            db_video.duration = video.duration
            db_video.size = video.size
            db_video.status = video.status
            self.db.commit()
            self.db.refresh(db_video)
            return self._to_entity(db_video)
        raise ValueError(f"Video with id {video.id} not found")
    
    def delete(self, video_id: int) -> bool:
        """删除视频"""
        db_video = self.db.query(VideoModel).filter(VideoModel.id == video_id).first()
        if db_video:
            self.db.delete(db_video)
            self.db.commit()
            return True
        return False
    
    def _to_entity(self, db_video: VideoModel) -> Video:
        """将数据库模型转换为实体"""
        return Video(
            id=db_video.id,
            user_id=db_video.user_id,
            title=db_video.title,
            filename=db_video.filename,
            filepath=db_video.filepath,
            duration=db_video.duration,
            size=db_video.size,
            status=db_video.status,
            created_at=db_video.created_at,
            updated_at=db_video.updated_at
        )