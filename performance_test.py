#!/usr/bin/env python3
"""
性能测试脚本 - 测试GUI和爬虫的性能优化效果
作者: mshellc
"""

import time
import os
import json
import subprocess
import threading
from datetime import datetime

def test_file_stat_performance():
    """测试文件统计性能"""
    print("=== 文件统计性能测试 ===")
    
    # 创建测试数据目录
    test_dir = "test_performance_data"
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建一些测试JSON文件
    for i in range(50):
        test_data = {
            "items": [{"id": j, "title": f"Test Movie {j}"} for j in range(100)]
        }
        with open(os.path.join(test_dir, f"test_{i}.json"), 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False)
    
    # 测试传统方法
    start_time = time.time()
    
    # 方法1: os.listdir + os.path 方式
    total_movies = 0
    total_files = 0
    total_size = 0
    
    if os.path.exists(test_dir):
        json_files = [f for f in os.listdir(test_dir) if f.endswith('.json')]
        total_files = len(json_files)
        
        for filename in json_files:
            file_path = os.path.join(test_dir, filename)
            file_size = os.path.getsize(file_path)
            total_size += file_size
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total_movies += len(data.get('items', []))
            except:
                continue
    
    time_method1 = time.time() - start_time
    print(f"传统方法耗时: {time_method1:.3f}秒")
    print(f"统计结果: {total_files}个文件, {total_movies}条数据, {total_size}字节")
    
    # 测试优化方法
    start_time = time.time()
    
    total_movies = 0
    total_files = 0
    total_size = 0
    
    if os.path.exists(test_dir):
        json_files = []
        for entry in os.scandir(test_dir):
            if entry.is_file() and entry.name.endswith('.json'):
                json_files.append(entry.name)
                file_size = entry.stat().st_size
                total_size += file_size
                
                try:
                    # 优化读取方式
                    with open(entry.path, 'r', encoding='utf-8') as f:
                        content_start = f.read(2000)
                        if '"items":' in content_start:
                            f.seek(0)
                            data = json.load(f)
                            total_movies += len(data.get('items', []))
                        else:
                            f.seek(0)
                            data = json.load(f)
                            total_movies += len(data.get('items', []))
                except:
                    continue
        
        total_files = len(json_files)
    
    time_method2 = time.time() - start_time
    print(f"优化方法耗时: {time_method2:.3f}秒")
    print(f"统计结果: {total_files}个文件, {total_movies}条数据, {total_size}字节")
    
    improvement = (time_method1 - time_method2) / time_method1 * 100
    print(f"性能提升: {improvement:.1f}%")
    
    # 清理测试文件
    for filename in os.listdir(test_dir):
        os.remove(os.path.join(test_dir, filename))
    os.rmdir(test_dir)

def test_memory_usage():
    """测试内存使用情况"""
    print("\n=== 内存使用测试 ===")
    
    try:
        import psutil
        process = psutil.Process()
        
        # 测试前内存
        memory_before = process.memory_info().rss / 1024 / 1024
        print(f"测试前内存使用: {memory_before:.1f} MB")
        
        # 执行一些操作
        test_data = []
        for i in range(10000):
            test_data.append({"id": i, "data": "x" * 100})
        
        # 测试后内存
        memory_after = process.memory_info().rss / 1024 / 1024
        print(f"测试后内存使用: {memory_after:.1f} MB")
        print(f"内存增加: {memory_after - memory_before:.1f} MB")
        
    except ImportError:
        print("psutil未安装，跳过内存测试")

def test_gui_startup():
    """测试GUI启动性能"""
    print("\n=== GUI启动性能测试 ===")
    
    # 测试GUI启动时间
    start_time = time.time()
    
    try:
        # 使用subprocess启动GUI并立即关闭
        process = subprocess.Popen(
            ['python', 'douban_gui.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 等待一小段时间让GUI初始化
        time.sleep(2)
        
        # 终止进程
        process.terminate()
        process.wait()
        
        startup_time = time.time() - start_time
        print(f"GUI启动到初始化完成耗时: {startup_time:.1f}秒")
        
    except Exception as e:
        print(f"GUI启动测试失败: {e}")

def main():
    """主测试函数"""
    print("豆瓣电影数据管理工具性能测试")
    print("=" * 50)
    
    # 运行各项测试
    test_file_stat_performance()
    test_memory_usage()
    test_gui_startup()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()