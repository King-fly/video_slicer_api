from typing import List, Tuple
import subprocess
import json
import os


class VideoAnalyzer:
    """视频分析器服务"""
    
    def __init__(self, ffmpeg_path: str):
        self.ffmpeg_path = ffmpeg_path
    
    def get_video_metadata(self, video_path: str) -> dict:
        """
        获取视频元数据
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            包含视频元数据的字典
        """
        # 直接使用 ffprobe 命令，因为它更适合获取视频元数据
        ffprobe_path = self.ffmpeg_path.replace('ffmpeg', 'ffprobe')
        cmd = [
            ffprobe_path,
            '-i', video_path,
            '-v', 'error',
            '-print_format', 'json',
            '-show_format',
            '-show_streams'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            # 提取关键信息
            video_stream = next((stream for stream in data['streams'] if stream['codec_type'] == 'video'), None)
            
            metadata = {
                'duration': float(data['format'].get('duration', 0)),
                'size': int(data['format'].get('size', 0)),
                'bitrate': int(data['format'].get('bit_rate', 0)) // 1000,
            }
            
            if video_stream:
                metadata.update({
                    'width': int(video_stream.get('width', 0)),
                    'height': int(video_stream.get('height', 0)),
                    'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                    'codec': video_stream.get('codec_name', ''),
                })
            
            return metadata
            
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Failed to analyze video: {e.stderr}")
        except json.JSONDecodeError:
            raise ValueError("Failed to parse video metadata")
    
    def detect_scene_changes(self, video_path: str, threshold: float = 0.3) -> List[int]:
        """
        检测视频场景变化点
        
        Args:
            video_path: 视频文件路径
            threshold: 场景变化阈值 (0-1)
            
        Returns:
            场景变化时间点列表（秒）
        """
        cmd = [
            self.ffmpeg_path,
            '-i', video_path,
            '-filter_complex', f"select='gt(scene,{threshold})',metadata=print:file=-",
            '-vsync', '0',
            '-f', 'null',
            '-'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            scene_changes = []
            for line in result.stderr.splitlines():
                if 'pts_time:' in line:
                    time_str = line.split('pts_time:')[1].strip()
                    scene_changes.append(int(float(time_str)))
            
            # 去重并排序
            scene_changes = sorted(list(set(scene_changes)))
            
            return scene_changes
            
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Failed to detect scene changes: {e.stderr}")
    
    def generate_slice_points(
        self, 
        video_path: str, 
        method: str = 'fixed',
        duration: int = 60,
        scene_threshold: float = 0.3
    ) -> List[Tuple[int, int]]:
        """
        生成切片时间点
        
        Args:
            video_path: 视频文件路径
            method: 切片方法 ('fixed' 或 'scene')
            duration: 固定切片时长（秒）
            scene_threshold: 场景变化阈值
            
        Returns:
            切片时间点列表 [(开始时间, 结束时间)]
        """
        metadata = self.get_video_metadata(video_path)
        total_duration = int(metadata['duration'])
        
        if method == 'fixed':
            # 固定时长切片
            slices = []
            for start in range(0, total_duration, duration):
                end = min(start + duration, total_duration)
                slices.append((start, end))
            return slices
            
        elif method == 'scene':
            # 基于场景变化切片
            scene_changes = self.detect_scene_changes(video_path, scene_threshold)
            
            # 添加开始和结束点
            all_points = [0] + scene_changes + [total_duration]
            
            slices = []
            current_start = 0
            
            for i in range(1, len(all_points)):
                if all_points[i] - current_start >= duration * 0.8:  # 允许80%的目标时长
                    slices.append((current_start, all_points[i]))
                    current_start = all_points[i]
            
            # 处理最后一段
            if current_start < total_duration:
                slices.append((current_start, total_duration))
            
            return slices
            
        else:
            raise ValueError(f"Unknown slice method: {method}")