# 豆瓣电影推荐数据爬虫

这是一个定时爬取豆瓣电影推荐数据的Python项目，可以自动定时抓取豆瓣2025年电影推荐数据。

## 功能特性

- ✅ 定时自动爬取（可配置间隔时间）
- ✅ 失败重试机制
- ✅ 数据保存为JSON格式
- ✅ 详细的日志记录
- ✅ 配置文件管理

## 项目结构

```
douban_crawler/
├── douban_crawler.py    # 主爬虫程序
├── config.json          # 配置文件
├── run_crawler.bat      # Windows批处理文件
├── README.md           # 项目说明
└── data/               # 数据保存目录（自动创建）
```

## 安装依赖

```bash
pip install requests
```

## 配置说明

编辑 `config.json` 文件来自定义爬虫行为：

```json
{
  "crawl_interval": 3600,      // 爬取间隔（秒），默认1小时
  "max_retries": 3,            // 失败重试次数
  "timeout": 30,               // 请求超时时间（秒）
  "output_directory": "data", // 数据保存目录
  "log_level": "INFO"         // 日志级别（DEBUG/INFO/WARNING/ERROR）
}
```

## 使用方法

### 🖥️ 1. 图形界面（推荐）
```bash
# 启动GUI界面
python douban_gui.py
```
或者直接双击运行 `run_gui.bat`

**GUI功能**:
- ✅ 可视化控制爬虫启动/停止
- ✅ 实时日志显示
- ✅ 配置参数设置
- ✅ 一键导出Excel
- ✅ 状态监控

### 2. 命令行运行

#### 单次运行
```bash
python douban_crawler.py
```

#### 定时运行（Windows）
使用Windows任务计划程序：
1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器（每天/每小时）
4. 操作为"启动程序"
5. 程序选择：`python.exe`
6. 参数：`d:\py_project\douban_crawler.py`
7. 起始于：`d:\py_project\`

或者直接双击运行 `run_crawler.bat`

#### 后台持续运行
```bash
# 启动爬虫（会一直运行）
python douban_crawler.py

# 按 Ctrl+C 停止
```

#### 数据导出
```bash
# 导出数据到Excel
python export_to_excel.py
```
或者双击运行 `run_export.bat`

## 数据格式

爬取的数据保存为JSON格式，文件名示例：`douban_movies_20241201_143052.json`

数据包含豆瓣电影推荐的完整信息，包括：
- 电影标题、评分、导演、演员
- 上映时间、类型、地区
- 简介、海报链接等

## 注意事项

1. 请合理设置爬取间隔，避免对豆瓣服务器造成压力
2. 遵守豆瓣的robots.txt协议
3. 数据仅用于个人学习和研究
4. 建议在非高峰时段运行爬虫

## 日志文件

程序运行日志保存在 `douban_crawler.log` 文件中，包含：
- 爬取时间
- 成功/失败信息
- 错误详情
- 数据统计

## 故障排除

如果遇到问题，请检查：
1. 网络连接是否正常
2. Python和requests库是否安装正确
3. 配置文件格式是否正确
4. 查看日志文件获取详细错误信息