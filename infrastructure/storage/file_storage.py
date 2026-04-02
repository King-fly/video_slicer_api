import os
import uuid
from typing import Optional
import shutil
from pathlib import Path


class FileStorage:
    """文件存储服务"""
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.ensure_dir_exists(base_dir)
    
    def save_file(
        self,
        file_content: bytes,
        filename: str,
        subdirectory: Optional[str] = None
    ) -> str:
        """
        保存文件
        
        Args:
            file_content: 文件内容
            filename: 文件名
            subdirectory: 子目录
            
        Returns:
            保存后的文件路径（相对于基础目录）
        """
        # 生成唯一文件名
        unique_filename = self._generate_unique_filename(filename)
        
        # 构建保存路径
        if subdirectory:
            save_dir = os.path.join(self.base_dir, subdirectory)
            relative_path = os.path.join(subdirectory, unique_filename)
        else:
            save_dir = self.base_dir
            relative_path = unique_filename
        
        # 确保目录存在
        self.ensure_dir_exists(save_dir)
        
        # 保存文件
        file_path = os.path.join(save_dir, unique_filename)
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return relative_path
    
    def save_file_from_stream(
        self,
        file_stream,
        filename: str,
        subdirectory: Optional[str] = None
    ) -> str:
        """
        从文件流保存文件
        
        Args:
            file_stream: 文件流
            filename: 文件名
            subdirectory: 子目录
            
        Returns:
            保存后的文件路径（相对于基础目录）
        """
        # 生成唯一文件名
        unique_filename = self._generate_unique_filename(filename)
        
        # 构建保存路径
        if subdirectory:
            save_dir = os.path.join(self.base_dir, subdirectory)
            relative_path = os.path.join(subdirectory, unique_filename)
        else:
            save_dir = self.base_dir
            relative_path = unique_filename
        
        # 确保目录存在
        self.ensure_dir_exists(save_dir)
        
        # 保存文件
        file_path = os.path.join(save_dir, unique_filename)
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file_stream, f)
        
        return relative_path
    
    def get_file_path(self, relative_path: str) -> str:
        """
        获取文件的完整路径
        
        Args:
            relative_path: 相对于基础目录的路径
            
        Returns:
            完整的文件路径
        """
        return os.path.join(self.base_dir, relative_path)
    
    def delete_file(self, relative_path: str) -> bool:
        """
        删除文件
        
        Args:
            relative_path: 相对于基础目录的路径
            
        Returns:
            是否删除成功
        """
        file_path = self.get_file_path(relative_path)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception:
                return False
        return False
    
    def file_exists(self, relative_path: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            relative_path: 相对于基础目录的路径
            
        Returns:
            文件是否存在
        """
        return os.path.exists(self.get_file_path(relative_path))
    
    def get_file_size(self, relative_path: str) -> Optional[int]:
        """
        获取文件大小
        
        Args:
            relative_path: 相对于基础目录的路径
            
        Returns:
            文件大小（字节），如果文件不存在则返回None
        """
        file_path = self.get_file_path(relative_path)
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return None
    
    def create_subdirectory(self, subdirectory: str) -> bool:
        """
        创建子目录
        
        Args:
            subdirectory: 子目录名
            
        Returns:
            是否创建成功
        """
        dir_path = os.path.join(self.base_dir, subdirectory)
        return self.ensure_dir_exists(dir_path)
    
    def delete_subdirectory(self, subdirectory: str) -> bool:
        """
        删除子目录（包含所有文件）
        
        Args:
            subdirectory: 子目录名
            
        Returns:
            是否删除成功
        """
        dir_path = os.path.join(self.base_dir, subdirectory)
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                return True
            except Exception:
                return False
        return False
    
    def ensure_dir_exists(self, dir_path: str) -> bool:
        """
        确保目录存在
        
        Args:
            dir_path: 目录路径
            
        Returns:
            是否创建成功
        """
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
    
    def _generate_unique_filename(self, original_filename: str) -> str:
        """
        生成唯一的文件名
        
        Args:
            original_filename: 原始文件名
            
        Returns:
            唯一的文件名
        """
        # 获取文件扩展名
        _, ext = os.path.splitext(original_filename)
        
        # 生成UUID作为文件名
        unique_id = uuid.uuid4().hex
        
        # 组合新文件名
        return f"{unique_id}{ext}"