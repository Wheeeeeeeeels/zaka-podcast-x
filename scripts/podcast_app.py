import streamlit as st
import os
import tempfile
from audio_processor import AudioProcessor
from config.music_crawler import MusicCrawler
import openai
from dotenv import load_dotenv

# 添加 FFmpeg 路径到系统环境变量
ffmpeg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ffmpeg', 'bin')
os.environ['PATH'] = ffmpeg_path + os.pathsep + os.environ['PATH']

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="播客制作工具",
    page_icon="🎙️",
    layout="wide"
)

# 初始化工具
@st.cache_resource
def get_audio_processor():
    return AudioProcessor()

@st.cache_resource
def get_music_crawler():
    return MusicCrawler()

audio_processor = get_audio_processor()
music_crawler = get_music_crawler()

# 侧边栏
st.sidebar.title("设置")
client_id = st.sidebar.text_input("Jamendo Client ID")
client_secret = st.sidebar.text_input("Jamendo Client Secret", type="password")
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

if client_id and client_secret:
    os.environ["JAMENDO_CLIENT_ID"] = client_id
    os.environ["JAMENDO_CLIENT_SECRET"] = client_secret

if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
    openai.api_key = openai_api_key

# 主页面
st.title("🎙️ 播客制作工具")

# 创建标签页
tab1, tab2, tab3 = st.tabs(["播客生成", "音乐管理", "音频处理"])

# 播客生成标签页
with tab1:
    st.header("播客生成")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 选择要模仿的播客风格
        podcast_style = st.selectbox(
            "选择要模仿的播客风格",
            ["姜思达", "梁文道", "李诞", "马东", "许知远"],
            key="podcast_style"
        )
        
        # 输入主题
        topic = st.text_input("输入播客主题", placeholder="例如：现代人的孤独感")
        
        # 输入时长
        duration = st.slider("播客时长（分钟）", 1, 30, 3)
        
        # 选择音乐风格
        music_style = st.selectbox(
            "背景音乐风格",
            ["relaxing", "business", "energetic", "motivational"],
            format_func=lambda x: {
                "relaxing": "轻松",
                "business": "商务",
                "energetic": "活力",
                "motivational": "励志"
            }[x],
            key="generate_music_style"
        )
        
        if st.button("生成播客"):
            if not topic:
                st.error("请输入播客主题")
            elif not openai_api_key:
                st.error("请输入 OpenAI API Key")
            else:
                with st.spinner("正在生成播客脚本..."):
                    try:
                        # 生成播客脚本
                        prompt = f"""
                        请模仿{podcast_style}的播客风格，创作一个关于{topic}的播客脚本。
                        要求：
                        1. 时长约{duration}分钟
                        2. 保持{podcast_style}的语言风格和表达方式
                        3. 包含开场白、主体内容和结束语
                        4. 在适当位置标注[音乐渐入]、[音乐过渡]、[音乐渐强]、[音乐渐弱]、[音乐结束]
                        5. 语言要自然流畅，有个人特色
                        """
                        
                        # 使用旧版 API
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "你是一个专业的播客脚本创作助手。"},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.7,
                            max_tokens=2000
                        )
                        
                        script = response.choices[0].message.content
                        
                        # 保存脚本到会话状态
                        st.session_state.script = script
                        
                        # 下载音乐
                        with st.spinner("正在下载背景音乐..."):
                            music_list = music_crawler.crawl_jamendo(music_style, 1)
                            if music_list:
                                st.session_state.music_path = music_list[0]['path']
                                st.success("背景音乐下载成功")
                            else:
                                st.error("下载背景音乐失败")
                        
                    except Exception as e:
                        st.error(f"生成播客时出错: {str(e)}")
    
    with col2:
        if "script" in st.session_state:
            st.subheader("生成的播客脚本")
            st.text_area("脚本内容", st.session_state.script, height=300)
            
            if st.button("生成音频"):
                if "music_path" not in st.session_state:
                    st.error("请先下载背景音乐")
                else:
                    with st.spinner("正在生成音频..."):
                        try:
                            # 使用 gTTS 生成语音
                            from gtts import gTTS
                            tts = gTTS(text=st.session_state.script, lang='zh-cn')
                            voice_path = "temp_voice.mp3"
                            tts.save(voice_path)
                            
                            # 处理音频
                            output_path = audio_processor.process_audio(
                                voice_path=voice_path,
                                music_path=st.session_state.music_path,
                                music_volume=0.3
                            )
                            
                            # 提供下载链接
                            with open(output_path, "rb") as f:
                                st.download_button(
                                    label="下载播客音频",
                                    data=f,
                                    file_name="podcast.mp3",
                                    mime="audio/mp3"
                                )
                            
                            # 清理临时文件
                            os.unlink(voice_path)
                            
                        except Exception as e:
                            st.error(f"生成音频时出错: {str(e)}")

# 音乐管理标签页
with tab2:
    st.header("音乐管理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.selectbox(
            "音乐类别",
            ["", "business", "relaxing", "energetic", "motivational"],
            format_func=lambda x: {
                "": "请选择类别",
                "business": "商业",
                "relaxing": "放松",
                "energetic": "活力",
                "motivational": "励志"
            }[x],
            key="music_category"
        )
        
        limit = st.number_input("下载数量", min_value=1, max_value=50, value=10)
        
        if st.button("下载音乐"):
            if not category:
                st.error("请选择音乐类别")
            else:
                with st.spinner("正在下载音乐..."):
                    try:
                        music_list = music_crawler.crawl_jamendo(category, limit)
                        if music_list:
                            st.success(f"成功下载 {len(music_list)} 首音乐")
                            st.session_state.music_list = music_list
                        else:
                            st.error("下载音乐失败")
                    except Exception as e:
                        st.error(f"下载音乐时出错: {str(e)}")
    
    with col2:
        st.subheader("已下载的音乐")
        if "music_list" in st.session_state:
            for music in st.session_state.music_list:
                st.write(f"🎵 {music['title']} - {music['artist']}")

# 音频处理标签页
with tab3:
    st.header("音频处理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        voice_file = st.file_uploader("上传语音文件", type=["wav", "mp3"])
        music_file = st.file_uploader("上传背景音乐（可选）", type=["wav", "mp3"])
        
        if not music_file:
            category = st.selectbox(
                "音乐类别",
                ["", "business", "relaxing", "energetic", "motivational"],
                format_func=lambda x: {
                    "": "请选择类别",
                    "business": "商业",
                    "relaxing": "放松",
                    "energetic": "活力",
                    "motivational": "励志"
                }[x],
                key="process_category"
            )
        
        volume = st.slider("背景音乐音量", 0.0, 1.0, 0.3, 0.1)
        
        if st.button("开始处理"):
            if not voice_file:
                st.error("请上传语音文件")
            else:
                with st.spinner("正在处理音频..."):
                    try:
                        # 保存上传的文件到临时目录
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as voice_temp:
                            voice_temp.write(voice_file.getvalue())
                            voice_path = voice_temp.name
                        
                        music_path = None
                        if music_file:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as music_temp:
                                music_temp.write(music_file.getvalue())
                                music_path = music_temp.name
                        
                        # 处理音频
                        output_path = audio_processor.process_audio(
                            voice_path=voice_path,
                            music_path=music_path,
                            category=category if not music_path else None,
                            music_volume=volume
                        )
                        
                        # 提供下载链接
                        with open(output_path, "rb") as f:
                            st.download_button(
                                label="下载处理后的音频",
                                data=f,
                                file_name="processed_audio.mp3",
                                mime="audio/mp3"
                            )
                        
                        # 清理临时文件
                        os.unlink(voice_path)
                        if music_path:
                            os.unlink(music_path)
                        
                    except Exception as e:
                        st.error(f"处理音频时出错: {str(e)}")
    
    with col2:
        st.subheader("处理说明")
        st.markdown("""
        1. 上传语音文件（必选）
        2. 上传背景音乐（可选）
           - 如果不上传背景音乐，可以选择音乐类别自动下载
        3. 调整背景音乐音量
        4. 点击"开始处理"按钮
        5. 处理完成后下载结果
        """) 