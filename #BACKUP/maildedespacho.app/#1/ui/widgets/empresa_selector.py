# coding: utf-8
"""
ui/widgets/empresa_selector.py — Selector de Línea de negocio (RRGG / Transportes).

Emite empresa_changed(str) cuando el usuario hace clic en uno de los botones.
"""

from PySide6.QtCore import Signal, QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from svgs import SVG, apply_svg_icon
from theme import QSSD


class EmpresaSelector(QWidget):
    """Dos pushbuttons grandes: RRGG y Transportes."""

    empresa_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._selected: str = ""
        self._btns: dict[str, QPushButton] = {}
        self._build()

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(QSSD["btn_linea_spacing"])

        opciones = [
            ("RRGG",        SVG.RRGG,        QSSD["accent_rrgg"]),
            ("Transportes", SVG.TRANSPORTES,  QSSD["accent_trans"]),
        ]

        for nombre, svg, _ in opciones:
            btn = QPushButton(f"  {nombre}")
            btn.setProperty("role", "btn-linea")
            btn.setProperty("selected", "false")
            apply_svg_icon(btn, svg, QSize(*QSSD["btn_linea_icon_size"]), QSSD["btn_linea_text"])
            btn.clicked.connect(lambda checked, n=nombre, b=btn: self._on_click(n, b))
            lay.addWidget(btn)
            self._btns[nombre] = btn

    def _on_click(self, nombre: str, btn: QPushButton):
        if self._selected == nombre:
            return  # ya seleccionado

        # Deseleccionar todos
        for b in self._btns.values():
            b.setProperty("selected", "false")
            b.style().unpolish(b)
            b.style().polish(b)
            apply_svg_icon(b, SVG.RRGG if "RRGG" in b.text() else SVG.TRANSPORTES,
                           QSize(*QSSD["btn_linea_icon_size"]), QSSD["btn_linea_text"])

        # Seleccionar el clickeado
        btn.setProperty("selected", "true")
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        apply_svg_icon(btn,
                       SVG.RRGG if nombre == "RRGG" else SVG.TRANSPORTES,
                       QSize(*QSSD["btn_linea_icon_size"]), "#FFFFFF")

        self._selected = nombre
        self.empresa_changed.emit(nombre)

    def reset(self):
        self._selected = ""
        for b in self._btns.values():
            b.setProperty("selected", "false")
            b.style().unpolish(b)
            b.style().polish(b)
