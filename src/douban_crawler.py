"""
豆瓣电影数据爬虫核心模块
作者: mshellc
"""

import requests
import json
import time
from datetime import datetime
import logging
import os

# 加载配置
def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        # 默认配置
        return {
            "crawl_interval": 3600,
            "max_retries": 3,
            "timeout": 30,
            "output_directory": "data",
            "log_level": "INFO"
        }
    except json.JSONDecodeError as e:
        print(f"配置文件格式错误: {e}")
        return None

# 配置日志
config = load_config()
if config is None:
    exit(1)

log_level = getattr(logging, config.get('log_level', 'INFO'))
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('douban_crawler.log'),
        logging.StreamHandler()
    ]
)

def fetch_douban_movies(config=None):
    """爬取豆瓣电影推荐数据"""
    if config is None:
        config = load_config()
    count = config.get('count', 20)
    start = config.get('start', 0)
    tags = config.get('tags', '2025')
    sort = config.get('sort', 'R')
    actual_count = config.get('actual_count', 0)
    max_retries = config.get('max_retries', 3)
    
    base_url = f"https://m.douban.com/rexxar/api/v2/movie/recommend?refresh=0&start={{}}&count={count}&selected_categories={{}}&uncollect=false&score_range=0,10&tags={tags}&sort={sort}"
    
    headers = {
        'Referer': 'https://movie.douban.com/explore',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive'
    }
    
    timeout = config.get('timeout', 30)
    
    all_items = []
    total_count = 0
    start_pos = start
    count_per_page = count
    
    def make_request_with_retry(url, max_attempts=3):
        """带重试机制的请求函数"""
        for attempt in range(max_attempts):
            try:
                response = requests.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt == max_attempts - 1:
                    raise
                wait_time = 2 ** attempt  # 指数退避
                logging.warning(f"请求失败，{wait_time}秒后重试 (尝试 {attempt + 1}/{max_attempts}): {e}")
                time.sleep(wait_time)
    
    try:
        # 先获取第一页数据来获取total总数
        first_page_url = base_url.format(start_pos, "{}")
        response = make_request_with_retry(first_page_url, max_retries)
        
        first_data = response.json()
        total_count = first_data.get('total', 0)
        
        if total_count == 0:
            logging.warning("未获取到电影数据")
            return False
        
        logging.info(f"总共需要爬取 {total_count} 条电影数据，每页 {count_per_page} 条，起始位置: {start}")
        
        # 添加第一页数据
        all_items.extend(first_data.get('items', []))
        
        # 如果设置了实际爬取数量限制，且已经达到限制，则停止爬取
        if actual_count > 0 and len(all_items) >= actual_count:
            all_items = all_items[:actual_count]
            logging.info(f"已达到实际爬取数量限制 {actual_count} 条，停止爬取")
        else:
            # 计算需要爬取的页数
            total_pages = (total_count + count_per_page - 1) // count_per_page
            
            # 从第二页开始爬取剩余页面
            for page in range(1, total_pages):
                start_pos = page * count_per_page
                if start_pos >= total_count:
                    break
                    
                page_url = base_url.format(start_pos, "{}")
                logging.info(f"正在爬取第 {page + 1} 页，起始位置: {start_pos}")
                
                response = make_request_with_retry(page_url, max_retries)
                
                page_data = response.json()
                all_items.extend(page_data.get('items', []))
                
                # 如果设置了实际爬取数量限制，且已经达到限制，则停止爬取
                if actual_count > 0 and len(all_items) >= actual_count:
                    all_items = all_items[:actual_count]
                    logging.info(f"已达到实际爬取数量限制 {actual_count} 条，停止爬取")
                    break
                
                # 智能延迟控制：根据当前请求速度动态调整
                # 如果当前页数据量较少，减少延迟；数据量多则增加延迟
                current_items = len(page_data.get('items', []))
                delay = max(0.5, min(2.0, 2.0 - (current_items / count_per_page) * 1.5))
                time.sleep(delay)
        
        # 创建完整的返回数据
        complete_data = {
            'count': len(all_items),
            'total': total_count,
            'items': all_items,
            'recommend_categories': first_data.get('recommend_categories', []),
            'show_rating_filter': first_data.get('show_rating_filter', False)
        }
        
        # 创建输出目录
        output_dir = config.get('output_directory', 'data')
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存数据到文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"douban_movies_{timestamp}.json")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(complete_data, f, ensure_ascii=False, indent=2)
        
        logging.info(f"成功爬取所有数据并保存到 {filename}")
        logging.info(f"总共爬取到 {len(all_items)} 条电影数据，预期总数: {total_count}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        logging.error(f"网络请求错误: {e}, URL: {first_page_url if 'first_page_url' in locals() else 'N/A'}")
        if hasattr(e, 'response') and e.response is not None:
            logging.error(f"HTTP状态码: {e.response.status_code}")
        return False
    except json.JSONDecodeError as e:
        logging.error(f"JSON解析错误: {e}, URL: {first_page_url if 'first_page_url' in locals() else 'N/A'}")
        return False
    except Exception as e:
        logging.error(f"未知错误: {e}, URL: {first_page_url if 'first_page_url' in locals() else 'N/A'}")
        return False

def main():
    """主函数"""
    config = load_config()
    if config is None:
        return False
    
    crawl_interval = config.get('crawl_interval', 3600)
    max_retries = config.get('max_retries', 3)
    
    logging.info(f"豆瓣电影爬虫启动，爬取间隔: {crawl_interval}秒")
    
    success = False
    retries = 0
    
    while not success and retries < max_retries:
        logging.info(f"开始第 {retries + 1} 次爬取尝试...")
        success = fetch_douban_movies(config)
        if not success:
            retries += 1
            if retries < max_retries:
                logging.warning(f"爬取失败，{30}秒后重试...")
                time.sleep(30)
    
    if not success:
        logging.error("所有重试均失败")
        return False
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("程序被用户中断")
    except Exception as e:
        logging.error(f"程序异常: {e}")