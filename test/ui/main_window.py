# coding: utf-8
"""
ui/main_window.py — Ventana principal de MailDeDespacho.

Cambios clave:
  - Acento cambia con setProperty("empresa", X) + polish() — sin regenerar QSS
  - Vista previa expande el ancho de la ventana (no divide espacio existente)
  - Estado 0: todos los headers visibles desde el arranque, contenido oculto
  - Navegación sin reseteo al cambiar L2 dentro del mismo L1
  - Validación en CustomMessageBox listando campos pendientes
"""

from __future__ import annotations
import logging
from pathlib import Path

from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame,
    QFileDialog, QRadioButton, QButtonGroup,
)

from theme import QSSD, build_qss, get_palette
from svgs import SVG, apply_svg_icon
from config_loader import ConfigLoader, parse_clipboard_data
from template_engine import TemplateEngine, DespachoContext
from outlook_bridge import OutlookBridge, OutlookError

from ui.widgets.block_widget import BlockWidget
from ui.widgets.empresa_selector import EmpresaSelector
from ui.widgets.plantilla_selector import PlantillaSelector
from ui.widgets.modo_envio import ModoEnvio
from ui.widgets.datos_despacho import DatosDespacho
from ui.widgets.vista_previa import VistaPrevia
from ui.dialogs.outlook_dialog import OutlookWarningDialog, ErrorDialog

logger = logging.getLogger(__name__)

_ACCENT_MAP = {
    "RRGG":        ("accent_rrgg",  "accent_rrgg_dark",  "accent_rrgg_light"),
    "Transportes": ("accent_trans", "accent_trans_dark",  "accent_trans_light"),
}


# =============================================================================
# TITLEBAR
# =============================================================================

class AppTitleBar(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("AppTitleBar")
        self.setFixedHeight(QSSD["titlebar_fixed_height"])
        self._drag_pos: QPoint | None = None
        self._win = parent
        self._build()

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(*QSSD["margins_titlebar_inner"])
        lay.setSpacing(QSSD["spacing_titlebar"])

        lbl = QLabel("MailDeDespacho")
        lbl.setObjectName("AppTitleLabel")
        lay.addWidget(lbl)
        lay.addStretch()

        icon_sz = QSize(*QSSD["titlebar_logo_size"])
        bw = QSSD["titlebar_btn_width"]
        bh = QSSD["titlebar_fixed_height"]

        for role, svg, slot in [
            ("titlebar-min",   SVG.MINIMIZAR, lambda: self._win.showMinimized()),
            ("titlebar-max",   SVG.MAXIMIZAR, self._toggle_max),
            ("titlebar-close", SVG.CERRAR,    self._win.close),
        ]:
            btn = QPushButton()
            btn.setProperty("role", role)
            btn.setFixedSize(bw, bh)
            apply_svg_icon(btn, svg, icon_sz, QSSD["text_on_dark"])
            btn.clicked.connect(slot)
            lay.addWidget(btn)

    def _toggle_max(self):
        self._win.showNormal() if self._win.isMaximized() else self._win.showMaximized()

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self._win.frameGeometry().topLeft()

    def mouseMoveEvent(self, e: QMouseEvent):
        if self._drag_pos and e.buttons() == Qt.LeftButton:
            self._win.move(e.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, _):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, _):
        self._toggle_max()


# =============================================================================
# VENTANA PRINCIPAL
# =============================================================================

class MainWindow(QWidget):
    """
    Layout:
      ┌─ TitleBar ──────────────────────────────────────────┐
      ├─ QHBoxLayout ───────────────────────────────────────┤
      │  ┌─ Columna izq. (scroll fijo) ──┐  ┌─ Preview ──┐ │
      │  │  Bloques del formulario       │  │  (oculto   │ │
      │  │                               │  │   hasta    │ │
      │  │                               │  │   toggle)  │ │
      │  └───────────────────────────────┘  └────────────┘ │
      └─────────────────────────────────────────────────────┘

    Al activar preview: la ventana crece en ancho.
    Al ocultar preview: la ventana vuelve al ancho original.
    El formulario NO pierde espacio.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setMinimumSize(QSSD["app_min_width"], QSSD["app_min_height"])
        self.resize(QSSD["app_default_width"], QSSD["app_default_height"])
        self.setWindowTitle("MailDeDespacho")

        # Servicios
        self._cfg     = ConfigLoader()
        self._engine  = TemplateEngine()
        self._outlook = OutlookBridge()

        # Estado
        self._empresa:  str  = ""
        self._tpl_l1:   str  = ""
        self._tpl_l2:   str  = ""
        self._modo:     str  = ""
        self._msg_path: str  = ""
        self._asunto_usr_edited: bool = False
        self._preview_visible:   bool = False
        self._base_width: int = QSSD["app_default_width"]

        self._build_ui()

        # QSS estático — UNA SOLA VEZ
        self.setStyleSheet(build_qss())
        # Propiedad de empresa vacía al inicio
        self.setProperty("empresa", "")

        self._set_nav_state(0)

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(*QSSD["margins_app_root"])
        root.setSpacing(QSSD["spacing_app_root"])
        root.addWidget(AppTitleBar(self))

        # Contenedor principal horizontal
        self._main_row = QHBoxLayout()
        self._main_row.setContentsMargins(0, 0, 0, 0)
        self._main_row.setSpacing(0)
        root.addLayout(self._main_row)

        # ── Columna izquierda: formulario (ancho fijo) ────────────────────────
        left = QWidget()
        left.setFixedWidth(QSSD["app_default_width"])
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_lay.addWidget(scroll)

        form = QWidget()
        self._form_lay = QVBoxLayout(form)
        self._form_lay.setContentsMargins(*QSSD["margins_scroll_content"])
        self._form_lay.setSpacing(QSSD["spacing_scroll_content"])
        scroll.setWidget(form)

        self._build_blocks()
        self._form_lay.addStretch()

        self._left_col = left
        self._main_row.addWidget(left)

        # ── Columna derecha: preview (oculta inicialmente) ────────────────────
        sep = QFrame()
        sep.setFixedWidth(1)
        sep.setStyleSheet(f"background-color: {QSSD['border_block']};")
        self._main_row.addWidget(sep)
        self._preview_sep = sep
        self._preview_sep.hide()

        right = QWidget()
        right.setFixedWidth(QSSD["preview_panel_width"])
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(10, 10, 10, 10)
        right_lay.setSpacing(6)

        lbl_p = QLabel("VISTA PREVIA DEL CORREO")
        lbl_p.setObjectName("SLabel")
        right_lay.addWidget(lbl_p)

        self._preview = VistaPrevia()
        right_lay.addWidget(self._preview)

        self._right_col = right
        self._right_col.hide()
        self._main_row.addWidget(right)

    def _build_blocks(self):
        """Construye todos los bloques. En estado 0, el contenido interno está oculto."""

        # ── Bloque 1: Línea de negocio ────────────────────────────────────────
        blk1 = BlockWidget("Línea de negocio")
        self._empresa_sel = EmpresaSelector()
        self._empresa_sel.empresa_changed.connect(self._on_empresa)
        blk1.add_widget(self._empresa_sel)
        self._form_lay.addWidget(blk1)

        # ── Bloque 2: Tipo de plantilla ───────────────────────────────────────
        blk2 = BlockWidget("Tipo de plantilla")
        self._tpl_sel = PlantillaSelector()
        self._tpl_sel.l1_changed.connect(self._on_tpl_l1)
        self._tpl_sel.l2_changed.connect(self._on_tpl_l2)
        blk2.add_widget(self._tpl_sel)
        self._blk_tpl = blk2
        self._form_lay.addWidget(blk2)

        # ── Bloque 3: Modo de envío ───────────────────────────────────────────
        blk3 = BlockWidget("Modo de envío")
        self._modo_sel = ModoEnvio()
        self._modo_sel.modo_changed.connect(self._on_modo)
        blk3.add_widget(self._modo_sel)
        self._blk_modo = blk3
        self._form_lay.addWidget(blk3)

        # ── Bloque 4: Correo original .msg ────────────────────────────────────
        self._blk_msg = BlockWidget("Correo original (.msg)")
        self._build_msg_block()
        self._blk_msg.hide()
        self._form_lay.addWidget(self._blk_msg)

        # ── Bloque 5: Datos del despacho ──────────────────────────────────────
        blk5 = BlockWidget("Datos del despacho")
        self._datos = DatosDespacho(self._cfg)
        self._datos.data_changed.connect(self._on_data_changed)
        self._datos.paste_requested.connect(self._on_paste)
        blk5.add_widget(self._datos)
        self._blk_datos = blk5
        self._blk_datos_inner = self._datos   # referencia directa al contenido
        self._form_lay.addWidget(blk5)

        # ── Barra de acciones ─────────────────────────────────────────────────
        self._bar_actions = self._build_action_bar()
        self._form_lay.addWidget(self._bar_actions)

    def _build_msg_block(self):
        lay = QVBoxLayout()
        lay.setSpacing(8)

        self._btn_msg = QPushButton("  Seleccionar archivo .msg...")
        self._btn_msg.setProperty("role", "btn-paste")
        apply_svg_icon(self._btn_msg, SVG.ARCHIVO_MSG, QSize(16, 16),
                       QSSD["btn_paste_text"])
        self._btn_msg.clicked.connect(self._on_select_msg)
        lay.addWidget(self._btn_msg)

        radio_row = QHBoxLayout()
        radio_row.setSpacing(16)
        lbl_as = QLabel("Asunto:")
        lbl_as.setObjectName("FieldLabel")
        radio_row.addWidget(lbl_as)

        self._rb_original = QRadioButton("Mantener asunto original")
        self._rb_nuevo    = QRadioButton("Generar nuevo asunto")
        self._rb_original.setChecked(True)

        self._bg_asunto = QButtonGroup(self)
        self._bg_asunto.addButton(self._rb_original, 0)
        self._bg_asunto.addButton(self._rb_nuevo,    1)
        self._bg_asunto.idClicked.connect(self._on_asunto_opt)

        radio_row.addWidget(self._rb_original)
        radio_row.addWidget(self._rb_nuevo)
        radio_row.addStretch()
        lay.addLayout(radio_row)
        self._blk_msg.add_layout(lay)

    def _build_action_bar(self) -> QWidget:
        bar = QWidget()
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(0, 4, 0, 8)
        lay.setSpacing(8)

        self._btn_limpiar = QPushButton("  Limpiar")
        self._btn_limpiar.setProperty("role", "btn-secondary")
        apply_svg_icon(self._btn_limpiar, SVG.LIMPIAR,
                       QSize(14, 14), QSSD["btn_secondary_text"])
        self._btn_limpiar.clicked.connect(self._on_limpiar)

        self._btn_preview_toggle = QPushButton("  Vista previa")
        self._btn_preview_toggle.setProperty("role", "btn-secondary")
        apply_svg_icon(self._btn_preview_toggle, SVG.ARCHIVO_MSG,
                       QSize(14, 14), QSSD["btn_secondary_text"])
        self._btn_preview_toggle.clicked.connect(self._on_toggle_preview_validated)

        self._btn_outlook = QPushButton("  Abrir en Outlook")
        self._btn_outlook.setProperty("role", "btn-primary")
        apply_svg_icon(self._btn_outlook, SVG.OUTLOOK, QSize(15, 15), "#FFFFFF")
        self._btn_outlook.clicked.connect(self._on_abrir_outlook)

        lay.addWidget(self._btn_limpiar)
        lay.addWidget(self._btn_preview_toggle)
        lay.addStretch()
        lay.addWidget(self._btn_outlook)
        return bar

    # ── Navegación por estados ────────────────────────────────────────────────

    def _set_nav_state(self, state: int):
        """
        0 → Arranque: todos los bloques visibles con solo el header,
            contenido interno oculto excepto empresa y barra de acciones.
        1 → Empresa seleccionada: L1 visible.
        2 → L2 seleccionado: modo habilitado.
        3 → Modo elegido: datos visibles.
        """
        if state == 0:
            self._tpl_sel.hide_all()
            self._modo_sel.set_enabled(False)
            self._datos.hide()
            self._blk_msg.hide()

        elif state == 1:
            self._tpl_sel.show_l1()
            self._modo_sel.set_enabled(False)
            self._datos.hide()
            self._blk_msg.hide()

        elif state == 2:
            self._modo_sel.set_enabled(True)
            self._datos.hide()
            self._blk_msg.hide()

        elif state == 3:
            self._datos.show()
            if self._modo == "reply":
                self._blk_msg.show()
            else:
                self._blk_msg.hide()

    # ── Señales de empresa ────────────────────────────────────────────────────

    def _on_empresa(self, empresa: str):
        self._empresa  = empresa
        self._tpl_l1   = ""
        self._tpl_l2   = ""
        self._modo     = ""
        self._msg_path = ""
        self._asunto_usr_edited = False

        # Cambiar acento SIN regenerar QSS — solo polish
        self.setProperty("empresa", empresa)
        self.style().polish(self)

        self._tpl_sel.set_empresa(empresa)
        self._modo_sel.reset()
        self._datos.hard_reset()
        self._preview.clear()

        self._set_nav_state(1)

    # ── Señales de plantilla ──────────────────────────────────────────────────

    def _on_tpl_l1(self, l1: str):
        prev_l1 = self._tpl_l1
        self._tpl_l1 = l1
        self._tpl_l2 = ""
        self._asunto_usr_edited = False

        if prev_l1 and prev_l1 != l1:
            self._datos.soft_reset_for_l1(l1)

        self._modo_sel.reset()
        # No resetear modo completamente — mantener estado 2 si ya había L1
        self._set_nav_state(1)

    def _on_tpl_l2(self, l2: str):
        prev_l2 = self._tpl_l2
        self._tpl_l2 = l2
        self._asunto_usr_edited = False

        if prev_l2 and prev_l2 != l2:
            self._datos.soft_reset_for_l2(self._tpl_l1, prev_l2, l2)

        # Si ya había modo elegido, actualizar campos sin resetear modo
        if self._modo:
            self._datos.adapt_fields(
                tpl_l1=self._tpl_l1,
                tpl_l2=l2,
                cia=self._datos.get_cia(),
            )
            self._refresh_asunto()
            if self._preview_visible:
                self._refresh_preview()
            # Mantener estado 3 (datos visibles)
        else:
            self._set_nav_state(2)

    # ── Señales de modo de envío ──────────────────────────────────────────────

    def _on_modo(self, modo: str):
        self._modo = modo
        self._datos.adapt_fields(
            tpl_l1=self._tpl_l1,
            tpl_l2=self._tpl_l2,
            cia=self._datos.get_cia(),
        )
        self._refresh_asunto()
        self._set_nav_state(3)
        if self._preview_visible:
            self._refresh_preview()

    def _on_asunto_opt(self, _: int):
        self._refresh_asunto()

    def _on_select_msg(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar correo original", "",
            "Mensajes de Outlook (*.msg);;Todos los archivos (*.*)"
        )
        if path:
            self._msg_path = path
            self._btn_msg.setText(f"  {Path(path).name}")
            apply_svg_icon(self._btn_msg, SVG.ARCHIVO_MSG,
                           QSize(16, 16), QSSD["accent_rrgg"])

    def _on_paste(self):
        text = QApplication.clipboard().text()
        ok, datos, error = parse_clipboard_data(text)
        if not ok:
            self._datos.show_paste_error(error)
            return
        self._datos.apply_paste(datos, self._cfg)

    def _on_limpiar(self):
        self._datos.hard_reset()
        self._asunto_usr_edited = False
        self._preview.clear()
        self._refresh_asunto()

    def _on_toggle_preview(self):
        """Expande/contrae la ventana para mostrar el panel de preview."""
        panel_w = QSSD["preview_panel_width"]

        if not self._preview_visible:
            self._preview_visible = True
            # Expandir ventana hacia la derecha
            self._right_col.show()
            self._preview_sep.show()
            new_w = self.width() + panel_w + 1   # +1 por el separador
            self.resize(new_w, self.height())
            self._btn_preview_toggle.setText("  Ocultar preview")
            self._refresh_preview()
        else:
            self._preview_visible = False
            self._right_col.hide()
            self._preview_sep.hide()
            new_w = self.width() - panel_w - 1
            self.resize(max(new_w, QSSD["app_default_width"]), self.height())
            self._btn_preview_toggle.setText("  Vista previa")

    def _on_data_changed(self):
        self._refresh_asunto()
        if self._preview_visible:
            self._refresh_preview()

    # ── Abrir en Outlook ──────────────────────────────────────────────────────

    def _on_abrir_outlook(self):
        pending = self._get_pending_fields()
        if pending:
            self._show_pending_dialog(pending)
            return

        ctx  = self._build_context()
        html = self._engine.render(ctx)
        asunto = self._datos.get_asunto()

        try:
            if self._modo == "nuevo":
                self._outlook.nuevo_correo(asunto=asunto, html_body=html)
            else:
                ok, err = OutlookBridge.validate_msg_file(self._msg_path)
                if not ok:
                    self._show_error(err)
                    return
                mantener = self._rb_original.isChecked()
                self._outlook.responder_a_todos(
                    msg_path=self._msg_path, asunto=asunto,
                    html_body=html, mantener_asunto_original=mantener,
                )
            OutlookWarningDialog(self).exec()
        except OutlookError as e:
            self._show_error(str(e))

    # ── Validación con lista de pendientes ────────────────────────────────────

    def _get_pending_fields(self) -> list[str]:
        """Retorna lista de campos/pasos pendientes. Vacía = todo ok."""
        pending = []
        if not self._empresa:
            pending.append("• Línea de negocio")
        if not self._tpl_l1:
            pending.append("• Tipo de plantilla")
        elif not self._tpl_l2:
            pending.append("• Subtipo de plantilla")
        if not self._modo:
            pending.append("• Modo de envío")
        if self._modo == "reply" and not self._msg_path:
            pending.append("• Archivo .msg original")
        if not self._datos.get_contratante():
            pending.append("• Nombre contratante / asegurado")
        return pending

    def _show_pending_dialog(self, pending: list[str]):
        msg = "Antes de continuar, completa los siguientes campos:\n\n"
        msg += "\n".join(pending)
        ErrorDialog(msg, self, titulo="Campos pendientes").exec()

    # ── Vista previa también valida ───────────────────────────────────────────

    def _on_toggle_preview_validated(self):
        pending = self._get_pending_fields()
        if pending:
            self._show_pending_dialog(pending)
            return
        self._on_toggle_preview()

    # ── Asunto y preview ──────────────────────────────────────────────────────

    def _should_show_asunto(self) -> bool:
        return self._modo == "nuevo" or (
            self._modo == "reply" and self._rb_nuevo.isChecked()
        )

    def _refresh_asunto(self):
        mostrar = self._should_show_asunto() and bool(self._modo)
        self._datos.set_asunto_visible(mostrar)
        if mostrar and not self._asunto_usr_edited:
            self._datos.set_asunto(self._build_asunto_auto(), user_edit=False)

    def _build_asunto_auto(self) -> str:
        d   = self._datos.get_all_data()
        cli = d.get("contratante") or "…"
        cia = d.get("cia")         or "…"

        pols = d.get("polizas", [])
        ends = d.get("endosos", [])

        if self._tpl_l1 == "Declaración mensual":
            ramo = d.get("cia_ramo")   or "…"
            pol  = d.get("cia_poliza") or "…"
            mes  = (d.get("declaraciones") or [{}])[0].get("mes") or "…"
            return f"DESPACHO DECLARACIÓN MENSUAL | {cli} | {cia} | {ramo} Pól. {pol} | {mes}"

        if self._tpl_l1 == "Endoso":
            ramo = (ends[0].get("ramo") if ends else "") or "…"
            pol  = (ends[0].get("pol")  if ends else "") or "…"
            mov  = (ends[0].get("mov")  if ends else "") or "…"
            return f"DESPACHO DE ENDOSO | {cli} | {cia} | {ramo} Pól. {pol} | {mov}"

        ramo = (pols[0].get("ramo") if pols else "") or "…"
        pol  = (pols[0].get("pol")  if pols else "") or "…"
        vi   = d.get("vigencia_ini") or "…"
        vf   = d.get("vigencia_fin") or "…"

        if "programa" in self._tpl_l2.lower():
            return f"DESPACHO PROGRAMA DE SEGUROS | {cli} | {cia} | {vi}–{vf}"
        return f"DESPACHO DE PÓLIZA | {cli} | {cia} | {ramo} Pól. {pol} | {vi}–{vf}"

    def _refresh_preview(self):
        if not self._modo:
            return
        ctx  = self._build_context()
        html = self._engine.render(ctx)
        self._preview.set_html(html)

    def _build_context(self) -> DespachoContext:
        d = self._datos.get_all_data()
        c = QSSD
        ak, dk, _ = _ACCENT_MAP.get(self._empresa, _ACCENT_MAP["RRGG"])
        accent = c[ak]
        dark   = c[dk]

        # Para declaración mensual, ramo y póliza vienen de la fila CIA
        pols = d.get("polizas", [])
        if self._tpl_l1 == "Declaración mensual":
            pols = [{"ramo": d.get("cia_ramo", ""),
                     "pol":  d.get("cia_poliza", "")}]

        return DespachoContext(
            empresa=self._empresa, tpl_l1=self._tpl_l1, tpl_l2=self._tpl_l2,
            contratante=d.get("contratante", ""), contacto=d.get("contacto", ""),
            cia=d.get("cia", ""), vigencia_ini=d.get("vigencia_ini", ""),
            vigencia_fin=d.get("vigencia_fin", ""),
            mes_decl=(d.get("declaraciones") or [{}])[0].get("mes", ""),
            polizas=pols, endosos=d.get("endosos", []),
            declaraciones=d.get("declaraciones", []),
            label_endoso=self._cfg.label_endoso(d.get("cia", "")),
            asunto=self._datos.get_asunto(),
            color_acento=accent, color_acento_dark=dark,
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _show_error(self, msg: str):
        ErrorDialog(msg, self).exec()
