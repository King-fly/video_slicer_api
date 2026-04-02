from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from domain.entities.task import Task
from infrastructure.database.models.task import TaskModel


class TaskRepository:
    """任务数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, task: Task) -> Task:
        """创建任务"""
        db_task = TaskModel(
            id=task.id,
            user_id=task.user_id,
            task_type=task.task_type,
            status=task.status,
            progress=task.progress
        )
        if task.result:
            db_task.set_result(task.result)
        if task.error:
            db_task.error = task.error
            
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        
        return self._to_entity(db_task)
    
    def get_by_id(self, task_id: str) -> Optional[Task]:
        """根据ID获取任务"""
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if db_task:
            return self._to_entity(db_task)
        return None
    
    def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """根据用户ID获取任务列表"""
        db_tasks = self.db.query(TaskModel).filter(
            TaskModel.user_id == user_id
        ).order_by(TaskModel.created_at.desc()).offset(skip).limit(limit).all()
        return [self._to_entity(db_task) for db_task in db_tasks]
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """获取所有任务"""
        db_tasks = self.db.query(TaskModel).order_by(
            TaskModel.created_at.desc()
        ).offset(skip).limit(limit).all()
        return [self._to_entity(db_task) for db_task in db_tasks]
    
    def update(self, task: Task) -> Task:
        """更新任务"""
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task.id).first()
        if db_task:
            db_task.status = task.status
            db_task.progress = task.progress
            if task.result:
                db_task.set_result(task.result)
            if task.error:
                db_task.error = task.error
                
            self.db.commit()
            self.db.refresh(db_task)
            return self._to_entity(db_task)
        raise ValueError(f"Task with id {task.id} not found")
    
    def update_status(self, task_id: str, status: str, progress: int = None) -> Task:
        """更新任务状态"""
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if db_task:
            db_task.status = status
            if progress is not None:
                db_task.progress = progress
            self.db.commit()
            self.db.refresh(db_task)
            return self._to_entity(db_task)
        raise ValueError(f"Task with id {task_id} not found")
    
    def update_result(self, task_id: str, result: Dict[str, Any]) -> Task:
        """更新任务结果"""
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if db_task:
            db_task.set_result(result)
            self.db.commit()
            self.db.refresh(db_task)
            return self._to_entity(db_task)
        raise ValueError(f"Task with id {task_id} not found")
    
    def update_error(self, task_id: str, error: str) -> Task:
        """更新任务错误"""
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if db_task:
            db_task.error = error
            db_task.status = "failed"
            self.db.commit()
            self.db.refresh(db_task)
            return self._to_entity(db_task)
        raise ValueError(f"Task with id {task_id} not found")
    
    def delete(self, task_id: str) -> bool:
        """删除任务"""
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if db_task:
            self.db.delete(db_task)
            self.db.commit()
            return True
        return False
    
    def _to_entity(self, db_task: TaskModel) -> Task:
        """将数据库模型转换为实体"""
        return Task(
            id=db_task.id,
            user_id=db_task.user_id,
            task_type=db_task.task_type,
            status=db_task.status,
            progress=db_task.progress,
            result=db_task.get_result(),
            error=db_task.error,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at
        )