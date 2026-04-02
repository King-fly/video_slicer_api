from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import json

from infrastructure.database.db import Base


class TaskModel(Base):
    """任务数据库模型"""
    
    __tablename__ = "tasks"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_type = Column(String(50), nullable=False)
    status = Column(String(20), default="pending")
    progress = Column(Integer, default=0)
    result = Column(Text)  # JSON格式存储
    error = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("UserModel", back_populates="tasks")
    
    def get_result(self):
        """获取解析后的结果"""
        if self.result:
            return json.loads(self.result)
        return {}
    
    def set_result(self, result_dict):
        """设置结果"""
        self.result = json.dumps(result_dict, ensure_ascii=False)