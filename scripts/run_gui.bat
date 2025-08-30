@echo off
echo 正在启动豆瓣电影数据管理工具...
cd /d %~dp0
python src\douban_gui.py
echo 程序已退出
echo.
pause