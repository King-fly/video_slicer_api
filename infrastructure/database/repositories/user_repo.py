from typing import Optional, List
from sqlalchemy.orm import Session

from domain.entities.user import User
from infrastructure.database.models.user import UserModel


class UserRepository:
    """用户数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user: User) -> User:
        """创建用户"""
        db_user = UserModel(
            username=user.username,
            email=user.email,
            password_hash=user.password_hash
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return self._to_entity(db_user)
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            return self._to_entity(db_user)
        return None
    
    def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if db_user:
            return self._to_entity(db_user)
        return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if db_user:
            return self._to_entity(db_user)
        return None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """获取所有用户"""
        db_users = self.db.query(UserModel).offset(skip).limit(limit).all()
        return [self._to_entity(db_user) for db_user in db_users]
    
    def update(self, user: User) -> User:
        """更新用户"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        if db_user:
            db_user.username = user.username
            db_user.email = user.email
            db_user.password_hash = user.password_hash
            self.db.commit()
            self.db.refresh(db_user)
            return self._to_entity(db_user)
        raise ValueError(f"User with id {user.id} not found")
    
    def delete(self, user_id: int) -> bool:
        """删除用户"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False
    
    def _to_entity(self, db_user: UserModel) -> User:
        """将数据库模型转换为实体"""
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            password_hash=db_user.password_hash,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )