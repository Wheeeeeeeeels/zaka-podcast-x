import requests
import os
import json
import time
from datetime import datetime
import aiohttp
import asyncio
from slugify import slugify
from logger import logger
from exceptions import PublishingError, APIError
from config import Config

class PodcastPublisher:
    def __init__(self):
        self.config = Config()
        
        # 平台API密钥
        self.xiaoyuzhou_api_key = self.config.xiaoyuzhou_api_key
        self.xiaoyuzhou_api_url = self.config.xiaoyuzhou_api_url
        
        # 重试和超时设置
        self.max_retries = self.config.max_retries
        self.timeout = self.config.timeout
        
        # 支持的平台列表
        self.supported_platforms = ["xiaoyuzhou", "lizhi", "ximalaya", "qingting"]
    
    def publish(self, audio_info, content):
        """
        发布播客到各个平台
        audio_info: dict 音频文件信息
        content: dict 包含标题、脚本和描述
        返回: dict 包含发布结果
        """
        results = {}
        
        # 小宇宙平台发布
        if self.xiaoyuzhou_api_key:
            try:
                result = self._publish_to_xiaoyuzhou(audio_info, content)
                results["xiaoyuzhou"] = result
                logger.info(f"成功发布到小宇宙平台: {result.get('episode_id', '')}")
            except Exception as e:
                logger.error(f"小宇宙平台发布失败: {str(e)}")
                results["xiaoyuzhou"] = {"success": False, "error": str(e)}
        
        # 其他平台发布（可以异步处理）
        other_platforms_results = self._publish_to_other_platforms(audio_info, content)
        results.update(other_platforms_results)
        
        # 记录发布结果
        self._log_publish_results(audio_info, content, results)
        
        return results
    
    def _publish_to_xiaoyuzhou(self, audio_info, content):
        """发布到小宇宙平台"""
        try:
            logger.info("开始发布到小宇宙平台")
            
            # 准备请求数据
            audio_path = audio_info['path']
            
            # 小宇宙平台发布所需元数据
            metadata = {
                "title": content['title'],
                "description": content['description'],
                "slug": slugify(content['title']),
                "publish_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "category": self._determine_category(content),
                "tags": self._generate_tags(content),
                "explicit": False,  # 是否包含成人内容
                "season": 1,  # 季数
                "episode": self._get_next_episode_number()  # 集数
            }
            
            # 构建API请求
            headers = {
                "Authorization": f"Bearer {self.xiaoyuzhou_api_key}",
                "Accept": "application/json"
            }
            
            # 准备表单数据和文件
            with open(audio_path, 'rb') as audio_file:
                files = {
                    "audio": (os.path.basename(audio_path), audio_file, "audio/mpeg")
                }
                
                # 使用重试机制
                for attempt in range(self.max_retries):
                    try:
                        response = requests.post(
                            f"{self.xiaoyuzhou_api_url}/episodes",
                            headers=headers,
                            data=metadata,
                            files=files,
                            timeout=self.timeout
                        )
                        
                        if response.status_code == 200 or response.status_code == 201:
                            result = response.json()
                            return {
                                "success": True,
                                "platform": "xiaoyuzhou",
                                "episode_id": result.get("id", ""),
                                "episode_url": result.get("url", ""),
                                "publish_date": metadata["publish_date"]
                            }
                        else:
                            error_message = f"API错误: {response.status_code} - {response.text}"
                            logger.error(error_message)
                            
                            # 如果是最后一次尝试，则抛出异常
                            if attempt == self.max_retries - 1:
                                raise APIError(error_message, response.status_code, response.text)
                            
                            # 否则等待后重试
                            time.sleep(2)
                    except requests.RequestException as e:
                        if attempt == self.max_retries - 1:
                            raise PublishingError(f"请求失败: {str(e)}")
                        time.sleep(2)
        
        except Exception as e:
            logger.error(f"发布到小宇宙平台时出错: {str(e)}")
            raise PublishingError(f"发布到小宇宙平台失败: {str(e)}")
    
    def _publish_to_other_platforms(self, audio_info, content):
        """发布到其他播客平台"""
        results = {}
        
        # 这里可以实现其他平台的发布逻辑
        # 例如，荔枝FM、喜马拉雅、蜻蜓FM等
        
        logger.info("其他播客平台发布功能待实现")
        
        return results
    
    def _determine_category(self, content):
        """根据内容确定播客分类"""
        # 基于内容关键词判断分类
        style = content.get('style', '').lower()
        topic = content.get('topic', '').lower()
        
        # 分类映射
        if "商业" in style or "财经" in style or "创业" in topic or "投资" in topic:
            return "business"
        elif "科技" in style or "技术" in topic or "数码" in topic:
            return "technology"
        elif "教育" in topic or "学习" in topic or "知识" in style:
            return "education"
        elif "故事" in style or "文学" in topic:
            return "arts"
        elif "生活" in style or "健康" in topic:
            return "health"
        else:
            return "society"  # 默认分类
    
    def _generate_tags(self, content):
        """生成内容标签"""
        tags = []
        
        # 添加风格标签
        if 'style' in content:
            tags.append(content['style'])
        
        # 添加主题标签
        if 'topic' in content:
            # 将主题分割为关键词
            keywords = content['topic'].split()
            tags.extend(keywords[:3])  # 最多取3个关键词
        
        # 添加自定义标签
        custom_tags = ["播客", "AI生成", "zaka播客"]
        tags.extend(custom_tags)
        
        # 去重并限制数量
        unique_tags = list(set(tags))
        return unique_tags[:5]  # 最多5个标签
    
    def _get_next_episode_number(self):
        """获取下一集编号"""
        # 这里可以实现从数据库或文件读取当前最大集号
        # 简单起见，这里使用当前日期作为集号
        return int(datetime.now().strftime("%Y%m%d"))
    
    def _log_publish_results(self, audio_info, content, results):
        """记录发布结果"""
        # 准备日志数据
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "title": content['title'],
            "audio_info": {
                "filename": audio_info['filename'],
                "duration": audio_info['duration'],
                "size": audio_info['size']
            },
            "publish_results": results
        }
        
        # 写入日志文件
        log_file = os.path.join("logs", "publish_history.json")
        
        # 确保日志目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # 读取现有日志（如果存在）
        existing_logs = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    existing_logs = json.load(f)
            except:
                # 如果读取失败，使用空列表
                logger.warning("无法读取现有发布日志，将创建新日志文件")
        
        # 添加新日志
        existing_logs.append(log_data)
        
        # 写入文件
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(existing_logs, f, ensure_ascii=False, indent=2) 