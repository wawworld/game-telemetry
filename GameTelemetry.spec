# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path

# Get project root (where .spec file is located)
spec_root = Path(SPECPATH).resolve()

a = Analysis(
    [str(spec_root / 'src' / 'cli' / 'main.py')],
    pathex=[str(spec_root / 'src')],
    binaries=[],
    datas=[
        ('configs', 'configs'),
        ('reference_images', 'reference_images'),
    ],
    hiddenimports=[
        'pynput.keyboard',
        'pynput.mouse',
        'PIL',
        'PIL.Image',
        'cv2',
        'yaml',
        'psutil',
        'asyncio',
    ],
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
    name='GameTelemetry',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE',
)
