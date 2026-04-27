# coding: utf-8
"""
app.py — Punto de entrada de MailDeDespacho.

Uso:
    python app.py
    (o desde el ejecutable generado por PyInstaller)
"""

import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from theme import build_qss, get_palette
from ui.main_window import MainWindow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)


def main():
    # Soporte de DPI alto en Windows
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("MailDeDespacho")
    app.setOrganizationName("SGO")

    # Aplicar paleta y QSS
    app.setPalette(get_palette())
    app.setStyleSheet(build_qss())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
