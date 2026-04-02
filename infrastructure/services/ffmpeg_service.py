import subprocess
import os
import tempfile
from typing import Optional, Tuple
import shutil


class FFmpegService:
    """FFmpeg视频处理服务"""
    
    def __init__(self, ffmpeg_path: str):
        self.ffmpeg_path = ffmpeg_path
    
    def extract_slice(
        self,
        input_path: str,
        output_path: str,
        start_time: int,
        duration: int,
        video_codec: str = "libx264",
        audio_codec: str = "aac",
        crf: int = 23,
        preset: str = "medium"
    ) -> bool:
        """
        提取视频切片
        
        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            start_time: 开始时间（秒）
            duration: 持续时间（秒）
            video_codec: 视频编码器
            audio_codec: 音频编码器
            crf: 视频质量（0-51，越小质量越好）
            preset: 编码预设（ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow）
            
        Returns:
            是否成功
        """
        cmd = [
            self.ffmpeg_path,
            '-ss', str(start_time),  # 开始时间
            '-i', input_path,        # 输入文件
            '-t', str(duration),     # 持续时间
            '-c:v', video_codec,     # 视频编码器
            '-c:a', audio_codec,     # 音频编码器
            '-crf', str(crf),        # 视频质量
            '-preset', preset,       # 编码预设
            '-y',                    # 覆盖输出文件
            output_path              # 输出文件
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr}")
            return False
    
    def get_video_info(self, video_path: str) -> Optional[dict]:
        """
        获取视频信息
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            视频信息字典，包含时长、尺寸、码率等
        """
        cmd = [
            self.ffmpeg_path,
            '-i', video_path,
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            import json
            info = json.loads(result.stdout)
            
            # 提取关键信息
            video_stream = None
            audio_stream = None
            
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                elif stream.get('codec_type') == 'audio':
                    audio_stream = stream
            
            video_info = {
                'duration': float(info['format'].get('duration', 0)),
                'size': int(info['format'].get('size', 0)),
                'bitrate': int(info['format'].get('bit_rate', 0)) // 1000,
            }
            
            if video_stream:
                video_info.update({
                    'width': int(video_stream.get('width', 0)),
                    'height': int(video_stream.get('height', 0)),
                    'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                    'video_codec': video_stream.get('codec_name', ''),
                })
            
            if audio_stream:
                video_info.update({
                    'audio_codec': audio_stream.get('codec_name', ''),
                    'audio_channels': audio_stream.get('channels', 0),
                })
            
            return video_info
            
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return None
    
    def create_thumbnail(
        self,
        video_path: str,
        output_path: str,
        time: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> bool:
        """
        创建视频缩略图
        
        Args:
            video_path: 视频文件路径
            output_path: 输出图片路径
            time: 截图时间点（秒）
            width: 输出宽度
            height: 输出高度
            
        Returns:
            是否成功
        """
        cmd = [
            self.ffmpeg_path,
            '-ss', str(time),
            '-i', video_path,
            '-vframes', '1',
            '-y'
        ]
        
        if width and height:
            cmd.extend(['-s', f'{width}x{height}'])
        elif width:
            cmd.extend(['-vf', f'scale={width}:-1'])
        elif height:
            cmd.extend(['-vf', f'scale=-1:{height}'])
            
        cmd.append(output_path)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr}")
            return False
    
    def compress_video(
        self,
        input_path: str,
        output_path: str,
        target_bitrate: int = 2000,  # kbps
        video_codec: str = "libx264",
        audio_codec: str = "aac",
        audio_bitrate: int = 128,  # kbps
        preset: str = "medium"
    ) -> bool:
        """
        压缩视频
        
        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            target_bitrate: 目标视频码率（kbps）
            video_codec: 视频编码器
            audio_codec: 音频编码器
            audio_bitrate: 音频码率（kbps）
            preset: 编码预设
            
        Returns:
            是否成功
        """
        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-c:v', video_codec,
            '-b:v', f'{target_bitrate}k',
            '-c:a', audio_codec,
            '-b:a', f'{audio_bitrate}k',
            '-preset', preset,
            '-y',
            output_path
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr}")
            return False