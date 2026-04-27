# coding: utf-8
"""
ui/dialogs/outlook_dialog.py — Diálogos personalizados del sistema.

OutlookWarningDialog:
  Se muestra DESPUÉS de abrir Outlook exitosamente.
  Advierte al usuario sobre cómo manejar correcciones y adjuntos PDF.

ErrorDialog:
  Diálogo de error genérico para validaciones y errores de Outlook.
"""

from PySide6.QtCore import Qt, QPoint, QSize
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QWidget, QFrame,
)
from PySide6.QtGui import QMouseEvent

from svgs import SVG, svg_pixmap, apply_svg_icon
from theme import QSSD


class _BaseDialog(QDialog):
    """Base sin marco nativo con titlebar personalizada."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setModal(True)
        self._drag_pos: QPoint | None = None

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e: QMouseEvent):
        if self._drag_pos and e.buttons() == Qt.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, e: QMouseEvent):
        self._drag_pos = None

    def _make_titlebar(self, titulo: str) -> QWidget:
        bar = QWidget()
        bar.setObjectName("MsgTitleBar")
        bar.setFixedHeight(QSSD["titlebar_fixed_height"])
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(*QSSD["margins_msg_titlebar"])
        lay.setSpacing(QSSD["spacing_msg_titlebar"])

        lbl = QLabel(titulo)
        lbl.setObjectName("MsgTitleLabel")
        lay.addWidget(lbl)
        lay.addStretch()

        btn_close = QPushButton()
        btn_close.setProperty("role", "titlebar-close")
        btn_close.setFixedSize(QSSD["titlebar_btn_width"], QSSD["titlebar_fixed_height"])
        apply_svg_icon(btn_close, SVG.CERRAR, QSize(13, 13), QSSD["text_on_dark"])
        btn_close.clicked.connect(self.reject)
        lay.addWidget(btn_close)

        return bar


class OutlookWarningDialog(_BaseDialog):
    """
    Diálogo de advertencia que aparece justo después de abrir Outlook.
    Informa al usuario que debe cerrar el borrador si necesita corregir algo,
    y que los PDF se adjuntan directamente en Outlook.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(QSSD["msg_box_min_width"])
        self.setMaximumWidth(QSSD["msg_box_max_width"])
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Frame contenedor
        frame = QFrame()
        frame.setObjectName("MsgFrame")
        f_lay = QVBoxLayout(frame)
        f_lay.setContentsMargins(0, 0, 0, 0)
        f_lay.setSpacing(0)

        # Titlebar
        f_lay.addWidget(self._make_titlebar("Borrador generado en Outlook"))

        # Cuerpo
        body = QWidget()
        body.setObjectName("MsgBody")
        b_lay = QVBoxLayout(body)
        b_lay.setContentsMargins(*QSSD["margins_msg_body"])
        b_lay.setSpacing(QSSD["spacing_msg_body"])

        # Ícono de advertencia
        icon_row = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setObjectName("MsgIcon")
        pix = svg_pixmap(SVG.ADVERTENCIA, QSize(*QSSD["msg_icon_circle_size"]),
                         QSSD["msg_icon_color"])
        icon_lbl.setPixmap(pix)
        icon_row.addWidget(icon_lbl)
        icon_row.addStretch()
        b_lay.addLayout(icon_row)

        # Mensaje
        msg = QLabel(
            "<b>La ventana de Outlook se abrió con la plantilla aplicada.</b><br><br>"
            "Si necesitas corregir algún dato, <b>cierra el borrador sin enviar</b>, "
            "realiza los cambios aquí y vuelve a hacer clic en <b>Abrir en Outlook</b>.<br><br>"
            "Los archivos <b>PDF</b> deben adjuntarse directamente desde Outlook "
            "antes de enviar el correo."
        )
        msg.setObjectName("MsgBodyText")
        msg.setWordWrap(True)
        msg.setTextFormat(Qt.RichText)
        b_lay.addWidget(msg)

        # Botón
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(*QSSD["margins_msg_buttons"])
        btn_row.addStretch()
        btn_ok = QPushButton("Entendido")
        btn_ok.setObjectName("MsgBtnOk")
        btn_ok.setMinimumHeight(QSSD["msg_btn_min_height"])
        btn_ok.setMinimumWidth(QSSD["msg_btn_min_width"])
        btn_ok.clicked.connect(self.accept)
        btn_ok.setDefault(True)
        btn_row.addWidget(btn_ok)
        b_lay.addLayout(btn_row)

        f_lay.addWidget(body)
        root.addWidget(frame)


class ErrorDialog(_BaseDialog):
    """Diálogo de error genérico."""

    def __init__(self, mensaje: str, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(QSSD["msg_box_min_width"])
        self.setMaximumWidth(QSSD["msg_box_max_width"])
        self._mensaje = mensaje
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        frame = QFrame()
        frame.setObjectName("MsgFrame")
        f_lay = QVBoxLayout(frame)
        f_lay.setContentsMargins(0, 0, 0, 0)
        f_lay.setSpacing(0)

        f_lay.addWidget(self._make_titlebar("Error"))

        body = QWidget()
        body.setObjectName("MsgBody")
        b_lay = QVBoxLayout(body)
        b_lay.setContentsMargins(*QSSD["margins_msg_body"])
        b_lay.setSpacing(QSSD["spacing_msg_body"])

        # Ícono
        icon_lbl = QLabel()
        pix = svg_pixmap(SVG.ADVERTENCIA, QSize(*QSSD["msg_icon_circle_size"]),
                         QSSD["inline_error_border"])
        icon_lbl.setPixmap(pix)
        b_lay.addWidget(icon_lbl)

        msg = QLabel(self._mensaje)
        msg.setObjectName("MsgBodyText")
        msg.setWordWrap(True)
        msg.setTextFormat(Qt.PlainText)
        b_lay.addWidget(msg)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_ok = QPushButton("Cerrar")
        btn_ok.setObjectName("MsgBtnOk")
        btn_ok.setMinimumHeight(QSSD["msg_btn_min_height"])
        btn_ok.setMinimumWidth(QSSD["msg_btn_min_width"])
        btn_ok.clicked.connect(self.accept)
        btn_row.addWidget(btn_ok)
        b_lay.addLayout(btn_row)

        f_lay.addWidget(body)
        root.addWidget(frame)
