from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import os
import json

class MusicCategory(Enum):
    """音乐类别枚举"""
    BUSINESS = "business"  # 商业科技
    LIFESTYLE = "lifestyle"  # 生活文化
    NEWS = "news"  # 新闻资讯
    EDUCATION = "education"  # 教育学习
    STORY = "story"  # 故事讲述
    MUSIC = "music"  # 音乐欣赏
    WELLNESS = "wellness"  # 健康生活
    CUSTOM = "custom"  # 自定义类别

class MusicMood(Enum):
    """音乐情绪枚举"""
    ENERGETIC = "energetic"  # 充满活力
    PROFESSIONAL = "professional"  # 专业
    RELAXING = "relaxing"  # 放松
    COZY = "cozy"  # 温馨
    FORMAL = "formal"  # 正式
    SERIOUS = "serious"  # 严肃
    EDUCATIONAL = "educational"  # 教育
    FOCUSED = "focused"  # 专注
    NARRATIVE = "narrative"  # 叙事
    MYSTERIOUS = "mysterious"  # 神秘
    ARTISTIC = "artistic"  # 艺术
    CONTEMPORARY = "contemporary"  # 现代
    CALM = "calm"  # 平静
    NONE = "none"  # 无

@dataclass
class MusicLicense:
    """音乐版权信息"""
    license_type: str  # 许可证类型
    license_url: str  # 许可证链接
    attribution: str  # 署名要求
    commercial_use: bool  # 是否允许商业使用
    modification_allowed: bool  # 是否允许修改

@dataclass
class BackgroundMusic:
    """背景音乐配置"""
    id: str  # 唯一标识符
    name: str  # 音乐名称
    path: str  # 文件路径
    description: str  # 详细描述
    mood: MusicMood  # 情绪标签
    category: MusicCategory  # 类别标签
    duration: int  # 时长（秒）
    bpm: int  # 每分钟节拍数
    tags: List[str]  # 标签列表
    license: MusicLicense  # 版权信息
    version: str  # 版本号
    created_at: str  # 创建时间
    updated_at: str  # 更新时间
    is_active: bool  # 是否激活
    is_default: bool  # 是否默认
    metadata: Dict  # 元数据

class MusicManager:
    """背景音乐管理器"""
    def __init__(self, config_path: str = "config/music_config.json"):
        self.config_path = config_path
        self.music_library: Dict[str, BackgroundMusic] = {}
        self._load_config()
    
    def _load_config(self):
        """加载音乐配置"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.music_library = {
                    music_id: BackgroundMusic(**music_data)
                    for music_id, music_data in config.items()
                }
        else:
            self._initialize_default_library()
    
    def _initialize_default_library(self):
        """初始化默认音乐库"""
        default_music = [
            # 商业科技类
            {
                "id": "business_energetic_001",
                "name": "轻快节奏",
                "path": "assets/music/business/energetic_001.mp3",
                "description": "适合科技、商业类话题的轻快背景音乐",
                "mood": MusicMood.ENERGETIC,
                "category": MusicCategory.BUSINESS,
                "duration": 180,
                "bpm": 120,
                "tags": ["商业", "科技", "创新"],
                "license": MusicLicense(
                    license_type="CC BY-NC-SA",
                    license_url="https://creativecommons.org/licenses/by-nc-sa/4.0/",
                    attribution="Music by Zaka Podcast",
                    commercial_use=True,
                    modification_allowed=True
                ),
                "version": "1.0.0",
                "created_at": "2024-04-15",
                "updated_at": "2024-04-15",
                "is_active": True,
                "is_default": True,
                "metadata": {
                    "instrumentation": ["piano", "strings", "drums"],
                    "key": "C major",
                    "tempo": "moderate"
                }
            },
            # 更多默认音乐...
        ]
        
        for music_data in default_music:
            music = BackgroundMusic(**music_data)
            self.music_library[music.id] = music
        
        self._save_config()
    
    def _save_config(self):
        """保存音乐配置"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(
                {music_id: music.__dict__ for music_id, music in self.music_library.items()},
                f,
                ensure_ascii=False,
                indent=2
            )
    
    def get_music_by_id(self, music_id: str) -> Optional[BackgroundMusic]:
        """根据ID获取音乐"""
        return self.music_library.get(music_id)
    
    def get_music_by_category(self, category: MusicCategory) -> List[BackgroundMusic]:
        """根据类别获取音乐列表"""
        return [
            music for music in self.music_library.values()
            if music.category == category and music.is_active
        ]
    
    def get_music_by_mood(self, mood: MusicMood) -> List[BackgroundMusic]:
        """根据情绪获取音乐列表"""
        return [
            music for music in self.music_library.values()
            if music.mood == mood and music.is_active
        ]
    
    def get_music_by_tags(self, tags: List[str]) -> List[BackgroundMusic]:
        """根据标签获取音乐列表"""
        return [
            music for music in self.music_library.values()
            if any(tag in music.tags for tag in tags) and music.is_active
        ]
    
    def add_music(self, music: BackgroundMusic):
        """添加新音乐"""
        self.music_library[music.id] = music
        self._save_config()
    
    def update_music(self, music_id: str, **kwargs):
        """更新音乐信息"""
        if music_id in self.music_library:
            music = self.music_library[music_id]
            for key, value in kwargs.items():
                setattr(music, key, value)
            music.updated_at = "2024-04-15"  # 这里应该使用实际的时间
            self._save_config()
    
    def delete_music(self, music_id: str):
        """删除音乐"""
        if music_id in self.music_library:
            del self.music_library[music_id]
            self._save_config()
    
    def list_available_music(self) -> List[BackgroundMusic]:
        """获取所有可用的音乐"""
        return [music for music in self.music_library.values() if music.is_active]
    
    def list_available_categories(self) -> List[MusicCategory]:
        """获取所有可用的音乐类别"""
        return list(set(music.category for music in self.music_library.values() if music.is_active))
    
    def get_default_music(self, category: MusicCategory) -> Optional[BackgroundMusic]:
        """获取指定类别的默认音乐"""
        for music in self.music_library.values():
            if music.category == category and music.is_default and music.is_active:
                return music
        return None 