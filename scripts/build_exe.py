#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
豆瓣电影爬虫GUI程序打包脚本
使用PyInstaller将程序打包成独立的exe文件
作者: mshellc
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """检查是否安装了PyInstaller"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ PyInstaller安装失败")
        return False

def build_exe():
    """构建exe文件"""
    print("🚀 开始构建exe文件...")
    
    # PyInstaller参数
    args = [
        sys.executable, "-m", "PyInstaller",
        "src\\douban_gui.py",  # 主程序文件
        "--name=豆瓣电影爬虫工具",  # 程序名称
        "--onefile",  # 打包成单个exe文件
        "--windowed",  # 窗口程序，不显示控制台
        "--icon=NONE",  # 不使用图标
        "--add-data=config.json;.",  # 包含配置文件
        "--add-data=requirements.txt;.",  # 包含依赖文件
        "--hidden-import=requests",  # 隐藏导入
        "--hidden-import=tkinter",
        "--hidden-import=json",
        "--hidden-import=os",
        "--hidden-import=sys",
        "--hidden-import=time",
        "--hidden-import=datetime",
        "--hidden-import=threading",
        "--hidden-import=subprocess",
        "--hidden-import=webbrowser",
        "--hidden-import=messagebox",
        "--hidden-import=filedialog",
        "--hidden-import=scrolledtext",
        "--clean"  # 清理临时文件
    ]
    
    try:
        print("📦 正在打包，这可能需要几分钟...")
        result = subprocess.run(args, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ exe文件构建成功！")
            
            # 显示生成的文件路径
            dist_dir = os.path.join(os.getcwd(), "dist")
            exe_path = os.path.join(dist_dir, "豆瓣电影爬虫工具.exe")
            
            if os.path.exists(exe_path):
                print(f"📁 exe文件位置: {exe_path}")
                print(f"📊 文件大小: {os.path.getsize(exe_path) / (1024*1024):.2f} MB")
                
                # 创建发布包目录
                release_dir = os.path.join(os.getcwd(), "release")
                os.makedirs(release_dir, exist_ok=True)
                
                # 复制exe文件到发布目录
                shutil.copy2(exe_path, release_dir)
                
                # 复制必要的配置文件
                for config_file in ["config.json", "requirements.txt"]:
                    if os.path.exists(config_file):
                        shutil.copy2(config_file, release_dir)
                
                # 创建说明文件
                readme_content = """# 豆瓣电影爬虫工具

## 使用说明

1. 直接运行 `豆瓣电影爬虫工具.exe` 即可启动程序
2. 程序会自动创建必要的目录结构（data/, exports/, images/, logs/）
3. 首次使用建议先检查配置，然后开始爬取数据

## 功能特点
- 🎬 豆瓣电影数据爬取
- 💾 数据导出为Excel格式
- 🖼️ 高清电影封面下载
- 📊 实时日志显示
- ⚡ 状态栏实时监控

## 系统要求
- Windows 7/8/10/11
- .NET Framework 4.5+（通常系统自带）
- 不需要安装Python环境

## 注意事项
- 确保网络连接正常
- 首次运行可能会被Windows Defender拦截，请选择"允许运行"
- 程序需要写入文件的权限
"""
                
                with open(os.path.join(release_dir, "README.txt"), "w", encoding="utf-8") as f:
                    f.write(readme_content)
                
                print(f"📦 发布包已创建在: {release_dir}")
                print("🎉 打包完成！现在可以将release文件夹分享给其他用户")
                
            return True
        else:
            print("❌ 构建失败:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 构建过程中出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("📦 豆瓣电影爬虫工具 - EXE打包程序")
    print("=" * 60)
    
    # 检查当前目录
    if not os.path.exists("src\\douban_gui.py"):
        print("❌ 错误: 请在项目根目录运行此脚本")
        print("当前目录:", os.getcwd())
        return
    
    # 检查PyInstaller
    if not check_pyinstaller():
        print("⚠️  未检测到PyInstaller")
        if input("是否安装PyInstaller？(y/n): ").lower() == 'y':
            if not install_pyinstaller():
                return
        else:
            print("请手动安装: pip install pyinstaller")
            return
    
    # 开始构建
    if build_exe():
        print("\n🎯 打包成功！")
        print("💡 提示: 如果exe文件被杀毒软件误报，请添加到信任列表")
    else:
        print("\n❌ 打包失败")

if __name__ == "__main__":
    main()