import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 打印 Jamendo API 凭据
print("Jamendo Client ID:", os.getenv('JAMENDO_CLIENT_ID'))
print("Jamendo Client Secret:", os.getenv('JAMENDO_CLIENT_SECRET')) 