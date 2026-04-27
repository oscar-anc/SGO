# -*- mode: python ; coding: utf-8 -*-
# ============================================================
# launcher.spec — SGO Launcher
# ============================================================
# Uso:
#   pyinstaller launcher.spec
#
# Genera: dist/SGO.exe  (onefile — pequeño y rápido)
# El launcher.exe vive junto a las carpetas de cada app.
# ============================================================

import os

block_cipher = None
PROJECT_ROOT = os.path.dirname(os.path.abspath(SPEC))

def src(rel):
    return os.path.join(PROJECT_ROOT, rel)

datas = [
    (src('launcher_apps.json'), '.'),
    (src('imgs'),               'imgs'),
    (src('fonts'),              'fonts'),
]

a = Analysis(
    [src('launcher.py')],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=['qframelesswindow'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        'tkinter', 'matplotlib', 'numpy', 'scipy', 'pandas',
        'docxtpl', 'docx', 'docx2pdf', 'openpyxl', 'jinja2',
        'IPython', 'PIL', 'Pillow', 'wx', 'PyQt5', 'PyQt6',
        'sphinx', 'pytest', 'setuptools',
    ],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

_icon_path = src(os.path.join('imgs', 'app_icon_dark.ico'))
_icon = _icon_path if os.path.isfile(_icon_path) else None

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SGO',
    debug=False,
    strip=False,
    upx=True,
    upx_exclude=['Qt6Core.dll', 'Qt6Gui.dll', 'Qt6Widgets.dll'],
    console=False,
    icon=_icon,
    onefile=True,
)
