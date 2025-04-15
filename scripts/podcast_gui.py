import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import logging
from audio_processor import AudioProcessor
from config.music_crawler import MusicCrawler

class PodcastGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("播客制作工具")
        self.root.geometry("800x600")
        
        # 初始化工具
        self.audio_processor = AudioProcessor()
        self.music_crawler = MusicCrawler()
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建标签页
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建各个标签页
        self.create_music_tab()
        self.create_process_tab()
        self.create_settings_tab()
        
        # 配置网格权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
    
    def create_music_tab(self):
        """创建音乐管理标签页"""
        music_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(music_frame, text="音乐管理")
        
        # 音乐类别选择
        ttk.Label(music_frame, text="音乐类别:").grid(row=0, column=0, sticky=tk.W)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(music_frame, textvariable=self.category_var)
        self.category_combo['values'] = ['business', 'relaxing', 'energetic', 'motivational']
        self.category_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # 下载数量
        ttk.Label(music_frame, text="下载数量:").grid(row=1, column=0, sticky=tk.W)
        self.limit_var = tk.StringVar(value="10")
        ttk.Entry(music_frame, textvariable=self.limit_var).grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        # 下载按钮
        ttk.Button(music_frame, text="下载音乐", command=self.download_music).grid(row=2, column=0, columnspan=2, pady=5)
        
        # 音乐列表
        ttk.Label(music_frame, text="已下载的音乐:").grid(row=3, column=0, columnspan=2, sticky=tk.W)
        self.music_listbox = tk.Listbox(music_frame, height=10)
        self.music_listbox.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        music_frame.columnconfigure(1, weight=1)
        music_frame.rowconfigure(4, weight=1)
    
    def create_process_tab(self):
        """创建音频处理标签页"""
        process_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(process_frame, text="音频处理")
        
        # 语音文件选择
        ttk.Label(process_frame, text="语音文件:").grid(row=0, column=0, sticky=tk.W)
        self.voice_path_var = tk.StringVar()
        ttk.Entry(process_frame, textvariable=self.voice_path_var).grid(row=0, column=1, sticky=(tk.W, tk.E))
        ttk.Button(process_frame, text="浏览", command=self.browse_voice_file).grid(row=0, column=2)
        
        # 背景音乐选择
        ttk.Label(process_frame, text="背景音乐:").grid(row=1, column=0, sticky=tk.W)
        self.music_path_var = tk.StringVar()
        ttk.Entry(process_frame, textvariable=self.music_path_var).grid(row=1, column=1, sticky=(tk.W, tk.E))
        ttk.Button(process_frame, text="浏览", command=self.browse_music_file).grid(row=1, column=2)
        
        # 音乐类别选择
        ttk.Label(process_frame, text="音乐类别:").grid(row=2, column=0, sticky=tk.W)
        self.process_category_var = tk.StringVar()
        self.process_category_combo = ttk.Combobox(process_frame, textvariable=self.process_category_var)
        self.process_category_combo['values'] = ['business', 'relaxing', 'energetic', 'motivational']
        self.process_category_combo.grid(row=2, column=1, sticky=(tk.W, tk.E))
        
        # 音量控制
        ttk.Label(process_frame, text="背景音乐音量:").grid(row=3, column=0, sticky=tk.W)
        self.volume_var = tk.DoubleVar(value=0.3)
        self.volume_scale = ttk.Scale(process_frame, from_=0, to=1, variable=self.volume_var)
        self.volume_scale.grid(row=3, column=1, sticky=(tk.W, tk.E))
        
        # 处理按钮
        ttk.Button(process_frame, text="开始处理", command=self.process_audio).grid(row=4, column=0, columnspan=3, pady=5)
        
        # 配置网格权重
        process_frame.columnconfigure(1, weight=1)
    
    def create_settings_tab(self):
        """创建设置标签页"""
        settings_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(settings_frame, text="设置")
        
        # API 设置
        ttk.Label(settings_frame, text="Jamendo API 设置").grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        ttk.Label(settings_frame, text="Client ID:").grid(row=1, column=0, sticky=tk.W)
        self.client_id_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.client_id_var).grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(settings_frame, text="Client Secret:").grid(row=2, column=0, sticky=tk.W)
        self.client_secret_var = tk.StringVar()
        ttk.Entry(settings_frame, textvariable=self.client_secret_var).grid(row=2, column=1, sticky=(tk.W, tk.E))
        
        # 保存设置按钮
        ttk.Button(settings_frame, text="保存设置", command=self.save_settings).grid(row=3, column=0, columnspan=2, pady=5)
        
        # 配置网格权重
        settings_frame.columnconfigure(1, weight=1)
    
    def browse_voice_file(self):
        """浏览语音文件"""
        filename = filedialog.askopenfilename(
            title="选择语音文件",
            filetypes=[("音频文件", "*.wav *.mp3")]
        )
        if filename:
            self.voice_path_var.set(filename)
    
    def browse_music_file(self):
        """浏览背景音乐文件"""
        filename = filedialog.askopenfilename(
            title="选择背景音乐",
            filetypes=[("音频文件", "*.wav *.mp3")]
        )
        if filename:
            self.music_path_var.set(filename)
    
    def download_music(self):
        """下载音乐"""
        category = self.category_var.get()
        limit = int(self.limit_var.get())
        
        if not category:
            messagebox.showerror("错误", "请选择音乐类别")
            return
        
        try:
            music_list = self.music_crawler.crawl_jamendo(category, limit)
            if music_list:
                self.music_listbox.delete(0, tk.END)
                for music in music_list:
                    self.music_listbox.insert(tk.END, f"{music['title']} by {music['artist']}")
                messagebox.showinfo("成功", f"成功下载 {len(music_list)} 首音乐")
            else:
                messagebox.showerror("错误", "下载音乐失败")
        except Exception as e:
            messagebox.showerror("错误", f"下载音乐时出错: {str(e)}")
    
    def process_audio(self):
        """处理音频"""
        voice_path = self.voice_path_var.get()
        music_path = self.music_path_var.get()
        category = self.process_category_var.get()
        volume = self.volume_var.get()
        
        if not voice_path:
            messagebox.showerror("错误", "请选择语音文件")
            return
        
        try:
            output_path = self.audio_processor.process_audio(
                voice_path=voice_path,
                music_path=music_path if music_path else None,
                category=category if not music_path else None,
                music_volume=volume
            )
            messagebox.showinfo("成功", f"处理完成，输出文件：{output_path}")
        except Exception as e:
            messagebox.showerror("错误", f"处理音频时出错: {str(e)}")
    
    def save_settings(self):
        """保存设置"""
        # TODO: 实现设置保存功能
        messagebox.showinfo("提示", "设置已保存")

def main():
    root = tk.Tk()
    app = PodcastGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main() 