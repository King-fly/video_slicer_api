from typing import Optional, List
from sqlalchemy.orm import Session

from domain.entities.slice import Slice
from infrastructure.database.models.slice import SliceModel


class SliceRepository:
    """视频切片数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, slice_entity: Slice) -> Slice:
        """创建切片"""
        # 处理 tags 字段，将列表转换为字符串
        tags = slice_entity.tags
        if tags:
            tags = ','.join(tags)
        
        db_slice = SliceModel(
            video_id=slice_entity.video_id,
            title=slice_entity.title,
            description=slice_entity.description,
            tags=tags,
            filename=slice_entity.filename,
            filepath=slice_entity.filepath,
            start_time=slice_entity.start_time,
            end_time=slice_entity.end_time,
            duration=slice_entity.duration,
            size=slice_entity.size,
            status=slice_entity.status
        )
        self.db.add(db_slice)
        self.db.commit()
        self.db.refresh(db_slice)
        
        return self._to_entity(db_slice)
    
    def get_by_id(self, slice_id: int) -> Optional[Slice]:
        """根据ID获取切片"""
        db_slice = self.db.query(SliceModel).filter(SliceModel.id == slice_id).first()
        if db_slice:
            return self._to_entity(db_slice)
        return None
    
    def get_by_video_id(self, video_id: int, skip: int = 0, limit: int = 100) -> List[Slice]:
        """根据视频ID获取切片列表"""
        db_slices = self.db.query(SliceModel).filter(
            SliceModel.video_id == video_id
        ).offset(skip).limit(limit).all()
        return [self._to_entity(db_slice) for db_slice in db_slices]
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Slice]:
        """获取所有切片"""
        db_slices = self.db.query(SliceModel).offset(skip).limit(limit).all()
        return [self._to_entity(db_slice) for db_slice in db_slices]
    
    def update(self, slice_entity: Slice) -> Slice:
        """更新切片"""
        db_slice = self.db.query(SliceModel).filter(SliceModel.id == slice_entity.id).first()
        if db_slice:
            db_slice.title = slice_entity.title
            db_slice.description = slice_entity.description
            # 处理 tags 字段，将列表转换为字符串
            tags = slice_entity.tags
            if tags:
                tags = ','.join(tags)
            db_slice.tags = tags
            db_slice.filename = slice_entity.filename
            db_slice.filepath = slice_entity.filepath
            db_slice.start_time = slice_entity.start_time
            db_slice.end_time = slice_entity.end_time
            db_slice.duration = slice_entity.duration
            db_slice.size = slice_entity.size
            db_slice.status = slice_entity.status
            self.db.commit()
            self.db.refresh(db_slice)
            return self._to_entity(db_slice)
        raise ValueError(f"Slice with id {slice_entity.id} not found")
    
    def delete(self, slice_id: int) -> bool:
        """删除切片"""
        db_slice = self.db.query(SliceModel).filter(SliceModel.id == slice_id).first()
        if db_slice:
            self.db.delete(db_slice)
            self.db.commit()
            return True
        return False
    
    def bulk_create(self, slices: List[Slice]) -> List[Slice]:
        """批量创建切片"""
        db_slices = [
            SliceModel(
                video_id=slice_entity.video_id,
                title=slice_entity.title,
                description=slice_entity.description,
                tags=','.join(slice_entity.tags) if slice_entity.tags else None,
                filename=slice_entity.filename,
                filepath=slice_entity.filepath,
                start_time=slice_entity.start_time,
                end_time=slice_entity.end_time,
                duration=slice_entity.duration,
                size=slice_entity.size,
                status=slice_entity.status
            )
            for slice_entity in slices
        ]
        self.db.bulk_save_objects(db_slices)
        self.db.commit()
        
        # 获取创建后的切片
        return self.get_by_video_id(slices[0].video_id) if slices else []
    
    def _to_entity(self, db_slice: SliceModel) -> Slice:
        """将数据库模型转换为实体"""
        # 处理 tags 字段，将字符串转换为列表
        tags = db_slice.tags
        if tags:
            tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        return Slice(
            id=db_slice.id,
            video_id=db_slice.video_id,
            title=db_slice.title,
            description=db_slice.description,
            tags=tags,
            filename=db_slice.filename,
            filepath=db_slice.filepath,
            start_time=db_slice.start_time,
            end_time=db_slice.end_time,
            duration=db_slice.duration,
            size=db_slice.size,
            status=db_slice.status,
            created_at=db_slice.created_at,
            updated_at=db_slice.updated_at
        )