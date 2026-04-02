from datetime import datetime
from typing import Optional


class User:
    """用户实体"""
    
    def __init__(
        self,
        id: Optional[int] = None,
        username: str = "",
        email: str = "",
        password_hash: str = "",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"