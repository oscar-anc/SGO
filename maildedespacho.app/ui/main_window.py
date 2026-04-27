# coding: utf-8
"""
ui/main_window.py — Ventana principal de MailDeDespacho.

Estructura de la UI:
  ┌─ AppTitleBar ──────────────────────────────────────────────┐
  │  [Logo] MailDeDespacho              [Min][Max][X]          │
  └────────────────────────────────────────────────────────────┘
  ┌─ QScrollArea (scroll_area) ────────────────────────────────┐
  │  ┌─ BlockWidget: Línea de negocio ────────────────────────┐ │
  │  │  [RRGG]  [Transportes]                                 │ │
  │  └────────────────────────────────────────────────────────┘ │
  │  ┌─ BlockWidget: Tipo de plantilla (oculto hasta L.N.) ───┐ │
  │  │  [Póliza] [Endoso] [Declaración mensual]               │ │
  │  │  ── ── ── ── ── ──                                     │ │
  │  │  ○ Despacho individual   ○ Despacho programa           │ │
  │  │  ○ Regularización (ind)  ○ Regularización (prog)       │ │
  │  └────────────────────────────────────────────────────────┘ │
  │  ┌─ BlockWidget: Modo de envío ────────────────────────────┐ │
  │  │  [Correo nuevo]  [Responder a todos]                   │ │
  │  └────────────────────────────────────────────────────────┘ │
  │  ┌─ BlockWidget: Correo original (solo reply) ─────────────┐ │
  │  │  [📧 Seleccionar .msg...]                               │ │
  │  │  Asunto: ○ Mantener original  ○ Generar nuevo          │ │
  │  └────────────────────────────────────────────────────────┘ │
  │  ┌─ BlockWidget: Datos del despacho ───────────────────────┐ │
  │  │  Contratante  |  Contacto                               │ │
  │  │  CIA          |  Vigencia desde  |  Vigencia hasta      │ │
  │  │  [Filas dinámicas Ramo + Póliza]                        │ │
  │  │  [Filas dinámicas Endoso / Declaración]                 │ │
  │  │  Asunto del correo (editable)  [contador]               │ │
  │  │  [Pegar datos]                                          │ │
  │  └────────────────────────────────────────────────────────┘ │
  │  ┌─ BlockWidget: Vista previa ─────────────────────────────┐ │
  │  │  [QWebEngineView con HTML de la plantilla]              │ │
  │  └────────────────────────────────────────────────────────┘ │
  │  ┌─ Barra de acciones ─────────────────────────────────────┐ │
  │  │  [Limpiar]              [Abrir en Outlook]              │ │
  │  └────────────────────────────────────────────────────────┘ │
  └────────────────────────────────────────────────────────────┘
"""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import Qt, QSize, QPoint, QTimer
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QSizePolicy,
    QFileDialog,
)

from theme import QSSD, build_qss
from svgs import SVG, svg_icon, apply_svg_icon
from config_loader import ConfigLoader, parse_clipboard_data
from template_engine import TemplateEngine, DespachoContext
from outlook_bridge import OutlookBridge, OutlookError

from ui.widgets.block_widget import BlockWidget
from ui.widgets.empresa_selector import EmpresaSelector
from ui.widgets.plantilla_selector import PlantillaSelector
from ui.widgets.modo_envio import ModoEnvio
from ui.widgets.datos_despacho import DatosDespacho
from ui.widgets.vista_previa import VistaPrevia
from ui.dialogs.outlook_dialog import OutlookWarningDialog

logger = logging.getLogger(__name__)

# Acento por empresa
_ACCENT_MAP = {
    "RRGG":        (QSSD["accent_rrgg"],  QSSD["accent_rrgg_dark"],  QSSD["accent_rrgg_light"]),
    "Transportes": (QSSD["accent_trans"], QSSD["accent_trans_dark"], QSSD["accent_trans_light"]),
}


class AppTitleBar(QWidget):
    """Barra de título personalizada sin marco nativo."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("AppTitleBar")
        self.setFixedHeight(QSSD["titlebar_fixed_height"])
        self._drag_pos: QPoint | None = None
        self._window = parent

        lay = QHBoxLayout(self)
        lay.setContentsMargins(*QSSD["margins_titlebar_inner"])
        lay.setSpacing(QSSD["spacing_titlebar"])

        # Título
        self._lbl = QLabel("MailDeDespacho")
        self._lbl.setObjectName("AppTitleLabel")
        lay.addWidget(self._lbl)
        lay.addStretch()

        # Botones
        for role, svg, slot in [
            ("titlebar-min",   SVG.MINIMIZAR,  self._on_min),
            ("titlebar-max",   SVG.MAXIMIZAR,  self._on_max),
            ("titlebar-close", SVG.CERRAR,     self._on_close),
        ]:
            btn = QPushButton()
            btn.setProperty("role", role)
            btn.setFixedSize(QSSD["titlebar_btn_width"], QSSD["titlebar_fixed_height"])
            apply_svg_icon(btn, svg, QSize(14, 14), QSSD["text_on_dark"])
            btn.clicked.connect(slot)
            lay.addWidget(btn)

    def _on_min(self):   self._window.showMinimized()
    def _on_close(self): self._window.close()

    def _on_max(self):
        if self._window.isMaximized():
            self._window.showNormal()
        else:
            self._window.showMaximized()

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self._window.frameGeometry().topLeft()

    def mouseMoveEvent(self, e: QMouseEvent):
        if self._drag_pos and e.buttons() == Qt.LeftButton:
            self._window.move(e.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, e: QMouseEvent):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, e: QMouseEvent):
        self._on_max()


class MainWindow(QWidget):
    """Ventana principal sin marco nativo."""

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

        # Estado global de la selección
        self._empresa:  str = ""
        self._tpl_l1:   str = ""
        self._tpl_l2:   str = ""
        self._modo:     str = ""
        self._msg_path: str = ""
        self._asunto_usr_edited: bool = False

        self._build_ui()
        self._apply_theme()

        # Log de db.json
        if not self._cfg.is_loaded():
            logger.warning("db.json no disponible — usando valores por defecto.")

    # ── Construcción de UI ────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(*QSSD["margins_app_root"])
        root.setSpacing(QSSD["spacing_app_root"])

        # TitleBar
        self._titlebar = AppTitleBar(self)
        root.addWidget(self._titlebar)

        # ScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        root.addWidget(scroll)

        container = QWidget()
        self._content_lay = QVBoxLayout(container)
        self._content_lay.setContentsMargins(*QSSD["margins_scroll_content"])
        self._content_lay.setSpacing(QSSD["spacing_scroll_content"])
        scroll.setWidget(container)

        # ── Bloque 1: Línea de negocio ────────────────────────────────────────
        self._blk_empresa = BlockWidget("Línea de negocio")
        self._empresa_sel = EmpresaSelector()
        self._empresa_sel.empresa_changed.connect(self._on_empresa)
        self._blk_empresa.add_widget(self._empresa_sel)
        self._content_lay.addWidget(self._blk_empresa)

        # ── Bloque 2: Tipo de plantilla ───────────────────────────────────────
        self._blk_tpl = BlockWidget("Tipo de plantilla")
        self._tpl_sel = PlantillaSelector()
        self._tpl_sel.l1_changed.connect(self._on_tpl_l1)
        self._tpl_sel.l2_changed.connect(self._on_tpl_l2)
        self._blk_tpl.add_widget(self._tpl_sel)
        self._blk_tpl.hide()
        self._content_lay.addWidget(self._blk_tpl)

        # ── Bloque 3: Modo de envío ───────────────────────────────────────────
        self._blk_modo = BlockWidget("Modo de envío")
        self._modo_sel = ModoEnvio()
        self._modo_sel.modo_changed.connect(self._on_modo)
        self._blk_modo.add_widget(self._modo_sel)
        self._blk_modo.hide()
        self._content_lay.addWidget(self._blk_modo)

        # ── Bloque 4: Correo original .msg (reply) ────────────────────────────
        self._blk_msg = BlockWidget("Correo original (.msg)")
        self._blk_msg.hide()
        self._build_msg_block()
        self._content_lay.addWidget(self._blk_msg)

        # ── Bloque 5: Datos del despacho ──────────────────────────────────────
        self._blk_datos = BlockWidget("Datos del despacho")
        self._datos = DatosDespacho(self._cfg)
        self._datos.data_changed.connect(self._on_data_changed)
        self._datos.paste_requested.connect(self._on_paste)
        self._blk_datos.add_widget(self._datos)
        self._blk_datos.hide()
        self._content_lay.addWidget(self._blk_datos)

        # ── Bloque 6: Vista previa ────────────────────────────────────────────
        self._blk_preview = BlockWidget("Vista previa del correo")
        self._preview = VistaPrevia()
        self._blk_preview.add_widget(self._preview)
        self._blk_preview.hide()
        self._content_lay.addWidget(self._blk_preview)

        # ── Barra de acciones ─────────────────────────────────────────────────
        self._blk_actions = self._build_actions()
        self._blk_actions.hide()
        self._content_lay.addWidget(self._blk_actions)

        self._content_lay.addStretch()

    def _build_msg_block(self):
        """Construye el contenido del bloque .msg (selector + radio asunto)."""
        from PySide6.QtWidgets import QRadioButton, QButtonGroup

        lay = QVBoxLayout()
        lay.setSpacing(8)

        # Botón selector de archivo
        self._btn_msg = QPushButton("  Seleccionar archivo .msg...")
        self._btn_msg.setProperty("role", "btn-paste")
        apply_svg_icon(self._btn_msg, SVG.ARCHIVO_MSG, QSize(16, 16), QSSD["text_muted"])
        self._btn_msg.clicked.connect(self._on_select_msg)
        lay.addWidget(self._btn_msg)

        # Radio asunto
        radio_frame = QFrame()
        radio_frame.setObjectName("AsuntoRadioFrame")
        radio_lay = QHBoxLayout(radio_frame)
        radio_lay.setContentsMargins(12, 8, 12, 8)
        radio_lay.setSpacing(16)

        lbl_asunto = QLabel("Asunto:")
        lbl_asunto.setObjectName("FieldLabel")
        radio_lay.addWidget(lbl_asunto)

        self._rb_original = QRadioButton("Mantener asunto original")
        self._rb_nuevo    = QRadioButton("Generar nuevo asunto")
        self._rb_original.setChecked(True)

        self._bg_asunto = QButtonGroup(self)
        self._bg_asunto.addButton(self._rb_original, 0)
        self._bg_asunto.addButton(self._rb_nuevo,    1)
        self._bg_asunto.idClicked.connect(self._on_asunto_opt)

        radio_lay.addWidget(self._rb_original)
        radio_lay.addWidget(self._rb_nuevo)
        radio_lay.addStretch()

        lay.addWidget(radio_frame)
        self._blk_msg.add_layout(lay)

    def _build_actions(self) -> QWidget:
        """Construye la barra de acciones (Limpiar / Abrir en Outlook)."""
        bar = QWidget()
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(0, 4, 0, 8)
        lay.setSpacing(8)

        self._btn_limpiar = QPushButton("  Limpiar")
        self._btn_limpiar.setProperty("role", "btn-secondary")
        apply_svg_icon(self._btn_limpiar, SVG.LIMPIAR, QSize(14, 14), QSSD["text_muted"])
        self._btn_limpiar.clicked.connect(self._on_limpiar)

        self._btn_outlook = QPushButton("  Abrir en Outlook")
        self._btn_outlook.setProperty("role", "btn-primary")
        apply_svg_icon(self._btn_outlook, SVG.OUTLOOK, QSize(15, 15), "#FFFFFF")
        self._btn_outlook.clicked.connect(self._on_abrir_outlook)

        lay.addWidget(self._btn_limpiar)
        lay.addWidget(self._btn_outlook)
        return bar

    # ── Tema ──────────────────────────────────────────────────────────────────

    def _apply_theme(self):
        self.setStyleSheet(build_qss())

    def _update_accent(self, empresa: str):
        """Actualiza el color de acento en el QSS según la empresa activa."""
        from theme import QSSD as qssd
        accent, dark, light = _ACCENT_MAP.get(empresa, _ACCENT_MAP["RRGG"])
        qssd["accent"]            = accent
        qssd["accent_dark"]       = dark
        qssd["accent_light"]      = light
        qssd["btn_linea_sel_bg"]  = accent
        qssd["btn_linea_sel_border"] = accent
        qssd["radio_opt_sel_bg"]  = light
        qssd["radio_opt_sel_border"] = accent
        qssd["btn_primary_bg"]    = accent
        qssd["btn_primary_hover"] = dark
        qssd["btn_add_row_text"]  = accent
        qssd["btn_add_row_border"] = accent
        qssd["btn_add_row_hover_bg"] = light
        qssd["border_input_hover"] = accent
        qssd["border_input_focus"] = accent
        self._apply_theme()

    # ── Señales de la UI → lógica de estado ──────────────────────────────────

    def _on_empresa(self, empresa: str):
        self._empresa = empresa
        self._tpl_l1  = ""
        self._tpl_l2  = ""
        self._modo    = ""
        self._msg_path = ""
        self._asunto_usr_edited = False

        self._update_accent(empresa)

        # Actualizar selector de plantilla con opciones de la empresa
        self._tpl_sel.set_empresa(empresa)

        # Mostrar bloque de tipo de plantilla
        self._blk_tpl.show()

        # Ocultar bloques downstream
        self._blk_modo.hide()
        self._blk_msg.hide()
        self._blk_datos.hide()
        self._blk_preview.hide()
        self._blk_actions.hide()

        # Hard reset de datos
        self._datos.hard_reset()
        self._preview.clear()

    def _on_tpl_l1(self, l1: str):
        prev_l1 = self._tpl_l1
        self._tpl_l1 = l1
        self._tpl_l2 = ""
        self._modo   = ""

        # Soft reset: limpiar campos variables del L1 anterior
        if prev_l1 and prev_l1 != l1:
            self._datos.soft_reset_for_l1(l1)
            self._asunto_usr_edited = False

        self._blk_modo.hide()
        self._blk_msg.hide()
        self._blk_datos.hide()
        self._blk_preview.hide()
        self._blk_actions.hide()

    def _on_tpl_l2(self, l2: str):
        prev_l2 = self._tpl_l2
        self._tpl_l2 = l2
        self._asunto_usr_edited = False

        # Soft reset dentro del mismo L1
        if prev_l2:
            self._datos.soft_reset_for_l2(self._tpl_l1, prev_l2, l2)

        # Mostrar bloque de modo si todavía no lo estaba
        self._blk_modo.show()

        # Si el modo ya estaba elegido, actualizar campos y preview
        if self._modo:
            self._datos.adapt_fields(
                tpl_l1=self._tpl_l1,
                tpl_l2=l2,
                cia=self._datos.get_cia(),
            )
            self._refresh_asunto()
            self._refresh_preview()

    def _on_modo(self, modo: str):
        self._modo = modo

        if modo == "reply":
            self._blk_msg.show()
        else:
            self._blk_msg.hide()
            self._msg_path = ""

        self._blk_datos.show()
        self._blk_preview.show()
        self._blk_actions.show()

        # Adaptar campos según selección actual
        self._datos.adapt_fields(
            tpl_l1=self._tpl_l1,
            tpl_l2=self._tpl_l2,
            cia=self._datos.get_cia(),
        )
        self._refresh_asunto()
        self._refresh_preview()

    def _on_data_changed(self):
        """Llamado cada vez que cambia cualquier campo en DatosDespacho."""
        self._refresh_asunto()
        self._refresh_preview()

    def _on_asunto_opt(self, btn_id: int):
        # 0 = mantener original, 1 = generar nuevo
        self._refresh_asunto()

    def _on_select_msg(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar correo original",
            "",
            "Mensajes de Outlook (*.msg);;Todos los archivos (*.*)"
        )
        if path:
            self._msg_path = path
            name = Path(path).name
            self._btn_msg.setText(f"  {name}")
            apply_svg_icon(self._btn_msg, SVG.ARCHIVO_MSG, QSize(16, 16), QSSD["accent"])

    def _on_paste(self):
        """Parsea el portapapeles e intenta pre-llenar los campos."""
        from PySide6.QtWidgets import QApplication
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

    def _on_abrir_outlook(self):
        """Valida, construye el HTML y abre Outlook."""
        if not self._validate_before_open():
            return

        ctx = self._build_context()
        html = self._engine.render(ctx)
        asunto = self._datos.get_asunto()

        # Mostrar diálogo de advertencia PRIMERO, luego abrir Outlook
        dlg = OutlookWarningDialog(self)

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
                    msg_path=self._msg_path,
                    asunto=asunto,
                    html_body=html,
                    mantener_asunto_original=mantener,
                )

            dlg.exec()

        except OutlookError as e:
            self._show_error(str(e))

    # ── Validación ────────────────────────────────────────────────────────────

    def _validate_before_open(self) -> bool:
        """Retorna True si todo está listo para abrir Outlook."""
        if not self._empresa or not self._tpl_l1 or not self._tpl_l2 or not self._modo:
            self._show_error("Completa todas las selecciones antes de continuar.")
            return False

        if self._modo == "reply" and not self._msg_path:
            self._show_error(
                "Debes seleccionar el archivo .msg original\n"
                "para usar 'Responder a todos'."
            )
            return False

        if not self._datos.get_contratante():
            self._show_error("El campo 'Nombre contratante / asegurado' es obligatorio.")
            return False

        return True

    # ── Refresh de asunto y preview ───────────────────────────────────────────

    def _should_show_asunto(self) -> bool:
        if self._modo == "nuevo":
            return True
        if self._modo == "reply" and self._rb_nuevo.isChecked():
            return True
        return False

    def _refresh_asunto(self):
        mostrar = self._should_show_asunto()
        self._datos.set_asunto_visible(mostrar)

        if mostrar and not self._asunto_usr_edited:
            asunto = self._build_asunto_auto()
            self._datos.set_asunto(asunto, user_edit=False)

    def _build_asunto_auto(self) -> str:
        """Construye el asunto concatenado automáticamente."""
        d = self._datos.get_all_data()
        cli  = d.get("contratante") or "…"
        cia  = d.get("cia")         or "…"
        ramo = ""
        pol  = ""

        polizas = d.get("polizas", [])
        endosos = d.get("endosos", [])
        decls   = d.get("declaraciones", [])

        if polizas:
            ramo = polizas[0].get("ramo") or "…"
            pol  = polizas[0].get("pol")  or "…"
        elif endosos:
            ramo = endosos[0].get("ramo") or "…"
            pol  = endosos[0].get("pol")  or "…"

        vig_i = d.get("vigencia_ini") or "…"
        vig_f = d.get("vigencia_fin") or "…"
        mes   = d.get("mes_decl")     or "…"
        mov   = (endosos[0].get("mov") if endosos else "") or "…"

        if self._tpl_l1 == "Declaración mensual":
            return f"DESPACHO DECLARACIÓN MENSUAL | {cli} | {cia} | {ramo} Pól. {pol} | {mes}"
        if self._tpl_l1 == "Endoso":
            return f"DESPACHO DE ENDOSO | {cli} | {cia} | {ramo} Pól. {pol} | {mov}"
        if "programa" in self._tpl_l2.lower():
            return f"DESPACHO PROGRAMA DE SEGUROS | {cli} | {cia} | {vig_i}–{vig_f}"
        return f"DESPACHO DE PÓLIZA | {cli} | {cia} | {ramo} Pól. {pol} | {vig_i}–{vig_f}"

    def _refresh_preview(self):
        if not self._modo:
            return
        ctx = self._build_context()
        html = self._engine.render(ctx)
        self._preview.set_html(html)

    def _build_context(self) -> DespachoContext:
        """Construye el DespachoContext desde el estado actual del formulario."""
        d = self._datos.get_all_data()
        accent, dark, _ = _ACCENT_MAP.get(self._empresa, _ACCENT_MAP["RRGG"])

        return DespachoContext(
            empresa=self._empresa,
            tpl_l1=self._tpl_l1,
            tpl_l2=self._tpl_l2,
            contratante=d.get("contratante", ""),
            contacto=d.get("contacto", ""),
            cia=d.get("cia", ""),
            vigencia_ini=d.get("vigencia_ini", ""),
            vigencia_fin=d.get("vigencia_fin", ""),
            mes_decl=d.get("mes_decl", ""),
            polizas=d.get("polizas", []),
            endosos=d.get("endosos", []),
            declaraciones=d.get("declaraciones", []),
            label_endoso=self._cfg.label_endoso(d.get("cia", "")),
            asunto=self._datos.get_asunto(),
            color_acento=accent,
            color_acento_dark=dark,
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _show_error(self, msg: str):
        from ui.dialogs.outlook_dialog import ErrorDialog
        dlg = ErrorDialog(msg, self)
        dlg.exec()

    def asunto_manually_edited(self):
        """Llamado por DatosDespacho cuando el usuario edita el asunto."""
        self._asunto_usr_edited = True

    def asunto_reset_manual(self):
        """Llamado cuando cambia L1/L2 — resetea la bandera de edición manual."""
        self._asunto_usr_edited = False
