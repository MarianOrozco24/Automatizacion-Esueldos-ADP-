# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['A-Esueldos.py'],
    pathex=[],
    binaries=[],
    datas=[('rutas.json', '.'), ('C:/Users/Usuario/Desktop/Codigos Planificacion Estrategica/Automatizacion-Adm-Personal/esueldos/.venv/Lib/site-packages/mysql/connector/locales', 'mysql/connector/locales')],
    hiddenimports=['mysql', 'mysql.connector', 'mysql.connector.plugins.mysql_native_password'],
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
    name='A-Esueldos',
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
    icon=['icono\\icon.ico'],
)
