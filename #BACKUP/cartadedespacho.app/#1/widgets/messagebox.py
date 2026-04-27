# coding: utf-8
"""
widgets/message_box.py — CustomMessageBox

Fully styled QDialog replacement for QMessageBox. Supports warning, question,
information and critical modes. Returns QMessageBox.StandardButton values so
existing call-sites need no changes.
"""

from PySide6.QtWidgets import (
    QDialog, QWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QApplication, QSizePolicy, QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from theme import QSSA

class CustomMessageBox(QDialog):
    """
    Fully styled replacement for QMessageBox.
    Uses the application theme (styles.qss) instead of the OS native dialog.

    Usage mirrors QMessageBox static methods:

        # Warning (single OK button)
        CustomMessageBox.warning(parent, "Título", "Mensaje")

        # Question (Yes / No buttons) — returns QMessageBox.Yes or QMessageBox.No
        reply = CustomMessageBox.question(parent, "Título", "Mensaje",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        # Information (single OK button)
        CustomMessageBox.information(parent, "Título", "Mensaje")

        # Critical / Error (single OK button)
        CustomMessageBox.critical(parent, "Título", "Mensaje")
    """

    # Internal mode constants — determine which buttons to show
    _MODE_OK       = "ok"
    _MODE_QUESTION = "question"

    # Visual variant constants — control header + border color via QSS objectNames
    VARIANT_DEFAULT  = 'default'
    VARIANT_WARNING  = 'warning'
    VARIANT_ERROR    = 'error'
    VARIANT_INFO     = 'info'
    VARIANT_QUESTION = 'question'

    def __init__(self, parent, title, message, mode=_MODE_OK,
                 default_button=QMessageBox.No, variant=VARIANT_DEFAULT,
                 theme=None):
        super().__init__(parent)

        # Remove native OS title bar — we draw our own header
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setModal(True)
        self.setObjectName("CustomMessageBox")
        self.setMinimumWidth(QSSA['msg_box_min_width'])

        # Track which button was pressed so callers can check the return value
        self._result = QMessageBox.No if mode == self._MODE_QUESTION else QMessageBox.Ok

        # Visual variant — determines which QSS objectName is applied to
        # the title bar and frame so each dialog type has its own accent color.
        self._variant = variant

        # Optional theme override — used by theme_editor for live preview.
        # When provided, the overlay reads from this dict instead of QSSA.
        self._theme_override = theme

        # Overlay widget — semi-transparent dark layer drawn over the parent window
        # to visually dim the background and draw attention to this dialog.
        self._overlay = None
        self._setupOverlay(parent)

        # QDialog.finished is emitted unconditionally on every close path:
        # accept(), reject(), Escape key, title-bar ×, or any button.
        # This is more reliable than closeEvent which can be bypassed.
        self.finished.connect(self._removeOverlay)

        self._buildUI(title, message, mode, default_button)

    def _setupOverlay(self, parent):
        """
        Create a semi-transparent overlay that dims the app background.

        The overlay is parented to the nearest ancestor that is NOT the
        FramelessMainWindow itself — this keeps the TitleBar (which is a
        sibling of containerWidget, not a child) always interactive and visible.

        Walk the parent chain to find a QWidget that is a child of the top-level
        window. Sizing to that widget's rect covers the content area without
        touching the native title-bar strip managed by qframelesswindow.
        """
        if parent is None:
            return

        # Climb parent hierarchy to find the nearest window (dialog or main)
        # isWindow() returns True for both QDialog and QMainWindow
        top = parent
        while top.parent() and not top.isWindow():
            top = top.parent()
        # If top is the main window but a dialog is open, prefer the dialog
        from PySide6.QtWidgets import QDialog
        p = parent
        while p:
            if isinstance(p, QDialog) and p.isVisible():
                top = p
                break
            p = p.parent() if hasattr(p, 'parent') and callable(p.parent) else None

        topLevel = top
        from theme import QSSA
        # Use dialog height for dialogs, main titlebar height for main window
        TITLEBAR_H = QSSA.get(
            'dialog_titlebar_height' if isinstance(topLevel, QDialog)
            else 'titlebar_fixed_height', 30)
        fullRect   = topLevel.rect()

        self._overlay = QWidget(topLevel)
        self._overlay.setObjectName("DimOverlay")
        # For dialogs: cover full window including titlebar for complete dim
        # For main window: offset by titlebar height to keep titlebar interactive
        from PySide6.QtWidgets import QDialog
        if isinstance(topLevel, QDialog):
            self._overlay.setGeometry(fullRect)
        else:
            self._overlay.setGeometry(
                fullRect.x(),
                fullRect.y() + TITLEBAR_H,
                fullRect.width(),
                fullRect.height() - TITLEBAR_H,
            )
        # Use theme variables for color and opacity so it is editable in theme_editor
        # Use theme_override if provided (theme_editor live preview), else QSSA
        _theme = self._theme_override if self._theme_override is not None else QSSA
        hex_color       = _theme.get('overlay_color',  '#000000').lstrip('#')
        overlay_opacity = _theme.get('overlay_opacity', '120')
        # Convert hex to R,G,B components for rgba()
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        except (ValueError, IndexError):
            r, g, b = 0, 0, 0
        self._overlay.setStyleSheet(
            f"background-color: rgba({r}, {g}, {b}, {overlay_opacity});"
        )
        # Overlay shown immediately — it's on the parent dialog, not the MessageBox
        self._overlay.show()
        self._overlay.raise_()

    def _removeOverlay(self):
        """
        Destroy the dim overlay. Connected to QDialog.finished so it fires on
        every close path: accept(), reject(), Escape, × button, or any button.
        Using finished instead of closeEvent avoids the Qt edge-cases where
        closeEvent is not reliably called on modal QDialog subclasses.
        """
        if self._overlay is not None:
            self._overlay.deleteLater()
            self._overlay = None

    def showEvent(self, event):
        """Raise above overlay when shown."""
        super().showEvent(event)
        self.raise_()
        self.activateWindow()

    def _buildUI(self, title, message, mode, default_button):
        """
        Build the dialog layout: border frame → title bar → message → buttons.

        Border visibility fix for FramelessWindowHint dialogs:
        A QSS 'border' rule on a top-level frameless window is painted INSIDE
        the widget's own geometry, but the OS compositor clips it flush — the
        result is that no border appears visually. To work around this, we wrap
        all content inside an inner QFrame (#MsgFrame) and give the outer
        QDialog a 1px transparent margin. The QSS border on #MsgFrame is then
        drawn fully inside the composited area and is always visible, regardless
        of OS or Qt platform theme. The #CustomMessageBox rule on the outer
        dialog sets only background-color (transparent) so it stays invisible
        and doesn't interfere with the frame's border.
        """
        # Outer layout: no margin — the inner MsgFrame border is fully visible
        # within the composited area in Fusion style without needing external spacing.
        outerLayout = QVBoxLayout(self)
        outerLayout.setContentsMargins(*QSSA['margins_zero'])
        outerLayout.setSpacing(QSSA['spacing_zero'])

        # Inner frame — receives visible border via #MsgFrame* QSS.
        # Object name changes per variant so QSS applies the correct border color.
        innerFrame = QFrame()
        frame_name = {
            'warning':  'MsgFrameWarning',
            'error':    'MsgFrameError',
            'info':     'MsgFrameInfo',
            'question': 'MsgFrameQuestion',
        }.get(self._variant, 'MsgFrame')
        innerFrame.setObjectName(frame_name)
        innerLayout = QVBoxLayout(innerFrame)
        innerLayout.setContentsMargins(*QSSA['margins_zero'])
        innerLayout.setSpacing(QSSA['spacing_zero'])
        outerLayout.addWidget(innerFrame)

        # Redirect all child additions to innerLayout so existing code below
        # requires no further changes — we just swap the target layout variable.
        outerLayout = innerLayout

        # ── Custom title bar — uses _DialogTitleBar (close button only) ────
        from widgets.dialog import _DialogTitleBar
        titleBar = _DialogTitleBar(title, self, close_only=True)
        titlebar_name = {
            'warning':  'MsgTitleBarWarning',
            'error':    'MsgTitleBarError',
            'info':     'MsgTitleBarInfo',
            'question': 'MsgTitleBarQuestion',
        }.get(self._variant, 'MsgTitleBar')
        titleBar.setObjectName(titlebar_name)
        # Override close to reject (cancel result)
        titleBar.closeBtn.clicked.disconnect()
        titleBar.closeBtn.clicked.connect(self.reject)
        outerLayout.addWidget(titleBar)

        # ── Message body ──────────────────────────────────────────────────────
        bodyWidget = QWidget()
        bodyWidget.setObjectName("MsgBody")
        bodyLayout = QVBoxLayout(bodyWidget)
        bodyLayout.setContentsMargins(*QSSA['margins_msg_body'])
        bodyLayout.setSpacing(QSSA['spacing_msg_body'])

        msgLabel = QLabel(message)
        msgLabel.setObjectName("MsgText")
        msgLabel.setWordWrap(True)
        msgLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        bodyLayout.addWidget(msgLabel)

        # ── Buttons ───────────────────────────────────────────────────────────
        btnLayout = QHBoxLayout()
        btnLayout.setContentsMargins(*QSSA['margins_msg_buttons'])
        btnLayout.setSpacing(QSSA['spacing_msg_buttons'])
        btnLayout.addStretch()

        if mode == self._MODE_QUESTION:
            # No button — secondary/neutral style
            noBtn = QPushButton("No")
            noBtn.setObjectName("MsgBtnSecondary")
            noBtn.clicked.connect(self._onNo)
            btnLayout.addWidget(noBtn)

            # Yes button — primary/accent style
            yesBtn = QPushButton("Sí")
            yesBtn.setObjectName("MsgBtnPrimary")
            yesBtn.clicked.connect(self._onYes)
            btnLayout.addWidget(yesBtn)

            # Set focus on the default button
            if default_button == QMessageBox.Yes:
                yesBtn.setDefault(True)
                yesBtn.setFocus()
            else:
                noBtn.setDefault(True)
                noBtn.setFocus()
        else:
            # Single OK button — primary style
            okBtn = QPushButton("Aceptar")
            okBtn.setObjectName("MsgBtnPrimary")
            okBtn.clicked.connect(self._onOk)
            okBtn.setDefault(True)
            okBtn.setFocus()
            btnLayout.addWidget(okBtn)

        bodyLayout.addLayout(btnLayout)
        bodyLayout.addSpacing(QSSA['msg_body_gap'])
        outerLayout.addWidget(bodyWidget)

    # ── Button handlers ───────────────────────────────────────────────────────

    def _onYes(self):
        """User pressed Sí — store Yes result and close."""
        self._result = QMessageBox.Yes
        self.accept()

    def _onNo(self):
        """User pressed No — store No result and close."""
        self._result = QMessageBox.No
        self.reject()

    def _onOk(self):
        """User pressed Aceptar — store Ok result and close."""
        self._result = QMessageBox.Ok
        self.accept()

    def getResult(self):
        """Return the button result after the dialog closes."""
        return self._result

    # ── Static convenience methods (mirror QMessageBox API) ───────────────────

    @staticmethod
    def warning(parent, title, message, theme=None):
        """Show a warning dialog — amber header, Aceptar button."""
        dlg = CustomMessageBox(parent, title, message, CustomMessageBox._MODE_OK,
                               variant=CustomMessageBox.VARIANT_WARNING, theme=theme)
        dlg.exec()

    @staticmethod
    def information(parent, title, message, theme=None):
        """Show an information dialog — blue header, Aceptar button."""
        dlg = CustomMessageBox(parent, title, message, CustomMessageBox._MODE_OK,
                               variant=CustomMessageBox.VARIANT_INFO, theme=theme)
        dlg.exec()

    @staticmethod
    def critical(parent, title, message, theme=None):
        """Show a critical/error dialog — red header, Aceptar button."""
        dlg = CustomMessageBox(parent, title, message, CustomMessageBox._MODE_OK,
                               variant=CustomMessageBox.VARIANT_ERROR, theme=theme)
        dlg.exec()

    @staticmethod
    def question(parent, title, message,
                 buttons=QMessageBox.Yes | QMessageBox.No,
                 default_button=QMessageBox.No, theme=None):
        """Show a question dialog — neutral header, Sí/No buttons."""
        dlg = CustomMessageBox(parent, title, message,
                               CustomMessageBox._MODE_QUESTION, default_button,
                               variant=CustomMessageBox.VARIANT_QUESTION, theme=theme)
        dlg.exec()
        return dlg.getResult()


# ─────────────────────────────────────────────────────────────────────────────
# CARD WIDGET
# Replaces QGroupBox throughout the application.
# Renders as a slate header bar + dark body — visually matches the tab-panel
# style from the UI reference image.
#
# API:
#   card = CardWidget("TÍTULO")              # non-collapsible
#   card = CardWidget("TÍTULO", collapsible=True)  # with accordion toggle
#   card.addContent(layout_or_widget)        # add children to the body
#   card.setLayout(layout)                   # alias for addContent — keeps
#                                            # compatibility with existing code
#   card.setCollapsed(True/False)            # programmatic collapse
#
# Header colors:
#   #55606E  — standard header (most cards)
#   #4A5560  — slightly darker for nested cards (policy inside insured)
# Body color:
#   #343A41  — dark body matching reference
# Text: white throughout
# ─────────────────────────────────────────────────────────────────────────────
