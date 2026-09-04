# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for a single-file build_dashboard executable.
# The dashboard template is bundled inside the executable via `datas`, so end users
# need only the one file. Build with:  pyinstaller build_dashboard.spec
# (CI builds this on windows-latest to produce build_dashboard.exe.)

a = Analysis(
    ['build_dashboard.py'],
    pathex=[],
    binaries=[],
    datas=[('cmo_db_dashboard.template.html', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='build_dashboard',
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
    icon=None,
)
