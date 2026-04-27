# coding: utf-8
"""
ui/widgets/plantilla_selector.py — Selector de tipo de plantilla (L1 + L2).

L1: botones grandes — Póliza / Endoso / Declaración mensual
L2: radio-cards — las 4 opciones de cada L1

Señales:
  l1_changed(str)  — cuando se selecciona L1
  l2_changed(str)  — cuando se selecciona L2
"""

from __future__ import annotations
from PySide6.QtCore import Signal, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QFrame, QRadioButton, QButtonGroup, QLabel,
)
from PySide6.QtGui import QFont
from svgs import SVG, apply_svg_icon
from theme import QSSD

# Árbol de opciones por empresa
_TREE: dict[str, dict[str, list[str]]] = {
    "RRGG": {
        "Póliza":  [
            "Despacho individual", "Despacho programa",
            "Regularización (individual)", "Regularización (programa)",
        ],
        "Endoso":  [
            "Individual", "Colectivo",
            "Regularización (individual)", "Regularización (colectivo)",
        ],
    },
    "Transportes": {
        "Póliza":  [
            "Despacho individual", "Despacho programa",
            "Regularización (individual)", "Regularización (programa)",
        ],
        "Endoso":  [
            "Individual", "Colectivo",
            "Regularización (individual)", "Regularización (colectivo)",
        ],
        "Declaración mensual": [
            "Individual", "Colectivo",
            "Regularización (individual)", "Regularización (colectivo)",
        ],
    },
}

_L1_ICONS = {
    "Póliza":             SVG.POLIZA,
    "Endoso":             SVG.ENDOSO,
    "Declaración mensual": SVG.DECLARACION,
}


class PlantillaSelector(QWidget):
    l1_changed = Signal(str)
    l2_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._empresa:   str = ""
        self._sel_l1:    str = ""
        self._sel_l2:    str = ""
        self._l1_btns:   dict[str, QPushButton] = {}
        self._l2_group:  QButtonGroup | None = None
        self._l2_radios: dict[str, QRadioButton] = {}

        self._build()

    def _build(self):
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(10)

        # Fila de botones L1 (se construye en set_empresa)
        self._l1_row = QHBoxLayout()
        self._l1_row.setSpacing(QSSD["btn_linea_spacing"])
        self._lay.addLayout(self._l1_row)

        # Separador + grid L2 (ocultos hasta selección L1)
        self._sep = QFrame()
        self._sep.setFrameShape(QFrame.HLine)
        self._sep.setFixedHeight(1)
        self._sep.setStyleSheet(
            f"background-color: {QSSD['border_block']}; border: none;"
        )
        self._sep.hide()
        self._lay.addWidget(self._sep)

        self._l2_container = QWidget()
        self._l2_grid = QGridLayout(self._l2_container)
        self._l2_grid.setContentsMargins(0, 0, 0, 0)
        self._l2_grid.setSpacing(QSSD["radio_opt_grid_spacing"])
        self._l2_container.hide()
        self._lay.addWidget(self._l2_container)

    # ── API pública ───────────────────────────────────────────────────────────

    def set_empresa(self, empresa: str):
        """Reconstruye los botones L1 según la empresa seleccionada."""
        self._empresa = empresa
        self._sel_l1  = ""
        self._sel_l2  = ""

        # Limpiar L1
        while self._l1_row.count():
            item = self._l1_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._l1_btns.clear()

        # Ocultar L2
        self._sep.hide()
        self._l2_container.hide()
        self._clear_l2()

        # Construir botones L1
        opciones = list(_TREE.get(empresa, {}).keys())
        for nombre in opciones:
            btn = QPushButton(f"  {nombre}")
            btn.setProperty("role", "btn-tpl-l1")
            btn.setProperty("selected", "false")
            apply_svg_icon(
                btn, _L1_ICONS.get(nombre, SVG.POLIZA),
                QSize(20, 20), QSSD["btn_linea_text"]
            )
            btn.clicked.connect(lambda _, n=nombre, b=btn: self._on_l1(n, b))
            self._l1_row.addWidget(btn)
            self._l1_btns[nombre] = btn

    def reset_l2(self):
        """Deselecciona L2 sin borrar L1."""
        self._sel_l2 = ""
        self._sep.hide()
        self._l2_container.hide()
        self._clear_l2()

    # ── Handlers internos ─────────────────────────────────────────────────────

    def _on_l1(self, nombre: str, btn: QPushButton):
        prev = self._sel_l1
        self._sel_l1 = nombre
        self._sel_l2 = ""

        # Actualizar estilos L1
        for b in self._l1_btns.values():
            b.setProperty("selected", "false")
            b.style().unpolish(b)
            b.style().polish(b)
            apply_svg_icon(
                b, _L1_ICONS.get(b.text().strip(), SVG.POLIZA),
                QSize(20, 20), QSSD["btn_linea_text"]
            )
        btn.setProperty("selected", "true")
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        apply_svg_icon(
            btn, _L1_ICONS.get(nombre, SVG.POLIZA),
            QSize(20, 20), "#FFFFFF"
        )

        # Reconstruir L2
        self._build_l2(nombre)

        if prev != nombre:
            self.l1_changed.emit(nombre)

    def _build_l2(self, l1: str):
        self._clear_l2()
        opciones = _TREE.get(self._empresa, {}).get(l1, [])
        if not opciones:
            return

        self._l2_group = QButtonGroup(self)
        self._l2_group.setExclusive(True)

        for idx, opcion in enumerate(opciones):
            frame = QFrame()
            frame.setObjectName("RadioOptFrame")
            frame.setProperty("role", "radio-opt")
            frame.setProperty("selected", "false")
            frame.setMinimumHeight(QSSD["radio_opt_min_height"])

            f_lay = QHBoxLayout(frame)
            f_lay.setContentsMargins(12, 8, 12, 8)
            f_lay.setSpacing(8)

            rb = QRadioButton(opcion)
            self._l2_group.addButton(rb, idx)
            f_lay.addWidget(rb)

            row, col = divmod(idx, 2)
            self._l2_grid.addWidget(frame, row, col)
            self._l2_radios[opcion] = rb

            # Click en el frame selecciona el radio
            rb.toggled.connect(
                lambda checked, o=opcion, f=frame: self._on_l2(o, f, checked)
            )

        self._sep.show()
        self._l2_container.show()

    def _on_l2(self, opcion: str, frame: QFrame, checked: bool):
        if not checked:
            frame.setProperty("selected", "false")
            frame.style().unpolish(frame)
            frame.style().polish(frame)
            return

        # Deseleccionar todos los frames
        for i in range(self._l2_grid.count()):
            w = self._l2_grid.itemAt(i).widget()
            if w:
                w.setProperty("selected", "false")
                w.style().unpolish(w)
                w.style().polish(w)

        frame.setProperty("selected", "true")
        frame.style().unpolish(frame)
        frame.style().polish(frame)

        self._sel_l2 = opcion
        self.l2_changed.emit(opcion)

    def _clear_l2(self):
        while self._l2_grid.count():
            item = self._l2_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._l2_radios.clear()
        if self._l2_group:
            for btn in self._l2_group.buttons():
                self._l2_group.removeButton(btn)
            self._l2_group = None
