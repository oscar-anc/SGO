# coding: utf-8
"""
ui/widgets/datos_despacho.py — Widget principal de captura de datos.

Campos fijos (siempre visibles):
  Contratante, Contacto, CIA (QComboBox), Vigencia desde/hasta

Campos variables (aparecen según L1/L2):
  - Filas de Ramo + Póliza (máx 12 para programa, 1 para individual)
  - Filas de Endoso: Ramo, Póliza, Nro.Endoso/Suplemento, Movimiento (máx 5)
  - Declaración mensual: Nro.Declaración, Mes (máx 5)
  - Asunto editable con contador de caracteres

Señales:
  data_changed()    — cualquier cambio en los campos
  paste_requested() — clic en botón Pegar
"""

from __future__ import annotations
import logging
from PySide6.QtCore import Signal, QSize, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QFrame, QSizePolicy,
)
from svgs import SVG, apply_svg_icon
from theme import QSSD
from config_loader import ConfigLoader

logger = logging.getLogger(__name__)

MAX_POL  = 12
MAX_END  = 5
MAX_DECL = 5


def _field(label_text: str) -> tuple[QLabel, QLineEdit]:
    lbl = QLabel(label_text)
    lbl.setObjectName("FieldLabel")
    inp = QLineEdit()
    inp.setPlaceholderText(label_text)
    return lbl, inp


def _combo_field(label_text: str, items: list[str]) -> tuple[QLabel, QComboBox]:
    lbl = QLabel(label_text)
    lbl.setObjectName("FieldLabel")
    cb = QComboBox()
    cb.addItem("")
    cb.addItems(items)
    return lbl, cb


class DatosDespacho(QWidget):
    data_changed    = Signal()
    paste_requested = Signal()

    def __init__(self, cfg: ConfigLoader, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._cfg = cfg
        self._pol_rows:  list[dict] = []   # [{ramo_cb, pol_inp, row_widget}]
        self._end_rows:  list[dict] = []   # [{ramo_cb, pol_inp, end_inp, mov_inp, row_widget}]
        self._decl_rows: list[dict] = []   # [{nro_inp, mes_inp, row_widget}]
        self._asunto_usr_edited = False
        self._build()

    # ── Construcción ──────────────────────────────────────────────────────────

    def _build(self):
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(QSSD["spacing_datos_fields"])

        # ── Fila 1: Contratante + Contacto ───────────────────────────────────
        g1 = QGridLayout()
        g1.setSpacing(QSSD["spacing_field_inline"])
        lbl_c, self._inp_contratante = _field("Nombre contratante / asegurado")
        lbl_ct, self._inp_contacto   = _field("Persona de contacto")
        g1.addWidget(lbl_c,                 0, 0)
        g1.addWidget(self._inp_contratante, 1, 0)
        g1.addWidget(lbl_ct,                0, 1)
        g1.addWidget(self._inp_contacto,    1, 1)
        self._lay.addLayout(g1)

        # ── Fila 2: CIA + Vigencia desde + Vigencia hasta (o Mes decl) ───────
        self._cia_vig_grid = QGridLayout()
        self._cia_vig_grid.setSpacing(QSSD["spacing_field_inline"])

        lbl_cia, self._cb_cia = _combo_field("CIA aseguradora", self._cfg.aseguradoras())
        self._cia_vig_grid.addWidget(lbl_cia,     0, 0)
        self._cia_vig_grid.addWidget(self._cb_cia, 1, 0)

        lbl_vi, self._inp_vig_ini = _field("Vigencia desde")
        self._inp_vig_ini.setMaxLength(4)
        self._inp_vig_ini.setPlaceholderText("2024")
        self._cia_vig_grid.addWidget(lbl_vi,          0, 1)
        self._cia_vig_grid.addWidget(self._inp_vig_ini, 1, 1)

        lbl_vf, self._inp_vig_fin = _field("Vigencia hasta")
        self._inp_vig_fin.setMaxLength(4)
        self._inp_vig_fin.setPlaceholderText("2025")
        self._cia_vig_grid.addWidget(lbl_vf,          0, 2)
        self._cia_vig_grid.addWidget(self._inp_vig_fin, 1, 2)

        # Mes declaración (oculto por defecto)
        lbl_mes, self._inp_mes = _field("Mes de declaración")
        self._inp_mes.setPlaceholderText("Ej. Marzo 2025")
        self._cia_vig_grid.addWidget(lbl_mes,     0, 1)
        self._cia_vig_grid.addWidget(self._inp_mes, 1, 1)
        self._inp_mes.hide()
        lbl_mes.hide()
        self._lbl_mes = lbl_mes  # guardar ref para show/hide
        self._lay.addLayout(self._cia_vig_grid)

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

        # ── Separador ─────────────────────────────────────────────────────────
        self._sep_asunto = QFrame()
        self._sep_asunto.setFrameShape(QFrame.HLine)
        self._sep_asunto.setFixedHeight(1)
        self._sep_asunto.setStyleSheet(
            f"background-color: {QSSD['border_block']}; border: none;"
        )
        self._sep_asunto.hide()
        self._lay.addWidget(self._sep_asunto)

        # ── Asunto editable ───────────────────────────────────────────────────
        self._asunto_wrap = QWidget()
        self._asunto_wrap.hide()
        aw_lay = QVBoxLayout(self._asunto_wrap)
        aw_lay.setContentsMargins(0, 0, 0, 0)
        aw_lay.setSpacing(4)

        lbl_asunto = QLabel("Asunto del correo (editable)")
        lbl_asunto.setObjectName("FieldLabel")
        aw_lay.addWidget(lbl_asunto)

        self._inp_asunto = QLineEdit()
        self._inp_asunto.setObjectName("AsuntoEdit")
        self._inp_asunto.setPlaceholderText("Se generará automáticamente...")
        aw_lay.addWidget(self._inp_asunto)

        self._lbl_char = QLabel("0 caracteres")
        self._lbl_char.setObjectName("CharCount")
        self._lbl_char.setStyleSheet(f"color: {QSSD['asunto_char_normal']}; font-size: 11px;")
        aw_lay.addWidget(self._lbl_char)

        self._lay.addWidget(self._asunto_wrap)

        # ── Error de paste ────────────────────────────────────────────────────
        self._paste_error = QLabel("")
        self._paste_error.setObjectName("InlineError")
        self._paste_error.setWordWrap(True)
        self._paste_error.hide()
        self._lay.addWidget(self._paste_error)

        # ── Botón Pegar ───────────────────────────────────────────────────────
        self._btn_paste = QPushButton("  Pegar datos del portapapeles")
        self._btn_paste.setProperty("role", "btn-paste")
        apply_svg_icon(self._btn_paste, SVG.PEGAR, QSize(14, 14), QSSD["text_muted"])
        self._btn_paste.clicked.connect(self.paste_requested.emit)
        self._lay.addWidget(self._btn_paste)

        # ── Conectar señales de campos fijos ──────────────────────────────────
        self._inp_contratante.textEdited.connect(self.data_changed.emit)
        self._inp_contacto.textEdited.connect(self.data_changed.emit)
        self._cb_cia.currentIndexChanged.connect(self._on_cia_changed)
        self._inp_vig_ini.textEdited.connect(self.data_changed.emit)
        self._inp_vig_fin.textEdited.connect(self.data_changed.emit)
        self._inp_mes.textEdited.connect(self.data_changed.emit)
        self._inp_asunto.textEdited.connect(self._on_asunto_edited)

    # ── Botón Agregar ─────────────────────────────────────────────────────────

    def _make_add_btn(self, label: str, slot) -> QPushButton:
        btn = QPushButton(f"  {label}")
        btn.setProperty("role", "btn-add-row")
        apply_svg_icon(btn, SVG.AGREGAR, QSize(14, 14), QSSD["btn_add_row_text"])
        btn.clicked.connect(slot)
        return btn

    def _update_add_btn(self, btn: QPushButton, count: int, max_count: int,
                        base_label: str, visible: bool):
        btn.setVisible(visible)
        btn.setDisabled(count >= max_count)
        if count >= max_count:
            btn.setText(f"  Máximo {max_count} registros")
        else:
            btn.setText(f"  {base_label}")

    # ── Filas dinámicas ───────────────────────────────────────────────────────

    def _make_del_btn(self, slot) -> QPushButton:
        btn = QPushButton()
        btn.setProperty("role", "btn-del-row")
        btn.setToolTip("Eliminar fila")
        apply_svg_icon(btn, SVG.ELIMINAR, QSize(14, 14), QSSD["btn_del_icon"])
        btn.clicked.connect(slot)
        btn.setFixedSize(QSSD["btn_del_size"], QSSD["btn_del_size"])
        return btn

    def _make_pol_row(self, removable: bool, ramo: str = "", pol: str = "") -> dict:
        row_w = QWidget()
        lay = QHBoxLayout(row_w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(QSSD["spacing_field_inline"])

        # Ramo
        ramo_w = QWidget()
        rw = QVBoxLayout(ramo_w); rw.setContentsMargins(0,0,0,0); rw.setSpacing(4)
        lbl_r = QLabel("Ramo"); lbl_r.setObjectName("FieldLabel")
        cb_r = QComboBox()
        cb_r.addItem(""); cb_r.addItems(self._cfg.ramos())
        if ramo: cb_r.setCurrentText(ramo)
        rw.addWidget(lbl_r); rw.addWidget(cb_r)
        lay.addWidget(ramo_w)

        # Póliza
        pol_w = QWidget()
        pw = QVBoxLayout(pol_w); pw.setContentsMargins(0,0,0,0); pw.setSpacing(4)
        lbl_p = QLabel("Nro. de póliza"); lbl_p.setObjectName("FieldLabel")
        inp_p = QLineEdit(); inp_p.setPlaceholderText("001-2024-00123")
        if pol: inp_p.setText(pol)
        pw.addWidget(lbl_p); pw.addWidget(inp_p)
        lay.addWidget(pol_w)

        if removable:
            del_btn = self._make_del_btn(lambda _, r=None: self._remove_pol_row(r))
            lay.addWidget(del_btn, 0, Qt.AlignBottom)
            d = {"ramo_cb": cb_r, "pol_inp": inp_p, "row_widget": row_w, "del_btn": del_btn}
            del_btn.clicked.disconnect()
            del_btn.clicked.connect(lambda _, dd=d: self._remove_pol_row(dd))
        else:
            d = {"ramo_cb": cb_r, "pol_inp": inp_p, "row_widget": row_w}

        cb_r.currentIndexChanged.connect(self.data_changed.emit)
        inp_p.textEdited.connect(self.data_changed.emit)

        return d

    def _make_end_row(self, removable: bool, label_endoso: str,
                      ramo: str = "", pol: str = "",
                      end: str = "", mov: str = "") -> dict:
        row_w = QWidget()
        lay = QHBoxLayout(row_w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(QSSD["spacing_field_inline"])

        def _vfield(lbl_txt, placeholder, value=""):
            w = QWidget()
            vl = QVBoxLayout(w); vl.setContentsMargins(0,0,0,0); vl.setSpacing(4)
            lbl = QLabel(lbl_txt); lbl.setObjectName("FieldLabel")
            inp = QLineEdit(); inp.setPlaceholderText(placeholder)
            if value: inp.setText(value)
            vl.addWidget(lbl); vl.addWidget(inp)
            return w, lbl, inp

        # Ramo
        ramo_w = QWidget()
        rw = QVBoxLayout(ramo_w); rw.setContentsMargins(0,0,0,0); rw.setSpacing(4)
        lbl_r = QLabel("Ramo"); lbl_r.setObjectName("FieldLabel")
        cb_r = QComboBox()
        cb_r.addItem(""); cb_r.addItems(self._cfg.ramos())
        if ramo: cb_r.setCurrentText(ramo)
        rw.addWidget(lbl_r); rw.addWidget(cb_r)
        lay.addWidget(ramo_w)

        pol_cont, _, inp_p = _vfield("Nro. de póliza", "Nro.", pol)
        end_cont, lbl_e, inp_e = _vfield(label_endoso, "END-001", end)
        mov_cont, _, inp_m = _vfield("Movimiento del endoso", "Descripción...", mov)

        lay.addWidget(pol_cont)
        lay.addWidget(end_cont)
        lay.addWidget(mov_cont)

        d = {
            "ramo_cb": cb_r, "pol_inp": inp_p,
            "end_inp": inp_e, "mov_inp": inp_m,
            "lbl_end": lbl_e, "row_widget": row_w,
        }

        if removable:
            del_btn = self._make_del_btn(lambda _, dd=d: self._remove_end_row(dd))
            lay.addWidget(del_btn, 0, Qt.AlignBottom)
            d["del_btn"] = del_btn

        cb_r.currentIndexChanged.connect(self.data_changed.emit)
        for inp in [inp_p, inp_e, inp_m]:
            inp.textEdited.connect(self.data_changed.emit)

        return d

    def _make_decl_row(self, removable: bool,
                       nro: str = "", mes: str = "") -> dict:
        row_w = QWidget()
        lay = QHBoxLayout(row_w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(QSSD["spacing_field_inline"])

        def _vf(lbl_txt, ph, val=""):
            w = QWidget()
            vl = QVBoxLayout(w); vl.setContentsMargins(0,0,0,0); vl.setSpacing(4)
            lbl = QLabel(lbl_txt); lbl.setObjectName("FieldLabel")
            inp = QLineEdit(); inp.setPlaceholderText(ph)
            if val: inp.setText(val)
            vl.addWidget(lbl); vl.addWidget(inp)
            return w, inp

        nro_cont, inp_n = _vf("Nro. de declaración", "DEC-001", nro)
        mes_cont, inp_m = _vf("Mes de declaración", "Ej. Marzo 2025", mes)

        lay.addWidget(nro_cont)
        lay.addWidget(mes_cont)

        d = {"nro_inp": inp_n, "mes_inp": inp_m, "row_widget": row_w}

        if removable:
            del_btn = self._make_del_btn(lambda _, dd=d: self._remove_decl_row(dd))
            lay.addWidget(del_btn, 0, Qt.AlignBottom)
            d["del_btn"] = del_btn

        inp_n.textEdited.connect(self.data_changed.emit)
        inp_m.textEdited.connect(self.data_changed.emit)

        return d

    # ── Remove rows ───────────────────────────────────────────────────────────

    def _remove_pol_row(self, d: dict):
        d["row_widget"].deleteLater()
        self._pol_rows.remove(d)
        self._update_add_btn(self._btn_add_pol, len(self._pol_rows), MAX_POL,
                             "Agregar póliza", True)
        self.data_changed.emit()

    def _remove_end_row(self, d: dict):
        d["row_widget"].deleteLater()
        self._end_rows.remove(d)
        self._update_add_btn(self._btn_add_end, len(self._end_rows), MAX_END,
                             "Agregar endoso", True)
        self.data_changed.emit()

    def _remove_decl_row(self, d: dict):
        d["row_widget"].deleteLater()
        self._decl_rows.remove(d)
        self._update_add_btn(self._btn_add_decl, len(self._decl_rows), MAX_DECL,
                             "Agregar declaración", True)
        self.data_changed.emit()

    # ── Add rows ──────────────────────────────────────────────────────────────

    def _on_add_pol(self):
        if len(self._pol_rows) >= MAX_POL: return
        lb = self._cfg.label_endoso(self._cb_cia.currentText())
        d = self._make_pol_row(removable=True)
        self._pol_rows.append(d)
        self._sec_pol_lay.addWidget(d["row_widget"])
        self._update_add_btn(self._btn_add_pol, len(self._pol_rows), MAX_POL,
                             "Agregar póliza", True)
        self.data_changed.emit()

    def _on_add_end(self):
        if len(self._end_rows) >= MAX_END: return
        lb = self._cfg.label_endoso(self._cb_cia.currentText())
        d = self._make_end_row(removable=True, label_endoso=lb)
        self._end_rows.append(d)
        self._sec_end_lay.addWidget(d["row_widget"])
        self._update_add_btn(self._btn_add_end, len(self._end_rows), MAX_END,
                             "Agregar endoso", True)
        self.data_changed.emit()

    def _on_add_decl(self):
        if len(self._decl_rows) >= MAX_DECL: return
        d = self._make_decl_row(removable=True)
        self._decl_rows.append(d)
        self._sec_decl_lay.addWidget(d["row_widget"])
        self._update_add_btn(self._btn_add_decl, len(self._decl_rows), MAX_DECL,
                             "Agregar declaración", True)
        self.data_changed.emit()

    def _on_cia_changed(self):
        cia = self._cb_cia.currentText()
        lb = self._cfg.label_endoso(cia)
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
        if n > 100:
            self._lbl_char.setStyleSheet(f"color: {QSSD['asunto_char_over']}; font-size: 11px;")
        elif n > 80:
            self._lbl_char.setStyleSheet(f"color: {QSSD['asunto_char_warn']}; font-size: 11px;")
        else:
            self._lbl_char.setStyleSheet(f"color: {QSSD['asunto_char_normal']}; font-size: 11px;")

    # ── API pública ───────────────────────────────────────────────────────────

    def adapt_fields(self, tpl_l1: str, tpl_l2: str, cia: str):
        """Muestra/oculta secciones según L1+L2 seleccionados."""
        es_pol  = tpl_l1 == "Póliza"
        es_end  = tpl_l1 == "Endoso"
        es_decl = tpl_l1 == "Declaración mensual"
        es_prog = "programa" in tpl_l2.lower()
        es_col  = "colectivo" in tpl_l2.lower()

        # Vigencia
        show_anual = not es_decl
        self._inp_vig_ini.setVisible(show_anual)
        self._inp_vig_fin.setVisible(show_anual)
        # Labels de vigencia (columnas 0,1 y 0,2 del grid)
        for col in [1, 2]:
            item = self._cia_vig_grid.itemAtPosition(0, col)
            if item and item.widget(): item.widget().setVisible(show_anual)
        self._inp_mes.setVisible(es_decl)
        self._lbl_mes.setVisible(es_decl)

        # Sección pólizas
        if es_pol:
            self._sec_pol.show()
            # Asegurar que existe al menos la fila base
            if not self._pol_rows:
                d = self._make_pol_row(removable=False)
                self._pol_rows.append(d)
                self._sec_pol_lay.addWidget(d["row_widget"])
            self._update_add_btn(self._btn_add_pol, len(self._pol_rows), MAX_POL,
                                 "Agregar póliza", es_prog or es_col)
        else:
            self._sec_pol.hide()
            self._btn_add_pol.hide()

        # Sección endosos
        if es_end:
            self._sec_end.show()
            lb = self._cfg.label_endoso(cia)
            if not self._end_rows:
                d = self._make_end_row(removable=False, label_endoso=lb)
                self._end_rows.append(d)
                self._sec_end_lay.addWidget(d["row_widget"])
            # Actualizar label en fila base
            if self._end_rows and "lbl_end" in self._end_rows[0]:
                self._end_rows[0]["lbl_end"].setText(lb)
            self._update_add_btn(self._btn_add_end, len(self._end_rows), MAX_END,
                                 "Agregar endoso", es_col)
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
            self._update_add_btn(self._btn_add_decl, len(self._decl_rows), MAX_DECL,
                                 "Agregar declaración", es_col)
        else:
            self._sec_decl.hide()
            self._btn_add_decl.hide()

    def hard_reset(self):
        """Limpia todo — se usa al cambiar de empresa o al hacer Limpiar."""
        for inp in [self._inp_contratante, self._inp_contacto,
                    self._inp_vig_ini, self._inp_vig_fin, self._inp_mes,
                    self._inp_asunto]:
            inp.clear()
        self._cb_cia.setCurrentIndex(0)

        for rows, lay in [
            (self._pol_rows,  self._sec_pol_lay),
            (self._end_rows,  self._sec_end_lay),
            (self._decl_rows, self._sec_decl_lay),
        ]:
            for d in rows:
                d["row_widget"].deleteLater()
            rows.clear()

        self._asunto_usr_edited = False
        self._update_char_count()
        self._paste_error.hide()

    def soft_reset_for_l1(self, new_l1: str):
        """Limpia solo las secciones variables que no comparten el nuevo L1."""
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
        """
        Soft reset entre opciones del mismo L1.
        De multi (programa/colectivo) a individual: conserva solo fila base.
        """
        def _is_multi(l2): return "programa" in l2.lower() or "colectivo" in l2.lower()

        era_multi = _is_multi(prev_l2)
        sera_multi = _is_multi(new_l2)

        if era_multi and not sera_multi:
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
            self._inp_asunto.setText(texto)
            self._update_char_count()

    def get_asunto(self) -> str:
        return self._inp_asunto.text().strip()

    def get_contratante(self) -> str:
        return self._inp_contratante.text().strip()

    def get_cia(self) -> str:
        return self._cb_cia.currentText()

    def get_all_data(self) -> dict:
        """Retorna todos los datos del formulario como dict."""
        polizas = [
            {"ramo": d["ramo_cb"].currentText(), "pol": d["pol_inp"].text().strip()}
            for d in self._pol_rows
        ]
        endosos = [
            {
                "ramo": d["ramo_cb"].currentText(),
                "pol":  d["pol_inp"].text().strip(),
                "end":  d["end_inp"].text().strip(),
                "mov":  d["mov_inp"].text().strip(),
            }
            for d in self._end_rows
        ]
        decls = [
            {"nro_decl": d["nro_inp"].text().strip(), "mes": d["mes_inp"].text().strip()}
            for d in self._decl_rows
        ]
        return {
            "contratante": self._inp_contratante.text().strip(),
            "contacto":    self._inp_contacto.text().strip(),
            "cia":         self._cb_cia.currentText(),
            "vigencia_ini": self._inp_vig_ini.text().strip(),
            "vigencia_fin": self._inp_vig_fin.text().strip(),
            "mes_decl":    self._inp_mes.text().strip(),
            "polizas":     polizas,
            "endosos":     endosos,
            "declaraciones": decls,
        }

    def show_paste_error(self, msg: str):
        self._paste_error.setText(msg)
        self._paste_error.show()

    def apply_paste(self, datos: dict, cfg: ConfigLoader):
        """Pre-llena campos desde datos del portapapeles."""
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
                    f"CIA '{datos['aseguradora']}' no encontrada en la lista. "
                    "Selecciónala manualmente."
                )
        if "nro_poliza" in datos and self._pol_rows:
            self._pol_rows[0]["pol_inp"].setText(datos["nro_poliza"])
        if "ramo" in datos and self._pol_rows:
            idx = self._pol_rows[0]["ramo_cb"].findText(datos["ramo"])
            if idx >= 0:
                self._pol_rows[0]["ramo_cb"].setCurrentIndex(idx)
        if "vigencia_inicio" in datos:
            self._inp_vig_ini.setText(datos["vigencia_inicio"])
        if "vigencia_fin" in datos:
            self._inp_vig_fin.setText(datos["vigencia_fin"])

        self._asunto_usr_edited = False
        self.data_changed.emit()
