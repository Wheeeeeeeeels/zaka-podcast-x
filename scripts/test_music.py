import os
import logging
from audio_processor import AudioProcessor

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """主函数"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # 创建音频处理器
    processor = AudioProcessor()
    
    # 使用已下载的背景音乐作为测试
    test_music = "assets/music/business/1525942.mp3"  # 使用已下载的音乐文件
    
    if not os.path.exists(test_music):
        logger.error(f"测试音乐文件不存在: {test_music}")
        return
    
    try:
        # 创建一个简单的测试音频
        import numpy as np
        import soundfile as sf
        
        # 生成一个简单的测试音频（1秒的静音）
        test_voice = "test_voice.wav"
        sample_rate = 44100
        duration = 1.0  # 1秒
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        test_audio = np.sin(2 * np.pi * 440 * t) * 0.5  # 440Hz正弦波
        
        # 保存测试音频
        sf.write(test_voice, test_audio, sample_rate)
        
        # 处理播客音频，添加背景音乐
        output_path = processor.add_background_music(
            test_voice,
            test_music,
            music_volume=0.3  # 背景音乐音量，可以根据需要调整
        )
        
        logger.info(f"处理完成，输出文件: {output_path}")
        
        # 清理测试文件
        if os.path.exists(test_voice):
            os.remove(test_voice)
        
    except Exception as e:
        logger.error(f"处理失败: {str(e)}")

if __name__ == '__main__':
    main() 