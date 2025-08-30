# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\douban_gui.py', 'src\\douban_crawler.py', 'src\\export_to_excel.py'],
    pathex=[],
    binaries=[],
    datas=[('config.json', '.'), ('requirements.txt', '.')],
    hiddenimports=['requests', 'tkinter', 'json', 'os', 'sys', 'time', 'datetime', 'threading', 'subprocess', 'webbrowser', 'messagebox', 'filedialog', 'scrolledtext'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='豆瓣电影爬虫工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE',
)
