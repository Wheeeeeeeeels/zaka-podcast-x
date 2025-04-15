#!/usr/bin/env python
import argparse
import logging
from dotenv import load_dotenv
from config.music_crawler import MusicCrawler

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()
    
    parser = argparse.ArgumentParser(description='音乐爬取工具')
    parser.add_argument('--source', type=str, default='jamendo',
                       choices=['jamendo', 'fma'],
                       help='音乐来源')
    parser.add_argument('--category', type=str, required=True,
                       help='音乐类别')
    parser.add_argument('--limit', type=int, default=10,
                       help='爬取数量限制')
    parser.add_argument('--save-dir', type=str, default='assets/music',
                       help='保存目录')
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # 创建爬虫
    crawler = MusicCrawler(save_dir=args.save_dir)
    
    try:
        # 根据来源选择爬取方法
        if args.source == 'jamendo':
            logger.info(f"从 Jamendo 爬取 {args.category} 类别的音乐...")
            music_list = crawler.crawl_jamendo(args.category, args.limit)
        else:
            logger.info(f"从 Free Music Archive 爬取 {args.category} 类别的音乐...")
            music_list = crawler.crawl_free_music_archive(args.category, args.limit)
        
        # 保存音乐信息
        if music_list:
            crawler.save_music_info(music_list, args.category)
            logger.info(f"成功爬取 {len(music_list)} 首音乐")
            for music in music_list:
                logger.info(f"- {music['title']} by {music['artist']} ({music['mood']})")
        else:
            logger.warning("没有找到符合条件的音乐")
    
    except Exception as e:
        logger.error(f"爬取失败: {str(e)}")

if __name__ == '__main__':
    main() 