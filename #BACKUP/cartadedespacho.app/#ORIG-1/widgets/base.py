# coding: utf-8
"""
widgets/base.py — Base input widgets.

NoNewlineLineEdit: QLineEdit that strips newlines/carriage returns/tabs when
text is pasted or set programmatically. Use everywhere instead of plain
QLineEdit to prevent hidden line breaks corrupting generated documents.
"""

from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import QMimeData

class NoNewlineLineEdit(QLineEdit):
    """
    QLineEdit that removes newlines, carriage returns and tabs when text
    is pasted or set programmatically. Prevents invisible line breaks from
    entering form fields and corrupting generated documents.
    """

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


