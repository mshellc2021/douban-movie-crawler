@echo off
chcp 936 >nul
echo.
echo ================================
echo Douban Movie Crawler - Packager
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.7+
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip not found. Please check Python installation
    pause
    exit /b 1
)

REM Check if main program exists - use relative path from script location
if not exist "%~dp0..\src\douban_gui.py" (
    echo ERROR: Main program not found at %~dp0..\src\douban_gui.py
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

echo Environment check passed
echo Starting packaging process...
echo.

REM Run Python packaging script
python scripts\build_exe.py

if errorlevel 1 (
    echo Packaging failed!
    pause
    exit /b 1
)

echo.
echo Packaging completed successfully!
echo EXE file: dist\DoubanMovieCrawler.exe
echo Release package: release\
echo.
pause