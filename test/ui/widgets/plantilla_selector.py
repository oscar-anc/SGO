# coding: utf-8
"""
ui/widgets/plantilla_selector.py — Selector de tipo de plantilla (L1 + L2).

API pública actualizada:
  set_empresa(str)  → reconstruye botones L1 según empresa
  hide_all()        → oculta L1 y L2 (estado 0 de navegación)
  show_l1()         → muestra botones L1 (estado 1 de navegación)
  reset_l2()        → deselecciona L2 sin tocar L1

Señales:
  l1_changed(str)
  l2_changed(str)
"""

from __future__ import annotations
from PySide6.QtCore import Signal, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QFrame, QRadioButton, QButtonGroup,
)
from svgs import SVG, apply_svg_icon
from theme import QSSD

_TREE: dict[str, dict[str, list[str]]] = {
    "RRGG": {
        "Póliza":  ["Despacho individual", "Despacho programa",
                    "Regularización (individual)", "Regularización (programa)"],
        "Endoso":  ["Individual", "Colectivo",
                    "Regularización (individual)", "Regularización (colectivo)"],
    },
    "Transportes": {
        "Póliza":  ["Despacho individual", "Despacho programa",
                    "Regularización (individual)", "Regularización (programa)"],
        "Endoso":  ["Individual", "Colectivo",
                    "Regularización (individual)", "Regularización (colectivo)"],
        "Declaración mensual": ["Individual", "Colectivo",
                                "Regularización (individual)", "Regularización (colectivo)"],
    },
}

_L1_ICONS = {
    "Póliza":              SVG.POLIZA,
    "Endoso":              SVG.ENDOSO,
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
        self._build()

    def _build(self):
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(10)

        # Contenedor L1 (oculto en estado 0)
        self._l1_container = QWidget()
        self._l1_row = QHBoxLayout(self._l1_container)
        self._l1_row.setContentsMargins(0, 0, 0, 0)
        self._l1_row.setSpacing(QSSD["btn_linea_spacing"])
        self._l1_container.hide()
        self._lay.addWidget(self._l1_container)

        # Separador + L2 (ocultos hasta L1 seleccionado)
        self._sep = QFrame()
        self._sep.setFrameShape(QFrame.HLine)
        self._sep.setFixedHeight(1)
        self._sep.hide()
        self._lay.addWidget(self._sep)

        self._l2_container = QWidget()
        self._l2_grid = QGridLayout(self._l2_container)
        self._l2_grid.setContentsMargins(0, 0, 0, 0)
        self._l2_grid.setSpacing(QSSD["radio_opt_grid_spacing"])
        self._l2_container.hide()
        self._lay.addWidget(self._l2_container)

    # ── API pública ───────────────────────────────────────────────────────────

    def hide_all(self):
        """Estado 0: oculta L1 y L2."""
        self._l1_container.hide()
        self._sep.hide()
        self._l2_container.hide()

    def show_l1(self):
        """Estado 1: muestra solo L1 (L2 sigue oculto hasta click)."""
        self._l1_container.show()
        # L2 permanece oculto hasta que se elija L1

    def set_empresa(self, empresa: str):
        """Reconstruye los botones L1 según la empresa. Llama a hide_all() internamente."""
        self._empresa = empresa
        self._sel_l1  = ""
        self._sel_l2  = ""
        self._clear_l1_btns()
        self._clear_l2()
        self._sep.hide()
        self._l2_container.hide()

        opciones = list(_TREE.get(empresa, {}).keys())
        for nombre in opciones:
            btn = QPushButton(f"  {nombre}")
            btn.setProperty("role", "btn-tpl-l1")
            btn.setProperty("selected", "false")
            apply_svg_icon(btn, _L1_ICONS.get(nombre, SVG.POLIZA),
                           QSize(*QSSD["btn_linea_icon_size"]), QSSD["btn_linea_text"])
            btn.clicked.connect(lambda _, n=nombre, b=btn: self._on_l1(n, b))
            self._l1_row.addWidget(btn)
            self._l1_btns[nombre] = btn

    def reset_l2(self):
        self._sel_l2 = ""
        self._sep.hide()
        self._l2_container.hide()
        self._clear_l2()

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _on_l1(self, nombre: str, btn: QPushButton):
        prev = self._sel_l1
        self._sel_l1 = nombre
        self._sel_l2 = ""

        # Estilos L1
        for b in self._l1_btns.values():
            b.setProperty("selected", "false")
            b.style().unpolish(b); b.style().polish(b)
            apply_svg_icon(b, _L1_ICONS.get(b.text().strip(), SVG.POLIZA),
                           QSize(*QSSD["btn_linea_icon_size"]), QSSD["btn_linea_text"])
        btn.setProperty("selected", "true")
        btn.style().unpolish(btn); btn.style().polish(btn)
        apply_svg_icon(btn, _L1_ICONS.get(nombre, SVG.POLIZA),
                       QSize(*QSSD["btn_linea_icon_size"]), "#FFFFFF")

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
            frame.setProperty("role", "radio-opt")
            frame.setProperty("selected", "false")
            frame.setMinimumHeight(QSSD["radio_opt_min_height"])

            f_lay = QHBoxLayout(frame)
            f_lay.setContentsMargins(12, 8, 12, 8)
            f_lay.setSpacing(8)

            rb = QRadioButton(opcion)
            self._l2_group.addButton(rb, idx)
            f_lay.addWidget(rb)
            rb.toggled.connect(
                lambda checked, o=opcion, f=frame: self._on_l2(o, f, checked)
            )

            row, col = divmod(idx, 2)
            self._l2_grid.addWidget(frame, row, col)

        self._sep.show()
        self._l2_container.show()

    def _on_l2(self, opcion: str, frame: QFrame, checked: bool):
        if not checked:
            frame.setProperty("selected", "false")
            frame.style().unpolish(frame); frame.style().polish(frame)
            return

        for i in range(self._l2_grid.count()):
            w = self._l2_grid.itemAt(i).widget()
            if w:
                w.setProperty("selected", "false")
                w.style().unpolish(w); w.style().polish(w)

        frame.setProperty("selected", "true")
        frame.style().unpolish(frame); frame.style().polish(frame)

        self._sel_l2 = opcion
        self.l2_changed.emit(opcion)

    # ── Limpieza ──────────────────────────────────────────────────────────────

    def _clear_l1_btns(self):
        while self._l1_row.count():
            item = self._l1_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._l1_btns.clear()

    def _clear_l2(self):
        while self._l2_grid.count():
            item = self._l2_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if self._l2_group:
            for b in self._l2_group.buttons():
                self._l2_group.removeButton(b)
            self._l2_group = None
        self._sel_l2 = ""
