#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试长链接自动换行功能
作者: mshellc
"""

import re

def process_long_urls(message):
    """处理消息中的长链接，自动添加换行符"""
    # 匹配URL的正则表达式
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

# 测试长链接
test_url = 'https://m.douban.com/rexxar/api/v2/movie/recommend?refresh=0&start=180&count=20&selected_categories=%7B%7D&uncollect=false&score_range=0,10&tags=2025&sort=R'

print("原始链接长度:", len(test_url))
print("原始链接:")
print(test_url)
print("\n" + "="*50)

processed = process_long_urls(test_url)
print("处理后的链接:")
print(processed)

# 测试包含多个链接的消息
test_message = f"错误信息: 无法连接到 {test_url}，请检查网络连接。另一个链接: https://img9.doubanio.com/view/photo/m_ratio_poster/public/p2924330946.jpg"
print("\n" + "="*50)
print("原始消息:")
print(test_message)
print("\n处理后的消息:")
print(process_long_urls(test_message))