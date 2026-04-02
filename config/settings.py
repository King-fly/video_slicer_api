from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置设置"""
    # 应用配置
    app_name: str = "VideoSlicer"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # 数据库配置
    database_url: str = "sqlite:///./video_slicer.db"
    
    # Redis配置
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT配置
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 文件存储配置
    upload_dir: str = "./uploads"
    max_file_size: int = 5368709120  # 5GB
    
    # FFmpeg配置
    ffmpeg_path: str = "/opt/homebrew/bin/ffmpeg"
    
    # Ollama配置
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()