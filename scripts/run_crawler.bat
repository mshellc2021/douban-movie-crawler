@echo off
echo 正在启动豆瓣电影爬虫...
cd /d %~dp0
python douban_crawler.py
echo 爬虫执行完成
echo 任务完成时间: %date% %time%
pause