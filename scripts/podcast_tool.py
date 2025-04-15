#!/usr/bin/env python
import os
import click
import logging
from typing import Optional
from audio_processor import AudioProcessor
from config.music_crawler import MusicCrawler

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PodcastTool:
    """播客工具类"""
    
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.music_crawler = MusicCrawler()
    
    def list_music_categories(self):
        """列出可用的音乐类别"""
        categories = ['business', 'relaxing', 'energetic', 'motivational']
        return categories
    
    def list_available_music(self, category: str):
        """列出指定类别的可用音乐"""
        music_list = self.music_crawler.load_music_info(category)
        return music_list
    
    def process_audio(self, 
                     voice_path: str,
                     music_path: Optional[str] = None,
                     category: Optional[str] = None,
                     music_volume: float = 0.3) -> str:
        """处理音频文件"""
        if music_path:
            return self.audio_processor.add_background_music(
                voice_path, music_path, music_volume=music_volume
            )
        else:
            return self.audio_processor.process_podcast(
                voice_path, category, music_volume=music_volume
            )

@click.group()
def cli():
    """播客制作工具"""
    pass

@cli.command()
def list_categories():
    """列出可用的音乐类别"""
    tool = PodcastTool()
    categories = tool.list_music_categories()
    click.echo("可用的音乐类别：")
    for category in categories:
        click.echo(f"- {category}")

@cli.command()
@click.argument('category')
def list_music(category):
    """列出指定类别的音乐"""
    tool = PodcastTool()
    music_list = tool.list_available_music(category)
    if music_list:
        click.echo(f"{category} 类别的音乐：")
        for music in music_list:
            click.echo(f"- {music['title']} by {music['artist']}")
    else:
        click.echo(f"没有找到 {category} 类别的音乐")

@cli.command()
@click.argument('voice_path')
@click.option('--music-path', help='背景音乐文件路径')
@click.option('--category', help='背景音乐类别')
@click.option('--volume', type=float, default=0.3, help='背景音乐音量 (0-1)')
def process(voice_path, music_path, category, volume):
    """处理音频文件，添加背景音乐"""
    if not os.path.exists(voice_path):
        click.echo(f"错误：音频文件 {voice_path} 不存在")
        return
    
    tool = PodcastTool()
    output_path = tool.process_audio(
        voice_path=voice_path,
        music_path=music_path,
        category=category,
        music_volume=volume
    )
    
    click.echo(f"处理完成，输出文件：{output_path}")

@cli.command()
@click.argument('category')
@click.option('--limit', type=int, default=10, help='下载数量限制')
def download_music(category, limit):
    """下载指定类别的背景音乐"""
    tool = PodcastTool()
    music_list = tool.music_crawler.crawl_jamendo(category, limit)
    if music_list:
        click.echo(f"成功下载 {len(music_list)} 首音乐")
        for music in music_list:
            click.echo(f"- {music['title']} by {music['artist']}")
    else:
        click.echo(f"下载 {category} 类别的音乐失败")

if __name__ == '__main__':
    cli() 