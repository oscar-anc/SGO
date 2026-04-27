# coding: utf-8
"""
ui/dialogs/outlook_dialog.py — Diálogos personalizados.

OutlookWarningDialog — aviso post-apertura de Outlook.
ErrorDialog          — error genérico, acepta titulo opcional.
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

    def mouseReleaseEvent(self, _): self._drag_pos = None

    def _titlebar(self, titulo: str) -> QWidget:
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
        btn = QPushButton()
        btn.setProperty("role", "titlebar-close")
        btn.setFixedSize(QSSD["titlebar_btn_width"], QSSD["titlebar_fixed_height"])
        apply_svg_icon(btn, SVG.CERRAR, QSize(13, 13), QSSD["text_on_dark"])
        btn.clicked.connect(self.reject)
        lay.addWidget(btn)
        return bar


class OutlookWarningDialog(_BaseDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(QSSD["msg_box_min_width"])
        self.setMaximumWidth(QSSD["msg_box_max_width"])
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        frame = QFrame()
        frame.setObjectName("MsgFrame")
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(0)
        fl.addWidget(self._titlebar("Borrador generado en Outlook"))

        body = QWidget()
        body.setObjectName("MsgBody")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(*QSSD["margins_msg_body"])
        bl.setSpacing(QSSD["spacing_msg_body"])

        icon_lbl = QLabel()
        icon_lbl.setPixmap(svg_pixmap(SVG.ADVERTENCIA,
                                      QSize(*QSSD["msg_icon_circle_size"]),
                                      QSSD["msg_icon_color"]))
        bl.addWidget(icon_lbl)

        msg = QLabel(
            "<b>La ventana de Outlook se abrió con la plantilla aplicada.</b><br><br>"
            "Si necesitas corregir algún dato, <b>cierra el borrador sin enviar</b>, "
            "realiza los cambios aquí y vuelve a hacer clic en <b>Abrir en Outlook</b>.<br><br>"
            "Los archivos <b>PDF</b> se adjuntan directamente en Outlook antes de enviar."
        )
        msg.setObjectName("MsgBodyText")
        msg.setWordWrap(True)
        msg.setTextFormat(Qt.RichText)
        bl.addWidget(msg)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(*QSSD["margins_msg_buttons"])
        btn_row.addStretch()
        btn = QPushButton("Entendido")
        btn.setObjectName("MsgBtnOk")
        btn.setMinimumHeight(QSSD["msg_btn_min_height"])
        btn.setMinimumWidth(QSSD["msg_btn_min_width"])
        btn.setDefault(True)
        btn.clicked.connect(self.accept)
        btn_row.addWidget(btn)
        bl.addLayout(btn_row)

        fl.addWidget(body)
        root.addWidget(frame)


class ErrorDialog(_BaseDialog):
    def __init__(self, mensaje: str, parent=None, titulo: str = "Error"):
        super().__init__(parent)
        self.setMinimumWidth(QSSD["msg_box_min_width"])
        self.setMaximumWidth(QSSD["msg_box_max_width"])
        self._mensaje = mensaje
        self._titulo  = titulo
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        frame = QFrame()
        frame.setObjectName("MsgFrame")
        fl = QVBoxLayout(frame)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(0)
        fl.addWidget(self._titlebar(self._titulo))

        body = QWidget()
        body.setObjectName("MsgBody")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(*QSSD["margins_msg_body"])
        bl.setSpacing(QSSD["spacing_msg_body"])

        icon_lbl = QLabel()
        icon_lbl.setPixmap(svg_pixmap(SVG.ADVERTENCIA,
                                      QSize(*QSSD["msg_icon_circle_size"]),
                                      QSSD["inline_error_border"]))
        bl.addWidget(icon_lbl)

        msg = QLabel(self._mensaje)
        msg.setObjectName("MsgBodyText")
        msg.setWordWrap(True)
        msg.setTextFormat(Qt.PlainText)
        bl.addWidget(msg)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(*QSSD["margins_msg_buttons"])
        btn_row.addStretch()
        btn = QPushButton("Cerrar")
        btn.setObjectName("MsgBtnOk")
        btn.setMinimumHeight(QSSD["msg_btn_min_height"])
        btn.setMinimumWidth(QSSD["msg_btn_min_width"])
        btn.setDefault(True)
        btn.clicked.connect(self.accept)
        btn_row.addWidget(btn)
        bl.addLayout(btn_row)

        fl.addWidget(body)
        root.addWidget(frame)
