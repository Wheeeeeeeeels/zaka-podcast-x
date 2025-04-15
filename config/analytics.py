from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import os
import logging
from collections import defaultdict

class MusicAnalytics:
    """音乐数据分析器"""
    def __init__(self, data_path: str = "data/analytics"):
        self.data_path = data_path
        self.logger = logging.getLogger(__name__)
        self.usage_stats: Dict[str, Dict] = defaultdict(lambda: {
            "total_plays": 0,
            "total_duration": 0,
            "user_count": 0,
            "last_played": None,
            "play_history": []
        })
        self.user_preferences: Dict[str, Dict] = defaultdict(lambda: {
            "favorite_categories": [],
            "favorite_moods": [],
            "play_history": [],
            "preferred_duration": None
        })
        
        self._load_data()
    
    def _load_data(self):
        """加载分析数据"""
        os.makedirs(self.data_path, exist_ok=True)
        
        # 加载使用统计
        stats_file = os.path.join(self.data_path, "usage_stats.json")
        if os.path.exists(stats_file):
            with open(stats_file, 'r', encoding='utf-8') as f:
                self.usage_stats.update(json.load(f))
        
        # 加载用户偏好
        prefs_file = os.path.join(self.data_path, "user_preferences.json")
        if os.path.exists(prefs_file):
            with open(prefs_file, 'r', encoding='utf-8') as f:
                self.user_preferences.update(json.load(f))
    
    def _save_data(self):
        """保存分析数据"""
        # 保存使用统计
        with open(os.path.join(self.data_path, "usage_stats.json"), 'w', encoding='utf-8') as f:
            json.dump(dict(self.usage_stats), f, ensure_ascii=False, indent=2)
        
        # 保存用户偏好
        with open(os.path.join(self.data_path, "user_preferences.json"), 'w', encoding='utf-8') as f:
            json.dump(dict(self.user_preferences), f, ensure_ascii=False, indent=2)
    
    def record_play(self, music_id: str, user_id: str, duration: int):
        """记录音乐播放"""
        timestamp = datetime.now().isoformat()
        
        # 更新使用统计
        stats = self.usage_stats[music_id]
        stats["total_plays"] += 1
        stats["total_duration"] += duration
        stats["last_played"] = timestamp
        stats["play_history"].append({
            "user_id": user_id,
            "timestamp": timestamp,
            "duration": duration
        })
        
        # 更新用户偏好
        prefs = self.user_preferences[user_id]
        prefs["play_history"].append({
            "music_id": music_id,
            "timestamp": timestamp,
            "duration": duration
        })
        
        self._save_data()
    
    def get_music_stats(self, music_id: str) -> Dict:
        """获取音乐使用统计"""
        return self.usage_stats.get(music_id, {})
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """获取用户偏好"""
        return self.user_preferences.get(user_id, {})
    
    def get_popular_music(self, limit: int = 10) -> List[Dict]:
        """获取热门音乐"""
        return sorted(
            [
                {
                    "music_id": music_id,
                    "total_plays": stats["total_plays"],
                    "total_duration": stats["total_duration"],
                    "user_count": stats["user_count"]
                }
                for music_id, stats in self.usage_stats.items()
            ],
            key=lambda x: x["total_plays"],
            reverse=True
        )[:limit]
    
    def get_user_activity(self, user_id: str, days: int = 30) -> Dict:
        """获取用户活动统计"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        activity = {
            "total_plays": 0,
            "total_duration": 0,
            "favorite_categories": defaultdict(int),
            "favorite_moods": defaultdict(int),
            "daily_activity": defaultdict(int)
        }
        
        for play in self.user_preferences[user_id]["play_history"]:
            play_date = datetime.fromisoformat(play["timestamp"])
            if start_date <= play_date <= end_date:
                activity["total_plays"] += 1
                activity["total_duration"] += play["duration"]
                activity["daily_activity"][play_date.date().isoformat()] += 1
        
        return activity
    
    def analyze_music_effectiveness(self, music_id: str) -> Dict:
        """分析音乐效果"""
        stats = self.usage_stats[music_id]
        
        # 计算平均播放时长
        avg_duration = stats["total_duration"] / stats["total_plays"] if stats["total_plays"] > 0 else 0
        
        # 计算用户留存率
        unique_users = len(set(play["user_id"] for play in stats["play_history"]))
        user_retention = unique_users / stats["total_plays"] if stats["total_plays"] > 0 else 0
        
        return {
            "music_id": music_id,
            "total_plays": stats["total_plays"],
            "unique_users": unique_users,
            "average_duration": avg_duration,
            "user_retention": user_retention,
            "last_played": stats["last_played"]
        }
    
    def generate_recommendations(self, user_id: str, limit: int = 5) -> List[str]:
        """生成音乐推荐"""
        user_prefs = self.user_preferences[user_id]
        
        # 获取用户最常听的类别和情绪
        category_counts = defaultdict(int)
        mood_counts = defaultdict(int)
        
        for play in user_prefs["play_history"]:
            music_id = play["music_id"]
            if music_id in self.usage_stats:
                stats = self.usage_stats[music_id]
                category_counts[stats.get("category", "")] += 1
                mood_counts[stats.get("mood", "")] += 1
        
        # 找出最受欢迎的类别和情绪
        favorite_category = max(category_counts.items(), key=lambda x: x[1])[0]
        favorite_mood = max(mood_counts.items(), key=lambda x: x[1])[0]
        
        # 生成推荐
        recommendations = []
        for music_id, stats in self.usage_stats.items():
            if (stats.get("category") == favorite_category and 
                stats.get("mood") == favorite_mood and 
                music_id not in [play["music_id"] for play in user_prefs["play_history"]]):
                recommendations.append(music_id)
        
        return recommendations[:limit] 