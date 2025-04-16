#!/usr/bin/env python
import os
import sys
from openai import OpenAI
import logging
from gtts import gTTS
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from audio_processor import AudioProcessor
from config.music_crawler import MusicCrawler

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not client.api_key:
    raise ValueError("请在 .env 文件中设置 OPENAI_API_KEY")

def generate_podcast_script(topic="现代人的孤独感", style="姜思达", duration=5):
    """生成播客脚本"""
    logger.info(f"开始生成播客脚本 - 主题: {topic}, 风格: {style}, 时长: {duration}分钟")
    
    prompt = f"""
    请模仿{style}的播客风格，创作一个关于{topic}的播客脚本。
    要求：
    1. 时长约{duration}分钟
    2. 保持{style}的语言风格和表达方式
    3. 包含开场白、主体内容和结束语
    4. 在适当位置标注[音乐渐入]、[音乐过渡]、[音乐渐强]、[音乐渐弱]、[音乐结束]
    5. 语言要自然流畅，有个人特色
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一个专业的播客脚本创作助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        script = response.choices[0].message.content
        logger.info("脚本生成成功")
        return script
        
    except Exception as e:
        logger.error(f"生成脚本时出错: {str(e)}")
        raise

def create_podcast(script, music_style="relaxing"):
    """创建播客音频"""
    logger.info(f"开始创建播客音频 - 音乐风格: {music_style}")
    
    try:
        # 初始化工具
        audio_processor = AudioProcessor()
        music_crawler = MusicCrawler()
        
        # 生成语音
        logger.info("正在生成语音...")
        tts = gTTS(text=script, lang='zh-cn')
        voice_path = "temp_voice.mp3"
        tts.save(voice_path)
        logger.info(f"语音已保存到: {voice_path}")
        
        # 下载背景音乐
        logger.info("正在下载背景音乐...")
        music_list = music_crawler.crawl_jamendo(music_style, 1)
        if not music_list:
            raise Exception("下载背景音乐失败")
        
        music_path = music_list[0]['path']
        logger.info(f"背景音乐已下载到: {music_path}")
        
        # 处理音频
        logger.info("正在处理音频...")
        output_path = audio_processor.process_audio(
            voice_path=voice_path,
            music_path=music_path,
            music_volume=0.3
        )
        logger.info(f"音频处理完成: {output_path}")
        
        # 清理临时文件
        os.unlink(voice_path)
        logger.info("临时文件已清理")
        
        return output_path
        
    except Exception as e:
        logger.error(f"创建播客时出错: {str(e)}")
        if os.path.exists(voice_path):
            os.unlink(voice_path)
        raise

def main():
    """主函数"""
    try:
        # 生成脚本
        logger.info("开始生成播客...")
        script = generate_podcast_script()
        
        # 保存脚本
        script_path = "content/podcast_script.txt"
        os.makedirs(os.path.dirname(script_path), exist_ok=True)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)
        logger.info(f"脚本已保存到: {script_path}")
        
        # 创建播客
        output_path = create_podcast(script)
        logger.info(f"播客已生成: {output_path}")
        
    except Exception as e:
        logger.error(f"生成播客时出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 