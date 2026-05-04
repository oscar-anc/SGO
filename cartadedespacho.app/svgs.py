"""
svgs.py — Centralized SVG icon assets for CartaDeDespacho.

ARCHITECTURE
-------------
SVGs are split into two categories:

1. CODE-LOADED (this file) — loaded as QPixmap/QIcon in Python via
   QPixmap.loadFromData(). No files needed, no QSS url() involved.
   Colors use 'currentColor' (inherits from widget) or parameterized colors.
   Includes: action icons, toolbar icons, formatting icons, window controls.

2. FILE-BASED (imgs/ folder) — referenced by QSS url(imgs/file.svg).
   Qt QSS url() only accepts file paths, not inline SVG strings.
   Colors are hardcoded in the SVG files.
   Includes: arrows (combo/date dropdowns), calendar icon, checkboxes.

COLOR STRATEGY
--------------
- Icons on colored backgrounds (buttons): white/default via function parameter
- Icons inheriting widget color: use 'currentColor'
- Icons with fixed colors: color hardcoded in SVG (e.g., #858889)
- Parameterized icons: accept color as function argument with sensible default

FUTURE: For dynamic colors in file-based SVGs without disk writes,
investigate QProxyStyle.drawPrimitive() for checkbox/radio.
"""

from PySide6.QtWidgets import QPushButton, QTableWidget, QHeaderView
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QByteArray, Qt

from theme import QSSA


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _svg_to_pixmap(svg_str: str, size: int = 16) -> QPixmap:
    """Convert SVG string to QPixmap with smooth scaling."""
    px = QPixmap()
    px.loadFromData(QByteArray(svg_str.encode('utf-8')), 'SVG')
    if not px.isNull():
        return px.scaled(
            size, size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
    return QPixmap()


def svg_to_qicon(svg_str: str, size: int = 16) -> QIcon:
    """
    Convert an SVG string to a QIcon scaled to size×size pixels.
    Useful for setting icons on buttons or other widgets.
    """
    px = _svg_to_pixmap(svg_str, size)
    return QIcon(px) if not px.isNull() else QIcon()


def make_svg_button(svg_str: str, object_name: str = '', size: int = 32,
                    icon_size: int = 18, tooltip: str = '', role: str = '') -> QPushButton:
    """
    Build a square icon-only QPushButton from an inline SVG string.
    Colors controlled via QSS role property (preferred) or objectName.
    Returns a QPushButton ready to use.
    """
    btn = QPushButton()
    if role:
        btn.setProperty('role', role)
        btn.style().unpolish(btn)
        btn.style().polish(btn)
    elif object_name:
        btn.setObjectName(object_name)
    btn.setFixedSize(size, size)
    btn.setToolTip(tooltip)

    px = _svg_to_pixmap(svg_str, icon_size)
    if not px.isNull():
        btn.setIcon(QIcon(px))
    return btn


def make_styled_table() -> QTableWidget:
    """
    Create a QTableWidget with app-styled headers and proportional columns.
    Returns a configured QTableWidget instance.
    """
    tbl = QTableWidget()
    tbl.verticalHeader().setDefaultSectionSize(28)
    tbl.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    tbl.verticalHeader().setFixedWidth(QSSA['endtable_col_header_width'])
    tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    tbl.horizontalHeader().setStretchLastSection(True)
    tbl.setAlternatingRowColors(True)
    tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
    tbl.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
    return tbl


# =============================================================================
# ACTION ICONS (trash, view, edit, excel, gear, download)
# =============================================================================

def get_svg_trash(color: str = '#FFFFFF') -> str:
    """Trash/delete icon. Default white — sits on colored btn_quitar_svg_bg."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'<polyline points="3 6 5 6 21 6"/>'
        f'<path d="M19 6l-1 14H6L5 6"/>'
        f'<path d="M10 11v6M14 11v6"/>'
        f'<path d="M9 6V4h6v2"/>'
        f'</svg>'
    )


SVG_TRASH = get_svg_trash('#FFFFFF')


def get_svg_download_template(color: str = '#858889') -> str:
    """Download template icon - downward arrow into document. viewBox 24x24."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
        f'<polyline points="14 2 14 8 20 8"/>'
        f'<line x1="12" y1="18" x2="12" y2="12"/>'
        f'<polyline points="9 15 12 18 15 15"/>'
        f'</svg>'
    )


SVG_DOWNLOAD_TEMPLATE = get_svg_download_template()


# Fixed-color icons (no parameterization needed)
SVG_VIEW = """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none">
  <path fill-rule="evenodd" clip-rule="evenodd" d="M10 .5a9.5 9.5 0 1 0 0 19c2.082 0 4.008-.67 5.573-1.806l4.72 4.72a1 1 0 0 0 1.414 0l.707-.707a1 1 0 0 0 0-1.414l-4.72-4.72A9.46 9.46 0 0 0 19.5 10 9.5 9.5 0 0 0 10 .5M3.5 10a6.5 6.5 0 1 1 13 0 6.5 6.5 0 0 1-13 0" fill="#858889"/>
</svg>"""

SVG_EDIT = """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none">
  <path d="M17.067 2.272a3.568 3.568 0 0 1 3.888 5.818l-.518.518-5.045-5.045.518-.518a3.6 3.6 0 0 1 1.157-.773m-3.09 2.705L3.655 15.3a1 1 0 0 0-.258.444l-1.362 4.993a1 1 0 0 0 1.228 1.228l4.993-1.362a1 1 0 0 0 .444-.258l10.323-10.322z" fill="#858889"/>
</svg>"""

SVG_EXCEL_IMPORT = """<svg xmlns="http://www.w3.org/2000/svg" height="18" width="18" viewBox="0 0 0.585 0.585" xml:space="preserve">
  <path style="fill:#858889" d="M.566.068H.36v.067h.068v.046H.36v.044h.068V.27H.36v.045h.068V.36H.36v.045h.068V.45H.36v.068h.206c.01 0 .019-.009.019-.02V.087Q.584.069.566.067M.54.45H.45V.405h.09zm0-.09H.45V.315h.09zm0-.09H.45V.225h.09zm0-.09H.45V.135h.09zM0 .065V.52l.337.065V0zm.213.342L.174.333.169.318H.168L.163.334.124.408H.063L.136.294.07.18h.062l.033.068.007.019h.001L.18.247.216.179h.057L.205.292l.07.115z"/>
</svg>"""


# =============================================================================
# TOOLBAR ICONS (gear, column operations)
# =============================================================================

def get_svg_gear(color: str = '#9a9a9a') -> str:
    """Gear/cog icon — Flowbite outline style."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">'
        f'<path stroke="{color}" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"'
        f' d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 0 0 2.573 1.066c1.543-.94 3.31.826 2.37'
        f' 2.37a1.724 1.724 0 0 0 1.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 0 0-1.066'
        f' 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 0 0-2.572 1.065c-.426 1.756-2.924'
        f' 1.756-3.35 0a1.724 1.724 0 0 0-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724'
        f' 1.724 0 0 0-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 0 0'
        f' 1.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>'
        f'<circle cx="12" cy="12" r="3" stroke="{color}" stroke-width="2"/>'
        '</svg>'
    )


def get_svg_col_add(color: str = '#FFFFFF') -> str:
    """Add column icon — plus sign."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'<line x1="12" y1="5" x2="12" y2="19"/>'
        f'<line x1="5" y1="12" x2="19" y2="12"/>'
        f'</svg>'
    )


def get_svg_col_remove(color: str = '#FFFFFF') -> str:
    """Remove column icon — minus sign."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'<line x1="5" y1="12" x2="19" y2="12"/>'
        f'</svg>'
    )


def get_svg_col_rename(color: str = '#FFFFFF') -> str:
    """Rename/update column icon — circular arrow."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'<polyline points="1 4 1 10 7 10"/>'
        f'<path d="M3.51 15a9 9 0 1 0 .49-4.5"/>'
        f'</svg>'
    )


# =============================================================================
# COLLAPSIBLE CARD CHEVRON
# =============================================================================

def get_svg_chevron(expanded: bool = True, color: str = '#858889', size: int = 18) -> str:
    """
    Chevron icon for collapsible cards (stroke style).
    expanded=True  → chevron pointing down (body visible)
    expanded=False → chevron pointing right (body collapsed)
    """
    path = "M4,8 L12,16 L20,8" if expanded else "M8,4 L16,12 L8,20"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"'
        f' width="{size}" height="{size}">'
        f'<path d="{path}" fill="none" stroke="{color}"'
        f' stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
        f'</svg>'
    )


# =============================================================================
# TEXT FORMATTING ICONS (bold, italic, underline, list, clear)
# =============================================================================

def get_svg_bold(color: str = '#4f5f6f') -> str:
    """Bold — Flowbite outline icon."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">'
        f'<path stroke="{color}" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"'
        f' d="M6 12h8a4 4 0 0 0 0-8H6v8Zm0 0h9a4 4 0 0 1 0 8H6v-8Z"/>'
        '</svg>'
    )


def get_svg_italic(color: str = '#4f5f6f') -> str:
    """Italic — Flowbite outline icon."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">'
        f'<path stroke="{color}" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"'
        f' d="M11 5h4M7 19h4m1-14-4 14"/>'
        '</svg>'
    )


def get_svg_underline(color: str = '#4f5f6f') -> str:
    """Underline — Flowbite outline icon."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">'
        f'<path stroke="{color}" stroke-linecap="round" stroke-width="2"'
        f' d="M6 19h12M8 5v8a4 4 0 0 0 8 0V5M6 5h4m4 0h4"/>'
        '</svg>'
    )


def get_svg_list_bullet(color: str = '#4f5f6f') -> str:
    """Bullet list — Flowbite outline icon."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">'
        f'<path stroke="{color}" stroke-linecap="round" stroke-width="2"'
        f' d="M9 6h11M9 12h11M9 18h11M5 6v.01M5 12v.01M5 18v.01"/>'
        '</svg>'
    )


def get_svg_clear_format(color: str = '#4f5f6f') -> str:
    """Clear formatting — Flowbite outline icon."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none">'
        f'<path stroke="{color}" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"'
        f' d="M6 5h12M6 9h12m-8 4h8m-6 4h6M3 19l4-4m0 0 4-4m-4 4-4-4m4 4 4 4"/>'
        '</svg>'
    )


# =============================================================================
# WINDOW TITLEBAR BUTTONS (minimize, maximize, restore, close)
# =============================================================================

def get_svg_minimize_btn(color: str = '#ffffff') -> str:
    """Minimize button — horizontal line, Flowbite-style. viewBox 14x14 square."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 14">'
        f'<line x1="2" y1="7" x2="12" y2="7" stroke="{color}"'
        f' stroke-width="1.5" stroke-linecap="round"/>'
        '</svg>'
    )


def get_svg_maximize_btn(color: str = '#ffffff') -> str:
    """Maximize button — open square. viewBox 14x14 square."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 14">'
        f'<rect x="2" y="2" width="10" height="10" rx="1"'
        f' stroke="{color}" stroke-width="1.5" fill="none"/>'
        '</svg>'
    )


def get_svg_restore_btn(color: str = '#ffffff') -> str:
    """Restore button — two overlapping squares. viewBox 14x14 square."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 14">'
        f'<rect x="4" y="1" width="9" height="9" rx="1"'
        f' stroke="{color}" stroke-width="1.5" fill="none"/>'
        f'<rect x="1" y="4" width="9" height="9" rx="1"'
        f' stroke="{color}" stroke-width="1.5" fill="none"/>'
        '</svg>'
    )


def get_svg_close_btn(color: str = '#ffffff') -> str:
    """Close button X — Flowbite outline style. viewBox 14x14 square."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 14">'
        f'<path stroke="{color}" stroke-linecap="round" stroke-linejoin="round"'
        f' stroke-width="1.5" d="M1 1 13 13M13 1 1 13"/>'
        '</svg>'
    )


# =============================================================================
# FORMAT BUTTON SEPARATOR ICON
# =============================================================================

def get_svg_plus_separator(color: str = '#888888') -> str:
    """Plus separator icon for dual format button. viewBox 10x10 square."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
        f'<line x1="5" y1="1" x2="5" y2="9" stroke="{color}"'
        f' stroke-width="1.5" stroke-linecap="round"/>'
        f'<line x1="1" y1="5" x2="9" y2="5" stroke="{color}"'
        f' stroke-width="1.5" stroke-linecap="round"/>'
        '</svg>'
    )


# =============================================================================
# DOCUMENT TYPE ICONS (Word, PDF)
# =============================================================================

def get_svg_word() -> str:
    """Microsoft Word 2025 official SVG icon. viewBox: 0 0 35 36."""
    return (
        '<svg id="uuid-70d351c3-9d52-4d9c-bf87-a1f0a8eb5856" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 35 36">'
        '<defs>'
        '<radialGradient id="uuid-ed2a8eb8-fce0-4bde-952b-86ec8e241ee9" cx="-619.29" cy="488.84" fx="-619.29" fy="488.84" r="1" gradientTransform="translate(29495.74 9885.89) scale(47.57 -20.15)" gradientUnits="userSpaceOnUse">'
        '<stop offset=".18" stop-color="#1657f4"/><stop offset=".57" stop-color="#0036c4"/></radialGradient>'
        '<linearGradient id="uuid-07943580-643e-4611-b102-f1fc868bd013" x1="5" y1="97" x2="27.97" y2="97" gradientTransform="translate(0 116) scale(1 -1)" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#66c0ff"/><stop offset=".26" stop-color="#0094f0"/></linearGradient>'
        '<radialGradient id="uuid-4901e95c-54b1-4d8b-bf14-0e9c7bb90b87" cx="-637.72" cy="517.98" fx="-637.72" fy="517.98" r="1" gradientTransform="translate(-40017.96 -12225.34) rotate(133.55) scale(29.36 -72.32)" gradientUnits="userSpaceOnUse"><stop offset=".14" stop-color="#d471ff"/><stop offset=".83" stop-color="#509df5" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="uuid-9988b974-07fe-47ee-9919-3660c45bf150" cx="-611.76" cy="514.18" fx="-611.76" fy="514.18" r="1" gradientTransform="translate(1363.5 17878.99) rotate(90) scale(18.62 -101.65)" gradientUnits="userSpaceOnUse"><stop offset=".28" stop-color="#4f006f" stop-opacity="0"/><stop offset="1" stop-color="#4f006f"/></radialGradient>'
        '<linearGradient id="uuid-0983714d-6efe-4203-b8da-170f38fe7225" x1="5" y1="107.22" x2="35" y2="106.72" gradientTransform="translate(0 116) scale(1 -1)" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#9deaff"/><stop offset=".2" stop-color="#3bd5ff"/></linearGradient>'
        '<radialGradient id="uuid-ca2eb1c3-4f62-4719-880a-75c33625c87b" cx="-650.27" cy="515.34" fx="-650.27" fy="515.34" r="1" gradientTransform="translate(-26921.47 -31089.42) rotate(166.85) scale(29.49 -70.64)" gradientUnits="userSpaceOnUse"><stop offset=".06" stop-color="#e4a7fe"/><stop offset=".54" stop-color="#e4a7fe" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="uuid-b0298544-4529-40e9-8c27-57a5501fe390" cx="-600.8" cy="515.58" fx="-600.8" fy="515.58" r="1" gradientTransform="translate(1363.5 17878.99) rotate(45) scale(22.63 -22.63)" gradientUnits="userSpaceOnUse"><stop offset=".08" stop-color="#367af2"/><stop offset=".87" stop-color="#001a8f"/></radialGradient>'
        '<radialGradient id="uuid-6f25899f-fcb5-4141-ab07-b61a25bf93ff" cx="-598.04" cy="557.24" fx="-598.04" fy="557.24" r="1" gradientTransform="translate(-7105.12 6724.6) rotate(90) scale(11.2 -12.77)" gradientUnits="userSpaceOnUse"><stop offset=".59" stop-color="#2763e5" stop-opacity="0"/><stop offset=".97" stop-color="#58aafe"/></radialGradient>'
        '</defs>'
        '<path d="M5,27.09l14-17.09,16,11.11v11.39c0,1.93-1.57,3.5-3.5,3.5H11c-3.31,0-6-2.69-6-6v-2.91Z" style="fill:url(#uuid-ed2a8eb8-fce0-4bde-952b-86ec8e241ee9);"/>'
        '<path d="M5,15.04c0-2.49,2.01-4.5,4.5-4.5h20.39l5.11-2.54v12.5c0,1.93-1.57,3.5-3.5,3.5H11c-3.31,0-6,2.69-6,6v-14.96Z" style="fill:url(#uuid-07943580-643e-4611-b102-f1fc868bd013);"/>'
        '<path d="M5,15.04c0-2.49,2.01-4.5,4.5-4.5h20.39l5.11-2.54v12.5c0,1.93-1.57,3.5-3.5,3.5H11c-3.31,0-6,2.69-6,6v-14.96Z" style="fill:url(#uuid-4901e95c-54b1-4d8b-bf14-0e9c7bb90b87); fill-opacity:.6;"/>'
        '<path d="M5,15.04c0-2.49,2.01-4.5,4.5-4.5h20.39l5.11-2.54v12.5c0,1.93-1.57,3.5-3.5,3.5H11c-3.31,0-6,2.69-6,6v-14.96Z" style="fill:url(#uuid-9988b974-07fe-47ee-9919-3660c45bf150); fill-opacity:.1;"/>'
        '<path d="M5,6C5,2.69,7.69,0,11,0h20.5c1.93,0,3.5,1.57,3.5,3.5v5c0,1.93-1.57,3.5-3.5,3.5H11c-3.31,0-6,2.69-6,6V6Z" style="fill:url(#uuid-0983714d-6efe-4203-b8da-170f38fe7225);"/>'
        '<path d="M5,6C5,2.69,7.69,0,11,0h20.5c1.93,0,3.5,1.57,3.5,3.5v5c0,1.93-1.57,3.5-3.5,3.5H11c-3.31,0-6,2.69-6,6V6Z" style="fill:url(#uuid-ca2eb1c3-4f62-4719-880a-75c33625c87b); fill-opacity:.8;"/>'
        '<rect y="17" width="16" height="16" rx="3.25" ry="3.25" style="fill:url(#uuid-b0298544-4529-40e9-8c27-57a5501fe390);"/>'
        '<rect y="17" width="16" height="16" rx="3.25" ry="3.25" style="fill:url(#uuid-6f25899f-fcb5-4141-ab07-b61a25bf93ff); fill-opacity:.65;"/>'
        '<path d="M13.49,20.43l-1.97,9.14h-2.35s-1.16-5.48-1.16-5.48l-1.22,5.49h-2.38l-1.89-9.14h1.94l1.17,6.03,1.16-6.03h2.38l1.21,6.03,1.14-6.03h1.97Z" style="fill:#fff;"/>'
        '</svg>'
    )


def get_svg_pdf() -> str:
    """PDF file icon — clean red rounded square design. viewBox: 0 0 60 58.5."""
    return (
        '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" x="0" y="0" '
        'viewBox="0 0 60 58.5" xml:space="preserve">'
        '<path d="M10.6 0h38.8C55.2 0 60 4.8 60 10.6v37.2c0 5.9-4.8 10.6-10.6 10.6H10.6C4.8 58.5 0 53.7 0 47.9V10.6C0 4.8 4.8 0 10.6 0z" fill="#b30b00"/>'
        '<path d="M48.2 33.9C47 32.6 44.7 32 41.4 32c-1.8 0-3.7.2-5.5.5-1.2-1.1-2.2-2.4-3.2-3.7-.7-1-1.4-2-2-3.1 1-2.8 1.6-5.8 1.8-8.8 0-2.7-1.1-5.6-4.1-5.6-1 0-2 .6-2.5 1.5-1.3 2.2-.8 6.7 1.3 11.4-.7 2.1-1.5 4.2-2.4 6.5-.8 2-1.7 3.9-2.8 5.7-3.1 1.2-9.6 4.2-10.2 7.5-.2 1 .1 2 .9 2.6.7.6 1.7 1 2.7.9 3.9 0 7.8-5.4 10.5-10.1 1.5-.5 3-1 4.6-1.4 1.7-.4 3.3-.8 4.8-1.1 4.2 3.6 7.9 4.2 9.7 4.2 2.5 0 3.5-1.1 3.8-2 .4-1.1.2-2.3-.6-3.1zm-2.7 1.9c-.1.7-.9 1.2-1.9 1.2-.3 0-.6 0-.9-.1-2-.5-3.9-1.5-5.5-2.8 1.3-.2 2.7-.3 4-.3.9 0 1.8.1 2.7.2.9.2 1.9.6 1.6 1.8zM27.6 13.7c.2-.3.5-.5.9-.6 1 0 1.2 1.1 1.2 2.1-.1 2.3-.5 4.5-1.2 6.7-1.7-4.3-1.5-7.2-.9-8.2zm5.6 19.2c-1.1.2-2.2.5-3.3.8-.8.2-1.6.5-2.5.7.4-.9.8-1.8 1.2-2.6.5-1.1.9-2.2 1.3-3.3.4.6.7 1.1 1.1 1.6.7 1 1.5 1.9 2.2 2.8zm-12.1 5.8c-2.5 4-5 6.6-6.4 6.6-.2 0-.5-.1-.6-.2-.3-.2-.4-.6-.3-.9.2-1.5 3.1-3.6 7.3-5.5z" fill="#fff"/>'
        '</svg>'
    )
