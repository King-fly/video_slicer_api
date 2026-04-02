from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies import (
    get_db,
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_active_user
)
from api.schemas.auth import (
    UserCreate,
    UserResponse,
    Token,
    UserLogin
)
from domain.entities.user import User
from infrastructure.database.repositories.user_repo import UserRepository
from config.settings import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    注册新用户
    """
    # 检查用户名是否已存在
    user_repo = UserRepository(db)
    existing_user = user_repo.get_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # 检查邮箱是否已存在
    existing_email = user_repo.get_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )
    
    created_user = user_repo.create(user)
    return created_user


@router.post("/login", response_model=Token)
def login_for_access_token(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    用户登录获取访问令牌
    """
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/login/json", response_model=Token)
def login_json(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    用户登录获取访问令牌（JSON格式）
    """
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户信息
    """
    return current_user