# coding: utf-8
"""
widgets/base.py — Base input widgets.

NoNewlineLineEdit: QLineEdit that strips newlines/carriage returns/tabs when
text is pasted or set programmatically. Use everywhere instead of plain
QLineEdit to prevent hidden line breaks corrupting generated documents.

setMinimumHeight is applied in __init__ using QSSD['lineedit_min_height'] so
that Qt's layout engine always respects the same height value that QSS
min-height declares. Without this, layouts that size widgets from sizeHint()
(which is font-metrics-based, not QSS-based) can produce shorter fields even
when min-height is set in the stylesheet.
"""

from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import QMimeData
from theme import QSSA

class NoNewlineLineEdit(QLineEdit):
    """
    QLineEdit that removes newlines, carriage returns and tabs when text
    is pasted or set programmatically. Prevents invisible line breaks from
    entering form fields and corrupting generated documents.

    Also enforces the theme min-height at the Python layout level so all
    instances are sized consistently regardless of container or layout type.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(int(QSSA['lineedit_min_height']))
        self.setMinimumWidth(int(QSSA['lineedit_min_width']))

    def insertFromMimeData(self, source):
        if source.hasText():
            clean = (source.text()
                     .replace('\r\n', ' ').replace('\n', ' ')
                     .replace('\r', ' ').replace('\t', ' '))
            clean_mime = QMimeData()
            clean_mime.setText(clean)
            super().insertFromMimeData(clean_mime)
        else:
            super().insertFromMimeData(source)

    def setText(self, text: str):
        if text:
            text = (text.replace('\r\n', ' ').replace('\n', ' ')
                    .replace('\r', ' ').replace('\t', ' '))
        super().setText(text)


