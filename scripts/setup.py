import os
import sys
import subprocess
import platform
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_ffmpeg():
    """检查系统是否已安装 FFmpeg"""
    # 首先检查系统 PATH 中的 ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info("FFmpeg 已安装（通过系统 PATH）")
        return True
    except FileNotFoundError:
        # 检查 D:\ffmpeg 目录
        ffmpeg_path = r"D:\ffmpeg\bin\ffmpeg.exe"
        if os.path.exists(ffmpeg_path):
            try:
                subprocess.run([ffmpeg_path, '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                logging.info("FFmpeg 已安装（在 D:\\ffmpeg 目录）")
                return True
            except Exception as e:
                logging.warning(f"检测到 FFmpeg 但无法运行: {str(e)}")
                return False
        logging.warning("未检测到 FFmpeg")
        return False

def install_ffmpeg():
    """根据操作系统安装 FFmpeg"""
    system = platform.system().lower()
    
    if system == 'windows':
        logging.info("Windows 系统 FFmpeg 安装指南：")
        logging.info("1. 访问 https://github.com/BtbN/FFmpeg-Builds/releases")
        logging.info("2. 下载最新版本（ffmpeg-master-latest-win64-gpl.zip）")
        logging.info("3. 解压下载的文件")
        logging.info("4. 将解压后的 bin 目录添加到系统环境变量 PATH 中")
        logging.info("5. 重启终端")
        logging.info("完成上述步骤后，请重新运行此脚本进行验证")
        return False
    
    elif system == 'darwin':  # macOS
        try:
            # 检查是否安装了 Homebrew
            subprocess.run(['brew', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logging.info("正在使用 Homebrew 安装 FFmpeg...")
            subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
            logging.info("FFmpeg 安装成功")
            return True
        except FileNotFoundError:
            logging.error("未找到 Homebrew，请先安装 Homebrew：")
            logging.info("/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            return False
        except subprocess.CalledProcessError as e:
            logging.error(f"安装 FFmpeg 时出错：{str(e)}")
            return False
    
    elif system == 'linux':
        try:
            logging.info("正在更新包列表...")
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
            logging.info("正在安装 FFmpeg...")
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'ffmpeg'], check=True)
            logging.info("FFmpeg 安装成功")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"安装 FFmpeg 时出错：{str(e)}")
            return False
    
    else:
        logging.error(f"不支持的操作系统：{system}")
        return False

def setup_environment():
    """设置环境"""
    if check_ffmpeg():
        logging.info("环境检查完成，FFmpeg 已就绪")
        return True
    
    logging.info("正在安装 FFmpeg...")
    if install_ffmpeg():
        logging.info("FFmpeg 安装成功")
        return True
    else:
        logging.warning("FFmpeg 安装未完成，请按照提示手动安装")
        return False

if __name__ == "__main__":
    setup_environment() 