import logging
import os
from datetime import datetime

# 创建日志目录
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# 配置日志格式
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# 创建日志文件路径
log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")

# 配置日志记录器
logger = logging.getLogger('zaka-podcast')
logger.setLevel(logging.INFO)

# 创建文件处理器
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(log_format))

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(log_format))

# 添加处理器到日志记录器
logger.addHandler(file_handler)
logger.addHandler(console_handler) 