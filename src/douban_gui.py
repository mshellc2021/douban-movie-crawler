"""
豆瓣电影数据管理工具GUI界面
作者: mshellc
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import subprocess
import os
import json
import time
import requests
from datetime import datetime

class ToolTip:
    """
    悬浮提示工具类
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = self.id = None
        self.x = self.y = 0
        
        # 绑定鼠标事件
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
    
    def enter(self, event=None):
        """鼠标进入时显示提示"""
        self.schedule()
    
    def leave(self, event=None):
        """鼠标离开时隐藏提示"""
        self.unschedule()
        self.hidetip()
    
    def schedule(self):
        """安排显示提示"""
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)
    
    def unschedule(self):
        """取消显示提示"""
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)
    
    def showtip(self):
        """显示提示窗口"""
        if self.tip_window:
            return
        
        # 获取鼠标位置
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 25
        
        # 创建提示窗口
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        # 设置提示样式
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                       background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                       font=('Microsoft YaHei', 9))
        label.pack(ipadx=1)
    
    def hidetip(self):
        """隐藏提示窗口"""
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

class DoubanCrawlerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 豆瓣电影数据管理工具")
        self.root.geometry("1100x750")
        self.root.minsize(1000, 650)
        
        # 设置主题样式
        self.setup_style()
        
        # 设置主窗口背景色
        root.configure(background='#f8f9fa')
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置行列权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=0)
        main_frame.columnconfigure(1, weight=2)  # 日志区域权重增加
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=0)
        
        # 标题区域
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 25), sticky=(tk.W, tk.E))
        
        ttk.Label(title_frame, text="🎬 豆瓣电影数据管理工具", 
                 font=('Microsoft YaHei', 18, 'bold'), foreground="#2c3e50").pack()
        ttk.Label(title_frame, text="专业的豆瓣电影数据采集与管理解决方案", 
                 font=('Microsoft YaHei', 11), foreground="#7f8c8d").pack(pady=(2, 0))
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="📊 控制面板", padding="12")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 12))
        
        # 控制面板行列权重
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        control_frame.rowconfigure(6, weight=1)
        
        # 变量初始化
        self.interval_var = tk.StringVar(value="3600")
        self.retries_var = tk.StringVar(value="3")
        self.timeout_var = tk.StringVar(value="30")
        self.count_var = tk.StringVar(value="20")
        self.start_var = tk.StringVar(value="0")
        self.tags_var = tk.StringVar(value="2025")
        self.enable_schedule_var = tk.BooleanVar(value=False)  # 定时任务开关
        
        # 连接参数分组
        connection_frame = ttk.LabelFrame(control_frame, text="🔗 连接设置", padding="8")
        connection_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 定时任务开关
        ttk.Checkbutton(connection_frame, text="启用定时任务", variable=self.enable_schedule_var, 
                       width=12).grid(row=0, column=0, sticky=tk.W, pady=3)
        ToolTip(ttk.Frame(connection_frame), "启用定时爬取功能，将按照设置的间隔时间自动重复爬取")
        
        ttk.Label(connection_frame, text="爬取间隔(秒):", font=('Microsoft YaHei', 9)).grid(row=1, column=0, sticky=tk.W, pady=3)
        ttk.Entry(connection_frame, textvariable=self.interval_var, width=10, font=('Microsoft YaHei', 9)).grid(row=1, column=1, sticky=tk.W, pady=3, padx=(6, 0))
        
        ttk.Label(connection_frame, text="重试次数:", font=('Microsoft YaHei', 9)).grid(row=2, column=0, sticky=tk.W, pady=3)
        ttk.Entry(connection_frame, textvariable=self.retries_var, width=10, font=('Microsoft YaHei', 9)).grid(row=2, column=1, sticky=tk.W, pady=3, padx=(6, 0))
        
        ttk.Label(connection_frame, text="超时时间(秒):", font=('Microsoft YaHei', 9)).grid(row=3, column=0, sticky=tk.W, pady=3)
        ttk.Entry(connection_frame, textvariable=self.timeout_var, width=10, font=('Microsoft YaHei', 9)).grid(row=3, column=1, sticky=tk.W, pady=3, padx=(6, 0))
        
        # 爬虫参数分组
        crawler_frame = ttk.LabelFrame(control_frame, text="🎯 爬虫参数", padding="8")
        crawler_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(crawler_frame, text="单次请求爬取条数:", font=('Microsoft YaHei', 9)).grid(row=0, column=0, sticky=tk.W, pady=3)
        ttk.Spinbox(crawler_frame, textvariable=self.count_var, width=8, font=('Microsoft YaHei', 9), 
                   from_=1, to=100, increment=1).grid(row=0, column=1, sticky=tk.W, pady=3, padx=(6, 0))
        
        ttk.Label(crawler_frame, text="起始位置:", font=('Microsoft YaHei', 9)).grid(row=1, column=0, sticky=tk.W, pady=3)
        ttk.Entry(crawler_frame, textvariable=self.start_var, width=10, font=('Microsoft YaHei', 9)).grid(row=1, column=1, sticky=tk.W, pady=3, padx=(6, 0))
        
        ttk.Label(crawler_frame, text="电影年份:", font=('Microsoft YaHei', 9)).grid(row=2, column=0, sticky=tk.W, pady=3)
        ttk.Entry(crawler_frame, textvariable=self.tags_var, width=10, font=('Microsoft YaHei', 9)).grid(row=2, column=1, sticky=tk.W, pady=3, padx=(6, 0))
        
        ttk.Label(crawler_frame, text="电影排序:", font=('Microsoft YaHei', 9)).grid(row=3, column=0, sticky=tk.W, pady=3)
        self.sort_var = tk.StringVar(value="R")
        sort_combo = ttk.Combobox(crawler_frame, textvariable=self.sort_var, width=8, font=('Microsoft YaHei', 9),
                                 values=["综合排序", "近期热度", "首映时间", "高分优先"], state="readonly")
        sort_combo.grid(row=3, column=1, sticky=tk.W, pady=3, padx=(6, 0))

        ttk.Label(crawler_frame, text="需要爬取数(0无限制):", font=('Microsoft YaHei', 9)).grid(row=4, column=0, sticky=tk.W, pady=3)
        self.actual_count_var = tk.StringVar(value="0")
        ttk.Entry(crawler_frame, textvariable=self.actual_count_var, width=10, font=('Microsoft YaHei', 9)).grid(row=4, column=1, sticky=tk.W, pady=3, padx=(6, 0))
        
        # 按钮区域 - 使用网格布局节省空间
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(8, 15))
        
        # 第一行按钮 - 核心操作
        self.start_btn = ttk.Button(button_frame, text="🚀 启动", command=self.start_crawler, width=10)
        self.start_btn.grid(row=0, column=0, padx=2, pady=2)
        ToolTip(self.start_btn, "启动豆瓣电影数据爬虫")
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ 停止", command=self.stop_crawler, state=tk.DISABLED, width=10)
        self.stop_btn.grid(row=0, column=1, padx=2, pady=2)
        ToolTip(self.stop_btn, "停止正在运行的爬虫")
        
        self.export_btn = ttk.Button(button_frame, text="📊 导出", command=self.export_to_excel, width=10)
        self.export_btn.grid(row=0, column=2, padx=2, pady=2)
        ToolTip(self.export_btn, "将爬取的数据导出到Excel文件")
        
        # 第二行按钮 - 目录访问
        self.open_data_btn = ttk.Button(button_frame, text="📁 数据", command=self.open_data_dir, width=10)
        self.open_data_btn.grid(row=1, column=0, padx=2, pady=2)
        ToolTip(self.open_data_btn, "打开数据文件目录")
        
        self.open_excel_btn = ttk.Button(button_frame, text="📂 Excel", command=self.open_excel_dir, width=10)
        self.open_excel_btn.grid(row=1, column=1, padx=2, pady=2)
        ToolTip(self.open_excel_btn, "打开Excel导出文件目录")
        
        self.open_images_btn = ttk.Button(button_frame, text="🖼️ 封面", command=self.open_images_dir, width=10)
        self.open_images_btn.grid(row=1, column=2, padx=2, pady=2)
        ToolTip(self.open_images_btn, "打开封面图片目录")
        
        # 第三行按钮 - 图片相关功能
        self.download_covers_btn = ttk.Button(button_frame, text="下载封面", command=self.download_high_res_covers, width=10)
        self.download_covers_btn.grid(row=2, column=0, padx=2, pady=2)
        ToolTip(self.download_covers_btn, "批量下载高清电影封面到images目录")
        
        # 导出选项复选框
        self.include_images_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(button_frame, text="导出包含图片", variable=self.include_images_var, 
                       width=10).grid(row=2, column=1, padx=2, pady=2)
        

        
        # 右侧日志区域
        log_frame = ttk.LabelFrame(main_frame, text="📝 运行日志", padding="10")
        log_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 创建带滚动条的日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, height=18, width=60, 
                                                 font=('Segoe UI Emoji', 10), wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=2, pady=2)
        
        # 日志控制按钮
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(6, 0))
        
        clear_btn = ttk.Button(log_control_frame, text="🗑️ 清空", command=self.clear_log, width=10)
        clear_btn.pack(side=tk.LEFT, padx=(0, 6))
        ToolTip(clear_btn, "清空日志内容")
        
        save_btn = ttk.Button(log_control_frame, text="💾 保存", command=self.save_log, width=10)
        save_btn.pack(side=tk.LEFT)
        ToolTip(save_btn, "保存日志到文件")
        
        # 状态栏
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))
        
        # 创建状态栏容器，包含多个信息区域
        status_container = ttk.Frame(status_frame)
        status_container.pack(fill=tk.X)
        
        # 程序状态区域
        self.status_var = tk.StringVar(value="🟢 就绪")
        status_label = ttk.Label(status_container, textvariable=self.status_var, 
                               font=('Microsoft YaHei', 10), width=15)
        status_label.pack(side=tk.LEFT, padx=(10, 5))
        
        # 分隔线
        ttk.Separator(status_container, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 内存使用情况区域
        self.memory_var = tk.StringVar(value="💾 内存: 计算中...")
        memory_label = ttk.Label(status_container, textvariable=self.memory_var, 
                               font=('Microsoft YaHei', 9), width=20)
        memory_label.pack(side=tk.LEFT, padx=5)
        
        # 分隔线
        ttk.Separator(status_container, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 数据文件统计区域
        self.data_stats_var = tk.StringVar(value="📊 数据文件: 0")
        data_stats_label = ttk.Label(status_container, textvariable=self.data_stats_var, 
                                   font=('Microsoft YaHei', 9), width=15)
        data_stats_label.pack(side=tk.LEFT, padx=5)
        
        # 添加Excel文件统计区域
        ttk.Separator(status_container, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        self.excel_stats_var = tk.StringVar(value="📋 Excel文件: 0")
        excel_stats_label = ttk.Label(status_container, textvariable=self.excel_stats_var, 
                                    font=('Microsoft YaHei', 9), width=15)
        excel_stats_label.pack(side=tk.LEFT, padx=5)
        
        # 分隔线
        ttk.Separator(status_container, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 最后更新时间区域
        self.last_update_var = tk.StringVar(value="📅 最后更新: 从未")
        last_update_label = ttk.Label(status_container, textvariable=self.last_update_var, 
                                    font=('Microsoft YaHei', 9), width=25)
        last_update_label.pack(side=tk.LEFT, padx=5)
        
        # 分隔线
        ttk.Separator(status_container, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 作者信息和免责声明区域
        author_info = "👤 作者: mshellc | 📜 免责声明: 本工具仅供学习研究使用"
        author_label = ttk.Label(status_container, text=author_info, 
                                font=('Microsoft YaHei', 8), foreground="#666666")
        author_label.pack(side=tk.RIGHT, padx=5)
        
        # 设置状态栏整体样式
        status_container.configure(relief=tk.SUNKEN)
        status_container['padding'] = 6
        
        # 启动状态栏更新定时器
        self.update_status_bar()
        
        # 初始化变量
        self.crawler_process = None
        self.is_running = False
        self.log_file = None
        self.after_ids = []  # 存储定时任务的after回调ID
        
        self.load_config()
        self.update_stats()
        self.log("✅ GUI界面初始化完成", "INFO")
    
    def setup_style(self):
        """设置界面样式"""
        style = ttk.Style()
        
        # 设置主题颜色
        style.configure('.', background='#f8f9fa')
        style.configure('TFrame', background='#f8f9fa')
        style.configure('TLabel', background='#f8f9fa', foreground='#2c3e50')
        style.configure('TButton', font=('Segoe UI Emoji', 10), padding=(8, 4))
        style.configure('TLabelframe', font=('Microsoft YaHei', 11, 'bold'), 
                       background='#f8f9fa', foreground='#2c3e50')
        style.configure('TLabelframe.Label', font=('Microsoft YaHei', 11, 'bold'), 
                       background='#f8f9fa', foreground='#2c3e50')
        
        # 按钮样式
        style.map('TButton', 
                 background=[('active', '#3498db'), ('pressed', '#2980b9')])
        
        # 输入框样式
        style.configure('TEntry', font=('Microsoft YaHei', 10), padding=5)
        style.configure('TSpinbox', font=('Microsoft YaHei', 10), padding=5)
        style.configure('TCombobox', font=('Microsoft YaHei', 10))
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.interval_var.set(str(config.get('crawl_interval', 3600)))
                self.retries_var.set(str(config.get('max_retries', 3)))
                self.timeout_var.set(str(config.get('timeout', 30)))
                self.count_var.set(str(config.get('count', 20)))
                self.start_var.set(str(config.get('start', 0)))
                self.tags_var.set(config.get('tags', '2025'))
                
                # 将字母排序参数映射为中文显示
                sort_mapping = {
                    "R": "首映时间",
                    "T": "综合排序", 
                    "S": "高分优先",
                    "U": "近期热度"
                }
                sort_value = config.get('sort', 'R')
                self.sort_var.set(sort_mapping.get(sort_value, "综合排序"))
                
                # 加载实际爬取数量
                self.actual_count_var.set(str(config.get('actual_count', 0)))
                
                self.log("✅ 配置加载成功", "INFO")
        except Exception as e:
            self.log(f"❌ 加载配置失败: {e}", "ERROR")
    
    def save_config(self):
        """保存配置"""
        try:
            # 将中文排序方式映射回字母参数
            sort_mapping = {
                "首映时间": "R",
                "综合排序": "T", 
                "高分优先": "S",
                "近期热度": "U"
            }
            
            config = {
                "crawl_interval": int(self.interval_var.get()),
                "max_retries": int(self.retries_var.get()),
                "timeout": int(self.timeout_var.get()),
                "count": int(self.count_var.get()),
                "start": int(self.start_var.get()),
                "tags": self.tags_var.get(),
                "sort": sort_mapping.get(self.sort_var.get(), "R"),
                "actual_count": int(self.actual_count_var.get() or 0),
                "output_directory": "data",
                "log_level": "INFO"
            }
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.log("✅ 配置已保存", "INFO")
            return True
        except ValueError:
            self.log("❌ 配置保存失败: 请输入有效的数字", "ERROR")
            messagebox.showerror("错误", "请输入有效的数字配置")
            return False
        except Exception as e:
            self.log(f"❌ 配置保存失败: {e}", "ERROR")
            return False
    
    def log(self, message, level="INFO"):
        """添加带时间戳和等级的日志信息 - 优化性能版本"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 处理长链接，自动添加换行符
        processed_message = self._process_long_urls(message)
        log_message = f"[{timestamp}] [{level}] {processed_message}"
        
        # 根据等级设置颜色
        colors = {
            "INFO": "black",
            "ERROR": "red",
            "WARNING": "orange",
            "SUCCESS": "green"
        }
        
        # 批量处理日志更新，避免频繁UI刷新导致抖动
        if not hasattr(self, '_log_buffer'):
            self._log_buffer = []
            self._last_log_update = 0
        
        # 添加到缓冲区
        self._log_buffer.append((log_message, level, colors.get(level, "black")))
        
        # 优化刷新策略：根据日志级别和缓冲区大小动态调整
        current_time = time.time()
        buffer_size = len(self._log_buffer)
        
        # 错误消息立即刷新，普通消息批量处理
        should_flush = (
            level == "ERROR" or  # 错误消息立即显示
            buffer_size >= 15 or  # 缓冲区较大时刷新
            (current_time - self._last_log_update > 0.2 and buffer_size > 0)  # 200ms间隔且有内容
        )
        
        if should_flush:
            self._flush_log_buffer()
    
    def _flush_log_buffer(self):
        """刷新日志缓冲区到UI"""
        if not hasattr(self, '_log_buffer') or not self._log_buffer:
            return
        
        # 批量插入所有缓冲日志
        for log_message, level, color in self._log_buffer:
            self.log_text.insert(tk.END, log_message + "\n")
            
            # 设置颜色
            start_index = self.log_text.index("end-2l")
            end_index = self.log_text.index("end-1l")
            self.log_text.tag_add(level, start_index, end_index)
            self.log_text.tag_config(level, foreground=color)
            
            # 保存到日志文件
            if self.log_file is None:
                log_dir = "logs"
                os.makedirs(log_dir, exist_ok=True)
                log_filename = f"douban_gui_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                self.log_file = os.path.join(log_dir, log_filename)
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + "\n")
        
        # 滚动到最后
        self.log_text.see(tk.END)
        
        # 更新状态栏为就绪状态
        self.status_var.set("🟢 就绪")
        
        # 清空缓冲区并更新时间戳
        self._log_buffer.clear()
        self._last_log_update = time.time()
    
    def update_status_bar(self):
        """更新状态栏信息"""
        try:
            # 检查psutil是否可用
            try:
                import psutil
                memory = psutil.virtual_memory()
                memory_usage = f"内存使用: {memory.percent}%"
                
                # 获取当前进程内存使用
                process = psutil.Process()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                self.memory_var.set(f"💾 内存: {memory_mb:.1f} MB")
                
            except ImportError:
                # psutil不可用，使用简化版本
                memory_usage = "内存: 运行中"
                self.memory_var.set("💾 内存: 运行中")
            except Exception:
                memory_usage = "内存: N/A"
                self.memory_var.set("💾 内存: N/A")
            
            # 获取当前时间
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 更新内存信息，但不覆盖状态显示
            # 状态栏主状态由其他方法控制，这里只更新内存和时间信息
            
        except Exception as e:
            # 异常处理，避免无限递归
            pass
        
        # 30秒后再次更新（大幅降低更新频率）
        self.root.after(30000, self.update_status_bar)
    
    def _process_long_urls(self, message):
        """处理消息中的长链接，自动添加换行符"""
        import re
        
        # 改进的URL正则表达式，更准确地匹配URL
        url_pattern = r'https?:\/\/[^\s<>"\']+'
        
        def insert_newlines(url):
            """在URL中每80个字符插入一个换行符"""
            if len(url) > 80:
                # 每80个字符插入一个换行符和缩进
                parts = []
                for i in range(0, len(url), 80):
                    part = url[i:i+80]
                    if i > 0:
                        part = " " * 25 + part  # 添加缩进
                    parts.append(part)
                return "\n".join(parts)
            return url
        
        # 替换消息中的所有URL
        processed_message = re.sub(url_pattern, lambda match: insert_newlines(match.group()), message)
        
        return processed_message
    
    def start_crawler(self):
        """启动爬虫"""
        if self.is_running:
            messagebox.showwarning("警告", "爬虫已经在运行中")
            return
        
        # 保存配置，如果失败则返回
        if not self.save_config():
            return
        
        # 检查是否启用定时任务
        if self.enable_schedule_var.get():
            self.log("⏰ 定时任务已启用，将按照设定间隔自动爬取", "INFO")
        else:
            self.log("🚀 启动单次爬虫任务", "INFO")
        
        def run_crawler():
            self.is_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.export_btn.config(state=tk.DISABLED)
            self.open_data_btn.config(state=tk.DISABLED)
            
            self.log("🚀 正在启动爬虫...", "INFO")
            
            try:
                # 使用subprocess运行爬虫（二进制模式读取，避免解码阻塞）
                self.crawler_process = subprocess.Popen(
                    ['python', 'src\\douban_crawler.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.getcwd()
                )
                
                # 实时输出标准输出
                def read_stdout():
                    while self.is_running and self.crawler_process:
                        try:
                            # 读取二进制数据
                            raw_line = self.crawler_process.stdout.readline()
                            if not raw_line:
                                # 检查进程是否已经结束
                                if self.crawler_process.poll() is not None:
                                    break
                                continue
                            # 解码为UTF-8，尝试多种解码方式
                            try:
                                line = raw_line.decode('utf-8').strip()
                            except UnicodeDecodeError:
                                # 如果UTF-8失败，尝试GBK编码（Windows中文环境）
                                try:
                                    line = raw_line.decode('gbk').strip()
                                except UnicodeDecodeError:
                                    # 如果都失败，使用忽略错误的方式
                                    line = raw_line.decode('utf-8', errors='ignore').strip()
                            if line:
                                self.root.after(0, self.log, line, "INFO")
                        except Exception as e:
                            # 如果发生异常，检查进程是否还在运行
                            if not self.is_running or self.crawler_process is None or self.crawler_process.poll() is not None:
                                break
                            self.root.after(0, self.log, f"读取输出错误: {e}", "ERROR")
                            break
                
                # 实时输出标准错误
                def read_stderr():
                    while self.is_running and self.crawler_process:
                        try:
                            # 读取二进制数据
                            raw_line = self.crawler_process.stderr.readline()
                            if not raw_line:
                                # 检查进程是否已经结束
                                if self.crawler_process.poll() is not None:
                                    break
                                continue
                            # 解码为UTF-8，尝试多种解码方式
                            try:
                                line = raw_line.decode('utf-8').strip()
                            except UnicodeDecodeError:
                                # 如果UTF-8失败，尝试GBK编码（Windows中文环境）
                                try:
                                    line = raw_line.decode('gbk').strip()
                                except UnicodeDecodeError:
                                    # 如果都失败，使用忽略错误的方式
                                    line = raw_line.decode('utf-8', errors='ignore').strip()
                            if line:
                                # 解析日志级别，根据实际内容确定日志等级
                                log_level = "ERROR"  # 默认设为ERROR
                                if "INFO" in line:
                                    log_level = "INFO"
                                elif "WARNING" in line:
                                    log_level = "WARNING"
                                elif "ERROR" in line:
                                    log_level = "ERROR"
                                self.root.after(0, self.log, line, log_level)
                        except Exception as e:
                            # 如果发生异常，检查进程是否还在运行
                            if not self.is_running or self.crawler_process is None or self.crawler_process.poll() is not None:
                                break
                            self.root.after(0, self.log, f"读取错误输出错误: {e}", "ERROR")
                            break
                
                # 启动读取线程
                stdout_thread = threading.Thread(target=read_stdout, daemon=True)
                stderr_thread = threading.Thread(target=read_stderr, daemon=True)
                stdout_thread.start()
                stderr_thread.start()
                
                # 等待进程结束并获取返回码
                returncode = self.crawler_process.wait()
                
                if returncode == 0:
                    self.log("✅ 爬虫任务完成", "SUCCESS")
                    # 如果启用了定时任务，等待指定间隔后重新启动
                    if self.enable_schedule_var.get() and self.is_running:
                        interval = int(self.interval_var.get())
                        self.log(f"⏰ 等待 {interval} 秒后重新启动爬虫...", "INFO")
                        # 使用after方法代替time.sleep，避免GUI卡死
                        after_id = self.root.after(interval * 1000, self._schedule_restart)
                        self.after_ids.append(after_id)
                else:
                    self.log(f"❌ 爬虫异常退出，返回码: {returncode}", "ERROR")
                    # 如果启用了定时任务，等待指定间隔后重新启动
                    if self.enable_schedule_var.get() and self.is_running:
                        interval = int(self.interval_var.get())
                        self.log(f"⏰ 等待 {interval} 秒后重新启动爬虫...", "INFO")
                        # 使用after方法代替time.sleep，避免GUI卡死
                        after_id = self.root.after(interval * 1000, self._schedule_restart)
                        self.after_ids.append(after_id)
                
            except Exception as e:
                self.root.after(0, self.log, f"❌ 爬虫运行错误: {e}", "ERROR")
                # 如果启用了定时任务，等待指定间隔后重新启动
                if self.enable_schedule_var.get() and self.is_running:
                    interval = int(self.interval_var.get())
                    self.log(f"⏰ 等待 {interval} 秒后重新启动爬虫...", "INFO")
                    # 使用after方法代替time.sleep，避免GUI卡死
                    after_id = self.root.after(interval * 1000, self._schedule_restart)
                    self.after_ids.append(after_id)
            finally:
                if not self.enable_schedule_var.get():
                    self.root.after(0, self.stop_crawler_ui)
                self.root.after(0, self.update_stats)
        
        # 在新线程中运行爬虫
        threading.Thread(target=run_crawler, daemon=True).start()
    
    def _start_crawler_direct(self):
        """直接启动爬虫（用于定时任务重启，不检查is_running状态）"""
        # 保存配置，如果失败则返回
        if not self.save_config():
            return
        
        # 检查是否启用定时任务
        if self.enable_schedule_var.get():
            self.log("⏰ 定时任务已启用，将按照设定间隔自动爬取", "INFO")
        else:
            self.log("🚀 启动单次爬虫任务", "INFO")
        
        def run_crawler():
            self.is_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.export_btn.config(state=tk.DISABLED)
            self.open_data_btn.config(state=tk.DISABLED)
            
            self.log("🚀 正在启动爬虫...", "INFO")
            
            try:
                # 使用subprocess运行爬虫（二进制模式读取，避免解码阻塞）
                self.crawler_process = subprocess.Popen(
                    ['python', 'src\\douban_crawler.py'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.getcwd()
                )
                
                # 实时输出标准输出
                def read_stdout():
                    while self.is_running and self.crawler_process:
                        try:
                            # 读取二进制数据
                            raw_line = self.crawler_process.stdout.readline()
                            if not raw_line:
                                # 检查进程是否已经结束
                                if self.crawler_process.poll() is not None:
                                    break
                                continue
                            # 解码为UTF-8，尝试多种解码方式
                            try:
                                line = raw_line.decode('utf-8').strip()
                            except UnicodeDecodeError:
                                # 如果UTF-8失败，尝试GBK编码（Windows中文环境）
                                try:
                                    line = raw_line.decode('gbk').strip()
                                except UnicodeDecodeError:
                                    # 如果都失败，使用忽略错误的方式
                                    line = raw_line.decode('utf-8', errors='ignore').strip()
                            if line:
                                self.root.after(0, self.log, line, "INFO")
                        except Exception as e:
                            # 如果发生异常，检查进程是否还在运行
                            if not self.is_running or self.crawler_process is None or self.crawler_process.poll() is not None:
                                break
                            self.root.after(0, self.log, f"读取输出错误: {e}", "ERROR")
                            break
                
                # 实时输出标准错误
                def read_stderr():
                    while self.is_running and self.crawler_process:
                        try:
                            # 读取二进制数据
                            raw_line = self.crawler_process.stderr.readline()
                            if not raw_line:
                                # 检查进程是否已经结束
                                if self.crawler_process.poll() is not None:
                                    break
                                continue
                            # 解码为UTF-8，尝试多种解码方式
                            try:
                                line = raw_line.decode('utf-8').strip()
                            except UnicodeDecodeError:
                                # 如果UTF-8失败，尝试GBK编码（Windows中文环境）
                                try:
                                    line = raw_line.decode('gbk').strip()
                                except UnicodeDecodeError:
                                    # 如果都失败，使用忽略错误的方式
                                    line = raw_line.decode('utf-8', errors='ignore').strip()
                            if line:
                                # 解析日志级别，根据实际内容确定日志等级
                                log_level = "ERROR"  # 默认设为ERROR
                                if "INFO" in line:
                                    log_level = "INFO"
                                elif "WARNING" in line:
                                    log_level = "WARNING"
                                elif "ERROR" in line:
                                    log_level = "ERROR"
                                self.root.after(0, self.log, line, log_level)
                        except Exception as e:
                            # 如果发生异常，检查进程是否还在运行
                            if not self.is_running or self.crawler_process is None or self.crawler_process.poll() is not None:
                                break
                            self.root.after(0, self.log, f"读取错误输出错误: {e}", "ERROR")
                            break
                
                # 启动读取线程
                stdout_thread = threading.Thread(target=read_stdout, daemon=True)
                stderr_thread = threading.Thread(target=read_stderr, daemon=True)
                stdout_thread.start()
                stderr_thread.start()
                
                # 等待进程结束并获取返回码
                returncode = self.crawler_process.wait()
                
                if returncode == 0:
                    self.log("✅ 爬虫任务完成", "SUCCESS")
                    # 如果启用了定时任务，等待指定间隔后重新启动
                    if self.enable_schedule_var.get() and self.is_running:
                        interval = int(self.interval_var.get())
                        self.log(f"⏰ 等待 {interval} 秒后重新启动爬虫...", "INFO")
                        # 使用after方法代替time.sleep，避免GUI卡死
                        self.root.after(interval * 1000, self._schedule_restart)
                else:
                    self.log(f"❌ 爬虫异常退出，返回码: {returncode}", "ERROR")
                    # 如果启用了定时任务，等待指定间隔后重新启动
                    if self.enable_schedule_var.get() and self.is_running:
                        interval = int(self.interval_var.get())
                        self.log(f"⏰ 等待 {interval} 秒后重新启动爬虫...", "INFO")
                        # 使用after方法代替time.sleep，避免GUI卡死
                        self.root.after(interval * 1000, self._schedule_restart)
                
            except Exception as e:
                self.root.after(0, self.log, f"❌ 爬虫运行错误: {e}", "ERROR")
                # 如果启用了定时任务，等待指定间隔后重新启动
                if self.enable_schedule_var.get() and self.is_running:
                    interval = int(self.interval_var.get())
                    self.log(f"⏰ 等待 {interval} 秒后重新启动爬虫...", "INFO")
                    # 使用after方法代替time.sleep，避免GUI卡死
                    self.root.after(interval * 1000, self._schedule_restart)
            finally:
                if not self.enable_schedule_var.get():
                    self.root.after(0, self.stop_crawler_ui)
                self.root.after(0, self.update_stats)
        
        # 在新线程中运行爬虫
        threading.Thread(target=run_crawler, daemon=True).start()
    
    def stop_crawler(self):
        """停止爬虫"""
        if not self.is_running:
            messagebox.showinfo("信息", "爬虫未在运行")
            return
        
        self.log("🛑 正在停止爬虫...", "INFO")
        self.is_running = False
        
        # 如果启用了定时任务，取消所有待定的定时重启
        if self.enable_schedule_var.get():
            # 取消所有after回调（包括可能的定时重启）
            for after_id in self.after_ids:
                self.root.after_cancel(after_id)
            self.after_ids.clear()
        
        if self.crawler_process:
            try:
                self.crawler_process.terminate()
                self.crawler_process.wait(timeout=5)
            except Exception as e:
                self.log(f"❌ 停止爬虫时发生错误: {e}", "ERROR")
        
        self.stop_crawler_ui()
    
    def stop_crawler_ui(self):
        """停止爬虫的UI更新"""
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.NORMAL)
        self.open_data_btn.config(state=tk.NORMAL)
        self.is_running = False
        self.crawler_process = None
        self.log("🟢 爬虫已停止", "INFO")
    
    def _schedule_restart(self):
        """定时任务重启方法"""
        # 检查定时任务是否仍然启用，而不是检查is_running状态
        if self.enable_schedule_var.get():
            # 直接启动爬虫，不检查is_running状态（因为这是定时重启）
            after_id = self.root.after(0, self._start_crawler_direct)
            self.after_ids.append(after_id)
    
    def export_to_excel(self):
        """导出数据到Excel"""
        try:
            include_images = self.include_images_var.get()
            
            # 禁用导出按钮，防止重复点击
            self.export_btn.config(state=tk.DISABLED)
            
            if include_images:
                self.log("📊 正在导出数据到Excel（包含封面图片）...", "INFO")
                cmd = ['python', 'src\\export_to_excel.py', '--progress']
            else:
                self.log("📊 正在导出数据到Excel（仅封面链接）...", "INFO")
                cmd = ['python', 'src\\export_to_excel.py', '--no-images', '--progress']
            
            # 在新线程中运行导出进程
            threading.Thread(target=self._run_export_process, args=(cmd,), daemon=True).start()
            
        except Exception as e:
            self.log(f"❌ 导出过程中发生错误: {e}", "ERROR")
            messagebox.showerror("错误", f"导出失败: {e}")
            self.export_btn.config(state=tk.NORMAL)
    
    def _run_export_process(self, cmd):
        """运行导出进程并实时显示进度"""
        try:
            # 创建子进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd(),
                bufsize=1,
                universal_newlines=True
            )
            
            # 实时读取输出
            def read_output():
                while process.poll() is None:  # 进程还在运行时读取
                    line = process.stdout.readline()
                    if not line:
                        break
                    line = line.strip()
                    # 处理所有输出信息，包括进度和普通信息
                    self.root.after(0, self.log, line, "INFO")
            
            # 实时读取错误
            def read_error():
                while process.poll() is None:  # 进程还在运行时读取
                    line = process.stderr.readline()
                    if not line:
                        break
                    line = line.strip()
                    self.root.after(0, self.log, line, "ERROR")
            
            # 启动读取线程
            stdout_thread = threading.Thread(target=read_output, daemon=True)
            stderr_thread = threading.Thread(target=read_error, daemon=True)
            stdout_thread.start()
            stderr_thread.start()
            
            # 等待进程完成
            process.wait()
            
            # 检查返回码
            if process.returncode == 0:
                self.root.after(0, self.log, "✅ Excel导出成功", "SUCCESS")
                # 强制刷新日志缓冲区，确保所有日志都显示
                self.root.after(0, self._flush_log_buffer)
                self.root.after(0, lambda: messagebox.showinfo("成功", "数据已成功导出到Excel文件"))
            else:
                self.root.after(0, self.log, f"❌ Excel导出失败，返回码: {process.returncode}", "ERROR")
                # 强制刷新日志缓冲区，确保所有日志都显示
                self.root.after(0, self._flush_log_buffer)
                self.root.after(0, lambda: messagebox.showerror("错误", f"导出失败，返回码: {process.returncode}"))
            
        except Exception as e:
            self.root.after(0, self.log, f"❌ 导出过程中发生错误: {e}", "ERROR")
            self.root.after(0, lambda: messagebox.showerror("错误", f"导出失败: {e}"))
        finally:
            # 重新启用导出按钮
            self.root.after(0, lambda: self.export_btn.config(state=tk.NORMAL))
    
    def open_data_dir(self):
        """打开数据目录"""
        try:
            data_dir = os.path.abspath('data')
            if os.path.exists(data_dir):
                os.startfile(data_dir)
                self.log("📁 已打开数据目录", "INFO")
            else:
                self.log("❌ 数据目录不存在", "WARNING")
                messagebox.showwarning("警告", "数据目录不存在")
        except Exception as e:
            self.log(f"❌ 打开数据目录失败: {e}", "ERROR")
    
    def open_excel_dir(self):
        """打开Excel目录"""
        try:
            excel_dir = os.path.abspath('exports')
            if os.path.exists(excel_dir):
                os.startfile(excel_dir)
                self.log("📂 已打开Excel目录", "INFO")
            else:
                self.log("❌ Excel目录不存在", "WARNING")
                messagebox.showwarning("警告", "Excel目录不存在，请先导出Excel文件")
        except Exception as e:
            self.log(f"❌ 打开Excel目录失败: {e}", "ERROR")

    def open_images_dir(self):
        """打开封面图片目录"""
        try:
            images_dir = os.path.abspath('images')
            if os.path.exists(images_dir):
                os.startfile(images_dir)
                self.log("🖼️ 已打开封面图片目录", "INFO")
            else:
                self.log("❌ 封面图片目录不存在", "WARNING")
                messagebox.showwarning("警告", "封面图片目录不存在，请先下载封面图片")
        except Exception as e:
            self.log(f"❌ 打开封面图片目录失败: {e}", "ERROR")

    def download_high_res_covers(self):
        """批量下载高清电影封面"""
        # 在新线程中执行下载操作，避免阻塞GUI界面
        threading.Thread(target=self._download_covers_thread, daemon=True).start()
    
    def _download_covers_thread(self):
        """下载封面的线程函数"""
        try:
            # 创建images目录
            images_dir = 'images'
            os.makedirs(images_dir, exist_ok=True)
            
            self.root.after(0, lambda: self.log("🖼️ 开始批量下载高清电影封面...", "INFO"))
            
            # 获取所有数据文件
            data_dir = 'data'
            if not os.path.exists(data_dir):
                self.root.after(0, lambda: self.log("❌ 数据目录不存在，请先爬取数据", "ERROR"))
                self.root.after(0, lambda: messagebox.showerror("错误", "数据目录不存在，请先爬取数据"))
                return
            
            json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
            if not json_files:
                self.root.after(0, lambda: self.log("❌ 没有找到数据文件", "ERROR"))
                self.root.after(0, lambda: messagebox.showerror("错误", "没有找到数据文件"))
                return
            
            total_downloaded = 0
            total_skipped = 0
            total_failed = 0
            
            for json_file in json_files:
                file_path = os.path.join(data_dir, json_file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    movies = data.get('items', [])
                    for movie in movies:
                        # 获取电影标题和ID
                        title = movie.get('title', '未知电影')
                        movie_id = movie.get('id', '未知ID')
                        
                        # 获取高清封面链接
                        pic = movie.get('pic', {})
                        large_url = pic.get('large')
                        
                        if not large_url:
                            continue
                        
                        # 生成文件名（电影名+ID）
                        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        filename = f"{safe_title}_{movie_id}.jpg"
                        filepath = os.path.join(images_dir, filename)
                        
                        # 检查文件是否已存在
                        if os.path.exists(filepath):
                            self.root.after(0, lambda f=filename: self.log(f"⏭️ 封面已存在，跳过: {f}", "INFO"))
                            total_skipped += 1
                            continue
                        
                        # 下载封面
                        try:
                            response = requests.get(large_url, timeout=30)
                            response.raise_for_status()
                            
                            with open(filepath, 'wb') as img_file:
                                img_file.write(response.content)
                            
                            self.root.after(0, lambda f=filename: self.log(f"✅ 下载成功: {f}", "SUCCESS"))
                            total_downloaded += 1
                            
                        except Exception as e:
                            self.root.after(0, lambda f=filename, e=e: self.log(f"❌ 下载失败 {f}: {e}", "ERROR"))
                            total_failed += 1
                            
                except Exception as e:
                    self.root.after(0, lambda f=json_file, e=e: self.log(f"❌ 处理文件 {f} 时出错: {e}", "ERROR"))
            
            # 显示下载结果
            result_msg = f"🎉 下载完成！成功: {total_downloaded} 个，跳过: {total_skipped} 个，失败: {total_failed} 个"
            self.root.after(0, lambda: self.log(result_msg, "SUCCESS"))
            self.root.after(0, lambda: messagebox.showinfo("完成", result_msg))
            
        except Exception as e:
            self.root.after(0, lambda e=e: self.log(f"❌ 下载高清封面失败: {e}", "ERROR"))
            self.root.after(0, lambda e=e: messagebox.showerror("错误", f"下载失败: {e}"))
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.log("🗑️ 日志已清空", "INFO")
    
    def save_log(self):
        """保存日志到文件"""
        try:
            log_content = self.log_text.get(1.0, tk.END)
            if not log_content.strip():
                messagebox.showwarning("警告", "没有日志内容可保存")
                return
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("日志文件", "*.log"), ("文本文件", "*.txt"), ("所有文件", "*.*")],
                title="保存日志文件"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                self.log(f"💾 日志已保存到: {file_path}", "INFO")
                messagebox.showinfo("成功", f"日志已保存到:\n{file_path}")
        except Exception as e:
            self.log(f"❌ 保存日志失败: {e}", "ERROR")
            messagebox.showerror("错误", f"保存失败: {e}")
    
    def update_stats(self):
        """更新统计信息 - 优化性能版本"""
        try:
            # 添加缓存机制，避免频繁计算
            current_time = time.time()
            if hasattr(self, '_last_stats_update') and current_time - self._last_stats_update < 30:
                return  # 30秒内不重复计算
            
            data_dir = 'data'
            total_movies = 0
            total_files = 0
            total_size = 0
            latest_file = None
            latest_time = 0
            
            if os.path.exists(data_dir):
                # 使用更高效的文件遍历方式
                json_files = []
                for entry in os.scandir(data_dir):
                    if entry.is_file() and entry.name.endswith('.json'):
                        json_files.append(entry.name)
                        
                        file_path = entry.path
                        file_time = entry.stat().st_mtime
                        file_size = entry.stat().st_size
                        total_size += file_size
                        
                        # 找到最新文件
                        if not latest_file or file_time > latest_time:
                            latest_file = file_path
                            latest_time = file_time
                        
                        # 统计总电影数量 - 使用更高效的方式
                        try:
                            # 只读取文件开头部分来获取items数量
                            with open(file_path, 'r', encoding='utf-8') as f:
                                # 读取前2000个字符，通常足够包含items数组信息
                                content_start = f.read(2000)
                                if '"items":' in content_start:
                                    # 如果items在文件开头，继续读取完整文件
                                    f.seek(0)
                                    data = json.load(f)
                                    total_movies += len(data.get('items', []))
                                else:
                                    # 完整读取文件
                                    f.seek(0)
                                    data = json.load(f)
                                    total_movies += len(data.get('items', []))
                        except:
                            continue
                
                total_files = len(json_files)
            
            # 格式化文件大小
            if total_size >= 1024 * 1024:
                size_str = f"{total_size / (1024 * 1024):.1f} MB"
            elif total_size >= 1024:
                size_str = f"{total_size / 1024:.1f} KB"
            else:
                size_str = f"{total_size} B"
            
            # 更新状态栏统计信息
            self.data_stats_var.set(f"📊 数据文件: {total_files} 个 ({size_str})")
            self.last_update_var.set(f"📅 最后更新: {datetime.fromtimestamp(latest_time).strftime('%Y-%m-%d %H:%M')}" if latest_time else "📅 最后更新: 从未")
            
            # 统计Excel文件
            excel_dir = 'exports'
            excel_files = 0
            if os.path.exists(excel_dir):
                excel_files = len([f for f in os.listdir(excel_dir) if f.endswith('.xlsx')])
            self.excel_stats_var.set(f"📋 Excel文件: {excel_files} 个")
            

                
            # 更新缓存时间
            self._last_stats_update = current_time
                
        except Exception as e:
            self.log(f"❌ 更新统计信息失败: {e}", "ERROR")
    
    def on_closing(self):
        """窗口关闭事件处理"""
        if self.is_running:
            if messagebox.askokcancel("确认", "爬虫正在运行，确定要退出吗？"):
                self.stop_crawler()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DoubanCrawlerGUI(root)
    # 设置窗口关闭事件
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    # 居中显示窗口
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")
    root.mainloop()

