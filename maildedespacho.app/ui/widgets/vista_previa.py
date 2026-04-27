# coding: utf-8
"""
ui/widgets/vista_previa.py — Vista previa del correo usando QWebEngineView.

Muestra el HTML renderizado de la plantilla en tiempo real.
El usuario no puede editar el contenido (solo lectura).
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import QUrl
from theme import QSSD

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    _WEB_AVAILABLE = True
except ImportError:
    _WEB_AVAILABLE = False


class VistaPrevia(QWidget):
    """
    Contenedor de la vista previa del correo.
    Usa QWebEngineView si está disponible, QLabel de fallback si no.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(*QSSD["margins_preview"])
        lay.setSpacing(0)

        frame = QFrame()
        frame.setObjectName("PreviewContainer")
        f_lay = QVBoxLayout(frame)
        f_lay.setContentsMargins(0, 0, 0, 0)

        if _WEB_AVAILABLE:
            self._view = QWebEngineView()
            self._view.setMinimumHeight(QSSD["preview_min_height"])
            # Deshabilitar interacción — solo lectura
            self._view.page().setBackgroundColor(__import__("PySide6.QtGui", fromlist=["QColor"]).QColor("white"))
            self._view.setContextMenuPolicy(__import__("PySide6.QtCore", fromlist=["Qt"]).Qt.NoContextMenu)
            f_lay.addWidget(self._view)
            self._fallback = None
        else:
            self._view = None
            self._fallback = QLabel(
                "Vista previa no disponible.\n"
                "Instala PySide6-WebEngine para activarla:\n"
                "pip install PySide6-WebEngine"
            )
            self._fallback.setWordWrap(True)
            self._fallback.setAlignment(__import__("PySide6.QtCore", fromlist=["Qt"]).Qt.AlignCenter)
            self._fallback.setStyleSheet(
                f"color: {QSSD['preview_empty_text']}; padding: 20px; font-size: 12px;"
            )
            self._fallback.setMinimumHeight(QSSD["preview_min_height"])
            f_lay.addWidget(self._fallback)

        lay.addWidget(frame)

    def set_html(self, html: str):
        """Actualiza el contenido de la vista previa."""
        if self._view:
            self._view.setHtml(html, QUrl("about:blank"))
        elif self._fallback:
            self._fallback.setText(
                "Vista previa: HTML generado correctamente.\n"
                "(Instala PySide6-WebEngine para ver el renderizado)"
            )

    def clear(self):
        """Limpia la vista previa."""
        if self._view:
            self._view.setHtml(
                f"<html><body style='background:#f5f7fa;'>"
                f"<p style='color:{QSSD['preview_empty_text']};font-family:Arial;"
                f"font-size:13px;padding:20px;'>Complete los datos para ver la plantilla...</p>"
                f"</body></html>"
            )
        elif self._fallback:
            self._fallback.setText("Complete los datos para ver la plantilla...")
