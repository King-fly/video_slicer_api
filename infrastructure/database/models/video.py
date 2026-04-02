from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from infrastructure.database.db import Base


class VideoModel(Base):
    """视频数据库模型"""
    
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(255), nullable=False)
    duration = Column(Integer, nullable=False)
    size = Column(Integer, nullable=False)
    status = Column(String(20), default="uploading")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("UserModel", back_populates="videos")
    slices = relationship("SliceModel", back_populates="video", cascade="all, delete-orphan")