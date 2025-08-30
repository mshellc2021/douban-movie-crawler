#!/usr/bin/env python3
"""
测试导出日志更新功能的脚本
模拟长时间导出过程，验证日志能否正常更新
作者: mshellc
"""

import time
import subprocess
import threading
import sys

def test_export_logs():
    """测试导出日志更新功能"""
    print("🚀 开始测试导出日志更新功能...")
    
    # 使用包含图片的导出命令
    cmd = ['python', 'export_to_excel.py', '--progress']
    
    print(f"执行命令: {' '.join(cmd)}")
    print("=" * 60)
    
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
            line_count = 0
            start_time = time.time()
            
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if line:
                    line_count += 1
                    elapsed = time.time() - start_time
                    print(f"[{elapsed:6.1f}s] {line}")
                    
                    # 模拟GUI的日志更新频率检测
                    if line_count > 0 and elapsed > 30 and "正在下载" in line:
                        print("⚠️  警告: 检测到长时间无日志更新!")
        
        # 实时读取错误
        def read_error():
            while True:
                line = process.stderr.readline()
                if not line:
                    break
                line = line.strip()
                if line:
                    print(f"[ERROR] {line}")
        
        # 启动读取线程
        stdout_thread = threading.Thread(target=read_output, daemon=True)
        stderr_thread = threading.Thread(target=read_error, daemon=True)
        stdout_thread.start()
        stderr_thread.start()
        
        # 等待进程完成
        process.wait()
        
        print("=" * 60)
        if process.returncode == 0:
            print("✅ 导出测试完成，返回码: 0")
        else:
            print(f"❌ 导出测试失败，返回码: {process.returncode}")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    import os
    test_export_logs()