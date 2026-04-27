# -*- mode: python ; coding: utf-8 -*-
# ============================================================
# MailDeDespacho.spec
# ============================================================
# Uso:
#   pyinstaller MailDeDespacho.spec
#
# Requisitos previos:
#   pip install pyinstaller pywin32 PySide6
#   imgs/app_icon.ico        — ícono de la aplicación
#   imgs/splash_screen.png   — imagen splash durante extracción (opcional)
#
# Estructura esperada en SGO/:
#   SGO/
#   ├── cartadedespacho.app/
#   │   └── db.json          ← leído en runtime, NO empaquetado aquí
#   └── maildedespacho.app/
#       ├── app.py
#       ├── MailDeDespacho.spec  (este archivo)
#       ├── theme.py
#       ├── svgs.py
#       ├── config_loader.py
#       ├── template_engine.py
#       ├── outlook_bridge.py
#       ├── templates/
#       │   ├── rrgg.html
#       │   ├── transportes.html
#       │   └── base.css
#       └── imgs/
#           └── app_icon.ico
#
# NOTA: db.json NO se empaqueta en el .exe — se lee desde la ruta
#       relativa ../cartadedespacho.app/db.json en runtime.
#       Ambas apps deben distribuirse juntas dentro de SGO/.
# ============================================================

import os

block_cipher = None

PROJECT_ROOT = os.path.dirname(os.path.abspath(SPEC))

def src(rel):
    """Resuelve una ruta relativa desde la raíz del proyecto."""
    return os.path.join(PROJECT_ROOT, rel)


# ── Datos a empaquetar ────────────────────────────────────────────────────────
# db.json NO va aquí — se lee desde ../cartadedespacho.app/db.json en runtime.
datas = [
    # Módulos Python del proyecto
    (src('theme.py'),              '.'),
    (src('svgs.py'),               '.'),
    (src('config_loader.py'),      '.'),
    (src('template_engine.py'),    '.'),
    (src('outlook_bridge.py'),     '.'),

    # Subcarpetas de UI
    (src('ui'),                    'ui'),

    # Plantillas HTML de correo
    (src('templates'),             'templates'),

    # Recursos de imagen (ícono, splash)
    (src('imgs'),                  'imgs'),
]


# ── Módulos ocultos ───────────────────────────────────────────────────────────
hidden_imports = [
    # PySide6
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtSvg',
    'PySide6.QtSvgWidgets',
    'PySide6.QtWebEngineWidgets',   # para vista previa del correo
    'PySide6.QtWebEngineCore',
    'PySide6.QtNetwork',

    # win32com — integración Outlook
    'win32com',
    'win32com.client',
    'win32com.shell',
    'pywintypes',
    'pythoncom',

    # Stdlib usada en runtime
    'json',
    'pathlib',
    'logging',
    'string',
    're',
    'dataclasses',
]

# ── Exclusiones para reducir tamaño del bundle ────────────────────────────────
excludes = [
    'tkinter', 'matplotlib', 'numpy', 'scipy', 'pandas',
    'IPython', 'PIL', 'Pillow', 'wx', 'PyQt5', 'PyQt6', 'PySide2',
    'sphinx', 'pytest', 'setuptools', 'distutils',
    'xmlrpc', 'unittest', 'pydoc',
    'docx', 'docxtpl', 'jinja2', 'openpyxl',   # no usados en esta app
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
    """Filtra entradas del TOC que coincidan con los patrones regex."""
    import re
    return [e for e in toc if not any(re.search(p, e[0].replace('\\', '/')) for p in patterns)]


_exclude_patterns = [
    r'/test/', r'/tests/', r'__pycache__', r'\.pyc$',
    r'/doc/', r'/docs/', r'/examples/', r'/sample/',
    r'Qt6WebEngine(?!Widget|Core)',  # excluir módulos WebEngine no usados
    r'Qt6Quick', r'Qt6Qml', r'Qt6Designer',
    r'Qt6Bluetooth', r'Qt6Location', r'Qt6Positioning',
    r'Qt6RemoteObjects', r'Qt6Sensors', r'Qt6SerialPort',
]

a.datas    = _filter(a.datas,    _exclude_patterns)
a.binaries = _filter(a.binaries, _exclude_patterns)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)


# ── Splash screen (opcional) ──────────────────────────────────────────────────
_splash_path = src(os.path.join('imgs', 'splash_screen.png'))

if os.path.isfile(_splash_path):
    splash = Splash(
        _splash_path,
        binaries=a.binaries,
        datas=a.datas,
        text_pos=None,
        text_size=12,
        always_on_top=True,
    )
    _splash_binaries = splash.binaries
    _extra_scripts = [splash]
else:
    splash = None
    _splash_binaries = []
    _extra_scripts = []


# ── Ejecutable ────────────────────────────────────────────────────────────────
_icon_path = src(os.path.join('imgs', 'app_icon.ico'))
_icon = _icon_path if os.path.isfile(_icon_path) else None

exe = EXE(
    pyz,
    a.scripts,
    *_extra_scripts,
    _splash_binaries,
    [],
    name='MailDeDespacho',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        'Qt6Core.dll',
        'Qt6Gui.dll',
        'Qt6Widgets.dll',
        'Qt6Svg.dll',
        'Qt6WebEngineWidgets.dll',
        'Qt6WebEngineCore.dll',
        'vcruntime140.dll',
        'msvcp140.dll',
        'pythoncom312.dll',   # ajustar versión según Python instalado
        'pywintypes312.dll',  # ajustar versión según Python instalado
    ],
    runtime_tmpdir=None,
    console=False,                   # sin consola — app de escritorio
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_icon,
    onefile=False,                   # onedir para facilitar actualizaciones
)


coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    *([splash.binaries] if splash else []),
    strip=False,
    upx=True,
    upx_exclude=[
        'Qt6Core.dll',
        'Qt6Gui.dll',
        'Qt6Widgets.dll',
        'Qt6Svg.dll',
        'Qt6WebEngineWidgets.dll',
        'Qt6WebEngineCore.dll',
        'vcruntime140.dll',
        'msvcp140.dll',
    ],
    name='maildedespacho.app',   # nombre de la carpeta de salida — coincide con SGO/
)
