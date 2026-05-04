"""
svgs.py — Centralized SVG icon assets for MailDeDespacho.

ARCHITECTURE
-------------
All SVGs are stored as class constants with 'ICON_COLOR' placeholder.
Use helper functions to apply colors at runtime.

USAGE
------
    from svgs import SVG, apply_svg_icon
    apply_svg_icon(button, SVG.RRGG, QSize(24, 24), "#FFFFFF")

    from svgs import SVG, svg_pixmap
    pixmap = svg_pixmap(SVG.RRGG, QSize(24, 24), color="#FFFFFF")

COLOR STRATEGY
--------------
- All paths use fill="ICON_COLOR" as replaceable placeholder
- Use svg_colored() to replace ICON_COLOR with desired hex color
- Helper functions handle color replacement automatically

GROUPS
------
LINEA_NEGOCIO  → RRGG, TRANSPORTES
TIPO_PLANTILLA → POLIZA, ENDOSO, DECLARACION
MODO_ENVIO     → CORREO_NUEVO, RESPONDER_TODOS
ACCIONES       → OUTLOOK, LIMPIAR, PEGAR, AGREGAR, ELIMINAR
TITLEBAR       → MINIMIZAR, MAXIMIZAR, RESTAURAR, CERRAR
MSG            → ADVERTENCIA, INFORMACION, EXITO
MISC           → COMBO_ARROW, ARCHIVO_MSG, ADJUNTO
"""

import re
from PySide6.QtCore import QByteArray, QSize
from PySide6.QtGui import QPixmap, QPainter, QColor, QIcon
from PySide6.QtSvg import QSvgRenderer


# =============================================================================
# SVG CONSTANTS
# =============================================================================

class SVG:
    """SVG icon constants with replaceable ICON_COLOR placeholder."""

    # ── Línea de negocio ──────────────────────────────────────────────────────

    RRGG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10
        10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93
        0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54
        c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0
        1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41
        0 2.08-.8 3.97-2.1 5.39z"/>
    </svg>"""

    TRANSPORTES = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2
        c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4z
        M6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z
        m13.5-9l1.96 2.5H17V9.5h2.5zm-1.5 9c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5
        1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/>
    </svg>"""

    # ── Tipo de plantilla ─────────────────────────────────────────────────────

    POLIZA = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12
        c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z
        M8 15h8v2H8zm0-4h8v2H8zm0-4h5v2H8z"/>
    </svg>"""

    ENDOSO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25z
        M20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0
        l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
    </svg>"""

    DECLARACION = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.1 0-2 .9-2 2v14
        c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11z
        M7 10h5v5H7z"/>
    </svg>"""

    # ── Modo de envío ─────────────────────────────────────────────────────────

    CORREO_NUEVO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h10.09
        c-.06-.33-.09-.66-.09-1 0-.34.03-.67.08-1H4l8-4.99L16.97 14
        c.69-.58 1.51-.97 2.41-1.14L20 12.99V6l-8 5-8-5V6h16v6.09
        c.71.12 1.38.38 2 .72V6c0-1.1-.9-2-2-2z"/>
        <path fill="ICON_COLOR" d="M23 17.5c0 2.49-2.01 4.5-4.5 4.5S14 19.99 14 17.5
        14 15.01 16.01 13 18.5 13 23 15.01 23 17.5zm-2 0
        c0-1.38-1.12-2.5-2.5-2.5S16 16.12 16 17.5s1.12 2.5 2.5 2.5S21 18.88 21 17.5z"/>
        <path fill="ICON_COLOR" d="M21 16h-2v-2h-1v2h-2v1h2v2h1v-2h2z"/>
    </svg>"""

    RESPONDER_TODOS = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M7 8V5l-7 7 7 7v-3.1c5 0 8.5 1.6 11 5.1
        -1-5-4-10-11-11z"/>
        <path fill="ICON_COLOR" d="M21 3H10c-1.1 0-2 .9-2 2v1.5l2 2V5h11v14H10
        v-3.5l-2 2V19c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/>
    </svg>"""

    # ── Botones de acción ─────────────────────────────────────────────────────

    OUTLOOK = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
    </svg>"""

    LIMPIAR = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41
        10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
    </svg>"""

    PEGAR = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M19 2h-4.18C14.4.84 13.3 0 12 0c-1.3 0-2.4.84-2.82 2H5
        c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z
        m-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm7 18H5V4h2v3h10V4h2v16z"/>
    </svg>"""

    AGREGAR = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
    </svg>"""

    ELIMINAR = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12z
        M19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
    </svg>"""

    # ── Titlebar ──────────────────────────────────────────────────────────────

    MINIMIZAR = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M6 19h12v2H6z"/>
    </svg>"""

    MAXIMIZAR = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M3 3h18v18H3V3zm2 2v14h14V5H5z"/>
    </svg>"""

    RESTAURAR = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M18 4H10c-1.1 0-2 .9-2 2v2H6c-1.1 0-2 .9-2 2v10
        c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2v-2h2c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2z
        m-4 14H6v-8h8v8zm4-4h-2V8c0-1.1-.9-2-2-2h-4V6h8v8z"/>
    </svg>"""

    CERRAR = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41
        10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
    </svg>"""

    # ── Mensajes / diálogos ───────────────────────────────────────────────────

    ADVERTENCIA = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2V7h2v4z"/>
    </svg>"""

    INFORMACION = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10
        10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
    </svg>"""

    EXITO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10
        10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
    </svg>"""

    # ── Misc ──────────────────────────────────────────────────────────────────

    COMBO_ARROW = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M7 10l5 5 5-5z"/>
    </svg>"""

    ARCHIVO_MSG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16
        c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
    </svg>"""

    ADJUNTO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path fill="ICON_COLOR" d="M16.5 6v11.5c0 2.21-1.79 4-4 4s-4-1.79-4-4V5
        c0-1.38 1.12-2.5 2.5-2.5s2.5 1.12 2.5 2.5v10.5c0 .55-.45 1-1 1s-1-.45-1-1V6H10
        v9.5c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V5c0-2.21-1.79-4-4-4S7 2.79 7 5v12.5
        c0 3.04 2.46 5.5 5.5 5.5s5.5-2.46 5.5-5.5V6h-1.5z"/>
    </svg>"""


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def svg_colored(svg_str: str, color: str) -> str:
    """
    Replace the 'ICON_COLOR' placeholder in the SVG with the given color.

    Args:
        svg_str: Raw SVG string from SVG class
        color:   CSS hex color, e.g. '#FFFFFF' or '#0078d4'

    Returns:
        SVG string with color applied
    """
    return svg_str.replace("ICON_COLOR", color)


def svg_pixmap(svg_str: str, size: QSize, color: str = "#4f5f6f") -> QPixmap:
    """
    Render an SVG string to QPixmap with the specified color and size.

    Args:
        svg_str: Raw SVG string from SVG class
        size:    QSize of the resulting pixmap
        color:   Hex color to replace ICON_COLOR

    Returns:
        Rendered QPixmap (with alpha if transparent)
    """
    colored = svg_colored(svg_str, color)
    renderer = QSvgRenderer(QByteArray(colored.encode("utf-8")))
    pixmap = QPixmap(size)
    pixmap.fill(QColor(0, 0, 0, 0))  # transparent background
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap


def svg_icon(svg_str: str, size: QSize, color: str = "#4f5f6f") -> QIcon:
    """
    Create a QIcon from an SVG string.

    Args:
        svg_str: Raw SVG string from SVG class
        size:    QSize of the icon
        color:   Hex color to replace ICON_COLOR

    Returns:
        QIcon ready to assign with button.setIcon()
    """
    return QIcon(svg_pixmap(svg_str, size, color))


def apply_svg_icon(
    button,
    svg_str: str,
    size: QSize,
    color: str = "#4f5f6f"
) -> None:
    """
    Apply an SVG icon directly to a QPushButton.
    Shortcut for the most common pattern: create icon and assign it.

    Args:
        button:  Target QPushButton
        svg_str: Raw SVG string from SVG class
        size:    QSize of the icon
        color:   Hex color to replace ICON_COLOR
    """
    button.setIcon(svg_icon(svg_str, size, color))
    button.setIconSize(size)
