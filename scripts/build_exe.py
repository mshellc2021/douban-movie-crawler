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
    
    # 使用现有的spec文件进行打包
    args = [
        sys.executable, "-m", "PyInstaller",
        "豆瓣电影爬虫工具.spec",  # 使用spec文件
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
                
                # 从VERSION文件读取版本号
                version = "0.0.1"
                if os.path.exists("VERSION"):
                    with open("VERSION", "r", encoding="utf-8") as f:
                        version = f.read().strip()
                
                # 创建完整的可移植发布包
                package_name = f"豆瓣电影爬虫工具_v{version}"
                package_dir = os.path.join(os.getcwd(), "release", package_name)
                os.makedirs(package_dir, exist_ok=True)
                
                # 复制exe文件到发布包目录
                shutil.copy2(exe_path, package_dir)
                
                # 复制必要的配置文件
                for config_file in ["config.json", "requirements.txt"]:
                    if os.path.exists(config_file):
                        shutil.copy2(config_file, package_dir)
                
                # 复制src源代码目录
                if os.path.exists("src"):
                    shutil.copytree("src", os.path.join(package_dir, "src"), dirs_exist_ok=True)
                
                # 创建必要的目录结构
                for subdir in ["data", "exports", "images", "logs"]:
                    os.makedirs(os.path.join(package_dir, subdir), exist_ok=True)
                
                # 创建说明文件
                readme_content = f"""# 豆瓣电影爬虫工具 v{version}

## 使用说明

1. 解压整个文件夹到任意位置
2. 直接运行 `豆瓣电影爬虫工具.exe` 即可启动程序
3. 程序会自动使用包内的目录结构（data/, exports/, images/, logs/）

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

## 目录结构
├── 豆瓣电影爬虫工具.exe    # 主程序
├── config.json            # 配置文件
├── requirements.txt       # 依赖说明
├── src/                  # 源代码目录（Python源码）
├── data/                 # 数据存储目录
├── exports/              # Excel导出目录
├── images/               # 电影封面目录
└── logs/                 # 日志文件目录

## 注意事项
- 确保网络连接正常
- 首次运行可能会被Windows Defender拦截，请选择"允许运行"
- 程序需要写入文件的权限
- 请勿删除包内的任何目录，否则可能导致功能异常
"""
                
                with open(os.path.join(package_dir, "README.txt"), "w", encoding="utf-8") as f:
                    f.write(readme_content)
                
                # 创建zip压缩包
                import zipfile
                zip_path = os.path.join(os.getcwd(), "release", f"{package_name}.zip")
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(package_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(package_dir))
                            zipf.write(file_path, arcname)
                        # 确保空目录也被包含
                        for dir_name in dirs:
                            dir_path = os.path.join(root, dir_name)
                            if not os.listdir(dir_path):  # 如果是空目录
                                zipf.write(dir_path, os.path.relpath(dir_path, os.path.dirname(package_dir)))
                
                print(f"📦 完整发布包已创建: {zip_path}")
                print(f"📁 包内包含完整目录结构，用户解压即可使用")
                
                # 清理中间产物，只保留zip文件
                shutil.rmtree(package_dir, ignore_errors=True)
                print("🧹 已清理临时文件，只保留最终的zip发布包")
                print("🎉 打包完成！现在可以将zip文件分享给其他用户")
                
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