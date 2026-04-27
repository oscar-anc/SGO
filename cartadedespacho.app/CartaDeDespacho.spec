# -*- mode: python ; coding: utf-8 -*-
# ============================================================
# CartaDeDespacho.spec
# ============================================================
# Uso:
#   pyinstaller CartaDeDespacho.spec
#
# Requisitos:
#   pip install pyinstaller
#   imgs/app_icon_dark.ico   — ícono para tema claro de Windows
#   imgs/app_icon_light.ico  — ícono para tema oscuro de Windows
#   imgs/splash_screen.png   — imagen splash durante extracción
# ============================================================

import os

block_cipher = None

PROJECT_ROOT = os.path.dirname(os.path.abspath(SPEC))

def src(rel):
    return os.path.join(PROJECT_ROOT, rel)


# ── Datos a empaquetar ────────────────────────────────────────────────────────
datas = [
    (src('svgs.py'),           '.'),
    (src('framelesswindow'),   'framelesswindow'),
    (src('widgets'),           'widgets'),
    (src('db.json'),                    '.'),
    (src('template.docx'),              '.'),
    (src('template_siniestros.docx'),   '.'),
    (src('template_garantias.docx'),    '.'),
    (src('template_cesiones.docx'),     '.'),
    (src('imgs'),                       'imgs'),
    (src('fonts'),                      'fonts'),
]

_signatures_path = src(os.path.join('imgs', 'signatures'))
if os.path.isdir(_signatures_path):
    datas.append((_signatures_path, os.path.join('imgs', 'signatures')))


# ── Módulos ocultos ───────────────────────────────────────────────────────────
hidden_imports = [
    'docxtpl',
    'docx',
    'docx.oxml',
    'docx.oxml.ns',
    'docx.shared',
    'docx.enum.text',
    'docx.enum.table',
    'jinja2',
    'jinja2.ext',
    'lxml',
    'lxml._elementpath',
    'lxml.etree',
    'lxml.builder',
    'framelesswindow',
    'framelesswindow.windows',
    'framelesswindow.windows.window_effect',
    'framelesswindow.titlebar',
    'framelesswindow.titlebar.title_bar_buttons',
    'framelesswindow._rc',
    'framelesswindow._rc.resource',
    'docx2pdf',
    'openpyxl',
    'openpyxl.styles',
    'openpyxl.utils',
    'PySide6.QtSvg',
    'PySide6.QtSvgWidgets',
]

excludes = [
    'tkinter', 'matplotlib', 'numpy', 'scipy', 'pandas',
    'IPython', 'PIL', 'Pillow', 'wx', 'PyQt5', 'PyQt6', 'PySide2',
    'sphinx', 'pytest', 'setuptools', 'distutils',
    'email', 'http', 'xmlrpc', 'unittest', 'pydoc',
]


# ── Análisis ──────────────────────────────────────────────────────────────────
a = Analysis(
    [src('app.py')],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

def _filter(toc, patterns):
    import re
    return [e for e in toc if not any(re.search(p, e[0].replace('\\', '/')) for p in patterns)]

_exclude_patterns = [
    r'/test/', r'/tests/', r'__pycache__', r'\.pyc$',
    r'/doc/', r'/docs/', r'/examples/', r'/sample/',
    r'Qt6WebEngine', r'Qt6Quick', r'Qt6Qml', r'Qt6Designer',
]

a.datas    = _filter(a.datas,    _exclude_patterns)
a.binaries = _filter(a.binaries, _exclude_patterns)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)


# ── Splash screen ─────────────────────────────────────────────────────────────
# Shown by the bootloader during bundle extraction — before Python starts.
# Image must be PNG or JPG. always_on_top keeps it visible over other windows.
_splash_path = src(os.path.join('imgs', 'splash_screen.png'))
splash = Splash(
    _splash_path,
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,       # no dynamic text overlay
    text_size=12,
    always_on_top=True,
)


# ── Ejecutable ────────────────────────────────────────────────────────────────
# Static exe icon: app_icon_dark.ico (navy logo — readable on both taskbar themes)
_icon_path = src(os.path.join('imgs', 'app_icon_dark.ico'))
_icon = _icon_path if os.path.isfile(_icon_path) else None

exe = EXE(
    pyz,
    a.scripts,
    splash,
    splash.binaries,
    [],
    name='CartaDeDespacho',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        'Qt6Core.dll', 'Qt6Gui.dll', 'Qt6Widgets.dll',
        'Qt6Svg.dll', 'vcruntime140.dll', 'msvcp140.dll',
    ],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_icon,
    onefile=False,
)


coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    splash.binaries,
    strip=False,
    upx=True,
    upx_exclude=[
        'Qt6Core.dll', 'Qt6Gui.dll', 'Qt6Widgets.dll',
        'Qt6Svg.dll', 'vcruntime140.dll', 'msvcp140.dll',
    ],
    name='cartadedespacho.app',
)
