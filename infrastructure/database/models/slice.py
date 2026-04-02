from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from infrastructure.database.db import Base


class SliceModel(Base):
    """视频切片数据库模型"""
    
    __tablename__ = "slices"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    title = Column(String(255))
    description = Column(Text)
    tags = Column(Text)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(255), nullable=False)
    start_time = Column(Integer, nullable=False)
    end_time = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)
    size = Column(Integer, nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    video = relationship("VideoModel", back_populates="slices")