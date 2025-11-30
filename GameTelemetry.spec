# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/Users/changhoonpark/Developer/spec-kit-project/src/cli/main.py'],
    pathex=[],
    binaries=[],
    datas=[('configs', 'configs'), ('reference_images', 'reference_images')],
    hiddenimports=['pynput.keyboard._win32', 'pynput.mouse._win32', 'PIL._tkinter_finder'],
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
