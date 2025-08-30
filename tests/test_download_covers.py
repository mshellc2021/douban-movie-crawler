#!/usr/bin/env python3
"""
测试下载高清封面功能的脚本
作者: mshellc
"""

import json
import os
import requests

def test_download_covers():
    """测试下载高清封面功能"""
    
    # 创建images目录
    images_dir = 'images'
    os.makedirs(images_dir, exist_ok=True)
    
    print("🖼️ 开始测试下载高清电影封面...")
    
    # 获取所有数据文件
    data_dir = 'data'
    if not os.path.exists(data_dir):
        print("❌ 数据目录不存在，请先爬取数据")
        return
    
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    if not json_files:
        print("❌ 没有找到数据文件")
        return
    
    total_downloaded = 0
    total_skipped = 0
    
    # 只测试第一个文件的前几个电影
    test_file = json_files[0]
    file_path = os.path.join(data_dir, test_file)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        movies = data.get('items', [])[:3]  # 只测试前3个电影
        
        for movie in movies:
            # 获取电影标题和ID
            title = movie.get('title', '未知电影')
            movie_id = movie.get('id', '未知ID')
            
            # 获取高清封面链接
            pic = movie.get('pic', {})
            large_url = pic.get('large')
            
            if not large_url:
                print(f"❌ 电影 '{title}' 没有高清封面链接")
                continue
            
            # 生成文件名（电影名+ID）
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}_{movie_id}.jpg"
            filepath = os.path.join(images_dir, filename)
            
            # 检查文件是否已存在
            if os.path.exists(filepath):
                print(f"⏭️ 封面已存在，跳过: {filename}")
                total_skipped += 1
                continue
            
            # 下载封面
            try:
                print(f"⬇️  正在下载: {filename}")
                response = requests.get(large_url, timeout=30)
                response.raise_for_status()
                
                with open(filepath, 'wb') as img_file:
                    img_file.write(response.content)
                
                print(f"✅ 下载成功: {filename}")
                total_downloaded += 1
                
            except Exception as e:
                print(f"❌ 下载失败 {filename}: {e}")
                
    except Exception as e:
        print(f"❌ 处理文件 {test_file} 时出错: {e}")
    
    # 显示测试结果
    print(f"\n🎉 测试完成！成功: {total_downloaded} 个，跳过: {total_skipped} 个")
    print(f"📁 封面文件保存在: {os.path.abspath(images_dir)}")

if __name__ == "__main__":
    test_download_covers()