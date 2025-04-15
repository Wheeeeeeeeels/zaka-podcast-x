import openai
from dotenv import load_dotenv
import os
from logger import logger
from exceptions import ContentGenerationError
from podcast_templates import PodcastTemplates
from config import Config

class PodcastGenerator:
    def __init__(self):
        self.config = Config()
        self.api_key = self.config.openai_api_key
        self.model = self.config.openai_model
        
        if not self.api_key:
            logger.error("未设置OpenAI API密钥")
            raise ContentGenerationError("未设置OpenAI API密钥")
            
        # 设置OpenAI API密钥
        openai.api_key = self.api_key
    
    def generate_content(self, style="知识型", topic=None, reference_podcast=None):
        """
        生成播客内容
        style: 播客风格
        topic: 主题，如果为None则自动选择热门话题
        reference_podcast: 参考的热门播客
        返回: dict 包含标题、脚本和描述
        """
        try:
            # 如果未指定主题，从热门话题中选择
            if not topic:
                trending_topics = PodcastTemplates.get_trending_topics()
                import random
                topic = random.choice(trending_topics)
                logger.info(f"自动选择热门话题: {topic}")
            
            # 获取播客模板
            if reference_podcast:
                # 根据参考播客查找其风格
                for podcast in PodcastTemplates.TRENDING_PODCASTS:
                    if podcast["name"] == reference_podcast:
                        style = podcast["style"]
                        logger.info(f"使用参考播客 '{reference_podcast}' 的风格: {style}")
                        break
            
            # 获取对应风格的模板
            template = PodcastTemplates.get_template_by_style(style, topic)
            
            if not template:
                logger.warning(f"未找到风格 '{style}' 的模板，使用默认模板")
                # 使用默认提示词
                prompt = f"""
                请创建一个关于{topic}的播客脚本。包含:
                1. 引人入胜的开场白
                2. 3-5个主要话题点
                3. 每个话题点的详细讨论
                4. 总结和结束语
                
                请用中文生成，风格要自然、口语化。
                """
            else:
                prompt = template["prompt"]
                logger.info(f"使用 '{style}' 风格模板生成内容")
            
            # 调用OpenAI API生成内容
            logger.debug(f"发送到OpenAI的提示词: {prompt}")
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的播客内容创作者，擅长创作吸引人的播客脚本"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            logger.info(f"内容生成成功，长度: {len(content)} 字符")
            
            # 生成标题和描述
            title = self._generate_title(content, topic)
            description = self._generate_description(content, topic)
            
            return {
                "title": title,
                "script": content,
                "description": description,
                "topic": topic,
                "style": style,
                "template_used": True if template else False
            }
            
        except Exception as e:
            logger.error(f"生成播客内容时出错: {str(e)}")
            raise ContentGenerationError(f"生成播客内容失败: {str(e)}")
    
    def generate_trending_content(self):
        """生成当前热门话题的播客内容"""
        trending_topics = PodcastTemplates.get_trending_topics()
        import random
        topic = random.choice(trending_topics)
        
        # 随机选择一个热门播客风格
        trending_podcasts = PodcastTemplates.TRENDING_PODCASTS
        reference_podcast = random.choice(trending_podcasts)["name"]
        
        return self.generate_content(topic=topic, reference_podcast=reference_podcast)
    
    def _generate_title(self, content, topic):
        """生成播客标题"""
        try:
            prompt = f"根据以下内容生成一个有吸引力的中文播客标题，标题要简短有力，能引发好奇心，不超过20个字。内容主题是：{topic}\n\n{content[:1000]}"
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的播客标题创作者，擅长创作吸引人的短标题"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.8
            )
            
            title = response.choices[0].message.content.strip().replace('"', '').replace('"', '')
            logger.info(f"生成标题: {title}")
            return title
            
        except Exception as e:
            logger.error(f"生成标题时出错: {str(e)}")
            return f"{topic}播客"
    
    def _generate_description(self, content, topic):
        """生成播客描述"""
        try:
            prompt = f"根据以下内容生成一个简短的播客描述，不超过100字，要吸引听众点击收听。内容主题是：{topic}\n\n{content[:1000]}"
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的播客描述创作者，擅长创作吸引人的简短描述"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            description = response.choices[0].message.content.strip()
            logger.info(f"生成描述: {description[:50]}...")
            return description
            
        except Exception as e:
            logger.error(f"生成描述时出错: {str(e)}")
            return f"这是一期关于{topic}的精彩播客，欢迎收听。" 