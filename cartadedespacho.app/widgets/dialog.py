# coding: utf-8
"""
widgets/dialog.py — CustomDialog base class.

Pure QDialog + Qt.FramelessWindowHint with a custom titlebar.
No FramelessDialog dependency — avoids the Win32 nativeEvent conflict
that breaks resize on the main window after a dialog closes.

Titlebar: Maximize + Close buttons (reusing TitleBarButton from framelesswindow)
Resize:   QDialog.setSizeGripEnabled(True) — native Qt grip in bottom-right corner
Drag:     mousePressEvent / mouseMoveEvent on titlebar widget
"""

from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QMouseEvent
from framelesswindow.titlebar.title_bar_buttons import MinimizeButton, MaximizeButton, CloseButton
from theme import QSSA


class _DialogTitleBar(QWidget):
    """
    Custom titlebar for CustomDialog.
    Draggable. Buttons: Maximize + Close.
    Heights and colors from QSSA — visually identical to main window titlebar.
    """

    def __init__(self, title: str, parent, close_only: bool = False):
        super().__init__(parent)
        self._dragPos  = QPoint()
        self._dragging = False

        h = QSSA.get('dialog_titlebar_height', 30)
        self.setFixedHeight(h)
        self.setObjectName('TitleBar')
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Background
        pal = self.palette()
        pal.setColor(pal.ColorRole.Window,
                     QColor(QSSA.get('titlebar_bg', '#4f5f6f')))
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 0, 0)
        layout.setSpacing(0)

        # Title label
        self._titleLabel = QLabel(title)
        self._titleLabel.setObjectName('TitleLabel')
        self._titleLabel.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(self._titleLabel)

        # Maximize button
        self.maxBtn = MaximizeButton(self)
        self.maxBtn.setFixedSize(46, h)
        self.maxBtn.clicked.connect(self._toggleMax)

        # Close button
        self.closeBtn = CloseButton(self)
        self.closeBtn.setFixedSize(46, h)
        self.closeBtn.clicked.connect(parent.close)

        # Apply colors from QSSA
        btn_text      = QColor(QSSA.get('titlebar_btn_text',        '#FFFFFF'))
        btn_hover     = QColor(QSSA.get('titlebar_btn_hover_bg',    '#59c2e6'))
        btn_pressed   = QColor(QSSA.get('titlebar_btn_pressed_bg',  '#3aaac8'))
        close_hover   = QColor(QSSA.get('titlebar_close_hover_bg',  '#fc4c7a'))
        close_pressed = QColor(QSSA.get('titlebar_close_pressed_bg','#d93060'))

        self.maxBtn.setNormalColor(btn_text)
        self.maxBtn.setHoverColor(btn_text)
        self.maxBtn.setPressedColor(btn_text)
        self.maxBtn.setNormalBackgroundColor(QColor(0, 0, 0, 0))
        self.maxBtn.setHoverBackgroundColor(btn_hover)
        self.maxBtn.setPressedBackgroundColor(btn_pressed)

        self.closeBtn.setNormalColor(btn_text)
        self.closeBtn.setHoverColor(btn_text)
        self.closeBtn.setPressedColor(btn_text)
        self.closeBtn.setNormalBackgroundColor(QColor(0, 0, 0, 0))
        self.closeBtn.setHoverBackgroundColor(close_hover)
        self.closeBtn.setPressedBackgroundColor(close_pressed)

        self.minBtn = MinimizeButton(self)
        self.minBtn.setFixedSize(46, h)
        self.minBtn.clicked.connect(parent.showMinimized)
        # Apply same colors as maxBtn
        self.minBtn.setNormalColor(btn_text)
        self.minBtn.setHoverColor(btn_text)
        self.minBtn.setPressedColor(btn_text)
        self.minBtn.setNormalBackgroundColor(QColor(0, 0, 0, 0))
        self.minBtn.setHoverBackgroundColor(btn_hover)
        self.minBtn.setPressedBackgroundColor(btn_pressed)

        if not close_only:
            layout.addWidget(self.minBtn)
            layout.addWidget(self.maxBtn)
        else:
            self.minBtn.hide()
            self.maxBtn.hide()
        layout.addWidget(self.closeBtn)

    def _toggleMax(self):
        win = self.window()
        if win.isMaximized():
            win.showNormal()
            self.maxBtn.setMaxState(False)
        else:
            win.showMaximized()
            self.maxBtn.setMaxState(True)

    def setTitle(self, title: str):
        self._titleLabel.setText(title)

    # ── Drag support ──────────────────────────────────────────────────────────

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._dragPos  = event.globalPosition().toPoint() -                              self.window().frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging and event.buttons() & Qt.MouseButton.LeftButton:
            win = self.window()
            if win.isMaximized():
                win.showNormal()
                self.maxBtn.setMaxState(False)
            win.move(event.globalPosition().toPoint() - self._dragPos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._dragging = False
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggleMax()
        super().mouseDoubleClickEvent(event)


class CustomDialog(QDialog):
    """
    Base frameless dialog with app-consistent titlebar.

    Titlebar: Maximize + Close (full height, QSSA colors)
    Resize:   native QSizeGrip via setSizeGripEnabled(True)
    Drag:     built into _DialogTitleBar

    Usage:
        class MyDialog(CustomDialog):
            def __init__(self, title='', parent=None):
                super().__init__(title, parent)
                self.contentLayout().addWidget(...)
    """

    def __init__(self, title: str = '', parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setSizeGripEnabled(True)

        # Titlebar
        self._titleBar = _DialogTitleBar(title, self)

        # Content area
        self._contentWidget = QWidget(self)
        self._contentWidget.setObjectName('MsgBody')
        self._contentWidget.setAttribute(Qt.WA_StyledBackground, True)
        self._contentLayout = QVBoxLayout(self._contentWidget)
        self._contentLayout.setContentsMargins(*QSSA['margins_dialog_body'])
        self._contentLayout.setSpacing(QSSA['spacing_dialog_body'])

        # Root layout
        root = QVBoxLayout(self)
        root.setContentsMargins(*QSSA['margins_zero'])
        root.setSpacing(QSSA['spacing_zero'])
        root.addWidget(self._titleBar)
        root.addWidget(self._contentWidget, 1)

        if title:
            self.setWindowTitle(title)

        # Dim overlay
        self._dimOverlay = None
        self.finished.connect(self._removeDim)
        if parent is not None:
            self._applyDim(parent)

    def _applyDim(self, parent):
        from PySide6.QtWidgets import QApplication
        target = parent.window() if parent is not None else QApplication.activeWindow()
        if target is None:
            return
        self._dimOverlay = QWidget(target)
        self._dimOverlay.setStyleSheet('background-color: rgba(0,0,0,80);')
        self._dimOverlay.setGeometry(target.rect())
        self._dimOverlay.raise_()
        self._dimOverlay.show()

    def _removeDim(self):
        if self._dimOverlay is not None:
            self._dimOverlay.hide()
            self._dimOverlay.deleteLater()
            self._dimOverlay = None

    def contentLayout(self) -> QVBoxLayout:
        """Return the QVBoxLayout of the content area."""
        return self._contentLayout

    def setSizeGripEnabled(self, enabled: bool):
        """Enable/disable the native size grip."""
        super().setSizeGripEnabled(enabled)

    def showEvent(self, event):
        """Apply DWM shadow once the native window handle exists."""
        super().showEvent(event)
        try:
            import sys
            if sys.platform == 'win32':
                from framelesswindow.windows.window_effect import WindowsWindowEffect
                effect = WindowsWindowEffect(self)
                effect.addShadowEffect(self.winId())
                effect.addWindowAnimation(self.winId())
        except Exception:
            pass
