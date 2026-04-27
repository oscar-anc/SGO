# coding: utf-8
"""
ui/widgets/modo_envio.py — Selector de modo de envío (Correo nuevo / Responder a todos).
"""
from PySide6.QtCore import Signal, QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from svgs import SVG, apply_svg_icon
from theme import QSSD


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

        opciones = [
            ("nuevo",  "Correo nuevo",       SVG.CORREO_NUEVO),
            ("reply",  "Responder a todos",  SVG.RESPONDER_TODOS),
        ]
        for key, label, svg in opciones:
            btn = QPushButton(f"  {label}")
            btn.setProperty("role", "btn-linea")
            btn.setProperty("selected", "false")
            apply_svg_icon(btn, svg, QSize(*QSSD["btn_linea_icon_size"]), QSSD["btn_linea_text"])
            btn.clicked.connect(lambda _, k=key, b=btn, s=svg: self._on_click(k, b, s))
            lay.addWidget(btn)
            self._btns[key] = btn

    def _on_click(self, key: str, btn: QPushButton, svg: str):
        if self._selected == key:
            return
        svgs_map = {
            "nuevo": SVG.CORREO_NUEVO,
            "reply": SVG.RESPONDER_TODOS,
        }
        for k, b in self._btns.items():
            b.setProperty("selected", "false")
            b.style().unpolish(b); b.style().polish(b)
            apply_svg_icon(b, svgs_map[k], QSize(*QSSD["btn_linea_icon_size"]), QSSD["btn_linea_text"])

        btn.setProperty("selected", "true")
        btn.style().unpolish(btn); btn.style().polish(btn)
        apply_svg_icon(btn, svg, QSize(*QSSD["btn_linea_icon_size"]), "#FFFFFF")

        self._selected = key
        self.modo_changed.emit(key)

    def reset(self):
        self._selected = ""
        svgs_map = {"nuevo": SVG.CORREO_NUEVO, "reply": SVG.RESPONDER_TODOS}
        for k, b in self._btns.items():
            b.setProperty("selected", "false")
            b.style().unpolish(b); b.style().polish(b)
            apply_svg_icon(b, svgs_map[k], QSize(*QSSD["btn_linea_icon_size"]), QSSD["btn_linea_text"])
