#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试GUI长链接自动换行功能
作者: mshellc
"""

import time
import subprocess
import os

def test_long_url_logging():
    """测试长链接日志记录功能"""
    
    # 启动GUI程序
    print("正在启动GUI程序...")
    gui_process = subprocess.Popen(['python', 'douban_gui.py'], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
    
    # 等待GUI启动
    time.sleep(3)
    
    # 模拟一个包含长链接的错误消息
    long_url = "https://m.douban.com/rexxar/api/v2/movie/recommend?refresh=0&start=180&count=20&selected_categories=%7B%7D&uncollect=false&score_range=0,10&tags=2025&sort=R"
    error_message = f"连接错误: 无法访问 {long_url}，请检查网络连接"
    
    print("测试长链接:")
    print(f"原始长度: {len(long_url)} 字符")
    print(f"原始链接: {long_url}")
    print()
    
    # 测试_process_long_urls方法
    from douban_gui import DoubanCrawlerGUI
    import tkinter as tk
    
    # 创建临时根窗口用于测试
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口
    
    gui = DoubanCrawlerGUI(root)
    processed = gui._process_long_urls(error_message)
    
    print("处理后的消息:")
    print(processed)
    print()
    
    # 清理
    gui_process.terminate()
    gui_process.wait()
    root.destroy()
    
    print("测试完成！")

if __name__ == "__main__":
    test_long_url_logging()