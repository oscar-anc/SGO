# coding: utf-8
"""
ui/widgets/modo_envio.py — Selector de modo de envío.

API pública actualizada:
  set_enabled(bool) → habilita/deshabilita los botones
  reset()           → deselecciona sin deshabilitar

Señales:
  modo_changed(str) → 'nuevo' | 'reply'
"""

from PySide6.QtCore import Signal, QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from svgs import SVG, apply_svg_icon
from theme import QSSD

_OPTS = [
    ("nuevo",  "Correo nuevo",      SVG.CORREO_NUEVO),
    ("reply",  "Responder a todos", SVG.RESPONDER_TODOS),
]


class ModoEnvio(QWidget):
    modo_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._selected = ""
        self._btns: dict[str, QPushButton] = {}
        self._build()

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(QSSD["btn_linea_spacing"])

        for key, label, svg in _OPTS:
            btn = QPushButton(f"  {label}")
            btn.setProperty("role", "btn-linea")
            btn.setProperty("selected", "false")
            apply_svg_icon(btn, svg, QSize(*QSSD["btn_linea_icon_size"]),
                           QSSD["btn_linea_text"])
            btn.clicked.connect(lambda _, k=key, b=btn, s=svg: self._on_click(k, b, s))
            lay.addWidget(btn)
            self._btns[key] = btn

    # ── API pública ───────────────────────────────────────────────────────────

    def set_enabled(self, enabled: bool):
        """Habilita o deshabilita ambos botones."""
        for btn in self._btns.values():
            btn.setEnabled(enabled)

    def reset(self):
        """Deselecciona sin deshabilitar."""
        self._selected = ""
        svgs = {"nuevo": SVG.CORREO_NUEVO, "reply": SVG.RESPONDER_TODOS}
        for k, b in self._btns.items():
            b.setProperty("selected", "false")
            b.style().unpolish(b); b.style().polish(b)
            apply_svg_icon(b, svgs[k], QSize(*QSSD["btn_linea_icon_size"]),
                           QSSD["btn_linea_text"])

    # ── Handler ───────────────────────────────────────────────────────────────

    def _on_click(self, key: str, btn: QPushButton, svg: str):
        if self._selected == key:
            return
        svgs = {"nuevo": SVG.CORREO_NUEVO, "reply": SVG.RESPONDER_TODOS}
        for k, b in self._btns.items():
            b.setProperty("selected", "false")
            b.style().unpolish(b); b.style().polish(b)
            apply_svg_icon(b, svgs[k], QSize(*QSSD["btn_linea_icon_size"]),
                           QSSD["btn_linea_text"])
        btn.setProperty("selected", "true")
        btn.style().unpolish(btn); btn.style().polish(btn)
        apply_svg_icon(btn, svg, QSize(*QSSD["btn_linea_icon_size"]), "#FFFFFF")
        self._selected = key
        self.modo_changed.emit(key)
