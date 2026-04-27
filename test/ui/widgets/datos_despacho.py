# coding: utf-8
"""
ui/widgets/datos_despacho.py — Formulario de datos del despacho.

Layout de campos según L1:
  Póliza           → CIA | Vig.desde | Vig.hasta  /  Ramo + Póliza (máx 12)
  Endoso           → CIA (ancho completo)          /  Ramo + Póliza + Endoso + Movimiento (máx 5)
  Declaración mens → CIA | Ramo | Nro.Póliza       /  Nro.Declaración + Mes + OPE (máx 5)

Vigencia guardada en memoria al cambiar de L1 y restaurada al volver a Póliza/Endoso.
OPE: campo numérico en cada fila de Declaración Mensual.
Todos los Signal/slot usan lambda sin args para evitar TypeError.
"""

from __future__ import annotations
import logging
from PySide6.QtCore import Signal, QSize, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QFrame,
)
from svgs import SVG, apply_svg_icon
from theme import QSSD
from config_loader import ConfigLoader

logger = logging.getLogger(__name__)

MAX_POL  = 12
MAX_END  = 5
MAX_DECL = 5


# ── helpers ───────────────────────────────────────────────────────────────────

def _lbl(text: str) -> QLabel:
    l = QLabel(text)
    l.setObjectName("FieldLabel")
    return l


def _inp(placeholder: str = "", numeric: bool = False) -> QLineEdit:
    e = QLineEdit()
    e.setPlaceholderText(placeholder)
    if numeric:
        from PySide6.QtGui import QIntValidator
        e.setValidator(QIntValidator())
    return e


def _cb(items: list[str]) -> QComboBox:
    c = QComboBox()
    c.addItem("")
    c.addItems(items)
    return c


def _vwrap(label: QLabel, widget: QWidget) -> QWidget:
    """Envuelve label + widget verticalmente."""
    w = QWidget()
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(4)
    lay.addWidget(label)
    lay.addWidget(widget)
    return w


class DatosDespacho(QWidget):
    data_changed    = Signal()
    paste_requested = Signal()

    def __init__(self, cfg: ConfigLoader, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._cfg = cfg

        # Filas dinámicas
        self._pol_rows:  list[dict] = []
        self._end_rows:  list[dict] = []
        self._decl_rows: list[dict] = []

        # Memoria de vigencia (se conserva al cambiar L1)
        self._mem_vig_ini: str = ""
        self._mem_vig_fin: str = ""

        # Bandera de edición manual del asunto
        self._asunto_usr_edited = False

        # L1 actual (para saber qué layout mostrar)
        self._current_l1: str = ""

        self._build()

    # ── Construcción ──────────────────────────────────────────────────────────

    def _build(self):
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(QSSD["spacing_datos_fields"])

        # ── Fila 1: Contratante + Contacto (siempre visible) ─────────────────
        row1 = QHBoxLayout()
        row1.setSpacing(QSSD["spacing_field_inline"])
        self._inp_contratante = _inp("Nombre completo o razón social")
        self._inp_contacto    = _inp("Contacto directo")
        row1.addWidget(_vwrap(_lbl("Nombre contratante / asegurado"), self._inp_contratante))
        row1.addWidget(_vwrap(_lbl("Persona de contacto"), self._inp_contacto))
        self._lay.addLayout(row1)

        # ── Fila 2: CIA + campos variables según L1 ───────────────────────────
        # Se reconstruye con _rebuild_cia_row() según el L1 activo.
        self._cia_row_widget = QWidget()
        self._cia_row_lay    = QHBoxLayout(self._cia_row_widget)
        self._cia_row_lay.setContentsMargins(0, 0, 0, 0)
        self._cia_row_lay.setSpacing(QSSD["spacing_field_inline"])

        # CIA siempre presente
        self._cb_cia = _cb(self._cfg.aseguradoras())
        self._cb_cia.currentIndexChanged.connect(lambda _: self._on_cia_changed())

        # Vigencia (Póliza)
        self._inp_vig_ini = _inp("2024"); self._inp_vig_ini.setMaxLength(4)
        self._inp_vig_fin = _inp("2025"); self._inp_vig_fin.setMaxLength(4)
        self._w_vig_ini   = _vwrap(_lbl("Vigencia desde"), self._inp_vig_ini)
        self._w_vig_fin   = _vwrap(_lbl("Vigencia hasta"), self._inp_vig_fin)

        # Ramo + Póliza para fila CIA (Declaración Mensual)
        self._cb_cia_ramo   = _cb(self._cfg.ramos())
        self._inp_cia_poliza = _inp("001-2024-00123")
        self._w_cia_ramo    = _vwrap(_lbl("Ramo"), self._cb_cia_ramo)
        self._w_cia_poliza  = _vwrap(_lbl("Nro. de póliza"), self._inp_cia_poliza)

        self._lay.addWidget(self._cia_row_widget)

        # ── Sección pólizas ───────────────────────────────────────────────────
        self._sec_pol = QWidget()
        self._sec_pol_lay = QVBoxLayout(self._sec_pol)
        self._sec_pol_lay.setContentsMargins(0, 0, 0, 0)
        self._sec_pol_lay.setSpacing(6)
        self._sec_pol.hide()
        self._lay.addWidget(self._sec_pol)
        self._btn_add_pol = self._make_add_btn("Agregar póliza", self._on_add_pol)
        self._btn_add_pol.hide()
        self._lay.addWidget(self._btn_add_pol)

        # ── Sección endosos ───────────────────────────────────────────────────
        self._sec_end = QWidget()
        self._sec_end_lay = QVBoxLayout(self._sec_end)
        self._sec_end_lay.setContentsMargins(0, 0, 0, 0)
        self._sec_end_lay.setSpacing(6)
        self._sec_end.hide()
        self._lay.addWidget(self._sec_end)
        self._btn_add_end = self._make_add_btn("Agregar endoso", self._on_add_end)
        self._btn_add_end.hide()
        self._lay.addWidget(self._btn_add_end)

        # ── Sección declaraciones ─────────────────────────────────────────────
        self._sec_decl = QWidget()
        self._sec_decl_lay = QVBoxLayout(self._sec_decl)
        self._sec_decl_lay.setContentsMargins(0, 0, 0, 0)
        self._sec_decl_lay.setSpacing(6)
        self._sec_decl.hide()
        self._lay.addWidget(self._sec_decl)
        self._btn_add_decl = self._make_add_btn("Agregar declaración", self._on_add_decl)
        self._btn_add_decl.hide()
        self._lay.addWidget(self._btn_add_decl)

        # ── Separador + Asunto ────────────────────────────────────────────────
        self._sep_asunto = QFrame()
        self._sep_asunto.setFrameShape(QFrame.HLine)
        self._sep_asunto.setFixedHeight(1)
        self._sep_asunto.hide()
        self._lay.addWidget(self._sep_asunto)

        self._asunto_wrap = QWidget()
        self._asunto_wrap.hide()
        aw = QVBoxLayout(self._asunto_wrap)
        aw.setContentsMargins(0, 0, 0, 0)
        aw.setSpacing(4)
        aw.addWidget(_lbl("Asunto del correo (editable)"))
        self._inp_asunto = QLineEdit()
        self._inp_asunto.setObjectName("AsuntoEdit")
        self._inp_asunto.setPlaceholderText("Se generará automáticamente...")
        aw.addWidget(self._inp_asunto)
        self._lbl_char = QLabel("0 caracteres")
        self._lbl_char.setStyleSheet(f"color: {QSSD['asunto_char_normal']}; font-size: 11px;")
        aw.addWidget(self._lbl_char)
        self._lay.addWidget(self._asunto_wrap)

        # ── Error paste ───────────────────────────────────────────────────────
        self._paste_error = QLabel("")
        self._paste_error.setObjectName("InlineError")
        self._paste_error.setWordWrap(True)
        self._paste_error.hide()
        self._lay.addWidget(self._paste_error)

        # ── Botón Pegar ───────────────────────────────────────────────────────
        self._btn_paste = QPushButton("  Pegar datos del portapapeles")
        self._btn_paste.setProperty("role", "btn-paste")
        apply_svg_icon(self._btn_paste, SVG.PEGAR, QSize(14, 14), QSSD["btn_paste_text"])
        self._btn_paste.clicked.connect(self.paste_requested.emit)
        self._lay.addWidget(self._btn_paste)

        # ── Conectar campos fijos ─────────────────────────────────────────────
        self._inp_contratante.textEdited.connect(lambda _: self.data_changed.emit())
        self._inp_contacto.textEdited.connect(lambda _: self.data_changed.emit())
        self._inp_vig_ini.textEdited.connect(lambda _: self.data_changed.emit())
        self._inp_vig_fin.textEdited.connect(lambda _: self.data_changed.emit())
        self._cb_cia_ramo.currentIndexChanged.connect(lambda _: self.data_changed.emit())
        self._inp_cia_poliza.textEdited.connect(lambda _: self.data_changed.emit())
        self._inp_asunto.textEdited.connect(lambda _: self._on_asunto_edited())

    # ── Reconstruir fila CIA según L1 ─────────────────────────────────────────

    def _rebuild_cia_row(self, l1: str):
        """Reconfigura la fila de CIA+campos según el L1 activo."""
        # Limpiar layout sin destruir widgets
        while self._cia_row_lay.count():
            self._cia_row_lay.takeAt(0)

        if l1 == "Póliza":
            # CIA | Vig.desde | Vig.hasta
            self._cia_row_lay.addWidget(_vwrap(_lbl("CIA aseguradora"), self._cb_cia))
            self._cia_row_lay.addWidget(self._w_vig_ini)
            self._cia_row_lay.addWidget(self._w_vig_fin)
            self._w_vig_ini.show(); self._w_vig_fin.show()
            self._w_cia_ramo.hide(); self._w_cia_poliza.hide()

            # Restaurar vigencia de memoria
            self._inp_vig_ini.blockSignals(True)
            self._inp_vig_fin.blockSignals(True)
            self._inp_vig_ini.setText(self._mem_vig_ini)
            self._inp_vig_fin.setText(self._mem_vig_fin)
            self._inp_vig_ini.blockSignals(False)
            self._inp_vig_fin.blockSignals(False)

        elif l1 == "Endoso":
            # Solo CIA (ancho completo)
            self._cia_row_lay.addWidget(_vwrap(_lbl("CIA aseguradora"), self._cb_cia))
            self._w_vig_ini.hide(); self._w_vig_fin.hide()
            self._w_cia_ramo.hide(); self._w_cia_poliza.hide()

        elif l1 == "Declaración mensual":
            # CIA | Ramo | Nro.Póliza
            self._cia_row_lay.addWidget(_vwrap(_lbl("CIA aseguradora"), self._cb_cia))
            self._cia_row_lay.addWidget(self._w_cia_ramo)
            self._cia_row_lay.addWidget(self._w_cia_poliza)
            self._w_vig_ini.hide(); self._w_vig_fin.hide()
            self._w_cia_ramo.show(); self._w_cia_poliza.show()

    # ── Botones de fila ───────────────────────────────────────────────────────

    def _make_add_btn(self, label: str, slot) -> QPushButton:
        btn = QPushButton(f"  {label}")
        btn.setProperty("role", "btn-add-row")
        apply_svg_icon(btn, SVG.AGREGAR, QSize(14, 14), QSSD["btn_linea_text"])
        btn.clicked.connect(slot)
        return btn

    def _make_del_btn(self, slot) -> QPushButton:
        btn = QPushButton()
        btn.setProperty("role", "btn-del-row")
        btn.setToolTip("Eliminar fila")
        btn.setFixedSize(QSSD["btn_del_size"], QSSD["btn_del_size"])
        apply_svg_icon(btn, SVG.ELIMINAR, QSize(14, 14), QSSD["btn_del_icon"])
        btn.clicked.connect(slot)
        return btn

    def _upd_add_btn(self, btn: QPushButton, count: int, max_n: int,
                     label: str, visible: bool):
        btn.setVisible(visible)
        at_max = count >= max_n
        btn.setDisabled(at_max)
        btn.setText(f"  Máximo {max_n}" if at_max else f"  {label}")

    # ── Fila póliza ───────────────────────────────────────────────────────────

    def _make_pol_row(self, removable: bool,
                      ramo: str = "", pol: str = "") -> dict:
        rw = QWidget()
        lay = QHBoxLayout(rw)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(QSSD["spacing_field_inline"])

        cb_r = _cb(self._cfg.ramos())
        if ramo:
            i = cb_r.findText(ramo)
            if i >= 0: cb_r.setCurrentIndex(i)
        inp_p = _inp("001-2024-00123")
        if pol: inp_p.setText(pol)

        lay.addWidget(_vwrap(_lbl("Ramo"), cb_r))
        lay.addWidget(_vwrap(_lbl("Nro. de póliza"), inp_p))

        d = {"ramo_cb": cb_r, "pol_inp": inp_p, "row_widget": rw}
        if removable:
            d["del_btn"] = self._make_del_btn(lambda _, dd=d: self._rem_pol(dd))
            lay.addWidget(d["del_btn"], 0, Qt.AlignBottom)

        cb_r.currentIndexChanged.connect(lambda _: self.data_changed.emit())
        inp_p.textEdited.connect(lambda _: self.data_changed.emit())
        return d

    # ── Fila endoso ───────────────────────────────────────────────────────────

    def _make_end_row(self, removable: bool, lbl_end: str,
                      ramo: str = "", pol: str = "",
                      end: str = "", mov: str = "") -> dict:
        rw = QWidget()
        lay = QHBoxLayout(rw)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(QSSD["spacing_field_inline"])

        cb_r = _cb(self._cfg.ramos())
        if ramo:
            i = cb_r.findText(ramo); i >= 0 and cb_r.setCurrentIndex(i)
        inp_p = _inp("Nro.")
        if pol: inp_p.setText(pol)
        lbl_e_w = _lbl(lbl_end)
        inp_e = _inp("END-001")
        if end: inp_e.setText(end)
        inp_m = _inp("Descripción...")
        if mov: inp_m.setText(mov)

        lay.addWidget(_vwrap(_lbl("Ramo"), cb_r))
        lay.addWidget(_vwrap(_lbl("Nro. de póliza"), inp_p))
        lay.addWidget(_vwrap(lbl_e_w, inp_e))
        lay.addWidget(_vwrap(_lbl("Movimiento"), inp_m))

        d = {
            "ramo_cb": cb_r, "pol_inp": inp_p,
            "end_inp": inp_e, "mov_inp": inp_m,
            "lbl_end": lbl_e_w, "row_widget": rw,
        }
        if removable:
            d["del_btn"] = self._make_del_btn(lambda _, dd=d: self._rem_end(dd))
            lay.addWidget(d["del_btn"], 0, Qt.AlignBottom)

        cb_r.currentIndexChanged.connect(lambda _: self.data_changed.emit())
        for w in [inp_p, inp_e, inp_m]:
            w.textEdited.connect(lambda _: self.data_changed.emit())
        return d

    # ── Fila declaración ──────────────────────────────────────────────────────

    def _make_decl_row(self, removable: bool,
                       nro: str = "", mes: str = "", ope: str = "") -> dict:
        rw = QWidget()
        lay = QHBoxLayout(rw)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(QSSD["spacing_field_inline"])

        inp_n = _inp("DEC-001")
        if nro: inp_n.setText(nro)
        inp_m = _inp("Ej. Marzo 2025")
        if mes: inp_m.setText(mes)
        inp_o = _inp("OPE", numeric=True)
        if ope: inp_o.setText(ope)

        lay.addWidget(_vwrap(_lbl("Nro. de declaración"), inp_n))
        lay.addWidget(_vwrap(_lbl("Mes de declaración"), inp_m))
        lay.addWidget(_vwrap(_lbl("OPE"), inp_o))

        d = {"nro_inp": inp_n, "mes_inp": inp_m,
             "ope_inp": inp_o, "row_widget": rw}
        if removable:
            d["del_btn"] = self._make_del_btn(lambda _, dd=d: self._rem_decl(dd))
            lay.addWidget(d["del_btn"], 0, Qt.AlignBottom)

        for w in [inp_n, inp_m, inp_o]:
            w.textEdited.connect(lambda _: self.data_changed.emit())
        return d

    # ── Remove ────────────────────────────────────────────────────────────────

    def _rem_pol(self, d: dict):
        if d in self._pol_rows:
            d["row_widget"].deleteLater()
            self._pol_rows.remove(d)
            self._upd_add_btn(self._btn_add_pol, len(self._pol_rows),
                              MAX_POL, "Agregar póliza", True)
            self.data_changed.emit()

    def _rem_end(self, d: dict):
        if d in self._end_rows:
            d["row_widget"].deleteLater()
            self._end_rows.remove(d)
            self._upd_add_btn(self._btn_add_end, len(self._end_rows),
                              MAX_END, "Agregar endoso", True)
            self.data_changed.emit()

    def _rem_decl(self, d: dict):
        if d in self._decl_rows:
            d["row_widget"].deleteLater()
            self._decl_rows.remove(d)
            self._upd_add_btn(self._btn_add_decl, len(self._decl_rows),
                              MAX_DECL, "Agregar declaración", True)
            self.data_changed.emit()

    # ── Add ───────────────────────────────────────────────────────────────────

    def _on_add_pol(self):
        if len(self._pol_rows) >= MAX_POL: return
        d = self._make_pol_row(removable=True)
        self._pol_rows.append(d)
        self._sec_pol_lay.addWidget(d["row_widget"])
        self._upd_add_btn(self._btn_add_pol, len(self._pol_rows),
                          MAX_POL, "Agregar póliza", True)
        self.data_changed.emit()

    def _on_add_end(self):
        if len(self._end_rows) >= MAX_END: return
        lb = self._cfg.label_endoso(self._cb_cia.currentText())
        d = self._make_end_row(removable=True, lbl_end=lb)
        self._end_rows.append(d)
        self._sec_end_lay.addWidget(d["row_widget"])
        self._upd_add_btn(self._btn_add_end, len(self._end_rows),
                          MAX_END, "Agregar endoso", True)
        self.data_changed.emit()

    def _on_add_decl(self):
        if len(self._decl_rows) >= MAX_DECL: return
        d = self._make_decl_row(removable=True)
        self._decl_rows.append(d)
        self._sec_decl_lay.addWidget(d["row_widget"])
        self._upd_add_btn(self._btn_add_decl, len(self._decl_rows),
                          MAX_DECL, "Agregar declaración", True)
        self.data_changed.emit()

    def _on_cia_changed(self):
        cia = self._cb_cia.currentText()
        lb  = self._cfg.label_endoso(cia)
        for row in self._end_rows:
            if "lbl_end" in row:
                row["lbl_end"].setText(lb)
        self.data_changed.emit()

    def _on_asunto_edited(self):
        self._asunto_usr_edited = True
        self._update_char_count()
        self.data_changed.emit()

    def _update_char_count(self):
        n = len(self._inp_asunto.text())
        self._lbl_char.setText(f"{n} caracteres")
        color = (QSSD['asunto_char_over']  if n > 100 else
                 QSSD['asunto_char_warn']   if n > 80  else
                 QSSD['asunto_char_normal'])
        self._lbl_char.setStyleSheet(f"color: {color}; font-size: 11px;")

    # ── API pública ───────────────────────────────────────────────────────────

    def adapt_fields(self, tpl_l1: str, tpl_l2: str, cia: str):
        """Muestra/oculta secciones. Reconstruye fila CIA si L1 cambió."""
        es_pol  = tpl_l1 == "Póliza"
        es_end  = tpl_l1 == "Endoso"
        es_decl = tpl_l1 == "Declaración mensual"
        es_multi = "programa" in tpl_l2.lower() or "colectivo" in tpl_l2.lower()

        # Guardar vigencia en memoria antes de cambiar L1
        if self._current_l1 == "Póliza" and tpl_l1 != "Póliza":
            self._mem_vig_ini = self._inp_vig_ini.text().strip()
            self._mem_vig_fin = self._inp_vig_fin.text().strip()

        if tpl_l1 != self._current_l1:
            self._rebuild_cia_row(tpl_l1)
            self._current_l1 = tpl_l1

        # Sección pólizas
        if es_pol:
            self._sec_pol.show()
            if not self._pol_rows:
                d = self._make_pol_row(removable=False)
                self._pol_rows.append(d)
                self._sec_pol_lay.addWidget(d["row_widget"])
            self._upd_add_btn(self._btn_add_pol, len(self._pol_rows),
                              MAX_POL, "Agregar póliza", es_multi)
        else:
            self._sec_pol.hide()
            self._btn_add_pol.hide()

        # Sección endosos
        if es_end:
            self._sec_end.show()
            lb = self._cfg.label_endoso(cia)
            if not self._end_rows:
                d = self._make_end_row(removable=False, lbl_end=lb)
                self._end_rows.append(d)
                self._sec_end_lay.addWidget(d["row_widget"])
            if self._end_rows and "lbl_end" in self._end_rows[0]:
                self._end_rows[0]["lbl_end"].setText(lb)
            self._upd_add_btn(self._btn_add_end, len(self._end_rows),
                              MAX_END, "Agregar endoso",
                              "colectivo" in tpl_l2.lower())
        else:
            self._sec_end.hide()
            self._btn_add_end.hide()

        # Sección declaraciones
        if es_decl:
            self._sec_decl.show()
            if not self._decl_rows:
                d = self._make_decl_row(removable=False)
                self._decl_rows.append(d)
                self._sec_decl_lay.addWidget(d["row_widget"])
            self._upd_add_btn(self._btn_add_decl, len(self._decl_rows),
                              MAX_DECL, "Agregar declaración",
                              "colectivo" in tpl_l2.lower())
        else:
            self._sec_decl.hide()
            self._btn_add_decl.hide()

    def hard_reset(self):
        """Reset total — bloquea señales durante limpieza."""
        for w in [self._inp_contratante, self._inp_contacto,
                  self._inp_vig_ini, self._inp_vig_fin,
                  self._inp_cia_poliza, self._inp_asunto]:
            w.blockSignals(True); w.clear(); w.blockSignals(False)

        for cb in [self._cb_cia, self._cb_cia_ramo]:
            cb.blockSignals(True); cb.setCurrentIndex(0); cb.blockSignals(False)

        for rows in [self._pol_rows, self._end_rows, self._decl_rows]:
            for d in rows: d["row_widget"].deleteLater()
            rows.clear()

        self._mem_vig_ini = ""
        self._mem_vig_fin = ""
        self._current_l1  = ""
        self._asunto_usr_edited = False
        self._update_char_count()
        self._paste_error.hide()

    def soft_reset_for_l1(self, new_l1: str):
        """Conserva campos fijos, limpia secciones variables que no corresponden."""
        # Guardar vigencia si venimos de Póliza
        if self._current_l1 == "Póliza":
            self._mem_vig_ini = self._inp_vig_ini.text().strip()
            self._mem_vig_fin = self._inp_vig_fin.text().strip()

        if new_l1 != "Póliza":
            for d in self._pol_rows: d["row_widget"].deleteLater()
            self._pol_rows.clear()
        if new_l1 != "Endoso":
            for d in self._end_rows: d["row_widget"].deleteLater()
            self._end_rows.clear()
        if new_l1 != "Declaración mensual":
            for d in self._decl_rows: d["row_widget"].deleteLater()
            self._decl_rows.clear()

    def soft_reset_for_l2(self, tpl_l1: str, prev_l2: str, new_l2: str):
        """Soft reset al cambiar entre L2 del mismo L1 (de multi → individual)."""
        def _is_multi(l2): return "programa" in l2.lower() or "colectivo" in l2.lower()
        if not (_is_multi(prev_l2) and not _is_multi(new_l2)):
            return
        if tpl_l1 == "Póliza" and len(self._pol_rows) > 1:
            for d in self._pol_rows[1:]: d["row_widget"].deleteLater()
            self._pol_rows = self._pol_rows[:1]
        elif tpl_l1 == "Endoso" and len(self._end_rows) > 1:
            for d in self._end_rows[1:]: d["row_widget"].deleteLater()
            self._end_rows = self._end_rows[:1]
        elif tpl_l1 == "Declaración mensual" and len(self._decl_rows) > 1:
            for d in self._decl_rows[1:]: d["row_widget"].deleteLater()
            self._decl_rows = self._decl_rows[:1]

    def set_asunto_visible(self, visible: bool):
        self._asunto_wrap.setVisible(visible)
        self._sep_asunto.setVisible(visible)

    def set_asunto(self, texto: str, user_edit: bool = False):
        if not user_edit and not self._asunto_usr_edited:
            self._inp_asunto.blockSignals(True)
            self._inp_asunto.setText(texto)
            self._inp_asunto.blockSignals(False)
            self._update_char_count()

    def get_asunto(self) -> str:    return self._inp_asunto.text().strip()
    def get_contratante(self) -> str: return self._inp_contratante.text().strip()
    def get_cia(self) -> str:       return self._cb_cia.currentText()

    def get_all_data(self) -> dict:
        polizas = [{"ramo": d["ramo_cb"].currentText(),
                    "pol":  d["pol_inp"].text().strip()}
                   for d in self._pol_rows]
        endosos = [{"ramo": d["ramo_cb"].currentText(),
                    "pol":  d["pol_inp"].text().strip(),
                    "end":  d["end_inp"].text().strip(),
                    "mov":  d["mov_inp"].text().strip()}
                   for d in self._end_rows]
        decls   = [{"nro_decl": d["nro_inp"].text().strip(),
                    "mes":      d["mes_inp"].text().strip(),
                    "ope":      d["ope_inp"].text().strip()}
                   for d in self._decl_rows]

        # Ramo/póliza de declaración están en la fila CIA para el L1 decl
        cia_ramo  = self._cb_cia_ramo.currentText()
        cia_poliza = self._inp_cia_poliza.text().strip()

        return {
            "contratante":  self._inp_contratante.text().strip(),
            "contacto":     self._inp_contacto.text().strip(),
            "cia":          self._cb_cia.currentText(),
            "vigencia_ini": self._inp_vig_ini.text().strip(),
            "vigencia_fin": self._inp_vig_fin.text().strip(),
            "cia_ramo":     cia_ramo,
            "cia_poliza":   cia_poliza,
            "polizas":      polizas,
            "endosos":      endosos,
            "declaraciones": decls,
        }

    def show_paste_error(self, msg: str):
        self._paste_error.setText(msg)
        self._paste_error.show()

    def apply_paste(self, datos: dict, cfg: ConfigLoader):
        self._paste_error.hide()
        if "contratante" in datos:
            self._inp_contratante.setText(datos["contratante"])
        if "contacto" in datos:
            self._inp_contacto.setText(datos["contacto"])
        if "aseguradora" in datos:
            idx = self._cb_cia.findText(datos["aseguradora"])
            if idx >= 0:
                self._cb_cia.setCurrentIndex(idx)
            else:
                self.show_paste_error(
                    f"CIA '{datos['aseguradora']}' no encontrada. "
                    "Selecciónala manualmente."
                )
        if self._pol_rows:
            if "nro_poliza" in datos:
                self._pol_rows[0]["pol_inp"].setText(datos["nro_poliza"])
            if "ramo" in datos:
                i = self._pol_rows[0]["ramo_cb"].findText(datos["ramo"])
                if i >= 0: self._pol_rows[0]["ramo_cb"].setCurrentIndex(i)
        if "vigencia_inicio" in datos:
            self._inp_vig_ini.setText(datos["vigencia_inicio"])
        if "vigencia_fin" in datos:
            self._inp_vig_fin.setText(datos["vigencia_fin"])
        self._asunto_usr_edited = False
        self.data_changed.emit()
