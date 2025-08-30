@echo off
chcp 65001 >nul
echo.
echo ================================
echo   豆瓣电影爬虫工具 - 打包程序
echo ================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未检测到Python，请先安装Python 3.6+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查pip是否可用
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: pip不可用，请检查Python安装
    pause
    exit /b 1
)

REM 检查主程序文件是否存在
if not exist "douban_gui.py" (
    echo ❌ 错误: 未找到douban_gui.py，请在项目根目录运行
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo.
echo 📦 开始打包过程...
echo 这可能需要几分钟时间，请耐心等待...
echo.

REM 运行打包脚本
python build_exe.py

echo.
echo 💡 打包完成！
echo 📁 生成的exe文件在: dist\豆瓣电影爬虫工具.exe
echo 📦 完整的发布包在: release\ 文件夹
echo.
echo 🎯 现在可以将release文件夹分享给其他用户使用
echo ⚠️  注意: 首次运行可能会被Windows Defender拦截，请选择"允许运行"
echo.
pause