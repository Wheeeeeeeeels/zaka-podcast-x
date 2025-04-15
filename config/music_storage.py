import os
import shutil
from typing import Optional
from datetime import datetime
import hashlib
import logging
from pathlib import Path

class MusicStorage:
    """音乐存储管理器"""
    def __init__(self, base_dir: str = "assets/music"):
        self.base_dir = base_dir
        self.cache_dir = "cache/music"
        self.backup_dir = "backup/music"
        self.logger = logging.getLogger(__name__)
        
        # 确保目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.base_dir,
            self.cache_dir,
            self.backup_dir,
            "temp"
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _generate_file_hash(self, file_path: str) -> str:
        """生成文件哈希值"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _get_file_extension(self, file_path: str) -> str:
        """获取文件扩展名"""
        return os.path.splitext(file_path)[1].lower()
    
    def upload_music(self, source_path: str, category: str, music_id: str) -> Optional[str]:
        """上传音乐文件"""
        try:
            # 验证文件格式
            if self._get_file_extension(source_path) not in ['.mp3', '.wav', '.ogg']:
                raise ValueError("不支持的音乐文件格式")
            
            # 创建目标目录
            target_dir = os.path.join(self.base_dir, category)
            os.makedirs(target_dir, exist_ok=True)
            
            # 生成目标文件名
            target_path = os.path.join(target_dir, f"{music_id}{self._get_file_extension(source_path)}")
            
            # 复制文件
            shutil.copy2(source_path, target_path)
            
            # 生成文件哈希
            file_hash = self._generate_file_hash(target_path)
            
            # 创建备份
            backup_path = os.path.join(self.backup_dir, f"{file_hash}{self._get_file_extension(source_path)}")
            shutil.copy2(target_path, backup_path)
            
            self.logger.info(f"音乐文件上传成功: {target_path}")
            return target_path
            
        except Exception as e:
            self.logger.error(f"音乐文件上传失败: {str(e)}")
            return None
    
    def convert_format(self, source_path: str, target_format: str) -> Optional[str]:
        """转换音乐文件格式"""
        try:
            # 这里需要实现实际的格式转换逻辑
            # 可以使用 ffmpeg 或其他音频处理库
            pass
        except Exception as e:
            self.logger.error(f"音乐文件格式转换失败: {str(e)}")
            return None
    
    def compress_music(self, source_path: str, quality: str) -> Optional[str]:
        """压缩音乐文件"""
        try:
            # 这里需要实现实际的压缩逻辑
            # 可以使用 ffmpeg 或其他音频处理库
            pass
        except Exception as e:
            self.logger.error(f"音乐文件压缩失败: {str(e)}")
            return None
    
    def cache_music(self, music_path: str) -> Optional[str]:
        """缓存音乐文件"""
        try:
            file_hash = self._generate_file_hash(music_path)
            cache_path = os.path.join(self.cache_dir, f"{file_hash}{self._get_file_extension(music_path)}")
            
            if not os.path.exists(cache_path):
                shutil.copy2(music_path, cache_path)
            
            return cache_path
        except Exception as e:
            self.logger.error(f"音乐文件缓存失败: {str(e)}")
            return None
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        try:
            temp_dir = "temp"
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        except Exception as e:
            self.logger.error(f"清理临时文件失败: {str(e)}")
    
    def get_file_info(self, file_path: str) -> dict:
        """获取文件信息"""
        try:
            stat = os.stat(file_path)
            return {
                "size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "hash": self._generate_file_hash(file_path)
            }
        except Exception as e:
            self.logger.error(f"获取文件信息失败: {str(e)}")
            return {}