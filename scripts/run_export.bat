@echo off
echo 正在导出豆瓣电影数据到Excel...
cd /d %~dp0
python export_to_excel.py
echo 导出完成
echo 请查看生成的Excel文件
echo.
pause