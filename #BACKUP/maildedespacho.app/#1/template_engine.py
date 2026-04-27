# coding: utf-8
"""
template_engine.py — Motor de plantillas HTML para correos de despacho.

Responsabilidades:
  1. Seleccionar la plantilla correcta (rrgg.html / transportes.html)
  2. Eliminar bloques condicionales que no aplican al contexto actual
  3. Sustituir todas las variables $VARIABLE por sus valores reales
  4. Retornar el HTML final listo para inyectar en Outlook

Uso:
    from template_engine import TemplateEngine, DespachoContext

    ctx = DespachoContext(
        empresa='RRGG',
        tpl_l1='Póliza',
        tpl_l2='Despacho programa',
        contratante='Empresa SAC',
        ...
    )
    engine = TemplateEngine()
    html = engine.render(ctx)

No usa Jinja2 ni dependencias externas.
Mecanismo: regex sobre marcadores %%BLOQUE_X_START%% ... %%BLOQUE_X_END%%
           + string.Template para variables $NOMBRE.
"""

import re
import logging
from dataclasses import dataclass, field
from pathlib import Path
from string import Template

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).parent / "templates"


# =============================================================================
# CONTEXTO DE DESPACHO — datos del formulario
# =============================================================================

@dataclass
class DespachoContext:
    """
    Todos los datos del formulario necesarios para renderizar la plantilla.
    Se construye en main_window.py justo antes de llamar a render().
    """

    # ── Selecciones de la UI ───────────────────────────────────────────────────
    empresa:    str = ""    # 'RRGG' | 'Transportes'
    tpl_l1:     str = ""    # 'Póliza' | 'Endoso' | 'Declaración mensual'
    tpl_l2:     str = ""    # ej. 'Despacho individual', 'Colectivo', etc.

    # ── Campos fijos ──────────────────────────────────────────────────────────
    contratante:    str = ""
    contacto:       str = ""
    cia:            str = ""
    vigencia_ini:   str = ""    # año, ej. "2024"
    vigencia_fin:   str = ""    # año, ej. "2025"
    mes_decl:       str = ""    # solo para Declaración mensual, ej. "Marzo 2025"

    # ── Filas dinámicas de póliza [{ramo, pol}] ───────────────────────────────
    # Índice 0 = fila base (siempre presente). Máx 12 para programa.
    polizas: list[dict] = field(default_factory=list)

    # ── Filas dinámicas de endoso [{ramo, pol, end, mov}] ────────────────────
    # Índice 0 = fila base. Máx 5 para colectivo.
    endosos: list[dict] = field(default_factory=list)

    # ── Filas dinámicas de declaración [{nro_decl, mes}] ─────────────────────
    # Índice 0 = fila base. Máx 5 para colectivo.
    declaraciones: list[dict] = field(default_factory=list)

    # ── Label dinámico del endoso (desde nomenclatura_comprobantes) ───────────
    label_endoso: str = "Nro. de Endoso"

    # ── Asunto (para referencia; no se inyecta en el HTML) ────────────────────
    asunto: str = ""

    # ── Colores de acento (resueltos según empresa) ───────────────────────────
    color_acento:       str = "#0078d4"
    color_acento_dark:  str = "#005a9e"

    # ── Helpers de clasificación ──────────────────────────────────────────────
    def es_poliza(self) -> bool:
        return self.tpl_l1 == "Póliza"

    def es_endoso(self) -> bool:
        return self.tpl_l1 == "Endoso"

    def es_decl(self) -> bool:
        return self.tpl_l1 == "Declaración mensual"

    def es_programa(self) -> bool:
        return "programa" in self.tpl_l2.lower()

    def es_colectivo(self) -> bool:
        return "colectivo" in self.tpl_l2.lower()


# =============================================================================
# MOTOR DE PLANTILLAS
# =============================================================================

class TemplateEngine:
    """
    Motor que toma un DespachoContext y produce HTML final.

    Proceso:
      1. Leer plantilla base (rrgg.html o transportes.html)
      2. Eliminar bloques que no aplican con _remove_block()
      3. Construir el dict de variables
      4. Sustituir con string.Template.safe_substitute()
    """

    def __init__(self, templates_dir: Path = _TEMPLATES_DIR) -> None:
        self._dir = templates_dir

    # ── Punto de entrada ──────────────────────────────────────────────────────

    def render(self, ctx: DespachoContext) -> str:
        """
        Renderiza la plantilla HTML completa para el contexto dado.

        Args:
            ctx: DespachoContext con todos los datos del formulario.

        Returns:
            String HTML listo para inyectar en Outlook como HTMLBody.
            Retorna string de error HTML si la plantilla no se encuentra.
        """
        tpl_file = "rrgg.html" if ctx.empresa == "RRGG" else "transportes.html"
        tpl_path = self._dir / tpl_file

        try:
            raw = tpl_path.read_text(encoding="utf-8")
        except OSError as e:
            logger.error("No se pudo leer la plantilla %s: %s", tpl_path, e)
            return self._error_html(str(e))

        html = self._apply_blocks(raw, ctx)
        variables = self._build_variables(ctx)
        html = Template(html).safe_substitute(variables)

        # Limpiar marcadores residuales (bloques vacíos mal formados)
        html = re.sub(r'%%[A-Z0-9_]+(?:_START|_END)%%\n?', '', html)

        return html

    # ── Bloques condicionales ─────────────────────────────────────────────────

    def _apply_blocks(self, html: str, ctx: DespachoContext) -> str:
        """
        Decide qué bloques conservar y cuáles eliminar según el contexto.
        Procesa los bloques en el orden correcto para evitar conflictos.
        """
        # ── Bloques principales por L1 ────────────────────────────────────────
        if ctx.es_poliza():
            html = self._keep_block(html, "BLOQUE_FILAS_POLIZA")
            html = self._remove_block(html, "BLOQUE_ENDOSO")
            html = self._remove_block(html, "BLOQUE_DECLARACION")
            html = self._keep_block(html, "BLOQUE_VIGENCIA_ANUAL")
            html = self._remove_block(html, "BLOQUE_MES_DECLARACION")

        elif ctx.es_endoso():
            html = self._remove_block(html, "BLOQUE_FILAS_POLIZA")
            html = self._keep_block(html, "BLOQUE_ENDOSO")
            html = self._remove_block(html, "BLOQUE_DECLARACION")
            html = self._keep_block(html, "BLOQUE_VIGENCIA_ANUAL")
            html = self._remove_block(html, "BLOQUE_MES_DECLARACION")

        elif ctx.es_decl():
            html = self._remove_block(html, "BLOQUE_FILAS_POLIZA")
            html = self._remove_block(html, "BLOQUE_ENDOSO")
            html = self._keep_block(html, "BLOQUE_DECLARACION")
            html = self._remove_block(html, "BLOQUE_VIGENCIA_ANUAL")
            html = self._keep_block(html, "BLOQUE_MES_DECLARACION")

        # ── Filas extra de póliza ─────────────────────────────────────────────
        n_pol = len(ctx.polizas)
        for i in range(1, 12):    # filas extra 1..11
            bloque = f"FILA_POLIZA_EXTRA_{i}"
            if i < n_pol:
                html = self._keep_block(html, bloque)
            else:
                html = self._remove_block(html, bloque)

        # ── Filas extra de endoso ─────────────────────────────────────────────
        n_end = len(ctx.endosos)
        for i in range(1, 5):    # filas extra 1..4
            bloque = f"FILA_ENDOSO_EXTRA_{i}"
            if i < n_end:
                html = self._keep_block(html, bloque)
            else:
                html = self._remove_block(html, bloque)

        # ── Filas extra de declaración ────────────────────────────────────────
        n_decl = len(ctx.declaraciones)
        for i in range(1, 5):    # filas extra 1..4
            bloque = f"FILA_DECL_EXTRA_{i}"
            if i < n_decl:
                html = self._keep_block(html, bloque)
            else:
                html = self._remove_block(html, bloque)

        return html

    @staticmethod
    def _remove_block(html: str, block_name: str) -> str:
        """Elimina todo el contenido entre %%BLOCK_START%% y %%BLOCK_END%%."""
        pattern = rf'%%{re.escape(block_name)}_START%%.*?%%{re.escape(block_name)}_END%%\n?'
        return re.sub(pattern, '', html, flags=re.DOTALL)

    @staticmethod
    def _keep_block(html: str, block_name: str) -> str:
        """Elimina solo los marcadores, conservando el contenido interior."""
        html = html.replace(f'%%{block_name}_START%%\n', '')
        html = html.replace(f'%%{block_name}_START%%', '')
        html = html.replace(f'%%{block_name}_END%%\n', '')
        html = html.replace(f'%%{block_name}_END%%', '')
        return html

    # ── Variables de sustitución ──────────────────────────────────────────────

    def _build_variables(self, ctx: DespachoContext) -> dict:
        """
        Construye el diccionario completo de variables para Template.safe_substitute().
        Valores vacíos se reemplazan con '—' para que el correo no quede con huecos.
        """
        def v(val: str) -> str:
            """Valor o guión si vacío."""
            return val.strip() if val and val.strip() else "—"

        vigencia = (
            f"{v(ctx.vigencia_ini)} – {v(ctx.vigencia_fin)}"
            if ctx.vigencia_ini or ctx.vigencia_fin
            else "—"
        )

        # Cuerpo del mensaje según L2
        cuerpo = self._build_cuerpo(ctx)

        variables: dict = {
            # Colores
            "COLOR_ACENTO":      ctx.color_acento,
            "COLOR_ACENTO_DARK": ctx.color_acento_dark,

            # Header
            "EMPRESA_NOMBRE":  "RRGG Seguros" if ctx.empresa == "RRGG" else "Transportes",
            "TIPO_PLANTILLA":  f"{ctx.tpl_l1} · {ctx.tpl_l2}" if ctx.tpl_l2 else ctx.tpl_l1,
            "BADGE_TEXTO":     ctx.tpl_l2.upper() if ctx.tpl_l2 else ctx.tpl_l1.upper(),

            # Datos fijos
            "CONTRATANTE": v(ctx.contratante),
            "CONTACTO":    v(ctx.contacto),
            "CIA":         v(ctx.cia),
            "VIGENCIA":    vigencia,
            "MES_DECLARACION": v(ctx.mes_decl),

            # Endoso
            "LABEL_ENDOSO": ctx.label_endoso,

            # Cuerpo
            "CUERPO_PRINCIPAL": cuerpo,
        }

        # Filas de póliza (índices 0..11)
        for i, pol in enumerate(ctx.polizas[:12]):
            variables[f"RAMO_{i}"]   = v(pol.get("ramo", ""))
            variables[f"POLIZA_{i}"] = v(pol.get("pol", ""))
        # Rellenar los no usados para que safe_substitute no deje $RAMO_x
        for i in range(len(ctx.polizas), 12):
            variables[f"RAMO_{i}"]   = "—"
            variables[f"POLIZA_{i}"] = "—"

        # Filas de endoso (índices 0..4)
        for i, end in enumerate(ctx.endosos[:5]):
            variables[f"ENDOSO_{i}"]     = v(end.get("end", ""))
            variables[f"MOVIMIENTO_{i}"] = v(end.get("mov", ""))
            # Filas extra tienen índice E1..E4 para ramo/poliza adicional
            if i > 0:
                variables[f"RAMO_E{i}"]   = v(end.get("ramo", ""))
                variables[f"POLIZA_E{i}"] = v(end.get("pol", ""))
        # La fila base (0) toma ramo/poliza de ctx.polizas[0] o ctx.endosos[0]
        if ctx.endosos:
            variables["RAMO_0"]   = v(ctx.endosos[0].get("ramo", ""))
            variables["POLIZA_0"] = v(ctx.endosos[0].get("pol", ""))
        for i in range(len(ctx.endosos), 5):
            variables[f"ENDOSO_{i}"]     = "—"
            variables[f"MOVIMIENTO_{i}"] = "—"
        for i in range(1, 5):
            variables.setdefault(f"RAMO_E{i}",   "—")
            variables.setdefault(f"POLIZA_E{i}", "—")

        # Filas de declaración (índices 0..4)
        for i, decl in enumerate(ctx.declaraciones[:5]):
            variables[f"DECL_{i}"]     = v(decl.get("nro_decl", ""))
            variables[f"MES_DECL_{i}"] = v(decl.get("mes", ""))
        for i in range(len(ctx.declaraciones), 5):
            variables[f"DECL_{i}"]     = "—"
            variables[f"MES_DECL_{i}"] = "—"

        return variables

    # ── Cuerpo del mensaje ────────────────────────────────────────────────────

    def _build_cuerpo(self, ctx: DespachoContext) -> str:
        """
        Genera el párrafo principal del correo según la selección L1+L2.
        Retorna HTML (puede incluir <p> y <strong>).
        """
        c = ctx.contratante or "[cliente]"
        cia = ctx.cia or "[CIA]"
        vigencia = (
            f"{ctx.vigencia_ini}–{ctx.vigencia_fin}"
            if ctx.vigencia_ini or ctx.vigencia_fin else "—"
        )
        mes = ctx.mes_decl or "—"

        cuerpos = {
            # Póliza
            ("Póliza", "Despacho individual"):
                f"<p>Por medio del presente hacemos despacho de la <strong>Póliza de Seguros</strong> "
                f"emitida para <strong>{c}</strong>, con la compañía aseguradora <strong>{cia}</strong>. "
                f"Vigencia: <strong>{vigencia}</strong>.</p>"
                f"<p>Favor confirmar la correcta recepción de la documentación adjunta.</p>",

            ("Póliza", "Despacho programa"):
                f"<p>Nos permitimos hacer despacho del <strong>Programa de Seguros</strong> vigente "
                f"del cliente <strong>{c}</strong>, asegurado con <strong>{cia}</strong>. "
                f"Vigencia del programa: <strong>{vigencia}</strong>.</p>"
                f"<p>Adjuntamos la documentación completa para su revisión y archivo.</p>",

            ("Póliza", "Regularización (individual)"):
                f"<p>Comunicamos la <strong>Regularización</strong> de la póliza del cliente "
                f"<strong>{c}</strong>, compañía <strong>{cia}</strong>. "
                f"Vigencia: <strong>{vigencia}</strong>.</p>"
                f"<p>Agradecemos su comprensión ante el ajuste realizado.</p>",

            ("Póliza", "Regularización (programa)"):
                f"<p>Comunicamos la <strong>Regularización del Programa de Seguros</strong> del cliente "
                f"<strong>{c}</strong>, compañía <strong>{cia}</strong>. "
                f"Vigencia: <strong>{vigencia}</strong>.</p>"
                f"<p>Favor de tener a bien el presente ajuste en su registro.</p>",

            # Endoso
            ("Endoso", "Individual"):
                f"<p>Hacemos despacho del <strong>Endoso</strong> emitido para <strong>{c}</strong>, "
                f"compañía <strong>{cia}</strong>.</p>"
                f"<p>Adjuntamos la documentación para archivo y validación.</p>",

            ("Endoso", "Colectivo"):
                f"<p>Hacemos despacho del <strong>Endoso Colectivo</strong> emitido para "
                f"<strong>{c}</strong>, compañía <strong>{cia}</strong>.</p>"
                f"<p>Adjuntamos la documentación correspondiente a cada póliza incluida.</p>",

            ("Endoso", "Regularización (individual)"):
                f"<p>Comunicamos la <strong>Regularización de Endoso</strong> para el cliente "
                f"<strong>{c}</strong>, compañía <strong>{cia}</strong>.</p>",

            ("Endoso", "Regularización (colectivo)"):
                f"<p>Comunicamos la <strong>Regularización de Endoso Colectivo</strong> para el cliente "
                f"<strong>{c}</strong>, compañía <strong>{cia}</strong>.</p>",

            # Declaración mensual (solo Transportes)
            ("Declaración mensual", "Individual"):
                f"<p>Hacemos despacho de la <strong>Declaración Mensual</strong> del cliente "
                f"<strong>{c}</strong>, compañía <strong>{cia}</strong>. "
                f"Período declarado: <strong>{mes}</strong>.</p>"
                f"<p>Adjuntamos la declaración para su proceso y registro.</p>",

            ("Declaración mensual", "Colectivo"):
                f"<p>Hacemos despacho de la <strong>Declaración Mensual Colectiva</strong> del cliente "
                f"<strong>{c}</strong>, compañía <strong>{cia}</strong>. "
                f"Período declarado: <strong>{mes}</strong>.</p>"
                f"<p>Adjuntamos las declaraciones correspondientes para su proceso y registro.</p>",

            ("Declaración mensual", "Regularización (individual)"):
                f"<p>Comunicamos la <strong>Regularización de Declaración Mensual</strong> del cliente "
                f"<strong>{c}</strong>, compañía <strong>{cia}</strong>. "
                f"Período regularizado: <strong>{mes}</strong>.</p>",

            ("Declaración mensual", "Regularización (colectivo)"):
                f"<p>Comunicamos la <strong>Regularización de Declaración Mensual Colectiva</strong> "
                f"del cliente <strong>{c}</strong>, compañía <strong>{cia}</strong>. "
                f"Período regularizado: <strong>{mes}</strong>.</p>",
        }

        key = (ctx.tpl_l1, ctx.tpl_l2)
        cuerpo = cuerpos.get(key)

        if cuerpo is None:
            logger.warning("Combinación L1+L2 sin cuerpo definido: %s", key)
            cuerpo = (
                f"<p>Adjuntamos la documentación correspondiente para "
                f"<strong>{c}</strong>.</p>"
            )

        return cuerpo

    # ── HTML de error ─────────────────────────────────────────────────────────

    @staticmethod
    def _error_html(mensaje: str) -> str:
        return (
            f"<html><body style='font-family:Arial;color:#c42b1c;padding:20px'>"
            f"<h3>Error al cargar la plantilla</h3>"
            f"<p>{mensaje}</p>"
            f"</body></html>"
        )
