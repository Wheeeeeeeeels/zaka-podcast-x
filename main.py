import os
import sys
import argparse
from dotenv import load_dotenv

# 添加 ffmpeg 路径到系统 PATH
ffmpeg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg', 'bin')
if os.path.exists(ffmpeg_path):
    os.environ['PATH'] = ffmpeg_path + os.pathsep + os.environ['PATH']
    print(f"已添加 ffmpeg 路径: {ffmpeg_path}")
else:
    print(f"警告: ffmpeg 路径不存在: {ffmpeg_path}")
    print("请下载 ffmpeg 并解压到项目根目录的 ffmpeg 文件夹中")
    print("下载地址: https://github.com/BtbN/FFmpeg-Builds/releases")
    print("下载 ffmpeg-master-latest-win64-gpl.zip")

from podcast_generator import PodcastGenerator
from audio_processor import AudioProcessor
from podcast_publisher import PodcastPublisher
from podcast_templates import PodcastTemplates
from config import Config
from logger import logger
from exceptions import PodcastError

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='Zaka播客自动生成系统')
    
    # 模式选择
    parser.add_argument('--mode', type=str, default='auto', choices=['auto', 'content', 'audio', 'publish'],
                        help='运行模式: auto(完整流程), content(只生成内容), audio(只生成音频), publish(只发布)')
    
    # 风格和主题参数
    parser.add_argument('--style', type=str, default=None,
                        help='播客风格类型，例如：知识型、故事型、对话型等')
    parser.add_argument('--topic', type=str, default=None,
                        help='播客主题，如果不指定则自动从热门话题中选择')
    parser.add_argument('--reference', type=str, default=None,
                        help='参考的热门播客，例如：故事FM、得到头条等')
    
    # 文件参数
    parser.add_argument('--content-file', type=str, default=None,
                        help='内容JSON文件路径（用于从文件加载播客内容）')
    parser.add_argument('--audio-file', type=str, default=None,
                        help='音频文件路径（用于直接发布现有音频）')
    
    # 平台参数
    parser.add_argument('--platforms', type=str, default='all',
                        help='要发布的平台，用逗号分隔，例如：xiaoyuzhou,lizhi')
    
    # 其他选项
    parser.add_argument('--list-styles', action='store_true',
                        help='列出所有可用的播客风格')
    parser.add_argument('--list-podcasts', action='store_true',
                        help='列出所有参考的热门播客')
    parser.add_argument('--list-topics', action='store_true',
                        help='列出热门话题')
    
    return parser.parse_args()

def list_available_styles():
    """列出所有可用的播客风格"""
    print("\n=== 可用的播客风格 ===")
    for style, info in PodcastTemplates.PODCAST_STYLES.items():
        print(f"- {style}: {info['description']}")
        print(f"  语调: {info['tone']}")
        print()

def list_trending_podcasts():
    """列出参考的热门播客"""
    print("\n=== 热门播客参考 ===")
    for podcast in PodcastTemplates.TRENDING_PODCASTS:
        print(f"- {podcast['name']}: {podcast['description']}")
        print(f"  风格: {podcast['style']}")
        print(f"  话题: {', '.join(podcast['topics'])}")
        print()

def list_trending_topics():
    """列出热门话题"""
    print("\n=== 当前热门话题 ===")
    for topic in PodcastTemplates.get_trending_topics():
        print(f"- {topic}")
    print()

def load_content_from_file(file_path):
    """从文件加载播客内容"""
    import json
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载内容文件时出错: {str(e)}")
        raise PodcastError(f"无法加载内容文件: {str(e)}")

def save_content_to_file(content):
    """将内容保存到文件"""
    import json
    from datetime import datetime
    
    # 创建输出目录
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(output_dir, f"content_{timestamp}.json")
    
    # 保存内容
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        logger.info(f"内容已保存到文件: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"保存内容到文件时出错: {str(e)}")
        return None

def main():
    """主程序入口"""
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 显示信息选项
        if args.list_styles:
            list_available_styles()
            return
        
        if args.list_podcasts:
            list_trending_podcasts()
            return
        
        if args.list_topics:
            list_trending_topics()
            return
        
        # 加载配置
        config = Config()
        
        # 初始化各个组件
        generator = PodcastGenerator()
        audio_processor = AudioProcessor()
        publisher = PodcastPublisher()
        
        # 根据模式执行相应功能
        if args.mode == 'auto' or args.mode == 'content':
            # 生成播客内容
            if args.content_file:
                # 从文件加载内容
                logger.info(f"从文件加载内容: {args.content_file}")
                podcast_content = load_content_from_file(args.content_file)
            else:
                # 生成新内容
                logger.info("开始生成播客内容...")
                if args.reference:
                    # 基于参考播客生成
                    logger.info(f"参考播客: {args.reference}")
                    podcast_content = generator.generate_content(
                        style=args.style,
                        topic=args.topic,
                        reference_podcast=args.reference
                    )
                else:
                    # 基于指定风格或者热门内容生成
                    if args.style or args.topic:
                        podcast_content = generator.generate_content(
                            style=args.style,
                            topic=args.topic
                        )
                    else:
                        # 使用热门话题和风格
                        podcast_content = generator.generate_trending_content()
                
                # 保存内容到文件
                content_file = save_content_to_file(podcast_content)
            
            # 显示生成的内容
            logger.info(f"生成播客标题: {podcast_content['title']}")
            logger.info(f"风格: {podcast_content.get('style', '默认')}")
            logger.info(f"主题: {podcast_content.get('topic', '未指定')}")
            
            # 如果只生成内容，这里就结束
            if args.mode == 'content':
                logger.info("内容生成完成，程序结束")
                return
        
        # 生成音频
        if args.mode == 'auto' or args.mode == 'audio':
            if args.audio_file:
                # 使用现有音频文件
                logger.info(f"使用现有音频文件: {args.audio_file}")
                audio_info = {
                    'path': args.audio_file,
                    'filename': os.path.basename(args.audio_file),
                    'duration': 0,  # 需要计算
                    'size': os.path.getsize(args.audio_file) / (1024 * 1024)  # MB
                }
            else:
                # 生成新音频
                logger.info("开始生成音频...")
                audio_info = audio_processor.generate_audio(podcast_content)
                logger.info(f"音频生成完成: {audio_info['filename']}")
                logger.info(f"时长: {audio_info['duration']:.2f}秒, 大小: {audio_info['size']:.2f}MB")
            
            # 如果只生成音频，这里就结束
            if args.mode == 'audio':
                logger.info("音频生成完成，程序结束")
                return
        
        # 发布到播客平台
        if args.mode == 'auto' or args.mode == 'publish':
            logger.info("开始发布到播客平台...")
            
            # 确定要发布的平台
            platforms = args.platforms.split(',') if args.platforms != 'all' else ['xiaoyuzhou']
            
            # 发布并获取结果
            publish_results = publisher.publish(audio_info, podcast_content)
            
            # 显示发布结果
            for platform, result in publish_results.items():
                if result.get('success', False):
                    logger.info(f"发布到 {platform} 成功: {result.get('episode_url', '')}")
                else:
                    logger.error(f"发布到 {platform} 失败: {result.get('error', 'Unknown error')}")
    
    except PodcastError as e:
        logger.error(f"程序出错: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"未处理的异常: {str(e)}")
        sys.exit(2)

if __name__ == "__main__":
    main() 