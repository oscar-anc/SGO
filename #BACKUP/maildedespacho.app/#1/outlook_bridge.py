# coding: utf-8
"""
outlook_bridge.py — Integración con Microsoft Outlook vía win32com.

Responsabilidades:
  - Abrir una ventana de "Nuevo correo" o "Responder a todos" en Outlook
  - Inyectar el HTML de la plantilla como cuerpo del correo
  - Establecer el asunto
  - NO enviar el correo automáticamente — siempre Display() para revisión

Requisitos:
  - Windows con Microsoft Outlook Desktop instalado y configurado
  - pip install pywin32

Uso:
    from outlook_bridge import OutlookBridge, OutlookError

    bridge = OutlookBridge()
    try:
        bridge.nuevo_correo(
            asunto="DESPACHO DE PÓLIZA | ...",
            html_body="<html>...</html>"
        )
    except OutlookError as e:
        mostrar_error(str(e))
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# win32com solo disponible en Windows — importación diferida para no romper
# en otros entornos (tests, CI, macOS de desarrollo)
try:
    import win32com.client as _win32
    _WIN32_AVAILABLE = True
except ImportError:
    _WIN32_AVAILABLE = False
    logger.warning(
        "pywin32 no está instalado. OutlookBridge funcionará en modo simulación."
    )


class OutlookError(Exception):
    """Error durante la integración con Outlook. Mostrar mensaje al usuario."""
    pass


class OutlookBridge:
    """
    Puente entre la app y Outlook Desktop vía win32com.

    Uso de instancia única por sesión — Dispatch() es costoso.
    La instancia se reutiliza para múltiples llamadas.
    """

    def __init__(self) -> None:
        self._outlook = None

    # ── Conexión ──────────────────────────────────────────────────────────────

    def _get_outlook(self):
        """
        Retorna la instancia de Outlook, creándola si no existe.
        Reutiliza la instancia existente si Outlook ya está abierto.

        Raises:
            OutlookError: Si Outlook no está instalado o no se puede conectar.
        """
        if not _WIN32_AVAILABLE:
            raise OutlookError(
                "pywin32 no está instalado.\n"
                "Ejecuta: pip install pywin32"
            )

        if self._outlook is None:
            try:
                # GetActiveObject reutiliza Outlook si ya está abierto
                try:
                    self._outlook = _win32.GetActiveObject("Outlook.Application")
                    logger.debug("Reutilizando instancia de Outlook activa.")
                except Exception:
                    self._outlook = _win32.Dispatch("Outlook.Application")
                    logger.debug("Nueva instancia de Outlook creada.")
            except Exception as e:
                raise OutlookError(
                    f"No se pudo conectar con Outlook.\n"
                    f"Verifica que Outlook Desktop esté instalado y configurado.\n"
                    f"Detalle: {e}"
                ) from e

        return self._outlook

    def reset_connection(self) -> None:
        """Fuerza reconexión en la próxima llamada. Usar si Outlook se cerró."""
        self._outlook = None

    # ── Acciones principales ──────────────────────────────────────────────────

    def nuevo_correo(
        self,
        asunto: str,
        html_body: str,
        para: str = "",
    ) -> None:
        """
        Abre una ventana de nuevo correo en Outlook con la plantilla aplicada.
        No envía — solo Display() para que el despachador revise y envíe.

        Args:
            asunto:    Asunto pre-llenado del correo.
            html_body: Cuerpo HTML completo de la plantilla renderizada.
            para:      Dirección de email del destinatario (opcional).
                       Si está vacío, el campo To: queda en blanco.

        Raises:
            OutlookError: Si hay un problema con Outlook.
        """
        outlook = self._get_outlook()

        try:
            mail = outlook.CreateItem(0)  # 0 = olMailItem

            mail.Subject  = asunto
            mail.HTMLBody = html_body

            if para:
                mail.To = para

            mail.Display(False)  # False = no modal, permite seguir usando la app
            logger.info("Nuevo correo abierto en Outlook. Asunto: %s", asunto)

        except OutlookError:
            raise
        except Exception as e:
            self.reset_connection()
            raise OutlookError(
                f"Error al crear el correo en Outlook.\n"
                f"Detalle: {e}"
            ) from e

    def responder_a_todos(
        self,
        msg_path: str,
        asunto: str,
        html_body: str,
        mantener_asunto_original: bool = True,
    ) -> None:
        """
        Abre una ventana de "Responder a todos" a partir de un archivo .msg,
        con la plantilla HTML inyectada al inicio del cuerpo.

        Args:
            msg_path:   Ruta absoluta al archivo .msg original.
            asunto:     Asunto a usar si mantener_asunto_original=False.
            html_body:  Cuerpo HTML de la plantilla (se prepende al hilo original).
            mantener_asunto_original: Si True, conserva el asunto del .msg.
                                      Si False, lo reemplaza con asunto.

        Raises:
            OutlookError: Si el archivo no existe o hay problemas con Outlook.
        """
        msg_file = Path(msg_path)
        if not msg_file.exists():
            raise OutlookError(
                f"El archivo .msg no se encontró:\n{msg_path}"
            )

        outlook = self._get_outlook()

        try:
            # Cargar el .msg original
            msg_original = outlook.CreateItemFromTemplate(str(msg_file.resolve()))

            # Crear respuesta a todos
            reply = msg_original.ReplyAll()

            # Inyectar plantilla ANTES del hilo original
            # reply.HTMLBody ya contiene el hilo — lo preservamos al final
            reply.HTMLBody = html_body + "<br><br>" + reply.HTMLBody

            if not mantener_asunto_original:
                reply.Subject = asunto

            reply.Display(False)
            logger.info(
                "Responder a todos abierto. Archivo: %s | Asunto original preservado: %s",
                msg_file.name,
                mantener_asunto_original
            )

            # Liberar el objeto original (no se envía, solo se usó de base)
            try:
                msg_original.Close(0)  # 0 = olDiscard — cierra sin guardar
            except Exception:
                pass  # No crítico si falla el cierre del original

        except OutlookError:
            raise
        except Exception as e:
            self.reset_connection()
            raise OutlookError(
                f"Error al abrir la respuesta en Outlook.\n"
                f"Verifica que el archivo .msg sea válido.\n"
                f"Detalle: {e}"
            ) from e

    # ── Utilidad ──────────────────────────────────────────────────────────────

    @staticmethod
    def is_available() -> bool:
        """
        True si pywin32 está instalado y Outlook puede intentar abrirse.
        Usar para deshabilitar el botón "Abrir en Outlook" si no es posible.
        """
        return _WIN32_AVAILABLE

    @staticmethod
    def validate_msg_file(path: str) -> tuple[bool, str]:
        """
        Valida que la ruta dada sea un archivo .msg accesible.

        Returns:
            (True, "") si es válido.
            (False, mensaje_error) si no.
        """
        if not path:
            return False, "No se ha seleccionado ningún archivo .msg."
        p = Path(path)
        if not p.exists():
            return False, f"El archivo no existe:\n{path}"
        if p.suffix.lower() != ".msg":
            return False, f"El archivo debe tener extensión .msg:\n{path}"
        if not p.is_file():
            return False, f"La ruta no es un archivo:\n{path}"
        return True, ""
