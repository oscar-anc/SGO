# coding: utf-8
"""
ui/widgets/block_widget.py — Contenedor visual de cada sección del formulario.

Un BlockWidget es una tarjeta con:
  - Un label de sección (SLABEL) en la parte superior
  - Un cuerpo blanco donde se agregan widgets hijos

Uso:
    blk = BlockWidget("Datos del despacho")
    blk.add_widget(mi_widget)
    blk.add_layout(mi_layout)
    blk.show() / blk.hide()
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from theme import QSSD


class BlockWidget(QWidget):
    """
    Tarjeta de sección del formulario progresivo.
    Encapsula un QFrame con borde redondeado y un QLabel de sección arriba.
    """

    def __init__(self, titulo: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build(titulo)

    def _build(self, titulo: str):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(*QSSD["margins_block_outer"])
        outer.setSpacing(0)

        # Frame principal (borde + fondo)
        self._frame = QFrame()
        self._frame.setObjectName("BlockWidget")
        frame_lay = QVBoxLayout(self._frame)
        frame_lay.setContentsMargins(*QSSD["padding_block_body"].replace("px", "").split() if False else (14, 14, 14, 14))
        frame_lay.setSpacing(QSSD["spacing_block_body"])

        # Label de sección (SLABEL)
        lbl = QLabel(titulo.upper())
        lbl.setObjectName("SLabel")
        frame_lay.addWidget(lbl)

        # Separador visual (línea delgada)
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {QSSD['border_block']}; border: none;")
        frame_lay.addWidget(sep)

        self._body_lay = QVBoxLayout()
        self._body_lay.setContentsMargins(0, 4, 0, 0)
        self._body_lay.setSpacing(QSSD["spacing_block_body"])
        frame_lay.addLayout(self._body_lay)

        outer.addWidget(self._frame)

    # ── API pública ───────────────────────────────────────────────────────────

    def add_widget(self, widget: QWidget) -> None:
        """Agrega un widget al cuerpo del bloque."""
        self._body_lay.addWidget(widget)

    def add_layout(self, layout) -> None:
        """Agrega un layout al cuerpo del bloque."""
        self._body_lay.addLayout(layout)

    def body_layout(self) -> QVBoxLayout:
        """Retorna el layout del cuerpo para manipulación directa."""
        return self._body_lay
