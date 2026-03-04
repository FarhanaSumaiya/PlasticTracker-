# -*- mode: python ; coding: utf-8 -*-

block_cipher = None  # <-- ADD THIS LINE

a = Analysis(
    ['PlasticTrack.py'],
    pathex=[],
    binaries=[],
    datas=[('products.json', '.')],
    hiddenimports=[
        'ttkbootstrap',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'reportlab',
        'reportlab.lib',
        'reportlab.lib.colors',
        'PIL'  # For Pillow (if using images)
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PlasticTrack',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want console output
    icon=None,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)