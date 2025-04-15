from gtts import gTTS
from pydub import AudioSegment
import os
from datetime import datetime
import random
from slugify import slugify
from logger import logger
from exceptions import AudioGenerationError
from config import Config
import numpy as np
import soundfile as sf
import librosa
import logging
from typing import Optional
from config.music_crawler import MusicCrawler

class AudioProcessor:
    """音频处理器"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self.music_crawler = MusicCrawler()
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        self.config = Config()
        self.bg_music_path = self.config.background_music_path
        self.audio_quality = self.config.audio_quality
        
        # 确保assets目录存在
        if not os.path.exists('assets'):
            os.makedirs('assets')
    
    def generate_audio(self, content):
        """
        将文本内容转换为音频文件
        content: dict 包含标题、脚本和描述
        返回: dict 包含音频文件信息
        """
        try:
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            slug = slugify(content['title'])
            filename = f"{slug}_{timestamp}.mp3"
            output_path = os.path.join(self.output_dir, filename)
            
            logger.info(f"开始生成音频: {output_path}")
            
            # 将不同部分分开转换为音频，以便应用不同的处理效果
            audio_parts = []
            
            # 标题部分（可以用不同的声音或效果）
            title_path = self._generate_temp_audio(content['title'], 'title')
            title_audio = AudioSegment.from_mp3(title_path)
            # 为标题添加特效（例如回声）
            title_audio = self._add_title_effects(title_audio)
            audio_parts.append(title_audio)
            
            # 添加间隔
            audio_parts.append(AudioSegment.silent(duration=1000))  # 1秒静音
            
            # 主体内容部分
            script_path = self._generate_temp_audio(content['script'], 'script')
            script_audio = AudioSegment.from_mp3(script_path)
            # 可以为脚本内容添加特效，例如标准化音量
            script_audio = self._normalize_audio(script_audio)
            audio_parts.append(script_audio)
            
            # 合并音频
            final_audio = audio_parts[0]
            for part in audio_parts[1:]:
                final_audio += part
                
            # 添加背景音乐
            final_audio = self._add_background_music(final_audio)
            
            # 应用音频质量设置
            final_audio = self._apply_quality_settings(final_audio)
            
            # 导出最终音频
            final_audio.export(output_path, format="mp3")
            
            # 清理临时文件
            self._cleanup_temp_files([title_path, script_path])
            
            logger.info(f"音频生成成功: {output_path}")
            
            return {
                'path': output_path,
                'filename': filename,
                'duration': len(final_audio) / 1000,  # 秒
                'size': os.path.getsize(output_path) / (1024 * 1024)  # MB
            }
            
        except Exception as e:
            logger.error(f"生成音频时出错: {str(e)}")
            raise AudioGenerationError(f"生成音频失败: {str(e)}")
    
    def _generate_temp_audio(self, text, part_name):
        """生成临时音频文件"""
        temp_path = os.path.join(self.output_dir, f"temp_{part_name}_{int(datetime.now().timestamp())}.mp3")
        tts = gTTS(text=text, lang='zh-cn', slow=False)
        tts.save(temp_path)
        return temp_path
    
    def _add_title_effects(self, audio):
        """为标题音频添加特效"""
        # 提高音量
        audio = audio + 3  # 增加3dB
        
        # 添加淡入效果
        audio = audio.fade_in(300)  # 300毫秒淡入
        
        return audio
    
    def _normalize_audio(self, audio):
        """标准化音频音量"""
        # 计算目标dBFS（一般为-14到-16 dBFS）
        target_dBFS = -15.0
        
        # 获取当前音量
        current_dBFS = audio.dBFS
        
        # 计算需要增加的分贝数
        change_in_dBFS = target_dBFS - current_dBFS
        
        # 调整音量
        normalized_audio = audio.apply_gain(change_in_dBFS)
        
        return normalized_audio
    
    def _add_background_music(self, audio):
        """
        为音频添加背景音乐
        audio: AudioSegment 主音频
        """
        try:
            # 从assets目录获取所有mp3文件作为可能的背景音乐
            bg_music_files = []
            for file in os.listdir('assets'):
                if file.endswith('.mp3'):
                    bg_music_files.append(os.path.join('assets', file))
            
            # 如果没有找到背景音乐文件，返回原始音频
            if not bg_music_files:
                logger.warning("未找到背景音乐文件")
                return audio
            
            # 随机选择一个背景音乐
            bg_music_path = random.choice(bg_music_files)
            logger.info(f"使用背景音乐: {bg_music_path}")
            
            # 加载背景音乐
            bg_music = AudioSegment.from_mp3(bg_music_path)
            
            # 调整背景音乐音量（降低20分贝，使其不遮盖主音频）
            bg_music = bg_music - 20
            
            # 循环背景音乐以匹配主音频长度
            while len(bg_music) < len(audio):
                bg_music += bg_music
            
            # 剪切背景音乐以匹配主音频长度
            bg_music = bg_music[:len(audio)]
            
            # 为背景音乐添加淡入淡出效果
            bg_music = bg_music.fade_in(2000).fade_out(2000)
            
            # 混合音频（叠加背景音乐）
            final_audio = audio.overlay(bg_music)
            
            return final_audio
        
        except Exception as e:
            logger.error(f"添加背景音乐时出错: {str(e)}")
            # 出错时返回原始音频
            return audio
    
    def _apply_quality_settings(self, audio):
        """根据配置应用不同的音频质量设置"""
        if self.audio_quality == 'high':
            # 高质量: 192kbps, 44.1kHz
            return audio.set_frame_rate(44100)
        elif self.audio_quality == 'medium':
            # 中等质量: 128kbps, 32kHz
            return audio.set_frame_rate(32000)
        else:
            # 低质量: 96kbps, 22.05kHz
            return audio.set_frame_rate(22050)
    
    def _cleanup_temp_files(self, file_paths):
        """清理临时文件"""
        for path in file_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                logger.warning(f"清理临时文件时出错: {str(e)}")
    
    def add_background_music(self, 
                           voice_path: str, 
                           music_path: str,
                           output_path: Optional[str] = None,
                           music_volume: float = 0.3) -> str:
        """添加背景音乐
        
        Args:
            voice_path: 语音文件路径
            music_path: 背景音乐文件路径
            output_path: 输出文件路径，如果为None则自动生成
            music_volume: 背景音乐音量（0-1）
            
        Returns:
            输出文件路径
        """
        try:
            # 加载语音和音乐
            voice, voice_sr = librosa.load(voice_path, sr=None)
            music, music_sr = librosa.load(music_path, sr=None)
            
            # 确保采样率一致
            if voice_sr != music_sr:
                music = librosa.resample(music, orig_sr=music_sr, target_sr=voice_sr)
            
            # 调整音乐长度以匹配语音
            if len(music) < len(voice):
                # 循环音乐直到长度足够
                music = np.tile(music, int(np.ceil(len(voice) / len(music))))
            music = music[:len(voice)]
            
            # 调整音乐音量
            music = music * music_volume
            
            # 混合音频
            mixed = voice + music
            
            # 归一化
            mixed = mixed / np.max(np.abs(mixed))
            
            # 生成输出路径
            if output_path is None:
                filename = os.path.basename(voice_path)
                name, ext = os.path.splitext(filename)
                output_path = os.path.join(self.output_dir, f"{name}_with_music{ext}")
            
            # 保存混合后的音频
            sf.write(output_path, mixed, voice_sr)
            
            self.logger.info(f"成功添加背景音乐，保存到: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"添加背景音乐失败: {str(e)}")
            return voice_path
    
    def process_podcast(self, 
                       voice_path: str,
                       category: str = "business",
                       music_volume: float = 0.3) -> str:
        """处理播客音频，添加背景音乐
        
        Args:
            voice_path: 语音文件路径
            category: 背景音乐类别
            music_volume: 背景音乐音量（0-1）
            
        Returns:
            处理后的音频文件路径
        """
        try:
            # 获取背景音乐
            music_list = self.music_crawler.load_music_info(category)
            if not music_list:
                self.logger.warning(f"没有找到 {category} 类别的背景音乐")
                return voice_path
            
            # 随机选择一首音乐
            music = np.random.choice(music_list)
            music_path = music['file_path']
            
            # 添加背景音乐
            return self.add_background_music(voice_path, music_path, music_volume=music_volume)
            
        except Exception as e:
            self.logger.error(f"处理播客音频失败: {str(e)}")
            return voice_path 