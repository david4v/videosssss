# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for building the Orchard portable Windows app."""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

block_cipher = None

a = Analysis(
    ['packaging/windows/app_entry.py'],
    pathex=[str(SRC), str(ROOT)],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PySide6.QtNetwork',
        'PySide6.QtSvg',
        'PySide6.QtPrintSupport',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OrchardVideoDownloader',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OrchardVideoDownloader',
)
