# coding: utf-8
"""
launcher.py — SGO Application Launcher

Reads launcher_apps.json from the same directory and displays
a frameless window with selectable app cards. Click a card to
select it, then press INICIAR (or double-click) to launch the app.

All visual values are centralized in PAL (palette) below.
Modify values in PAL to restyle the launcher without touching layout code.
"""

import sys
import os
import json
import subprocess

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame,
)
from PySide6.QtCore import Qt, QTimer, QByteArray
from PySide6.QtGui import QPixmap, QIcon, QFontDatabase
from framelesswindow import FramelessMainWindow

# =============================================================================
# PAL — single source of truth for ALL visual values in the launcher.
# Colors, borders, sizes, spacings, font properties — everything lives here.
# Groups are organized by component. State suffixes: _hover, _selected, _pressed.
# =============================================================================

PAL = {

    # ── Window ────────────────────────────────────────────────────────────────
    'window_bg':                    '#2b2d30',  # main background color
    'window_width':                 400,        # fixed width (px)
    'window_height':                600,        # initial height (px)
    'window_min_height':            300,        # minimum height (px)
    'window_margin_left':           20,         # inner margin — left (px)
    'window_margin_right':          20,         # inner margin — right (px)
    'window_margin_top':            20,         # inner margin — top (px)
    'window_margin_bottom':         20,         # inner margin — bottom (px)

    # ── Base typography ───────────────────────────────────────────────────────
    'font_family':                  'Segoe UI', # base font family
    'font_size_base':               '10pt',     # base font size
    'font_color_base':              '#d4d4d4',  # base text color
    'font_color_muted':             '#9a9a9a',  # secondary / muted text color

    # ── Header / Titlebar ─────────────────────────────────────────────────────
    'header_bg':                    '#2b2d30',  # header background
    'header_height':                52,         # header height (px)
    'header_spacing':               10,         # space between logo and title (px)
    'header_bottom_spacing':        12,         # space below header before card list (px)

    # ── Header separator line ─────────────────────────────────────────────────
    'sep_color':                    '#4a4d50',  # separator line color
    'sep_height':                   1,          # separator line height (px)
    'sep_margin_h':                 0,          # separator horizontal margin (px) — set >0 to indent

    # ── Logo ──────────────────────────────────────────────────────────────────
    'logo_size':                    24,         # logo icon render size (px)

    # ── System name label ─────────────────────────────────────────────────────
    'title_color':                  '#d4d4d4',  # system name text color
    'title_font_size':              '18pt',     # system name font size
    'title_font_weight':            'bold',     # system name font weight

    # ── Window control buttons (Minimize / Close) ────────────────────────────
    'wc_btn_width':                 32,         # button width (px)
    'wc_btn_height':                28,         # button height (px)
    'wc_btn_spacing':               4,          # gap between the two buttons (px)
    'wc_btn_icon_size':             12,         # icon size inside button (px)
    'wc_btn_icon_color':            '#9a9a9a',  # SVG stroke color (normal state)

    'wc_min_bg':                    '#3c3f41',  # minimize — normal background
    'wc_min_bg_hover':              '#4a4d50',  # minimize — hover background

    'wc_close_bg':                  '#3c3f41',  # close — normal background
    'wc_close_bg_hover':            '#c0292e',  # close — hover background

    # ── App card ──────────────────────────────────────────────────────────────
    'card_bg':                      '#3c3f41',  # card — normal background
    'card_border':                  '2px solid transparent', # card — normal border (full CSS string)
    'card_border_hover':            '2px solid #7ed957',     # card — hover border
    'card_border_selected':         '2px solid #7ed957',     # card — selected border
    'card_bg_selected':             '#7ed957',  # card — selected background
    'card_height':                  68,         # card height (px)
    'card_padding_h':               10,         # card horizontal padding (px)
    'card_padding_v':               8,          # card vertical padding (px)
    'card_spacing':                 8,          # vertical gap between cards (px)
    'card_icon_size':               36,         # app icon render size (px)
    'card_icon_area':               44,         # icon container fixed size (px)
    'card_icon_spacing':            12,         # gap between icon and app name (px)

    # ── App name label ────────────────────────────────────────────────────────
    'app_name_color':               '#d4d4d4',  # app name — normal color
    'app_name_color_selected':      '#1a1a1a',  # app name — selected color
    'app_name_font_size':           '10pt',     # app name font size
    'app_name_font_weight':         'bold',     # app name font weight
    'app_name_underline':           True,       # whether to underline app name

    # ── Version badge ─────────────────────────────────────────────────────────
    'badge_bg':                     '#4a4d50',          # badge — normal background
    'badge_color':                  '#9a9a9a',          # badge — normal text color
    'badge_bg_selected':            'rgba(0,0,0,0.2)',  # badge — selected background
    'badge_color_selected':         '#1a1a1a',          # badge — selected text color
    'badge_font_size':              '7pt',              # badge font size
    'badge_font_weight':            'normal',           # badge font weight
    'badge_padding':                '1px 5px',          # badge internal padding (CSS)
    'badge_height':                 18,                 # badge fixed height (px)
    'badge_min_width':              20,                 # badge minimum width (px)

    # ── Scroll area ───────────────────────────────────────────────────────────

    # ── INICIAR button ────────────────────────────────────────────────────────
    'iniciar_bg':                   '#4a5060',  # normal background
    'iniciar_bg_hover':             '#5a6070',  # hover background
    'iniciar_bg_pressed':           '#7ed957',  # pressed background
    'iniciar_color':                '#d4d4d4',  # normal text color
    'iniciar_color_pressed':        '#1a1a1a',  # pressed text color
    'iniciar_font_size':            '10pt',     # font size
    'iniciar_font_weight':          'bold',     # font weight
    'iniciar_letter_spacing':       '1px',      # letter spacing
    'iniciar_height':               44,         # button height (px)
    'iniciar_top_spacing':          12,         # space above button (px)

    # ── Layout margins — tuples of (left, top, right, bottom) ──────────────
    # Use *PAL['key'] to unpack directly into setContentsMargins()
    'margins_outer':            (0, 0, 0, 0),   # root layout — overridden by window_margin_* above
    'margins_header_wrapper':   (0, 0, 0, 0),   # header wrapper QVBoxLayout
    'margins_header_row':       (0, 0, 0, 0),   # title row QHBoxLayout — padding set via header_padding_*
    'margins_sep':              (0, 0, 0, 0),   # separator inner layout — set sep_margin_h for indent
    'margins_card_list':        (0, 12, 0, 12),  # card list container (left, top, right, bottom) — top/bottom = scroll padding
    'margins_footer':           (0, 0, 0, 0),   # footer QHBoxLayout

    # ── Layout spacings — single integer (px) ────────────────────────────────
    'spacing_outer':            0,   # between header / card list / footer
    'spacing_header_wrapper':   0,   # between title row and separator
    'spacing_sep_internal':     0,   # inside separator widget
    'spacing_footer':           0,   # inside footer layout


}

# =============================================================================
# SVG ICON STRINGS
# Paste SVG source code into the empty strings below.
# If left empty, simple line-based fallbacks are used automatically.
# =============================================================================

SVG_LOGO         = ""  # launcher logo — paste SVG source here
SVG_BTN_MINIMIZE = ""  # minimize icon — paste SVG source here (16x16 viewBox)
SVG_BTN_CLOSE    = ""  # close icon    — paste SVG source here (16x16 viewBox)


def _svg_minimize_fallback(color: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
        f'<line x1="2" y1="11" x2="14" y2="11" stroke="{color}" '
        f'stroke-width="1.5" stroke-linecap="round"/></svg>'
    )


def _svg_close_fallback(color: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
        f'<line x1="3" y1="3" x2="13" y2="13" stroke="{color}" '
        f'stroke-width="1.5" stroke-linecap="round"/>'
        f'<line x1="13" y1="3" x2="3" y2="13" stroke="{color}" '
        f'stroke-width="1.5" stroke-linecap="round"/></svg>'
    )


def _svg_to_icon(svg_str: str, size: int) -> QIcon:
    px = QPixmap()
    px.loadFromData(QByteArray(svg_str.encode()), 'SVG')
    if not px.isNull():
        return QIcon(px.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    return QIcon()


def _file_to_pixmap(path: str, size: int) -> QPixmap:
    px = QPixmap(resource_path(path))
    if px.isNull():
        return QPixmap()
    return px.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)


# =============================================================================
# QSS — pure template, all values from PAL, no literals
# =============================================================================

def build_launcher_qss(p: dict) -> str:
    underline = 'underline' if p.get('app_name_underline') else 'none'
    return f"""

/* ── Global base ── */
QWidget {{
    background-color: {p['window_bg']};
    color: {p['font_color_base']};
    font-family: '{p['font_family']}';
    font-size: {p['font_size_base']};
    outline: none;
    border: none;
}}

/* ── Header ── */
#Header {{
    background-color: {p['header_bg']};
}}

/* ── Separator ── */
#HeaderSep {{
    background-color: {p['sep_color']};
}}

/* ── System name ── */
#SystemName {{
    color: {p['title_color']};
    font-size: {p['title_font_size']};
    font-weight: {p['title_font_weight']};
    background-color: transparent;
}}

/* ── Window control — minimize ── */
#BtnMinimize {{
    background-color: {p['wc_min_bg']};
    border: none;
}}
#BtnMinimize:hover {{
    background-color: {p['wc_min_bg_hover']};
}}

/* ── Window control — close ── */
#BtnClose {{
    background-color: {p['wc_close_bg']};
    border: none;
}}
#BtnClose:hover {{
    background-color: {p['wc_close_bg_hover']};
}}

/* ── App card — normal ── */
#AppCard {{
    background-color: {p['card_bg']};
    border: {p['card_border']};
}}
#AppCard:hover {{
    border: {p['card_border_hover']};
}}

/* ── App card — selected ── */
#AppCardSelected {{
    background-color: {p['card_bg_selected']};
    border: {p['card_border_selected']};
}}

/* ── App name — normal ── */
#AppName {{
    color: {p['app_name_color']};
    font-size: {p['app_name_font_size']};
    font-weight: {p['app_name_font_weight']};
    text-decoration: {underline};
    background-color: transparent;
}}

/* ── App name — selected ── */
#AppNameSelected {{
    color: {p['app_name_color_selected']};
    font-size: {p['app_name_font_size']};
    font-weight: {p['app_name_font_weight']};
    text-decoration: {underline};
    background-color: transparent;
}}

/* ── Version badge — normal ── */
#VersionBadge {{
    background-color: {p['badge_bg']};
    color: {p['badge_color']};
    font-size: {p['badge_font_size']};
    font-weight: {p['badge_font_weight']};
    padding: {p['badge_padding']};
}}

/* ── Version badge — selected ── */
#VersionBadgeSelected {{
    background-color: {p['badge_bg_selected']};
    color: {p['badge_color_selected']};
    font-size: {p['badge_font_size']};
    font-weight: {p['badge_font_weight']};
    padding: {p['badge_padding']};
}}

/* ── INICIAR button ── */
#BtnIniciar {{
    background-color: {p['iniciar_bg']};
    color: {p['iniciar_color']};
    font-size: {p['iniciar_font_size']};
    font-weight: {p['iniciar_font_weight']};
    letter-spacing: {p['iniciar_letter_spacing']};
    border: none;
}}
#BtnIniciar:hover {{
    background-color: {p['iniciar_bg_hover']};
}}
#BtnIniciar:pressed {{
    background-color: {p['iniciar_bg_pressed']};
    color: {p['iniciar_color_pressed']};
}}

/* ── Scroll area transparent ── */
QScrollArea,
QScrollArea > QWidget,
QScrollArea > QWidget > QWidget {{
    background-color: transparent;
    border: none;
}}
"""


# =============================================================================
# HELPERS
# =============================================================================

def resource_path(rel: str) -> str:
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, rel)


def load_config() -> dict:
    try:
        with open(resource_path('launcher_apps.json'), encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"launcher_apps.json error: {e}")
        return {'system_name': 'SGO', 'logo_svg': '', 'apps': []}


# =============================================================================
# APP CARD WIDGET
# =============================================================================

class AppCard(QWidget):
    def __init__(self, app_data: dict, parent=None):
        super().__init__(parent)
        self._data = app_data
        self._selected = False
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName('AppCard')
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(PAL['card_height'])
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            PAL['card_padding_h'], PAL['card_padding_v'],
            PAL['card_padding_h'], PAL['card_padding_v'],
        )
        layout.setSpacing(PAL['card_icon_spacing'])

        # Icon
        self._iconLabel = QLabel()
        self._iconLabel.setFixedSize(PAL['card_icon_area'], PAL['card_icon_area'])
        self._iconLabel.setAlignment(Qt.AlignCenter)
        self._iconLabel.setAttribute(Qt.WA_TranslucentBackground)
        icon_path = self._data.get('icon_svg', '')
        if icon_path:
            px = _file_to_pixmap(icon_path, PAL['card_icon_size'])
            if not px.isNull():
                self._iconLabel.setPixmap(px)
                icon_path = None  # mark as loaded
        if icon_path is not None or not self._data.get('icon_svg', ''):
            self._iconLabel.setText('⬡')
            self._iconLabel.setStyleSheet(
                f"color: {PAL['font_color_muted']}; font-size: 20pt;"
            )
        layout.addWidget(self._iconLabel)

        # App name
        self._nameLabel = QLabel(self._data.get('name', ''))
        self._nameLabel.setObjectName('AppName')
        self._nameLabel.setAttribute(Qt.WA_TranslucentBackground)
        layout.addWidget(self._nameLabel, 1)

        # Version badge
        ver = self._data.get('version', '')
        if ver:
            self._verLabel = QLabel(ver)
            self._verLabel.setObjectName('VersionBadge')
            self._verLabel.setAlignment(Qt.AlignCenter)
            self._verLabel.setAttribute(Qt.WA_StyledBackground, True)
            self._verLabel.setFixedHeight(PAL['badge_height'])
            self._verLabel.setMinimumWidth(PAL['badge_min_width'])
            layout.addWidget(self._verLabel)
        else:
            self._verLabel = None

    def setSelected(self, selected: bool):
        self._selected = selected
        self.setObjectName('AppCardSelected' if selected else 'AppCard')
        self._nameLabel.setObjectName(
            'AppNameSelected' if selected else 'AppName'
        )
        if self._verLabel:
            self._verLabel.setObjectName(
                'VersionBadgeSelected' if selected else 'VersionBadge'
            )
        for w in (self, self._nameLabel, self._verLabel):
            if w:
                w.style().unpolish(w)
                w.style().polish(w)

    def appData(self) -> dict:
        return self._data

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.window()._selectCard(self)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.window()._launch()


# =============================================================================
# LAUNCHER WINDOW
# =============================================================================

class LauncherWindow(FramelessMainWindow):
    def __init__(self):
        super().__init__()
        self._config       = load_config()
        self._cards        = []
        self._selectedCard = None
        self._dragPos      = None

        # Apply accent from config
        accent = self._config.get('accent_color', PAL['card_bg_selected'])
        if accent != PAL['card_bg_selected']:
            for key in ('card_border_hover', 'card_border_selected',
                        'card_bg_selected', 'iniciar_bg_pressed'):
                if 'border' in key:
                    PAL[key] = f"2px solid {accent}"
                else:
                    PAL[key] = accent

        self.setFixedWidth(PAL['window_width'])
        self.setMinimumHeight(PAL['window_min_height'])
        self.resize(PAL['window_width'], PAL['window_height'])
        self.setWindowTitle(self._config.get('system_name', 'SGO'))

        self._buildUI()
        self.setStyleSheet(build_launcher_qss(PAL))

    # ── UI construction ───────────────────────────────────────────────────────

    def _buildUI(self):
        root = QWidget()
        root.setAttribute(Qt.WA_StyledBackground, True)

        outer = QVBoxLayout(root)
        outer.setContentsMargins(
            PAL['window_margin_left'],  PAL['window_margin_top'],
            PAL['window_margin_right'], PAL['window_margin_bottom'],
        )
        outer.setSpacing(PAL['spacing_outer'])

        outer.addWidget(self._buildHeader())
        outer.addSpacing(PAL['header_bottom_spacing'])
        outer.addWidget(self._buildCardList(), 1)
        outer.addSpacing(PAL['iniciar_top_spacing'])
        outer.addWidget(self._buildFooter())

        self.setCentralWidget(root)

    def _buildHeader(self) -> QWidget:
        wrapper = QWidget()
        wrapper.setAttribute(Qt.WA_StyledBackground, True)
        wl = QVBoxLayout(wrapper)
        wl.setContentsMargins(*PAL['margins_header_wrapper'])
        wl.setSpacing(PAL['spacing_header_wrapper'])

        # Title bar row
        header = QWidget()
        header.setObjectName('Header')
        header.setAttribute(Qt.WA_StyledBackground, True)
        header.setFixedHeight(PAL['header_height'])
        header.mousePressEvent   = self._titleMousePress
        header.mouseMoveEvent    = self._titleMouseMove
        header.mouseReleaseEvent = self._titleMouseRelease

        hl = QHBoxLayout(header)
        hl.setContentsMargins(*PAL['margins_header_row'])
        hl.setSpacing(PAL['header_spacing'])

        # Logo — inline SVG takes priority, then file path from config
        logo_sz = PAL['logo_size']
        if SVG_LOGO.strip():
            logo_px = _svg_to_icon(SVG_LOGO, logo_sz).pixmap(logo_sz, logo_sz)
            lbl = QLabel()
            lbl.setPixmap(logo_px)
            lbl.setFixedSize(logo_sz, logo_sz)
            lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            hl.addWidget(lbl)
        else:
            logo_path = self._config.get('logo_svg', '')
            if logo_path:
                lbl = QLabel()
                lbl.setPixmap(_file_to_pixmap(logo_path, logo_sz))
                lbl.setFixedSize(logo_sz, logo_sz)
                lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)
                hl.addWidget(lbl)

        # System name
        name_lbl = QLabel(self._config.get('system_name', 'SGO'))
        name_lbl.setObjectName('SystemName')
        name_lbl.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        hl.addWidget(name_lbl)
        hl.addStretch()

        # Window control buttons
        btn_w  = PAL['wc_btn_width']
        btn_h  = PAL['wc_btn_height']
        ic_sz  = PAL['wc_btn_icon_size']
        color  = PAL['wc_btn_icon_color']

        min_svg = SVG_BTN_MINIMIZE.strip() or _svg_minimize_fallback(color)
        cls_svg = SVG_BTN_CLOSE.strip()    or _svg_close_fallback(color)

        self._btnMin = QPushButton()
        self._btnMin.setObjectName('BtnMinimize')
        self._btnMin.setFixedSize(btn_w, btn_h)
        self._btnMin.setIcon(_svg_to_icon(min_svg, ic_sz))
        self._btnMin.setToolTip('Minimizar')
        self._btnMin.clicked.connect(self.showMinimized)

        self._btnClose = QPushButton()
        self._btnClose.setObjectName('BtnClose')
        self._btnClose.setFixedSize(btn_w, btn_h)
        self._btnClose.setIcon(_svg_to_icon(cls_svg, ic_sz))
        self._btnClose.setToolTip('Cerrar')
        self._btnClose.clicked.connect(self.close)

        hl.addSpacing(PAL['wc_btn_spacing'])
        hl.addWidget(self._btnMin)
        hl.addWidget(self._btnClose)

        wl.addWidget(header)

        # Separator
        sep = QWidget()
        sep.setObjectName('HeaderSep')
        sep.setAttribute(Qt.WA_StyledBackground, True)
        sep.setFixedHeight(PAL['sep_height'])
        sep_wrap = QHBoxLayout(sep)
        sep_wrap.setContentsMargins(*PAL['margins_sep'])
        sep_wrap.setSpacing(PAL['spacing_sep_internal'])
        wl.addWidget(sep)

        return wrapper

    def _buildCardList(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        vl = QVBoxLayout(container)
        vl.setContentsMargins(*PAL['margins_card_list'])
        vl.setSpacing(PAL['card_spacing'])

        for app_data in self._config.get('apps', []):
            if not app_data.get('enabled', True):
                continue
            card = AppCard(app_data)
            self._cards.append(card)
            vl.addWidget(card)

        vl.addStretch()
        scroll.setWidget(container)
        return scroll

    def _buildFooter(self) -> QWidget:
        footer = QWidget()
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(*PAL['margins_footer'])
        fl.setSpacing(PAL['spacing_footer'])

        self._btnIniciar = QPushButton('INICIAR')
        self._btnIniciar.setObjectName('BtnIniciar')
        self._btnIniciar.setFixedHeight(PAL['iniciar_height'])
        self._btnIniciar.setCursor(Qt.PointingHandCursor)
        self._btnIniciar.clicked.connect(self._launch)
        fl.addWidget(self._btnIniciar)

        return footer

    # ── Drag ─────────────────────────────────────────────────────────────────

    def _titleMousePress(self, event):
        if event.button() == Qt.LeftButton:
            self._dragPos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )

    def _titleMouseMove(self, event):
        if self._dragPos and event.buttons() == Qt.LeftButton and not self.isMaximized():
            self.move(event.globalPosition().toPoint() - self._dragPos)

    def _titleMouseRelease(self, event):
        self._dragPos = None

    # ── Selection & Launch ────────────────────────────────────────────────────

    def _selectCard(self, card: AppCard):
        if self._selectedCard and self._selectedCard is not card:
            self._selectedCard.setSelected(False)
        self._selectedCard = card
        card.setSelected(True)

    def _launch(self):
        if not self._selectedCard:
            return
        exe = self._selectedCard.appData().get('exe_path', '')
        if not exe:
            return
        if not os.path.isabs(exe):
            base = os.path.dirname(os.path.abspath(
                sys.executable if getattr(sys, 'frozen', False) else __file__
            ))
            exe = os.path.join(base, exe)
        if os.path.isfile(exe):
            subprocess.Popen([exe], cwd=os.path.dirname(exe))
            QTimer.singleShot(200, self.close)
        else:
            orig = self._btnIniciar.text()
            self._btnIniciar.setText('No encontrado')
            QTimer.singleShot(1800, lambda: self._btnIniciar.setText(orig))


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    for ff in ['fonts/OpenSans-Regular.ttf', 'fonts/OpenSans-Bold.ttf']:
        fp = resource_path(ff)
        if os.path.isfile(fp):
            QFontDatabase.addApplicationFont(fp)

    window = LauncherWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
