@echo off
echo 正在启动豆瓣电影爬虫...

REM 检查douban_crawler.py文件是否存在
if not exist "%~dp0douban_crawler.py" (
    echo 错误: 找不到 douban_crawler.py 文件！
    echo 请确保脚本在正确的目录中运行
    pause
    exit /b 1
)

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 找不到Python环境！
    echo 请确保Python已安装并添加到系统PATH中
    pause
    exit /b 1
)

cd /d %~dp0
echo 正在执行爬虫程序...
python douban_crawler.py

if errorlevel 1 (
    echo 爬虫执行失败！
) else (
    echo 爬虫执行完成
)

echo 任务完成时间: %date% %time%
pause