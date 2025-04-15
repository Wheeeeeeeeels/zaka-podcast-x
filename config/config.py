import os
from dotenv import load_dotenv
from config.background_music import MusicManager, MusicCategory, MusicMood
from config.music_storage import MusicStorage
from config.permissions import PermissionManager, UserRole, Permission
from config.analytics import MusicAnalytics

class Config:
    def __init__(self):
        load_dotenv()
        
        # OpenAI配置
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        # 音频配置
        self.audio_output_dir = os.getenv('AUDIO_OUTPUT_DIR', 'output')
        self.background_music_category = os.getenv('BACKGROUND_MUSIC_CATEGORY', 'business')
        self.background_music_mood = os.getenv('BACKGROUND_MUSIC_MOOD', 'energetic')
        self.audio_quality = os.getenv('AUDIO_QUALITY', 'high')  # high, medium, low
        self.background_music_path = os.path.join('assets', 'music', self.background_music_category)
        
        # 音乐管理器
        self.music_manager = MusicManager()
        self.music_storage = MusicStorage()
        self.permission_manager = PermissionManager()
        self.analytics = MusicAnalytics()
        
        # 日志配置
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', os.path.join('logs', 'app.log'))
        
        # 性能配置
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        self.timeout = int(os.getenv('TIMEOUT', '30'))
        
        # 确保必要的目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.audio_output_dir,
            os.path.dirname(self.log_file),
            self.background_music_path,
            os.path.join('assets', 'music', 'lifestyle'),
            os.path.join('assets', 'music', 'news'),
            os.path.join('assets', 'music', 'education'),
            os.path.join('assets', 'music', 'story'),
            os.path.join('assets', 'music', 'music'),
            os.path.join('assets', 'music', 'wellness'),
            'config',
            os.path.join('cache', 'music'),
            os.path.join('backup', 'music'),
            os.path.join('data', 'analytics'),
            'temp',
            'tests',
            'docs'
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def get_background_music(self, user_id: str = None):
        """获取背景音乐"""
        category = MusicCategory(self.background_music_category)
        mood = MusicMood(self.background_music_mood)
        
        # 检查权限
        if user_id and not self.permission_manager.check_permission(user_id, Permission.READ):
            return None
        
        # 首先尝试获取指定类别和情绪的音乐
        music_list = [
            music for music in self.music_manager.get_music_by_category(category)
            if music.mood == mood and music.is_active
        ]
        
        if music_list:
            music = music_list[0]
            # 记录使用统计
            if user_id:
                self.analytics.record_play(music.id, user_id, music.duration)
            return music
        
        # 如果没有找到，获取该类别的默认音乐
        return self.music_manager.get_default_music(category)
    
    def set_background_music(self, category: str, mood: str, user_id: str = None):
        """设置背景音乐"""
        # 检查权限
        if user_id and not self.permission_manager.check_permission(user_id, Permission.WRITE):
            return False
        
        self.background_music_category = category
        self.background_music_mood = mood
        return True
    
    def upload_music(self, file_path: str, category: str, music_id: str, user_id: str = None) -> bool:
        """上传音乐文件"""
        # 检查权限
        if user_id and not self.permission_manager.check_permission(user_id, Permission.UPLOAD):
            return False
        
        return self.music_storage.upload_music(file_path, category, music_id) is not None
    
    def get_music_stats(self, music_id: str, user_id: str = None) -> dict:
        """获取音乐使用统计"""
        # 检查权限
        if user_id and not self.permission_manager.check_permission(user_id, Permission.READ):
            return {}
        
        return self.analytics.get_music_stats(music_id)
    
    def get_user_preferences(self, user_id: str) -> dict:
        """获取用户偏好"""
        return self.analytics.get_user_preferences(user_id)
    
    def get_recommendations(self, user_id: str, limit: int = 5) -> list:
        """获取音乐推荐"""
        return self.analytics.generate_recommendations(user_id, limit) 