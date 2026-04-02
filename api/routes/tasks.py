from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies import get_db, get_current_active_user
from api.schemas.task import (
    TaskResponse,
    TaskListResponse
)
from domain.entities.user import User
from infrastructure.database.repositories.task_repo import TaskRepository
from config.settings import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def get_tasks(
    skip: int = 0,
    limit: int = 10,
    task_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的任务列表
    """
    task_repo = TaskRepository(db)
    tasks = task_repo.get_by_user_id(current_user.id, skip=skip, limit=limit)
    
    # 过滤任务类型和状态
    if task_type:
        tasks = [task for task in tasks if task.task_type == task_type]
    if status:
        tasks = [task for task in tasks if task.status == status]
    
    # 获取总数（简化处理，实际应该在数据库层面过滤）
    all_tasks = task_repo.get_by_user_id(current_user.id)
    if task_type:
        all_tasks = [task for task in all_tasks if task.task_type == task_type]
    if status:
        all_tasks = [task for task in all_tasks if task.status == status]
    total = len(all_tasks)
    
    return {
        "total": total,
        "items": tasks
    }


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取任务详情
    """
    task_repo = TaskRepository(db)
    task = task_repo.get_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # 检查权限
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this task"
        )
    
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除任务
    """
    task_repo = TaskRepository(db)
    task = task_repo.get_by_id(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # 检查权限
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this task"
        )
    
    # 删除任务
    task_repo.delete(task_id)
    
    return None