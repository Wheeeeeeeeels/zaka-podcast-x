import os
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging
from urllib.parse import urlparse
import re

class MusicCrawler:
    """音乐爬取器"""
    
    def __init__(self, save_dir: str = "assets/music"):
        self.save_dir = save_dir
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)
        
        # API 配置
        self.jamendo_client_id = os.getenv('JAMENDO_CLIENT_ID')
        self.jamendo_client_secret = os.getenv('JAMENDO_CLIENT_SECRET')
        self.fma_api_key = os.getenv('FMA_API_KEY')
        
        if not self.jamendo_client_id or not self.jamendo_client_secret:
            self.logger.warning("Jamendo API 凭据未配置")
    
    def crawl_free_music_archive(self, category: str, limit: int = 10) -> List[Dict]:
        """从 Free Music Archive 爬取音乐"""
        try:
            # FMA API 端点
            url = f"https://freemusicarchive.org/api/get/albums.json"
            params = {
                'api_key': self.fma_api_key,
                'limit': limit,
                'genre_handle': category
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            albums = response.json()['dataset']
            results = []
            
            for album in albums:
                # 获取专辑详情
                album_url = f"https://freemusicarchive.org/api/get/albums_{album['album_id']}.json"
                album_response = self.session.get(album_url, params={'api_key': self.fma_api_key})
                album_data = album_response.json()['dataset'][0]
                
                # 下载音乐文件
                for track in album_data['tracks']:
                    if track['track_downloadable']:
                        music_info = {
                            'id': track['track_id'],
                            'title': track['track_title'],
                            'artist': track['artist_name'],
                            'url': track['track_file'],
                            'duration': track['track_duration'],
                            'category': category,
                            'mood': self._analyze_mood(track['track_title']),
                            'license': track['license_title']
                        }
                        
                        # 下载文件
                        file_path = self._download_file(music_info['url'], category, music_info['id'])
                        if file_path:
                            music_info['file_path'] = file_path
                            results.append(music_info)
            
            return results
            
        except Exception as e:
            self.logger.error(f"从 Free Music Archive 爬取音乐失败: {str(e)}")
            return []
    
    def crawl_jamendo(self, category: str, limit: int = 10) -> List[Dict]:
        """从 Jamendo 爬取音乐"""
        try:
            if not self.jamendo_client_id or not self.jamendo_client_secret:
                self.logger.error("Jamendo API 凭据未配置")
                return []

            # Jamendo API 端点
            url = "https://api.jamendo.com/v3.0/tracks"
            params = {
                'client_id': self.jamendo_client_id,
                'format': 'json',
                'limit': limit,
                'tags': category,
                'license_cc0': 1,  # 只获取 CC0 许可的音乐
                'include': 'musicinfo'  # 获取更多音乐信息
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            tracks = response.json()['results']
            results = []
            
            for track in tracks:
                music_info = {
                    'id': track['id'],
                    'title': track['name'],
                    'artist': track['artist_name'],
                    'url': track['audio'],
                    'duration': track['duration'],
                    'category': category,
                    'mood': self._analyze_mood(track['name']),
                    'license': 'CC0'
                }
                
                # 下载文件
                file_path = self._download_file(music_info['url'], category, music_info['id'])
                if file_path:
                    music_info['file_path'] = file_path
                    results.append(music_info)
            
            return results
            
        except Exception as e:
            self.logger.error(f"从 Jamendo 爬取音乐失败: {str(e)}")
            return []
    
    def _download_file(self, url: str, category: str, music_id: str) -> Optional[str]:
        """下载音乐文件"""
        try:
            # 创建类别目录
            category_dir = os.path.join(self.save_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            
            # 获取文件扩展名
            parsed_url = urlparse(url)
            file_ext = os.path.splitext(parsed_url.path)[1] or '.mp3'
            
            # 生成文件名
            filename = f"{music_id}{file_ext}"
            file_path = os.path.join(category_dir, filename)
            
            # 下载文件
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return file_path
            
        except Exception as e:
            self.logger.error(f"下载音乐文件失败: {str(e)}")
            return None
    
    def _analyze_mood(self, title: str) -> str:
        """分析音乐情绪"""
        # 简单的情绪分析，可以根据需要扩展
        mood_keywords = {
            'energetic': ['upbeat', 'energetic', 'happy', 'joyful', 'exciting'],
            'calm': ['calm', 'peaceful', 'relaxing', 'soothing', 'meditation'],
            'sad': ['sad', 'melancholy', 'emotional', 'heartbreak'],
            'motivational': ['motivational', 'inspirational', 'uplifting', 'positive']
        }
        
        title_lower = title.lower()
        for mood, keywords in mood_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                return mood
        
        return 'neutral'
    
    def save_music_info(self, music_list: List[Dict], category: str):
        """保存音乐信息到 JSON 文件"""
        try:
            info_file = os.path.join(self.save_dir, category, 'music_info.json')
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(music_list, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存音乐信息失败: {str(e)}")
    
    def load_music_info(self, category: str) -> List[Dict]:
        """从 JSON 文件加载音乐信息"""
        try:
            info_file = os.path.join(self.save_dir, category, 'music_info.json')
            if os.path.exists(info_file):
                with open(info_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"加载音乐信息失败: {str(e)}")
            return [] 